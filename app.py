from flask import Flask, request
import joblib
from flask_apscheduler import APScheduler

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

def job1():
    print('hello world')

sched.add_job(id='job1', func=job1, trigger='interval', seconds=5)
#sched.start()
