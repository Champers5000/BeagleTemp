from datetime import datetime
import time
import os
from tempsensor import tempsensor
import ntplib
import socket
from threading import Thread, Lock
from flask import Flask, Response, redirect, request, url_for, render_template, send_file
from flask_socketio import SocketIO

loginterval = 60 #set the logging interval
logfile = "temperaturelog.csv" #name of log file

sensorname = set() #list of existing sensor names just for formatting the csv header
sensorlist = None

#Setup for web streaming
app = Flask(__name__)
app.config['SECRET_KEY']='Tommy boy'
socket = SocketIO(app)
connections = set()

def hasDuplicates(inputlist):
    tempset = set()
    for i in inputlist:
        tempset.add(i)
    return not len(inputlist) == len(tempset)


def checkSensors():
    #check for new sensors, returns true when new sensors are found
    global sensorname
    newsensor = False
    if os.path.exists(tempsensor.sensordir):
        for filename in os.listdir(tempsensor.sensordir):
            if filename[:3] == "28-" and not filename in sensorname:
                print("Found sensor "+ filename)
                sensorname.add(filename)
                newsensor=True
    else:
        print("Sensor directory not found. Please install the appropriate drivers for the temperature sensor")
        exit(1)
    return newsensor


def createCSVHeader():
    global sensorname
    global sensorlist
    tempsensorname = sensorname.copy() # Make a copy of all the existing sensors. If the sensor exists, then we will delete it from this set
    if os.path.exists(logfile):
        with open("temperaturelog.csv", 'r') as f:
            lines = f.readlines()
            header=lines[0].split(",")
            header=header[0:len(header)-1] # get rid of newline character at the end
            for name in header:
                if name in tempsensorname:
                    tempsensorname.remove(name)
        with open("temperaturelog.csv", 'w') as f:
            f.write(lines[0][0:lines[0].index('\n')])
            for name in tempsensorname:
                f.write(name + ',') # write out all the sensor names that don't exist in the csv already
            f.write('\n')
            f.writelines(lines[1:])
    else:
        print("No log file found, creating in the current directory")
        with open("temperaturelog.csv", 'w') as f:
            f.write("Date,Time,")
            for name in sensorname:
                f.write(name+",")
            f.write("\n")


    #Get the order of the sensor in the csv and store it into a list
    with open("temperaturelog.csv", 'r') as f:
        csvheader = f.readline().split(',')
        csvheader = csvheader[2:]
        if(hasDuplicates(csvheader)):
            print("Check the csv header. There may be duplicate entries, or the file may be corrupt.")
        sensorlist = [None]*(len(csvheader)-1)
        for i in range(0,len(sensorlist)):
            sensorlist[i] = tempsensor(csvheader[i])
        f.close()

def updateCSVHeader():
    global sensorname
    global sensorlist
    tempsensorname = sensorname.copy() # Make a copy of all the existing sensors. If the sensor exists, then we will delete it from this set
    for sensor in sensorlist:
        tempsensorname.remove(sensor.name)
    with open("temperaturelog.csv", 'r') as f:
        lines = f.readlines()
    with open("temperaturelog.csv", 'w') as f:
        f.write(lines[0][0:lines[0].index('\n')]) #write everything in first line without creating newline
        for name in tempsensorname:
            f.write(name + ',') # write out all the sensor names that don't exist in the csv already
            sensorlist.append(tempsensor(name))
        f.write('\n')
        f.writelines(lines[1:])
        f.close()

ntpworking=True
timestamp = None
c = ntplib.NTPClient()
def getTime():
    #get timestamp either from online or system clock
    global timestamp
    global ntpworking
    global c
    try:
        response = c.request('us.pool.ntp.org', version=3)
        #response.offset
        timestamp = datetime.fromtimestamp(response.tx_time, None) # Passing in None object for timezone parameter defaults to local timezone
        if not ntpworking:
            print("Connected to time server")
            ntpworking = True
    except (ntplib.NTPException, socket.gaierror):
        timestamp = datetime.now()
        if ntpworking:
            ntpworking = False
            print("Unable to connect to time server. Check internet connection. Defaulting to system clock")
    timestamp = str(timestamp)

tempreading = ""
def getSensorReading():
    global sensorname
    global sensorlist
    global tempreading
    '''
    # get all the sensor data with seperate threads
    threadlist = [None]*len(sensorlist)
    for i in range(0, len(sensorlist)):
        threadlist[i] = Thread(target = sensorlist[i].getTemp)
        threadlist[i].start()

    for i in range(0, len(threadlist)):
        threadlist[i].join()
    '''
    for i in range(0, len(sensorlist)):
        sensorlist[i].getTemp()
    
    tempreading = ""

    for i in range(0, len(sensorlist)):
        temp = sensorlist[i].temperature
        if(temp is not None):
            tempreading+=str(temp)
        tempreading+=','

def mainloop():
    global tempreading
    #Main loop for logging
    try:
        while True:
            #Start thread to get time
            timethread = Thread(target = getTime)
            timethread.start()

            starttime = int(datetime.now().timestamp())
            strout = tempreading

            #Wait for threads to finish and concatenate data
            timethread.join()
            strout = timestamp[:10] +','+ timestamp[11:19] + ',' + strout

            #write out all data
            try:
                with open("temperaturelog.csv", 'a') as f:
                    f.write(strout+'\n')
                    f.close()
            except:
                print("Unable to write to file. Printing readings to console")
                print(strout)

            #Look for new sensors
            if checkSensors():
                updateCSVHeader()
            # wait for time to hit the logging interval to continue
            while int(datetime.now().timestamp())-starttime < loginterval:
                time.sleep(.5)

    except KeyboardInterrupt:
        print ("Exiting")


#look for all the available sensors
checkSensors()

#exit if no sensors are found
'''
if len(sensorname) == 0:
    print("No temperature sensors are found. Exiting")
    exit(1)
'''
#check for temperature log and ensure the headers include all sensors
createCSVHeader()

t_main = Thread(target = mainloop)
t_main.start()

def serverloop():
    global t_main
    global connections
    while t_main.is_alive():
        getSensorReading()
        print(tempreading)
        if len(connections)>0:
            socket.emit('tempreadings', tempreading, broadcast = True)
        time.sleep(2)

t_web = Thread(target = serverloop)
t_web.start()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/temperaturelog.csv")
def downloadcsv():
    return send_file("./temperaturelog.csv")

@socket.on('connect')
def handleconnect():
    global connections
    connections.add(request.sid)

@socket.on('disconnect')
def handledc():
    global connections
    connections.remove(request.sid)

if __name__ == "__main__":
    socket.run(app, host = '0.0.0.0')



