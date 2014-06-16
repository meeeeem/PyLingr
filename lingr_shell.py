# -*-  coding:utf-8 -*-

import sys, re, subprocess, random
from getpass import getpass

from cmd import Cmd
from banner import banner
import config
from lingr import Lingr
from notify import notify


class LingrShell(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        if config.username is '' or config.password is '':
            modify_config()

        self.lingr = Lingr(config.username, config.password)
        self.lingr.create_session()
        self.rooms = {}
        for i, r in enumerate(self.lingr.get_rooms()):
            self.rooms.update({i+1: r})

        self.notify_send = False

        print(random.choice(banner))

        self.now_room = select_room(self.rooms)

        if self.now_room is not None:
            self.prompt = '(Lingr) {username}@{room} >>> '.format(username=config.username, room=self.now_room)

    def emptyline(self, dummy):
        pass

    '''
    # いらないっぽい機能
    def do_show_room(self, dummy):
        'Show rooms you joined: ROOMS'
        print(self.rooms)
    '''

    def do_change_room(self, dummy):
        'select room your joined: ROOM <room>'
        self.now_room = select_room(self.rooms)
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=config.username, room=self.now_room)

    def do_notify(self, toggle):
        'Toggle notify flag.(if notify on, then "*" given): NOTIFY'
        if self.notify_send is True:
            self.notify_send = False
            print('***notify off***')
            self.prompt = '(Lingr) {username}@{room} >>> '.format(username=config.username, room=self.now_room)
        elif self.notify_send is False:
            self.notify_send = True
            print('***notify on***')
            self.prompt = '(Lingr) *{username}@{room} >>> '.format(username=config.username, room=self.now_room)
        else:
            print('Prease input [on/off]')

    def do_show_msg(self, dummy):
        'Show message: SHOW_MSG'   
        self.lingr.subscribe(self.now_room)
        self.data = self.lingr.observe()
        if self.notify_send is True:
            #subprocess.call(['notify_send', message])
            pass

    def do_config(self, dummy):
        'Change Lingr setting: Config'
        modify_config()

    def do_bye(self, dummy):
        'exit this LingrShell: BYE'
        print('bye')
        sys.exit()


def modify_config():
        print('*Lingr setting start*')
        username = getpass('username:')
        password = getpass('password:')

        settings = "username = '{username}'\npassword = '{password}'".format(username=username, password=password)

        with open('config.py', 'w') as f:
            f.write(settings)

        print('*Lingr setting complete*')

def select_room(rooms):
    print('Please select room from berow.')
    for k, v in rooms.items():
        print('{key}: {value}'.format(key=k, value=v))

    return rooms[int(input('(Lingr) Input room key >>>'))]


if __name__ == '__main__':
    LingrShell().cmdloop()
