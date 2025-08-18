from flask import Flask
from threading import Thread
import datetime

app = Flask('')

@app.route('/')
def home():
    return "L2M Boss Timer Bot is alive!"

@app.route('/ping')
def ping():
    return "Pong! Bot is running."

@app.route('/status')
def status():
    return {"status": "online", "message": "L2M Boss Timer Bot is running"}

@app.route('/cron')
def cron():
    # Endpoint cho web cronjob - chạy mỗi 5 phút
    current_time = datetime.datetime.now()
    print(f"Cron job executed at: {current_time}")
    return f"Cron executed at {current_time.strftime('%Y-%m-%d %H:%M:%S')}!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
