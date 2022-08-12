from datetime import datetime
from pickle import FALSE
import time
import os
from tempsensor import tempsensor
import ntplib
import socket
from threading import Thread
from flask import Flask, Response, redirect, request, url_for, render_template, send_file
from flask_socketio import SocketIO

#Setup for web streaming
app = Flask(__name__)
app.config['SECRET_KEY']='bruh'
socket = SocketIO(app)
users = set()


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/temperaturelog.csv")
def downloadcsv():
    return send_file("./temperaturelog.csv")

@socket.on('connect')
def handlemsg(msg):
    global users
    users.add(request.sid)
    print(users)

@socket.on('message')
def handlemsg(msg):
    print("received "+msg)

@socket.on('disconnect')
def handledis():
    global users
    users.remove(request.sid)
    print(users)

def mainloop():
    while True:
        time.sleep(1)
        for i in range(0,1000):
            time.sleep(1)
            if(len(users) > 0):
                socket.emit('tempreadings', str(i)+','+str(i)+','+str(i)+',' , broadcast = True)
        print("stopped sending")

t_main = Thread(target=mainloop)
t_main.start()


if __name__ == "__main__":
    socket.run(app, host = '0.0.0.0')
