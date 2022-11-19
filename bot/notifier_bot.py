import argparse
import socket

class IRC:
    irc = socket.socket()
  
    def __init__(self):  
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        self.irc.send(bytes("PRIVMSG " + chan + " " + msg + "\n", "UTF-8"))

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
            print("Sending: "+log_line+" in: "+args.channel)
            irc.send(args.channel, log_line)
