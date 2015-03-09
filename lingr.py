# -*- coding:utf-8 -*-

from urllib import parse, request
import sys
import json


class Lingr(object):
    ENDPOINT = 'http://lingr.com/api/'
    ENDPOINT_OBSERVE = 'http://lingr.com:8080/api/'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.nickname = None
        self.session = None
        self.rooms = None
        self.publicid = None

        self.counter = 0

    def __del__(self):
        self.destroy_session()

    def check_status(self, status):
        if status == 'ok':
            return True
        else:
            return False

    def check_room(self, room):
        if room in self.rooms:
            return True
        else:
            return False


    '''
    API manage
    '''
    # SESSION
    def create_session(self):
        query = {
                 'user': self.username,
                 'password': self.password
                }

        data = self.url_open('session/create', query)
        if self.check_status(data['status']):
            self.session = data['session']
            self.nickname = data['nickname']
            self.rooms = self.get_rooms()
            self.publicid = data['public_id']

        return data

    def verify_session(self):
        query = {'session': self.session}
        data = self.url_open('session/verify', query)

        self.check_status(data['status'])

        return data

    def destroy_session(self):
        query = {'session': self.session}

        data = self.url_open('session/destroy', query)
        self.check_status(data['status'])

        return data


    # ROOM
    def get_rooms(self):
        query = {'session': self.session}
        data = self.url_open('user/get_rooms', query)

        if self.check_status(data['status']):
            self.rooms = data['rooms']

        return data

    def show(self, room):
        if self.check_room(room):
            query = {
                     'session': self.session,
                     'room': room
                    }
            data = self.url_open('room/show', query)
            self.check_status(data['status'])

            return data

    def get_archives(self, room, max_msg_id, limit):
        if self.check_room(room):
            query = {
                     'session': self.session,
                     'room': room,
                     'before': max_msg_id,
                     'limit': limit
                    }
            data = self.url_open('room/get_archives', query)
            self.check_status(data['status'])

            return data

    def subscribe(self, room, reset='true'):
        if self.check_room(room):
            query = {
                     'session': self.session,
                     'room': room,
                     'reset': reset
                    }
            data = self.url_open('room/subscribe', query)
            if self.check_status(data['status']):
                self.counter = data['counter']

            return data

    def unsubscribe(self, room):
        if self.check_room(room):
            query = {
                     'session': self.session,
                     'room': room
                    }

            data = self.url_open('room/unsubscribe', query)
            self.check_status(data['status'])

            return data

    def say(self, room, text):
        if self.check_room(room):
            query = {
                     'session': self.session,
                     'room': room,
                     'nickname': self.nickname,
                     'text': text
                    }
            data = self.url_open('room/say', query)
            self.check_status(data['status'])

            return data

    # FAVORITE
    def favorite_add(self, message):
        query = {
                    'session': self.session,
                    'message': message
                }
        data = self.url_open('favorite/add', query)
        self.check_status(data['status'])

        return data


    def favorite_remove(self, message):
        query = {
                    'session': self.session,
                    'message': message
                }
        data = self.url_open('favorite/remove', query)
        self.check_status(data['status'])

        return data


    # EVENT
    def observe(self):
        query = {
                 'session': self.session,
                 'counter': self.counter
                }
        data = self.url_open('event/observe', query)

        if self.check_status(data['status']):
            self.counter = data['counter']

        return data


    '''
    URL manage
    '''
    def url_open(self, path, query):
        url = self.get_url(path) + '?' + parse.urlencode(query)

        return json.loads(request.urlopen(url).read().decode('utf-8'))

    def get_url(self, path):
        url = self.ENDPOINT if path is not 'event/observe' else self.ENDPOINT_OBSERVE
        return url + path
