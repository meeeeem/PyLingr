# -*-  coding:utf-8 -*-

import sys, re, subprocess, random, os, json
from getpass import getpass
from cmd import Cmd
from banner import banner
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(__file__))

from lingr import Lingr

CONF_PATH = os.path.abspath(os.path.dirname(__file__) + '/config')


class LingrShell(Cmd):
    def __init__(self):
        Cmd.__init__(self)

        user_list = {}
        try:
            with open(CONF_PATH, 'r') as f:
                json_obj = json.load(f)

            for i, u in enumerate(json_obj.keys()):
                user_list.update({i+1: u})
            login_user = select_item(user_list, 'user')
            username = login_user
            password = json_obj[login_user]
        except:
            print('can not find login info.')
            username, password = None, None

        self.lingr, self.username, self.password = login(username, password)

        self.rooms = {}

        for i, r in enumerate(self.lingr.get_rooms()['rooms']):
            self.rooms.update({i+1: r})

        self.notify_send = False

        print(random.choice(banner))

        self.now_room = select_item(self.rooms, 'room')

        if self.now_room is not None:
            self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def emptyline(self, dummy):
        pass

    def do_show(self, dummy):
        'Show messages: show'
        data = self.lingr.show(self.now_room)
        messages = data['rooms'][0]['messages']

        print('=' * 50)
        for m in messages:
            print('{name} > {text}'.format(name=m['nickname'], text=m['text']))
            print('{time}'.format(time=m['timestamp']))
            print('=' * 50)

    def do_chroom(self, key):
        'Select room your joined: chroom <room>'
        if key == '' or key not in str(self.rooms.keys()):
            self.now_room = select_item(self.rooms, 'room')
        else:
            self.now_room = self.rooms[int(key)]
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_logs(self, limit):
        'Display logs(default past 10 posts): logs <count>'
        data = self.lingr.show(self.now_room)
        old = data['rooms'][0]['messages'][0]['id']
        if limit == '':
            limit = 10
        print(limit)
        logs = self.lingr.get_archives(self.now_room, old, limit)

        if logs['status'] == 'ok':
            for l in logs['messages']:
                print('{nickname} > {text}'.format(nickname=l['nickname'], text=l['text']))
                print('{time}'.format(time=l['timestamp']))
        else:
            print(logs)

    def do_say(self, text):
        'post <text> to joined room: say <text>'
        self.lingr.say(self.now_room, text)

    def do_hi(self, dummy):
        'post "hi" to joined room: hi'
        self.lingr.say(self.now_room, 'hi')

    def do_chuser(self, username):
        'Change login user: chuser'

        self.lingr.destroy_session()
        self.lingr, self.username, self.password = login(username=username)
        self.rooms = {}
        for i, r in enumerate(self.lingr.get_rooms()['rooms']):
            self.rooms.update({i+1: r})

        self.now_room = select_item(self.rooms, 'room')
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_isonline(self, dummy):
        'Pick up online users: isonline'
        data = self.lingr.show(self.now_room)
        members = data['rooms'][0]['roster']['members']
        for m in members:
            if m['is_online']:
                print(m['name'])

    def do_isoffline(self, dummy):
        'Pick up offline users: isoffline'
        data = self.lingr.show(self.now_room)
        members = data['rooms'][0]['roster']['members']
        for m in members:
            if m['is_online'] is False:
                print(m['name'])

    def do_members(self, dummy):
        'Pick up members of joined room: members'
        data = self.lingr.show(self.now_room)
        members = data['rooms'][0]['roster']['members']
        print('{num} members join in {room}.'.format(num=len(members), room=self.now_room))
        for m in members:
            print(m['name'], end='')
            if m['is_online']:
                print('*', end='')
            print('')

    def do_bots(self, dummy):
        'Pick up bots of joined room: bots'
        data = self.lingr.show(self.now_room)
        bots = data['rooms'][0]['roster']['bots']
        print('{num} bots assigned in {room}'.format(num=len(bots), room=self.now_room))
        for b in bots:
            print('{bot} is {status}'.format(bot=b['name'], status=b['status']))

    def do_bye(self, dummy):
        'exit this LingrShell: bye'
        print('bye')
        sys.exit()


def conf():
    username = input('username:')
    password = getpass('password:')

    try:
        with open(CONF_PATH) as f:
            user_list = json.load(f)
    except:
        user_list = {}

    user_list.update({username: password})

    with open(CONF_PATH, 'w') as f:
        f.write(json.dumps(user_list))

    return username, password

def login(username=None, password=None):
    while True:
        if username is not None:
            with open(CONF_PATH) as f:
                json_obj = json.load(f)
            password = json_obj.get(username, None)

        l = Lingr(username, password)
        data = l.create_session()

        if data['status'] == 'ok':
            print('login complete!')
            return l, username, password
        else:
            print('*login setting*')
            username, password = conf()
            del l

def select_item(dict_item, flag):
    print('print select {flag} from below'.format(flag=flag))
    for k, v in dict_item.items():
        print('{key}: {value}'.format(key=k, value=v))

    while True:
        key = input('(Lingr) Input {flag} number >>> '.format(flag=flag))
        if key == 'bye':
            sys.exit()
        elif re.search('\d+', key):
            if int(key) in dict_item.keys():
                return dict_item[int(key)]

if __name__ == '__main__':
    LingrShell().cmdloop()
