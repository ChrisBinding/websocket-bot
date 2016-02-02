import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlencode

import string
import json
import websocket
import _thread
import time


#// Grab hitbox ip and socket id //////////////////#



site = "http://api.hitbox.tv/chat/servers.json?redis=true"

jsite=urlopen(site).read()



lines = json.loads(jsite.decode('utf-8'))


for line in lines:
    ip = ".".join(line['server_ip'].split(".")[0].split("-")[1:])
    print ("usable ip:", ip)

site = "http://"+ip+"/socket.io/1/"
lines = urlopen(site).read().decode("utf-8")

socketid = lines.split(":")[0]
print ("socket id:", socketid)

socketstring = ("ws://"+ip+"/socket.io/1/websocket/" + socketid)
print(socketstring)

#// Grab token ///////////////////////////////////#

bot = json.load(open("botvalues.json"))
print ("Hitbox username:", bot['name'])

values = {'login' : bot['name'],
          'pass' : bot['password'],
          'app' : 'desktop' }

url = 'http://api.hitbox.tv/auth/token'

try:
    data = urlencode(values)
    data = data.encode('ascii')
    req = Request(url, data)
    response = urlopen(req).read()
 
    the_page = json.loads(response.decode('utf-8'))
    token = the_page["authToken"]
    print ("authToken:", token)
    
except (Exception, e):
    print ("Error: Are correct bot credentials in botvalues.json?")
    raise e

#// Hitbox Websocket Code ////////////////////////#

join_msg = ("5:::{\"name\":\"message\",\"args\":[{\"method\":\"joinChannel\",\"params\":{\"channel\":\""
            +bot['channel']+"\",\"name\":\""+bot['name']+"\",\"token\":\"" + token + "\",\"isAdmin\":false}}]}")

def hitbox_send_message(ws, message):
    ws.send ("5:::{\"name\":\"message\",\"args\":[{\"method\":\"chatMsg\",\"params\":{\"channel\":\""
            +bot['channel']+"\",\"name\":\""+bot['name']+"\",\"nameColor\":\"FA5858\",\"text\":\""+message+"\"}}]}")

def on_message(ws, message):
    
    if message == "2::": #playing ping/pong to maintain connection. 
        ws.send("2::")
    
    if message.startswith("5:::"):
        m = json.loads(message[4:])['args'][0]
        m2 = json.loads(m)
        inmessage = m2['params']['text']

        if 'time' in m2['params']:
            msg_time = m2['params']['time']

        if 'timestamp' in m2['params']:
            msg_time = m2['params']['timestamp']

        if (time.strftime("%D %H:%M", time.localtime(int(msg_time)))) < (time.strftime("%D %H:%M", time.localtime(int(time.time())))):
                return
            
        print(time.strftime("%D %H:%M", time.localtime(int(msg_time)))+ ': ' + inmessage)

        if inmessage == ('drongo'):
            hitbox_send_message(ws, 'Did someone call?')

        if inmessage == ('!decklist'):
            hitbox_send_message(ws,'https://gyazo.com/17fad4f82b409074dd08c6bcb501c495')


        if ' followed' in inmessage:
            user = inmessage[6:]
            username = ''
            for char in user:
                if char is '<':
                    break
                username=username+char
            hitbox_send_message(ws, 'Thanks for the follow ' + username + ' !')
            
def on_error(ws, error):
    print('error function called')
    raise error

def on_close(ws):
    print ("### closed ###")

def on_open(ws):
    print ("open")
    time.sleep(1)
    ws.send(join_msg)
    time.sleep(1)
    hitbox_send_message(ws, "Did someone say ........ DRONGO?")


if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(socketstring,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
   
