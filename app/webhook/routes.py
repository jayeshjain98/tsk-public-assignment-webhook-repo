from flask import Blueprint, json, request
from app.extensions import mongo
from datetime import datetime, timedelta
from multiprocessing import Value


counter = Value('i', 0)         # to count total request before refresh


webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/pushrequest', methods=["POST"])
def receiver():
    """ function to handle push request to git action-repo """
    
    data = request.json
    actions_data = mongo.db.github_actions      # mongodb object to handle query
    time_str = datetime.strptime(
                            data['head_commit']['timestamp'], 
                            "%Y-%m-%dT%H:%M:%S%z")
    time = (time_str - timedelta(hours=5, minutes=30)).strftime("%d %b %-I:%M %p") + " UTC"
    actions_data.insert({
                        "request_id": data['commits'][0]['id'], 
                        "author": data['head_commit']['author']['username'], 
                        "action": "PUSH", "from_branch": data['ref'].split("/")[-1], 
                        "to_branch": data['ref'].split("/")[-1], 
                        "timestamp": time,
                        })
    with counter.get_lock():
        counter.value += 1      # increase request count
    return json.dumps({"Action" : "request accepted and stored in collections"}), 200

@webhook.route('/pullrequest', methods=["POST"])
def pullrequest():
    """ function to handle pull request to git action-repo """

    data = request.json
    actions_data = mongo.db.github_actions      # mongodb object to handle query
    time = datetime.strptime(
                            data['pull_request']['merged_at'], 
                            "%Y-%m-%dT%H:%M:%S%z").strftime("%d %b %-I:%M %p %Z")
    if data['pull_request']['merged']:
        actions_data.insert({
                            "request_id": str(data['pull_request']['id']), 
                            "author": data['sender']['login'], "action": "MERGE", 
                            "from_branch": data['pull_request']['base']['ref'], 
                            "to_branch": data['pull_request']['head']['ref'], 
                            "timestamp": time
                            })
    else:
        actions_data.insert({
                            "request_id": str(data['pull_request']['id']), 
                            "author": data['sender']['login'], 
                            "action": "PULL_REQUEST", 
                            "from_branch": data['pull_request']['base']['ref'], 
                            "to_branch": data['pull_request']['head']['ref'], 
                            "timestamp": time
                            })
    with counter.get_lock():
        counter.value += 1      # increase request count
    return json.dumps({"Action" : "request accepted and stored in collections"}), 200

@webhook.route('', methods=["GET"])
def action_update():
    """ function to fetch update of last 15 seconds """

    with counter.get_lock():
        count = counter.value
        counter.value = 0

    count = 1 if count == 0 else count      # If no update in last 15 sec return last update in database

    actions_data = mongo.db.github_actions      # mongodb object to handle query
    records = actions_data.find().sort("_id",-1).limit(count)
    line = list()
    for record in records:

        if record['action'] == 'PUSH':
            statement = (
                        record['author'] 
                        + " pushed to " 
                        + record['to_branch'] 
                        + " on " 
                        + record['timestamp']
                        )

        elif record['action'] == 'PULL_REQUEST':
            statement =(
                        record['author'] 
                        + " submitted a pull request from " 
                        + record['from_branch'] 
                        + " to " 
                        + record['to_branch'] 
                        + " on " 
                        + record['timestamp'] 
                        )

        elif record['action'] == 'MERGE':
            statement = (
                        record['author'] 
                        + " merged branch " 
                        + record['from_branch'] 
                        + " to " 
                        + record['to_branch'] 
                        + " on " 
                        + record['timestamp']
                        )

        line.append(statement)              # collection of all updates in last 15 seconds
    
    formattedOutput = "<br><br>".join(line)     # Formatted output as response

    return """<meta http-equiv="refresh" content="15" /> 
            <br>{}""".format(formattedOutput)
