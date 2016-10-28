# -*- coding: utf-8 -*-
"""JIMAM: API system routines"""
from __future__ import print_function
from contextlib import closing
import datetime
import re
import requests
from StringIO import StringIO
import sys
from settings import *


__author__ = 'https://github.com/fractalvision/'

try:
    os.makedirs(os.path.join(BASEDIR, 'log'))
except OSError:
    if not os.path.isdir(os.path.join(BASEDIR, 'log')):
        raise


def log(event, console=True, save=False):
    now = str(datetime.datetime.now())[:19]
    if console:
        print('\n{} >>> {}\n'.format(now, event), file=sys.stderr)
    if save:
        with open(LOG_FILE, 'a+') as log_file:
            print('{} >>> {}\n'.format(now, event), file=log_file)


def send(event, url):
    try:
        post = requests.post(url, json={'username': JIMAM_USERNAME, 'text': event})
        return post.status_code
    except Exception as e:
        return e


def parse_event(json_data):
    def _tag_users(text):
        get_tag = re.compile(r'\W~(.*)](.*)')
        tag = lambda token: '@{}{}'.format(get_tag.match(token).group(1).lower(),
                                           get_tag.match(token).group(2)) if get_tag.search(token) else token
        return ' '.join(map(tag, text.split())) if text else text

    def _fmt(text):
        text = text and text.encode('utf8')
        get_fmt = re.compile(r'\s?({.*?})\s?')
        fmt = get_fmt.match(text).group(1) if get_fmt.match(text) else text
        return text.replace('{} '.format(fmt),
                            '{}'.format(fmt)).replace(' {}'.format(fmt), '{} '.format(fmt))

    with closing(StringIO()) as post_content:
        if all(['webhookEvent' in json_data.keys(), 'issue' in json_data.keys()]):
            webevent = json_data['webhookEvent']
            display_name = json_data['user']['displayName']
            issue_id = json_data['issue']['key']
            issue_rest_url = json_data['issue']['self']
            get_url = re.compile(r'(.*?)\/rest\/api\/.*')
            issue_url = '{}/browse/{}'.format(get_url.match(issue_rest_url).group(1), issue_id)
            summary = json_data['issue']['fields']['summary']
            description = _tag_users(_fmt(json_data['issue']['fields']['description']))

            if 'issue_event_type_name' in json_data.keys():
                issue_event_type_name = json_data['issue_event_type_name']
            else:
                issue_event_type_name = None

            if json_data['issue']['fields']['priority']:
                priority = json_data['issue']['fields']['priority']['name']
            else:
                priority = 'empty'

            if json_data['issue']['fields']['assignee']:
                assignee = json_data['issue']['fields']['assignee']['displayName']
            else:
                assignee = 'empty'

            if webevent.endswith('created'):
                post_content.write(''.join(['\n##### ', display_name, ' has created issue: [', issue_id, '](', issue_url,
                                             ')\n\n', summary, '\n\n> ', description, '\n\n###### Priority: ', priority,
                                             ' | Assignee: ', assignee, '\r\n']))
            elif any([webevent.endswith('updated'), webevent.endswith('deleted')]):
                post_content.write(''.join(['\n##### ', display_name, ' has ', webevent[-7:], ' issue: [', issue_id, '](',
                                             issue_url, ')\n\n', summary, '\n\n###### Priority: ', priority, ' | Assignee: ',
                                             assignee, '\r\n']))

            if 'changelog' in json_data.keys():
                changed_items = json_data['changelog']['items']
                for item in changed_items:
                    post_content.write(''.join(['\n##### Changed: ', item['field'].upper()]))
                    for field, value in item.iteritems():
                        if field in ('fromString', 'toString'):
                            value = _tag_users(_fmt(value)) or 'empty'
                            if item['field'] in ('summary', 'description'):
                                post_content.write(''.join(['\n\n> ', value if field.startswith('to') else '', '\n\n']))
                            else:
                                post_content.write(''.join([' [ ' if field.startswith('from') else '',
                                                            value, ' > ' if field.startswith('from') else ' ]\n']))

            if 'comment' in json_data.keys():
                comment = _tag_users(_fmt(json_data['comment']['body']))
                if issue_event_type_name in ('issue_commented',):
                    post_content.write(''.join(['\n##### New comment:\n\n> ', comment, '\n\n']))
                elif issue_event_type_name in ('issue_comment_deleted',):
                    post_content.write(''.join(['\n##### Removed comment:\n\n> ', comment, '\n\n']))
        else:
            if DEBUG:
                log('Skipped unhandled event: {}, {}'.format(json_data), save=DEBUG)
            else:
                log('Skipped unhandled event.')

        return post_content.getvalue()
