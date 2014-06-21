# -*-  coding:utf-8 -*-

import sys, re, subprocess, random, os
from getpass import getpass
from cmd import Cmd
from banner import banner
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(__file__))
import config

from lingr import Lingr

class LingrShell(Cmd):
    def __init__(self):
        Cmd.__init__(self)

        '''
        self.username = config.username
        self.password = config.password

        if config.username is '' or config.password is '':
            self.username, self.password = conf()

        self.lingr = Lingr(self.username, self.password)
        data = self.lingr.create_session()
        if data['status'] == 'error':
            print('login settins is error.')
            sys.exit()
        self.rooms = {}
        '''

        self.lingr, self.username, self.password = login(config.username, config.password)
        self.rooms = {}

        for i, r in enumerate(self.lingr.get_rooms()['rooms']):
            self.rooms.update({i+1: r})

        self.notify_send = False

        print(random.choice(banner))

        self.now_room = select_room(self.rooms)

        if self.now_room is not None:
            self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def emptyline(self, dummy):
        pass

    def do_show(self, dummy):
        'show messages: SHOW'
        data = self.lingr.show(self.now_room)
        messages = data['rooms'][0]['messages']

        print('=' * 50)
        for m in messages:
            print('{name} > {text}'.format(name=m['nickname'], text=m['text']))
            print('=' * 50)

    def do_chroom(self, key):
        'select room your joined: CHROOM <room>'
        if key == '' or int(key) not in self.rooms.keys():
            self.now_room = select_room(self.rooms)
        else:
            self.now_room = self.rooms[int(key)]
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_say(self, text):
        'post to joined room: SAY <text>'
        self.lingr.say(self.now_room, text)

    def do_chusr(self, dummy):
        'Change login user: CHUSR'

        self.lingr.destroy_session()
        self.username, self.password = conf()
        #self.lingr = Lingr(self.username, self.password)
        #data = self.lingr.create_session()
        self.username, self.password = login()

        self.rooms = {}
        for i, r in enumerate(self.lingr.get_rooms()['rooms']):
            self.rooms.update({i+1: r})
        print(self.rooms)

        self.now_room = select_room(self.rooms)
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_bye(self, dummy):
        'exit this LingrShell: BYE'
        print('bye')
        sys.exit()

def conf():
        username = input('username:')
        password = getpass('password:')

        settings = "username = '{username}'\npassword = '{password}'".format(username=username, password=password)

        with open(os.path.dirname(__file__) + '/config.py', 'w') as f:
            f.write(settings)


        return username, password


def login(username, password):
    while True:
        l = Lingr(username, password)
        data = l.create_session()

        if data['status'] == 'ok':
            print('login complete!')
            return l, username, password
        else:
            print('cannot login... please set to login.')
            print('*login setting*')
            username, password = conf()
            del l

def select_room(rooms):
    print('Please select room from below.')
    for k, v in rooms.items():
        print('{key}: {value}'.format(key=k, value=v))

    while True:
        key = input('(Lingr) Input room number >>> ')
        if key == 'bye':
            sys.exit()
        elif re.search('\d+', key):
            if int(key) in rooms.keys():
                return rooms[int(key)]

if __name__ == '__main__':
    LingrShell().cmdloop()
