# Dev Assessment - Webhook Receiver

Please use this repository for constructing the Flask webhook receiver.

*******************

## Setup

* Create a new virtual environment

```bash
pip install virtualenv
```

* Create the virtual env

```bash
virtualenv venv
```

* Activate the virtual env

```bash
source venv/bin/activate
```

* Install requirements

```bash
pip install -r requirements.txt
```

* Run the flask application (In production, please use Gunicorn)

```bash
python run.py
```

* The endpoint is at:

```bash
POST http://127.0.0.1:5000/webhook/receiver
```

* To connect your github repo webhook to your server, your server must be online. So we use framework called ngrok to serve our localhost:5000 online.

```bash
./ngrok http 5000
```

* Then create 2 webhooks for your action-repo with uri as follows(example):

```bash
http://e624aef12c73.ngrok.io/webhook/pushrequest
http://e624aef12c73.ngrok.io/webhook/pullrequest
```

* To get the latest update in database view the following uri:

```bash
http://e624aef12c73.ngrok.io/webhook
```

*******************
