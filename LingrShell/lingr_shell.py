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
        'show messages: SHOW'
        data = self.lingr.show(self.now_room)
        messages = data['rooms'][0]['messages']

        print('=' * 50)
        for m in messages:
            print('{name} > {text}'.format(name=m['nickname'], text=m['text']))
            print('=' * 50)

    def do_chroom(self, key):
        'select room your joined: CHROOM <room>'
        if key == '' or key not in str(self.rooms.keys()):
            self.now_room = select_item(self.rooms, 'room')
        else:
            self.now_room = self.rooms[int(key)]
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_say(self, text):
        'post <text> to joined room: SAY <text>'
        self.lingr.say(self.now_room, text)

    def do_hi(self, dummy):
        'post "hi" to joined room: HI'
        self.lingr.say(self.now_room, 'hi')

    def do_chuser(self, username):
        'Change login user: CHUSER'

        self.lingr.destroy_session()
        self.lingr, self.username, self.password = login(username=username)
        self.rooms = {}
        for i, r in enumerate(self.lingr.get_rooms()['rooms']):
            self.rooms.update({i+1: r})

        self.now_room = select_item(self.rooms, 'room')
        self.prompt = '(Lingr) {username}@{room} >>> '.format(username=self.username, room=self.now_room)

    def do_bye(self, dummy):
        'exit this LingrShell: BYE'
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
