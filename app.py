from flask import Flask, request
import joblib
from flask_apscheduler import APScheduler
import os
import subprocess
import requests

app = Flask(__name__)

sched = APScheduler()

@app.route('/')
def hello():
    print (__name__)
    return 'Hello World'

@app.post('/api/telegram')
def telegram():
    data = request.get_json()
    tfidf = joblib.load('./models/TEXT_SVM_VECTORIZER_MAIN_EVENTS.pkl')
    loaded_model = joblib.load('./models/TEXT_SVM_MAIN_EVENTS.pkl')

    # transform dicts in messages into an array of only texts
    texts = [ message["message"] for message in data["messages"] ]
    # return texts
    text_features = tfidf.transform(texts)
    predictions = loaded_model.predict(text_features)

    return_array = []
    for i in range(len(data["messages"])):
        obj = {
            "id": data["messages"][i]["id"],
            "message": data["messages"][i]["message"],
            "event_type_prediction": predictions[i]
        }
        return_array.append(obj)

        # return obj

    return return_array


# get channels that need to be updated
def getChannels():
    url = "https://analytics.mbsmonitoring.com/api/get-telegram-channels"
    payload = ""
    headers = {}

    print('> getting channels')

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        print('> got channels')
        channels = response.json()
        for channel in channels:
            print(f"> running tool for {channel["username"]}")
            job1(channel)

def job1(channel):
    try:
        cwd = os.getcwd()
        nwd = cwd + '../telegram-api'
        os.chdir(nwd)
        # run the subprocess for scrapping telegram data
        print("> Runing tool")
        if (channel["latest_social_media_post"]):
            result = subprocess.run(['python', 'main.py', '--telegram-channel', channel["username"], '--min-id', channel['latest_social_media_post']['platform_id']])
        else:
            result = subprocess.run(['python', 'main.py', '--telegram-channel', channel["username"]])

        print(result.stdout)
        os.chdir(cwd)
    except Exception as e:
        print(f"An error occured {e}")

sched.add_job(id='job1', func=getChannels, trigger='interval', hours=1)
#sched.start()
