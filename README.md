## JIMAM
##### Lightweight middleware API to convert incoming JIRA issue-related events into Mattermost format and relay them to its target webhook.

###### Installation
As it's quite preferable to run any service in a separate environment in order not to mess up the system libraries 
it's better to install [virtualenv](https://github.com/pypa/virtualenv 'virtualenv') first, if you don't have it already. 

* `pip install virtualenv` 
* make the environment folder `virtualenv env_name` 
* activate it by running `source /env_name/bin/activate` 
* clone this repository `git clone git@github.com:fractalvision/jimam.git`
* install the requirements `pip install -r requirements.txt`

###### Configuration
Set up the following variables in `/jimam/api/settings.py`, defaults are:

* `DEBUG = True` switch to `False` to suppress excessive logging and tell Flask to run the app normally.
* `JIMAM_USERNAME = 'JIMAM'` username to use while sending a message.
* `JIMAM_IP = '127.0.0.1'` IP to run the API at.
* `JIMAM_PORT = 8000` listening port.
* `API_ROOT = '/default'` input webhook, appending to `http://host_ip:port/jimam/`.
* `MATTERMOST_WEBHOOK = 'https://mattermost.host/webhook'` webhook of a target channel.

###### Startup

Just run `python jimam.py` to start JIMAM as standalone Flask app, or `gunicorn jimam:app` to start it up 
as WSGI-application using [Gunicorn](http://gunicorn.org/ 'Gunicorn') in case you have to process really heavy activity. 

###### Integration
* Configure Mattermost server and create a new incoming webhook for a desired channel, note the hook URL.
* Configure JIRA Webhooks to use `http://host_ip:port/jimam/input_webhook` as a target endpoint for the required JQL. 
* Profit!

Built using awesome [Flask-RESTful](https://github.com/flask-restful/flask-restful 'RESTful').

© 2016. If you've found this app useful and somehow willing to thank the author, feel free to [donate](donate 'Thanks!').  