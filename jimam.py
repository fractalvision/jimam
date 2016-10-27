#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""JIMAM: Middleware API to convert incoming JIRA events
into Mattermost format and relay them to a target webhook"""
from flask import Flask, request
from flask_restful import Api, Resource
from werkzeug.contrib.fixers import ProxyFix
from api.core import *

__author__ = 'https://github.com/fractalvision/'

app = Flask(__name__)
api = Api(app)


class Jimam(Resource):
    def post(self):
        user_id, user_key = request.args.get('user_id') or 'absent', request.args.get('user_key') or 'absent'
        json_data = request.get_json(force=True)
        event = parse_event(json_data)
        if event:
            relayed = send(event, MATTERMOST_WEBHOOK)
            if 'ConnectionError' in str(relayed):
                log('Delivery failed! [ {} ]'.format(relayed), save=DEBUG)
            else:
                log('Bridged JIRA event from: ' + user_id + '\n', save=DEBUG)

    def get(self):
        return 'JIMAM: JIRA to Mattermost translation API'

api.add_resource(Jimam, '/jimam{}'.format(API_ROOT))

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(host=JIMAM_IP, port=JIMAM_PORT, debug=DEBUG)
