# -*- coding: utf-8 -*-
"""JIMAM: API system routines"""
from __future__ import print_function
import datetime
import re
import requests
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
        print('\n%s >>> %s\n' % (now, event), file=sys.stderr)
    if save:
        with open(LOG_FILE, 'a+') as log_file:
            print('\n%s >>> %s\n' % (now, event), file=log_file)


def send(event, url):
    try:
        post = requests.post(url, json={'username': JIMAM_USERNAME, 'text': event})
        return post.status_code
    except Exception as e:
        return e


def parse_event(json_data, post_content=''):
    def _tag_users(text):
        get_tag = re.compile(r'\W~(.*)](.*)')
        tag = lambda token: '@%s%s' % (get_tag.match(token).group(1).lower() if get_tag.search(token) else token,
                                       get_tag.match(token).group(2)) if get_tag.search(token) else token
        return ' '.join(map(tag, text.split())) if text else text

    if all(['webhookEvent' in json_data.keys(), 'issue' in json_data.keys()]):
        webevent = json_data['webhookEvent']
        display_name = json_data.get('user') and json_data['user'].get('displayName') or 'System'
        issue_id = json_data['issue']['key']
        issue_rest_url = json_data['issue']['self']
        get_url = re.compile(r'(.*?)\/rest\/api\/.*')
        issue_url = '%s/browse/%s' % (get_url.match(issue_rest_url).group(1), issue_id)
        summary = json_data['issue']['fields'].get('summary', '')
        description = _tag_users(json_data['issue']['fields'].get('description', ''))
        issue_event_type_name = json_data.get('issue_event_type_name', '')

        if json_data['issue']['fields'].get('priority'):
            priority = json_data['issue']['fields']['priority']['name']
        else:
            priority = 'empty'

        if json_data['issue']['fields'].get('assignee'):
            assignee = json_data['issue']['fields']['assignee']['displayName']
        else:
            assignee = 'empty'

        if webevent.endswith('created'):
            post_content = ''.join(['\n##### ', display_name, ' has created issue: [', issue_id, '](', issue_url,
                                    ')\n\n', summary, '\n\n> ', description, '\n\n###### Priority: ', priority,
                                    ' | Assignee: ', assignee, '\r\n'])
        elif any([webevent.endswith('updated'), webevent.endswith('deleted')]):
            post_content = ''.join(['\n##### ', display_name, ' has ', webevent[-7:], ' issue: [', issue_id, '](',
                                    issue_url, ')\n\n', summary, '\n\n###### Priority: ', priority, ' | Assignee: ',
                                    assignee, '\r\n'])

        if 'changelog' in json_data.keys():
            changed_items = json_data['changelog']['items']
            for item in changed_items:
                post_content += (''.join(['\n##### Changed: ', item['field'].upper()]))
                for field, value in item.iteritems():
                    if field in ('fromString', 'toString'):
                        value = _tag_users(value) if value else 'empty'
                        if item['field'] in ('summary', 'description'):
                            post_content += ''.join(['\n\n> ', value if field.startswith('to') else '', '\n\n'])
                        else:
                            post_content += ''.join([' [ ' if field.startswith('from') else '',
                                                     value, ' > ' if field.startswith('from') else ' ]\n'])

        if 'comment' in json_data.keys():
            comment = _tag_users(json_data['comment']['body'])
            if issue_event_type_name in ('issue_commented',):
                post_content += ''.join(['\n##### New comment:\n\n> ', comment, '\n\n'])

    else:
        if DEBUG:
            log('Skipped unhandled event: {}, {}'.format(json_data), save=DEBUG)
        else:
            log('Skipped unhandled event.')

    return post_content
