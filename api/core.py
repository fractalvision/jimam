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


def log(info, console=True, save=False):
    now = str(datetime.datetime.now())[:19]
    if console:
        print('\n%s >>> %s\n' % (now, info), file=sys.stderr)
    if save:
        with open(LOG_FILE, 'a+') as log_file:
            print('\n%s >>> %s\n' % (now, info), file=log_file)


def send(event, url):
    try:
        post = requests.post(url, json={'username': JIMAM_USERNAME, 'text': event})
        return post.status_code
    except Exception as e:
        return e


def parse_event(json_data, post_content=''):
    def _tag_users(text):
        get_tag = re.compile(r'\[\~(.*?)](.*)')
        tag = lambda token: get_tag.search(token) and '@%s%s' % (get_tag.search(token).group(1).lower(),
                                                                 get_tag.search(token).group(2).lower()) or token
        return text and ' '.join(map(tag, text.split()))

    def _tag_files(text):
        get_tag = re.compile(r'\[\^(.*?)](.*)')
        tag = lambda token: get_tag.search(token) and 'file: %s%s' % (get_tag.search(token).group(1).lower(),
                                                                      get_tag.search(token).group(2).lower()) or token
        return text and ' '.join(map(tag, text.split()))

    def _unfmt(text):
        get_tag = re.compile(r'{(.*?)}')
        tag = lambda token: '```' if get_tag.search(token) and get_tag.search(token).group(1) else token
        return text and ' '.join(map(tag, text.split()))

    if all(['webhookEvent' in json_data.keys(), 'issue' in json_data.keys()]):
        webevent = json_data['webhookEvent']
        display_name = json_data.get('user') and json_data['user'].get('displayName') or 'System'
        issue_id = json_data['issue']['key']
        issue_rest_url = json_data['issue']['self']
        get_url = re.compile(r'(.*?)\/rest\/api\/.*')
        issue_url = '%s/browse/%s' % (get_url.match(issue_rest_url).group(1), issue_id)
        summary = _tag_users(_tag_files(_unfmt(json_data['issue']['fields'].get('summary', ''))))
        description = _tag_users(_tag_files(_unfmt(json_data['issue']['fields'].get('description', ''))))
        issue_event_type_name = json_data.get('issue_event_type_name', '')

        priority = (json_data['issue']['fields'].get('priority') and
                    json_data['issue']['fields']['priority']['name'] or 'empty')

        assignee = (json_data['issue']['fields'].get('assignee') and
                    json_data['issue']['fields']['assignee']['displayName'] or 'empty')

        if webevent.endswith('created'):
            post_content = ('\n##### %s has created issue: [%s](%s)\n\n'
                            '%s\n\n> %s\n\n'
                            '###### Priority: %s | Assignee: %s\r\n') % (display_name, issue_id, issue_url,
                                                                         summary, description, priority, assignee)

        elif any([webevent.endswith('updated'), webevent.endswith('deleted')]):
            post_content = ('\n##### %s has %s issue: [%s](%s)\n\n'
                            '%s\n\n###### Priority: %s | Assignee: %s\r\n') % (display_name, webevent[-7:], issue_id,
                                                                               issue_url, summary, priority, assignee)

        if 'changelog' in json_data.keys():
            changed_items = json_data['changelog']['items']
            for item in changed_items:
                field = item['field']
                from_value = item['fromString'] and _tag_users(_tag_files(_unfmt(item['fromString']))) or 'empty'
                to_value = item['toString'] and _tag_users(_tag_files(_unfmt(item['toString']))) or 'empty'
                post_content += '\n##### %s: ' % field.upper()
                if field in ('summary', 'description'):
                    post_content += '\n\n> %s\n' % to_value
                else:
                    post_content += '~~%s~~ %s' % (from_value, to_value)

        if 'comment' in json_data.keys():
            comment = _tag_users(_tag_files(_unfmt(json_data['comment']['body'])))
            if issue_event_type_name in ('issue_commented',):
                post_content += '\n##### New comment:\n\n> %s\n\n' % comment

    else:
        if DEBUG:
            log('Skipped. Raw: %s' % json_data, save=DEBUG)
        else:
            log('Do not want this. Skipped.')

    return post_content
