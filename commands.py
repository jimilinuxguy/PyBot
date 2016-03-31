#Embedded file name: /Users/jimisanchez/PyBot/commands.py
import os
import sys

class Commands:

    def __init__(self):
        self.help = ['!help', '!say <msg>', '!tell <target> <message>']
        self.masterHelp = ['!quit']
        self.colorCodes = {'White': 0,
         'Black': 1,
         'DarkBlue': 2,
         'DarkGreen': 3,
         'Red': 4,
         'DarkRed': 5,
         'DarkViolet': 6,
         'Orange': 7,
         'Yellow': 8,
         'LightGreen': 9,
         'Cyan': 10,
         'LightCyan': 11,
         'Blue': 12,
         'Violet': 13,
         'DarkGray': 14,
         'LightGray': 15}
        self.controlCodes = {'Bold': '\x02',
         'Color': '\x03',
         'Italic': '\t',
         'StrikeThrough': '\x13',
         'Reset': '\x0f',
         'Underline': '\x15',
         'Underline2': '\x1f',
         'Reverse': '\x16',
         'Action': '\x01'}

    def setBot(self, bot):
        self.bot = bot

    def sendServer(self, line):
        self.bot.socket.sendall(line + '\r\n')

    def sendPong(self, pong):
        self.sendServer('PONG ' + pong)

    def sendNick(self):
        self.sendServer('NICK %s' % self.bot.getNick())

    def sendUser(self):
        self.sendServer('USER %s %s %s :%s' % (self.bot.getNick(),
         self.bot.getServer(),
         self.bot.getServer(),
         self.bot.getWhois()))

    def sendMessage(self, target, message):
        self.sendServer('PRIVMSG ' + target + ' :' + message)

    def sendNotice(self, target, message):
        self.sendServer('NOTICE ' + target + ' :' + message)

    def handleJoin(self, user, chan):
        user = self.bot.getUserNick(user)
        if chan not in self.bot.channelUsers.keys():
            self.bot.channelUsers[chan] = []
        self.bot.channelUsers[chan].append(user)

    def handlePart(self, user, chan):
        user = self.bot.getUserNick(user)
        self.channelUsers[chan].remove(user)

    def partAll(self):
        for channel in self.bot.getMyChannels():
            self.sendMessage(channel, self.makeBold('wee!'))

    def quit(self):
        self.partAll()
        self.sendServer('QUIT :Gone to have lunch')

    def ctcp_reply(self, target):
        self.sendMessage(target, '\x01VERSION SUCK IT\x01')

    def makeAction(self, text):
        return self.controlCodes['Action'] + 'ACTION ' + text + self.controlCodes['Action']

    def makeBold(self, text):
        return self.controlCodes['Bold'] + text + self.controlCodes['Bold']

    def getCommandPart(self, line):
        try:
            value = line.split(' ')
            value.pop(0)
            print value
        except ValueError:
            print 'Failure'
            return False

        print 'Success'
        return value

    def handleCommand(self, parts):
        if parts['type'] == '001':
            if self.bot.password:
                self.sendMessage('NickServ', 'identify ' + self.bot.getPassword())
            print 'Joining channels'
            for channel in self.bot.channels:
                print 'Trying to join ' + channel
                self.sendServer('JOIN ' + channel)

        if parts['type'] == '353':
            for user in self.bot.getUsers(parts['information']):
                chan = self.bot.getChannel(parts['target'])
                self.handleJoin(user, chan)

        if parts['type'] == 'PING':
            print 'PING? PONG!'
            self.sendPong(parts['information'])
        if parts['type'] == 'PRIVMSG' and parts['information'] == '!who':
            if parts['target'] in self.bot.channelUsers.keys():
                users = self.bot.getUsersInChannel(parts['target'])
                self.sendMessage(parts['target'], 'Users in ' + parts['target'] + ': ' + users)
            else:
                self.sendMessage(parts['from'], 'I do not understand how to handle that, did you mean to send that in a private message?')
        if parts['type'] == 'JOIN':
            self.handleJoin(parts['from'], parts['target'])
        if parts['type'] == 'PART':
            self.handlePart(parts['from'], parts['target'])
        if parts['type'] == 'KICK':
            channel, user = self.getKICKInfo(parts['target'])
            self.handlePart(user, channel)
        if parts['information']:
            if parts['information'] == '!quit':
                self.quit()
            if parts['information'].startswith('!say'):
                value = self.getCommandPart(parts['information'])
                if value:
                    self.sendMessage(parts['target'], ' '.join(value))
                else:
                    self.sendMessage(parts['from'], 'Invalid command parameters')
            if parts['information'].startswith('!tell'):
                value = self.getCommandPart(parts['information'])
                if value:
                    target = value[0]
                    value.pop(0)
                    self.sendMessage(target, ' '.join(value))
            if parts['information'].startswith('!action'):
                value = self.getCommandPart(parts['information'])
                if value:
                    text = self.makeAction(' '.join(value))
                    self.sendMessage(parts['target'], self.makeAction(' '.join(value)))
            if parts['information'].startswith('\x01VERSION\x01'):
                self.sendNotice(parts['from'], '\x01VERSION Nyubis Python Bot\x01')
            if parts['information'].startswith('\x01PING'):
                self.sendNotice(parts['from'], '\x01PING 234234234234\x01')
            if parts['information'] == '!help':
                self.sendNotice(parts['from'], 'Valid commands are: ')
                self.sendNotice(parts['from'], ', '.join(self.help))
                if self.bot.master == parts['from']:
                    self.sendNotice(parts['from'], 'Master commands are: ')
                    self.sendNotice(parts['from'], ', '.join(self.masterHelp))
