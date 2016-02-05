import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlencode

import string
import json
import websocket
import _thread
import time

####### get hitbox and socket IP ######################################################
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

####### Get the Token ######################################################

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
    print ("Error: Are your bot credentials in botvalues.json? correct?")
    raise e



join_msg = ("5:::{\"name\":\"message\",\"args\":[{\"method\":\"joinChannel\",\"params\":{\"channel\":\""
            +bot['channel']+"\",\"name\":\""+bot['name']+"\",\"token\":\"" + token + "\",\"isAdmin\":false}}]}")

def hitbox_send_message(ws, message):
    ws.send ("5:::{\"name\":\"message\",\"args\":[{\"method\":\"chatMsg\",\"params\":{\"channel\":\""
            +bot['channel']+"\",\"name\":\""+bot['name']+"\",\"nameColor\":\"FA5858\",\"text\":\""+message+"\"}}]}")

def on_message(ws, message):

    if message == "2::": #playing ping/pong to maintain connection.
        ws.send("2::")

    if message.startswith("5:::"):
        m = json.loads(message[4:])['args'][0] #formatting message recieved for easy parsing.
        m2 = json.loads(m)

        inMessageType = m2['method'] #retrieving the message type 'method'

        if inMessageType == 'loginMsg':
            print('##### DRONGO BOT LOGGED IN #####') #recieve's system login message.
            return

        if 'text' in m2['params']:
            inmessage = m2['params']['text'] #retrieving the actual message in text.

        if 'name' in m2['params']:
            msg_name = m2['params']['name']

        if 'time' in m2['params']:
            msg_time = m2['params']['time'] #pulling the 'time' variable from the message.

        if 'timestamp' in m2['params']:
            msg_time = m2['params']['timestamp'] #pulling the 'timestamp' variable from the message.

        if (time.strftime("%y/%m/%d %H:%M", time.localtime(int(msg_time)))) < (time.strftime("%y/%m/%d %H:%M", time.localtime(int(time.time()))) ):
            return #this ends the process if the message receieved isnt a new message. This prevents old messages accidentaly triggering the bot.

        if inMessageType == ('chatMsg'): #chat messages console output
            print(time.strftime("%D %H:%M", time.localtime(int(msg_time)))+ ' ' + inMessageType + ' ' + msg_name + ': ' + inmessage) #prints a timestamp and the message into the console.
        if inMessageType == ('chatLog'): #chat logs console output
            print(time.strftime("%D %H:%M", time.localtime(int(msg_time)))+ ' ' + inMessageType + ' ' + 'SYSTEM' + ': ' + inmessage) #prints a timestamp and the message into the console.


        ########################### BOT FUNTTIONALITY ###########################################################
        ''' The the functionality code here should probably moved to its own file once it becomes larger.'''

        if inmessage == ('drongo'):
            hitbox_send_message(ws, 'Did someone call?') #drongo call

        if inmessage == ('!decklist'):
            hitbox_send_message(ws,'https://gyazo.com/17fad4f82b409074dd08c6bcb501c495') #decklist

        if inmessage == ('!nips'):
            hitbox_send_message(ws,'https://i.gyazo.com/71cfb92a271f615b20d938cdbf5c6b40.png') #nips

        if inMessageType == ('chatLog'):
            if ' followed' in inmessage: #chat post for new follower.
                user = inmessage[6:]
                username = ''
                for char in user:
                    if char is '<':
                        break
                    username=username+char
                hitbox_send_message(ws, 'Thanks for the follow ' + username + ' !')

        if inMessageType == ('infoMsg'):
            if ' subscribed' in inmessage: #chat post for new subscriber.
                user = inmessage[6:]
                username = ''
                for char in user:
                    if char is '<':
                        break
                    username=username+char
                hitbox_send_message(ws, 'Thanks for subscribing ' + username + ' !')

        #TBA: subscriber alert.
        #     on screen visual stuff
        #     automated moderation
        #     times events (chat posts etc)

        #########################################################################################################

def on_error(ws, error): #error handeling (needs to be improved)
    print('error function called')
    raise error

def on_close(ws): #on close of the bot.
    print ("### closed ###")

def on_open(ws): #when the bot initially connects.
    print ("open")
    time.sleep(1)
    ws.send(join_msg)
    time.sleep(1)
    hitbox_send_message(ws, "***DRONGO BOT STARTED***")

if __name__ == "__main__": #the main loop. The actual program. nothing actually to see down here.
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(socketstring,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
