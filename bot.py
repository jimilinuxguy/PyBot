import socket
import imp
import re

from commands import Commands
class Bot(object):

    foo = __import__('commands')
    ircRegex = re.compile('^(?:[:](?P<from>\S+) )?(?P<type>\S+)(?: (?!:)(?P<target>.+?))?(?: [:](?P<information>.+))?$')

    def __init__(self, server = '', port = 6667, nick = '', whois = '' , master = '', channels = [], password = ''):
        self.server = server
        self.port    = port
        self.nick    = nick
        self.whois = whois
        self.master = master
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channels = channels
        self.channelUsers = {}
        self.password = ''
        self.commands = Commands()
        self.commands.setBot(self)

    def getServer(self,):
        return self.server

    def getPort(self):
        return self.port

    def getNick(self):
        return self.nick

    def getWhois(self):
        return self.whois
    def getPassword(self):
        return self.password

    def getUserLine(self):
        return 'USER ' + self.getNick() + ' ' + self.getServer() + ' 8 :'+self.getWhois()
    def getUserNick(self, user):
        return user.split('!')[0]

    def getUsers(self, users):
        return users.split(' ')

    def getChannel(self, channel):
        return channel.split(' ')[2]

    def getKICKInfo(self, info):
        data = info.split(' ');
        return data
    def getUsersInChannel(self, channel):
        set = {}
        map(set.__setitem__, self.channelUsers[channel], [])
        return ', '.join(set.keys())
    def getMyChannels(self):
        return self.channels
    def cleanLine(self, input):
        line = input
        line = line.rstrip('\n')
        line = line.rstrip('\r')
        line = line.strip('\r')
        line = line.strip('\n')
        return line

    def parseLine(self, line):
        line = self.cleanLine(line)
        parts = re.search(self.ircRegex, line).groupdict()
        if '!' in parts['from']:
            parts['from'] = self.getUserNick(parts['from'])
            if self.master == parts['from']:
                print "MASTERRR"
        print parts
        self.commands.handleCommand(parts)

    def connect(self):
        if ( not self.getNick() or not self.getServer() ):
            print "Not configured"
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.getServer(), self.getPort()))

        self.commands.sendNick()
        self.commands.sendUser()

        for data in self.socket.makefile('r'):
            if not data: break
            self.parseLine(data)
       
        self.socket.close()
