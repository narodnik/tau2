import argparse
import json
import socket

class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        self.irc.send(bytes("PRIVMSG " + chan + " :" + msg + "\n", "UTF-8"))

    def connect(self, server, port, channel, botnick):
        print("connecting to: "+server+":"+str(port))
        self.irc.connect((server, port))
        self.irc.send(bytes("USER " + botnick + " " + botnick +" " + botnick + " :notifier\n", "UTF-8"))
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        self.irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))

# parse arguments
parser = argparse.ArgumentParser(description='IRC bot to send a pipe to an IRC channel')
parser.add_argument('--server',default='127.0.0.1', help='IRC server')
parser.add_argument('--port', default=11066, help='port of the IRC server')
parser.add_argument('--nickname', help='bot nickname in IRC')
parser.add_argument('--channel', default="#dev", action='append', help='channel to join')
parser.add_argument('--pipe', default="/tmp/tau2" , help='pipe to read from')

args = parser.parse_args()

irc = IRC()
irc.connect(args.server, args.port, args.channel, args.nickname)

while True:
    with open(args.pipe) as handle:
        while True:
            log_line = handle.readline()
            if not log_line:
                break
            print(log_line)
            msg = json.loads(log_line)
            cmd = msg['update']
            
            if cmd == "add_task":
                user = msg['params'][0]
                title = msg['params'][2]['title']
                assigned = ",".join(msg['params'][2]['assigned'])
                if len(assigned) > 0:
                    notification = f"{user} added a new task '{title}' assigned to @{assigned}"
                else:
                    notification = f"{user} added a new task '{title}'"
                print(notification)
                irc.send(args.channel, notification)
            elif cmd == "modify_task":
                user = msg['params'][0]
                title = msg['params'][2]
                action = msg['params'][3]
                assignees = []
                for act in action:
                    if act[1] == "assigned":
                        assignees.append(act[2])

                assignees = ",".join(assignees)
                if len(assignees) > 0:
                    notification = f"{user} modified task '{title}', action: assigned to @{assignees}"
                    print(notification)
                    irc.send(args.channel, notification)
            elif cmd == "add_task_comment":
                user = msg['params'][0]
                title = msg['params'][2]
                notification = f"{user} added a comment on task '{title}'"
                print(notification)
                irc.send(args.channel, notification)
            elif cmd == "change_task_status":
                user = msg['params'][0]
                title = msg['params'][2]
                state = msg['params'][3]
                notification = f"{user} changed state of task '{title}' to '{state}'"
                print(notification)
                irc.send(args.channel, notification)