# -*- coding: utf-8 -*-
import unittest
import os


class PyLingrTest(unittest.TestCase):

    def _getTargetClass(self):
        from lingr import Lingr
        return Lingr

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def setUp(self):
        self.username = os.environ['LINGR_USERNAME']
        self.password = os.environ['LINGR_PASSWORD']
        self.l = self._makeOne(username=self.username, password=self.password)
        self.session = self.l.create_session()

    def test_create_session(self):
        self.assertEqual(self.session['status'], 'ok')

    def test_get_rooms(self):
        room_data = self.l.get_rooms()
        self.assertEqual(len(room_data['rooms']), 9)

    def test_favorite_add(self):
        room = self.l.get_rooms()['rooms']
        message_id = self.l.show(room[0])['rooms'][0]['messages'][0]['id']

        fa = self.l.favorite_add(message_id)

        self.assertEqual(fa['status'], 'ok')
        self.assertEqual(int(message_id), self.l.show(room[0])['rooms'][0]['faved_message_ids'][0])

        fa = self.l.favorite_add(message_id)
        self.assertEqual(fa['status'], 'error')

        fr = self.l.favorite_remove(message_id)
        self.assertEqual(fr['status'], 'ok')
        self.assertEqual(len(self.l.show(room[0])['rooms'][0]['faved_message_ids']), 0)

        fr = self.l.favorite_remove(message_id)
        self.assertEqual(fr['status'], 'error')



if __name__ == '__main__':
    unittest.main()
