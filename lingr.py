# -*- coding:utf-8 -*-

from urllib import parse, request
import sys


class Lingr(object):
    __URL_BASE__ = 'http://lingr.com/api/'
    __URL_BASE_OBSERVE__ = 'http://lingr.com:8080/api/'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.nickname = None

        self.counter = 0

    def stream(self, room):
        self.create_session()
        self.get_rooms()
        self.subscribe(room=room)

        while True:
            obj = self.observe()
            if 'events' in obj:
                for event in obj['events']:
                    yield event

    def inspect(self, data):
        if data['status'] is 'ok':
            return True
        elif data['code'] is 'rate_limited':
            try:
                self.destroy_session()
                return False
            except Exception as e:
                print('rate limited')

    '''
    API manage
    '''
    # SESSION
    def create_session(self):
        query = {'user': self.username,
                 'password': self.password
                }

        data = self.url_open('session/create', query)

        if self.inspect(data):
            self.session = data['session']
            self.nickname = data['nickname']

            return
        else:
            sys.exit()

    def verify_session(self):
        query = {'session': self.session}
        data = self.url_open('session/verify', query)

        return 

    def destroy_session(self):
        query = {'session': self.session}
        self.url_open('session/destroy', query)

        return


    # ROOM
    def get_rooms(self):
        query = {'session': self.session}
        data = self.url_open('user/get_rooms', query)

        self.rooms = data['rooms']
        return self.rooms

    def show(self, room=None):
        query = {'session': self.session,
                 'room': self.room
                }

    def subscribe(self, room=None, reset='true'):
        if not room:
            room = ','.join(self.rooms)

        query = {'session': self.session,
                 'room': room,
                 'reset': reset
                }
        data = self.url_open('room/subscribe', query)

        self.counter = data['counter']

        return

    def say(self, room, nickname, text):
        query = {'sessison': self.session,
                 'room': room,
                 'nickname': nickname,
                 'text': text
                }
        data = self.url_open('room/say', query)
        print('say:', data)


    # EVENT
    def observe(self):
        query = {'session': self.session,
                 'counter': self.counter
                }
        data = self.url_open('event/observe', query)

        if 'counter' in data:
            self.counter = data['counter']
        return data


    '''
    URL manage
    '''
    def url_open(self, path, query):
        url = self.get_url(path) + '?' + parse.urlencode(query)

        return eval(request.urlopen(url).read())

    def get_url(self, path):
        url = self.__URL_BASE__
        if path is 'event/observe':
            url = self.__URL_BASE_OBSERVE__

        return url + path

