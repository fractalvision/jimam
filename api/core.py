# -*- coding: utf-8 -*-
"""JIMAM: API system routines"""

from __future__ import print_function
from settings import *
import sys
import datetime
import re
import requests

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


def parse_event(json_data, post_content=''):
    get_url = re.compile(r'(.*?)\/rest\/api\/.*')
    try:
        webevent = json_data['webhookEvent']
    except:
        return 'Wrong data'

    if 'issue' in json_data.keys():
        display_name = json_data['user']['displayName']
        issue_id = json_data['issue']['key']
        issue_rest_url = json_data['issue']['self']
        issue_url = '{}/browse/{}'.format(get_url.match(issue_rest_url).group(1), issue_id)
        priority = json_data['issue']['fields']['priority']['name'] if json_data['issue']['fields']['priority'] else 'empty'
        issue_event_type_name = json_data['issue_event_type_name']
        summary = json_data['issue']['fields']['summary']
        assignee = json_data['issue']['fields']['assignee']['displayName'] if json_data['issue']['fields']['assignee'] else 'empty'

        if webevent.endswith('created'):
            post_content = '##### ' + display_name + ' has created issue: [ ' + issue_id + ' ] ' + issue_url + '\n\n' \
                           + '###### ', + summary + '\n\nPriority: ' + priority + ', assignee: ' + assignee + '\r\n'
        elif webevent.endswith('updated'):
            post_content = '##### ' + display_name + ' has updated issue: [ ' + issue_id + ' ] ' + issue_url + '\n\n' \
                           + '###### ', +  summary + '\n\nPriority: ' + priority + ', assignee: ' + assignee + '\r\n'
        elif webevent.endswith('deleted'):
            post_content = '##### ' + display_name + ' has deleted issue: [ ' + issue_id + ' ] ' + issue_url + '\n\n' \
                           + '###### ', +  summary + '\n\nPriority: ' + priority + ', assignee: ' + assignee + '\r\n'
        else:
            log('unhandled event: {}, {}'.format(webevent, json_data), save=True)

        if 'changelog' in json_data.keys():
            changed_items = json_data['changelog']['items']
            for item in changed_items:
                post_content += ''.join(['\n##### Changed: ', item['field'].upper(), '\n'])
                for field, value in item.iteritems():
                    if field in ('fromString', 'toString'):
                        value = value or 'empty'
                        post_content += ''.join([value, ' > ' if field.startswith('from') else '' + '\n\n'])

        if 'comment' in json_data.keys():
            comment = json_data['comment']['body']
            if issue_event_type_name in ('issue_commented',):
                post_content += '\n##### New comment:\n\n' + comment
            elif issue_event_type_name in ('issue_comment_deleted',):
                post_content += '\n##### Removed comment:\n\n' + comment

    return post_content