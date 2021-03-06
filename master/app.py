#!/usr/bin/env python

import tornado.ioloop
import tornado.web
from tornado.escape import json_encode, json_decode
from datetime import datetime

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to BakeIoT_House\n")

class DoorHandler(tornado.web.RequestHandler):
    def get(self):
        obj = {
            'id': 'door_frontss',
            'status': 'open',
            'time': str(datetime.now())
        }
        self.write(json_encode(obj))

    def post(self):
        data = json_decode(self.request.body) 
        print data
        self.write('Success')

class OfficeHandler(tornado.web.RequestHandler):
    def get(self):
        obj = {
            'id': 'door_frontss',
            'status': 'open',
            'time': str(datetime.now())
        }
        self.write(json_encode(obj))

    def post(self):
        data = json_decode(self.request.body) 
        print data
        self.write('Success')


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/door", DoorHandler),
        (r"/office", OfficeHandler),
    ], debug=True)

if __name__ == "__main__":
    print '-Bake IoT Home-'
    print 'Master Server v.0.1'
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()