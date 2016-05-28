from flask import Flask
from flask import render_template
from flask import abort
from flask import request
from dateutil.parser import parse
import requests
import json
import os


application = Flask(__name__)
__reg_server = os.getenv('DOCKER_REGISTRY_URL', 'localhost')
__reg_user = os.getenv('DOCKER_REGISTRY_USER', '')
__reg_pass = os.getenv('DOCKER_REGISTRY_PASSWORD', '')


@application.route('/')
@application.route('/index')
def index():
    resp = requests.get('https://%s/v2/_catalog' % __reg_server,
                            auth=(__reg_user, __reg_pass), 
                            verify=False)
    if resp.status_code == 200:
        print(resp.json())
        return render_template("reg.htm",
                               registry=__reg_server,
                               repos=resp.json())
    else:
        abort(500)

    
@application.route('/repo/<name>')
def repo(name):
    resp = requests.get('https://%s/v2/%s/tags/list' % (__reg_server, name),
                        auth=(__reg_user, __reg_pass),
                        verify=False)

    if resp.status_code == 200 or resp.status_code == 404:
        repo = resp.json()

        # Last Updated
        if 'tags' in repo:
            repo['updated'] = {}
            for tag in repo['tags']:
                manifest = requests.get('https://%s/v2/%s/manifests/%s' % (__reg_server, name, tag),
                                        auth=(__reg_user, __reg_pass), 
                                        verify=False)

                if 'history' in manifest.json():
                    created = json.loads(manifest.json()['history'][0]['v1Compatibility'])['created']
                    repo['updated'][tag] = parse(created).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    if 'errors' in manifest.json():
                        repo['updated'][tag] = manifest.json()['errors'][0]['message']

        print(repo)
        return render_template("repo.htm",
                               registry=__reg_server,
                               repo=repo)
    else:
        abort(500)


@application.route('/health')
def health():
    return "OK"


if __name__ == '__main__':
    application.debug = True
    application.run()

