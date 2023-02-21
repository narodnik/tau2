import argparse
import json
import socket
import sys

class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        self.irc.send(bytes("PRIVMSG " + chan + " :" + msg + "\n", "UTF-8"))

    def connect(self, server, port, channels, botnick):
        print("connecting to: "+server+":"+str(port))
        self.irc.connect((server, port))
        self.irc.send(bytes("USER " + botnick + " " + botnick +" " + botnick + " :notifier\n", "UTF-8"))
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        for chan in channels:
            self.irc.send(bytes("JOIN " + chan + "\n", "UTF-8"))

# parse arguments
parser = argparse.ArgumentParser(description='IRC bot to send a pipe to an IRC channel')
parser.add_argument('--server',default='127.0.0.1', help='IRC server')
parser.add_argument('--port', default=11066, help='port of the IRC server')
parser.add_argument('--nickname', help='bot nickname in IRC')
parser.add_argument('--channel', default="#dev", action='append', help='channel to join')
parser.add_argument('--pipe', default="/tmp/tau2" , help='pipe to read from')
parser.add_argument('--skip', default="prv", help='Project or Tags to skip notifications for')
parser.add_argument('--alt-chan', default="#test", required='--skip' in sys.argv, help='Alternative channel to send notifications to when there are skipped tasks')

args = parser.parse_args()

channels = [args.channel, args.alt_chan] if args.alt_chan is not None else args.channel

irc = IRC()
irc.connect(args.server, args.port, channels, args.nickname)

while True:
    with open(args.pipe) as handle:
        while True:
            log_line = handle.readline()
            if not log_line:
                break
            print(log_line)
            print("======================================")
            msg = json.loads(log_line)
            cmd = msg['update']
            channel = args.channel

            if cmd == "add_task":
                user = msg['params'][0]
                id = msg['params'][1]
                task = msg['params'][2]
                title = task['title']
                assigned = ", @".join(task['assigned'])

                project = task['project'] if task['project'] is not None else []
                if args.skip in project or args.skip in task['tags']:
                    channel = args.alt_chan

                if len(assigned) > 0:
                    notification = f"{user} added task ({id}): {title}. assigned to @{assigned}"
                else:
                    notification = f"{user} added task ({id}): {title}"
                print(notification)
                irc.send(channel, notification)
            elif cmd == "modify_task":
                user = msg['params'][0]
                id = msg['params'][1]
                task = msg['params'][2]
                action = msg['params'][3]
                title = task['title']

                project = task['project'] if task['project'] is not None else []
                if args.skip in project or args.skip in task['tags']:
                    channel = args.alt_chan

                assignees = []
                removed_assignees = []
                for act in action:
                    if act[1] == "assigned":
                        if act[0] == "append":
                            assignees.append(act[2])
                        if act[0] == "remove":
                            removed_assignees.append(act[2])

                assignees = ", @".join(assignees)
                if len(assignees) > 0:
                    notification = f"{user} modified task ({id}): {title}, action: assigned to @{assignees}"
                    print(notification)
                    irc.send(channel, notification)
                removed_assignees = ", @".join(removed_assignees)
                if len(removed_assignees) > 0:
                    notification = f"{user} modified task ({id}): {title}, action: removed @{removed_assignees}"
                    print(notification)
                    irc.send(channel, notification)
            elif cmd == "add_task_comment":
                user = msg['params'][0]
                id = msg['params'][1]
                task = msg['params'][2]
                title = task['title']
                
                project = task['project'] if task['project'] is not None else []
                if args.skip in project or args.skip in task['tags']:
                    channel = args.alt_chan

                notification = f"{user} commented on task ({id}): {title}"
                print(notification)
                irc.send(channel, notification)
            elif cmd == "change_task_status":
                user = msg['params'][0]
                id = msg['params'][1]
                task = msg['params'][2]
                state = msg['params'][3]
                title = task['title']

                project = task['project'] if task['project'] is not None else []
                if args.skip in project or args.skip in task['tags']:
                    channel = args.alt_chan

                if state == "start":
                    notification = f"{user} started task ({id}): {title}"
                elif state == "pause":
                    notification = f"{user} paused task ({id}): {title}"
                elif state == "stop":
                    notification = f"{user} stopped task ({id}): {title}"
                elif state == "cancel":
                    notification = f"{user} canceled task ({id}): {title}"
                print(notification)
                irc.send(channel, notification)