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

channel = "#dev"
server = "127.0.0.1"
port = 11066
nickname = "tau-notifier"

irc = IRC()
irc.connect(server, port, channel, nickname)

while True:
    with open("/tmp/tau2") as handle:
        while True:
            log_line = handle.readline()
            if not log_line:
                break
            print(log_line)
            print("Sending: "+log_line+" in: "+channel)
            irc.send(channel, log_line)
