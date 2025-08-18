from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "L2M Boss Timer Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
