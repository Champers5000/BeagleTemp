from datetime import datetime
from pickle import FALSE
import time
import os
from tempsensor import tempsensor
import ntplib
import socket
from threading import Thread
from flask import Flask, Response, redirect, request, url_for, render_template
from flask_socketio import SocketIO

#Setup for web streaming
app = Flask(__name__)
app.config['SECRET_KEY']='bruh'
socket = SocketIO(app)
connected = False

def sendData():
    global connected
    for i in range(0,4):
        time.sleep(1)
        socket.send("idiot", broadcast = True)
        print("sent idiot")
    print("stopped sending")

@app.route("/")
def index():
    return render_template('index.html')

@socket.on('message')
def handlemsg(msg):
    global connected
    connected = True
    print("received "+msg)
    sendData()


@socket.on('disconnect')
def handlemsg():
    global connected
    print("disconnected ")
    connected = False

if __name__ == "__main__":
    socket.run(app)


