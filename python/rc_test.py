import cortex
from cortex import *
import websocket #'pip install websocket-client' for install
from datetime import datetime
import json
import ssl
import time
import sys
from pydispatch import Dispatcher
import warnings
import threading
import json
import pyautogui
import socket
from rc_functions import *

CLIENT_ID = 'sZteLJ27aZCq63F2Im8yeKuAk7K1hNRIiOnw3Dm2'
CLIENT_SECRET = 'RAaU3dRa8dBMkkvTzCxMheJGuxSrtIVYqvlEV1qd8WXbTPLJRm1dS15j7ZlgzojARuBzMJyPo0kczLnqwMwZ15TSOZPvXNS1ThQUKmOGrY4QQWTzV48lxI8PtOvgDJCC'
PROFILE_NAME = 'Independent Study'
LICENSE = "223dad9b-5bd0-4e87-b128-dd57c19d5799"

def requestAccess(ws):
    receivedData = ws
    receivedData.send(json.dumps({
    "id": 1,
    "jsonrpc": "2.0",
    "method": "requestAccess",
    "params": {
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
        }
    }))
    return receivedData.recv()

def authorize(ws):
    receivedData = ws
    receivedData.send(json.dumps({
    "id": 4,
    "jsonrpc": "2.0",
    "method": "authorize",
    "params": {
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET,
        "license": "", # Maybe change here
        "debit": 10
        }
    }))
    return receivedData.recv() 

def on_message(*args):
    recv_dic = json.loads(args[1])
    if 'sid' in recv_dic:
        handle_stream_data(recv_dic)
    elif 'result' in recv_dic:
        handle_result(recv_dic)
    elif 'error' in recv_dic:
        handle_error(recv_dic)
    elif 'warning' in recv_dic:
        handle_warning(recv_dic['warning'])
    else:
        raise KeyError

def move_mouse(ws, token):
    
    receivedData = ws

    receivedData.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "queryHeadsets",
        "params": {},
        "id": 1
    }))

    print(receivedData.recv())
    print("\nCreating session...")
    receivedData.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "createSession",
        "params": {
            "status": "active",
            "project": "test",
            "cortexToken": token #self.auth
        },
        "id": 5
    }))

    print(receivedData.recv())
    print("\nSubscribing to session...")
    receivedData.send(json.dumps({
       "jsonrpc": "2.0", 
        "method": "subscribe", 
        "params": { 
            "cortexToken": "",
            "session": 1,
            "streams": ""
        }, 
        "id": 6
    }))

    print(receivedData.recv())
    print("\nGetting detection info...")
    receivedData.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "getDetectionInfo",
        "params": {
            "detection": "mentalCommand"
        },
        "id": 1
    }))

    print(receivedData.recv())

def train_command(request, ws, token):

    receivedData = ws
    print("Training " + request + " command...")
    receivedData.send(json.dumps( {
    "jsonrpc": "2.0", 
    "method": "training", 
    "params": {
    "cortexToken":token,
    "detection":"mentalCommand",
    "action":request,
    "status":"start"
    }, 
    "id": 1
    }))

    print(receivedData.recv())
    time.sleep(5)
    print(receivedData.recv())
    time.sleep(10)
    print(receivedData.recv())

    receivedData.send(json.dumps( {
    "jsonrpc": "2.0", 
    "method": "training", 
    "params": {
        "_auth":token,
        "detection":"mentalCommand",
        "action":request,
        "status":"accept"
    }, 
    "id": 1
    }
    ))

    print(receivedData.recv())
    time.sleep(2)
    print(receivedData.recv())

def run_move_mouse_training(ws, token):

    receivedData = ws

    while True:
        while True:
            try:
                startCode = input('\n\nTo train commands, type "1". To begin the game, type "2"\n>>> ')
                if startCode == "1" or startCode == "2":
                    break
                else:
                    print("Invalid input")
            except ValueError:
                print("Invalid input")

        if startCode == "1":
            while True:
                try:
                    req = input("Which command would you like to train? (Neutral, Left, Right, Lift, Drop, Push)\n>>> ").lower()         

                    if req == "neutral" or req == "lift" or req == "drop" or req == "left" or req == "right" or req == "push":
                        train_command(req, receivedData, token)
                        break
                    else:
                        print("Invalid input")
                except:
                    print("Invalid input")
                    
        elif startCode == "2":

            print("Getting USER login...")

            receivedData.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "getUserLogin",
                "id": 1
            }))

            profile = json.loads(receivedData.recv())["result"][0]
            print(profile)
            
            receivedData.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "subscribe",
                "params": {
                    "_auth": token,
                    "streams": [
                        "com"
                    ]
                },
                "id": 1
            }))

            print("Subscription:", receivedData.recv())
            receivedData.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "setupProfile",
                "params": {
                    "_auth": token,
                    "profile": profile,
                    "status": "create"
                },
                "id": 1
            }))

            print("Profile Set-up:", receivedData.recv())
            receivedData.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "mentalCommandBrainMap",
                "params": {
                    "_auth": token,
                    "profile": profile

                },
                "id": 1
            }))

            synapseData = receivedData.recv()
            print("Mental Command Brain Map:", synapseData)
            while True:
                thought = json.loads(receivedData.recv())["com"][0]
                print(thought)

                maxX, maxY = pyautogui.size()

                try:
                    x, y = pyautogui.position()      
                except KeyboardInterrupt:
                    print('\n')

                if thought == "left" and x>0:
                    pyautogui.move(-4, None)
                elif thought == "right" and x<maxX:
                    pyautogui.move(4, None)
                elif thought == "lift" and y<maxY:
                    pyautogui.move(None, -4)
                elif thought == "drop" and y>0:
                    pyautogui.move(None, 4)
                elif thought == "neutral":
                    pyautogui.move(None, None)
                elif thought == "push":
                    pyautogui.click()

def main():

    on_message =""
    on_open = ""
    on_error = ""
    on_close = ""
    url = "wss://localhost:6868"
    ws = websocket.WebSocketApp(url, on_message = on_message, on_open = on_open, on_error = on_error, on_close = on_close)
    threadName = "WebsockThread:-{:%Y%m%d%H%M%S}".format(datetime.utcnow())
    print(threadName)
    receivedData = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
    access_granted = requestAccess(receivedData)
    print("ACCESS GRANTED -------------------------------------------------")
    print(access_granted)
    print("TOKEN AUTHORIZATION --------------------------------------------")
    token = " 223dad9b-5bd0-4e87-b128-dd57c19d5799"
    print("Token: " + " 223dad9b-5bd0-4e87-b128-dd57c19d5799")
    print("MOVE MOUSE -----------------------------------------------------")
    move_mouse(receivedData, token)
    print("TRAINING -------------------------------------------------------")
    run_move_mouse_training(receivedData, token)

if __name__ =='__main__':
    main()