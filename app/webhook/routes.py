from flask import Blueprint, json, request
from app.extensions import mongo
import flask_pymongo as pymongo
from datetime import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/pushrequest', methods=["POST"])
def receiver():

    data = request.json
    actions_data = mongo.db.github_actions
    actions_data.insert({"request_id": data['commits'][0]['id'], "author": data['head_commit']['author']['username'], "action": "PUSH", "from_branch": data['ref'].split("/")[-1], "to_branch": data['ref'].split("/")[-1], "timestamp": data['head_commit']['timestamp']})
    return json.dumps({"Action" : "request accepted and stored in collections"}), 200

@webhook.route('/pullrequest', methods=["POST"])
def pullrequest():

    data = request.json
    actions_data = mongo.db.github_actions
    if data['pull_request']['merged']:
        actions_data.insert({"request_id": str(data['pull_request']['id']), "author": data['sender']['login'], "action": "MERGE", "from_branch": data['pull_request']['base']['ref'], "to_branch": data['pull_request']['head']['ref'], "timestamp": data['pull_request']['merged_at']})
    else:
        actions_data.insert({"request_id": str(data['pull_request']['id']), "author": data['sender']['login'], "action": "PULL_REQUEST", "from_branch": data['pull_request']['base']['ref'], "to_branch": data['pull_request']['head']['ref'], "timestamp": data['pull_request']['updated_at']})

    return json.dumps({"Action" : "request accepted and stored in collections"}), 200

@webhook.route('', methods=["GET"])
def action_update():
    actions_data = mongo.db.github_actions
    data = actions_data.find().sort("_id",-1).limit(1)
    statement = "Nothing in database collection"
    for i in data:
        time = datetime.strptime(i['timestamp'], "%Y-%m-%dT%H:%M:%S%z").strftime("%d %b %-I:%M %p %Z")
        if i['action'] == 'PUSH':
            statement = i['author'] + " pushed to " + i['to_branch'] + " on " + time
        elif i['action'] == 'PULL_REQUEST':
            statement = i['author'] + " submitted a pull request from " + i['from_branch'] + " to " + i['to_branch'] + " on " + time
        elif i['action'] == 'MERGE':
            statement = i['author'] + " merged branch " + i['from_branch'] + " to " + i['to_branch'] + " on " + time
    
    # statement = statement if statement else "Nothing in database collection"
    return """<meta http-equiv="refresh" content="15" /> 
            Last Update!<br><br>{}""".format(statement)
