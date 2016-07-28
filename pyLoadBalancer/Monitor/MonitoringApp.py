import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import json
import pprint
from  tornado.escape import json_decode
from  tornado.escape import json_encode
import zmq
from ..colorprint import cprint
import argparse
import sys
from tornado.options import define, options


define("port", default=8000, help="run on the given port", type=int)

context = zmq.Context()
LB_HEALTHADRESS = None
LBReqSock = None
SOCKET_TIMEOUT = 1000


def setLBReqSock(LBReqSock):
    # self.LBReqSock = self.context.socket(zmq.REQ)
    LBReqSock.setsockopt(zmq.RCVTIMEO, SOCKET_TIMEOUT)  # Time out when asking worker
    LBReqSock.setsockopt(zmq.SNDTIMEO, SOCKET_TIMEOUT)
    LBReqSock.setsockopt(zmq.REQ_RELAXED, 1)
    LBReqSock.connect(LB_HEALTHADRESS)
    print('MONITOR - Conected to ', LB_HEALTHADRESS)

def sendReq(LBReqSock,command):
    try:
        LBReqSock.connect(LB_HEALTHADRESS)
        command['MONITOR'] = command.pop('iwouldlike')
        print('SENDING : ', command)
        LBReqSock.send_json(command)
        return LBReqSock.recv_json()
    except Exception as e:
        cprint( 'MONITOR - FAILED REQUESTING LOAD BALANCER: LB DOWN ? %s' % str(e), 'FAIL')
        LBReqSock.disconnect(LB_HEALTHADRESS)
        setLBReqSock(LBReqSock)
        return 0
        pass

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/jsontoLB/", WorkersHandler)
        ]
        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=None)


class WorkersHandler(tornado.web.RequestHandler):
    def post(self):
        json_obj = json_decode(self.request.body)
        print('Post data received')

        for key in list(json_obj.keys()):
            print('key: %s , value: %s' % (key, json_obj[key]))

        if 'iwouldlike' in json_obj:
            response_to_send = sendReq(LBReqSock,json_obj)

        print('Response to return')
        pprint.pprint(response_to_send)

        self.write(json.dumps(response_to_send))


def main():
    global LB_HEALTHADRESS,LBReqSock

    parser = argparse.ArgumentParser(description='Monitor Server Script for the pyLoadBalancer module.')
    parser.add_argument('-p', '--pfile', default=None, help='parameter file, in JSON format')
    parser.add_argument('-port', '--port', default=None, help='web server port')
    args = parser.parse_args()
    with open(os.path.join(os.path.dirname(__file__), '../parameters.json'), 'r') as fp:
        CONSTANTS = json.load(fp)  # Loading default constants

    if args.pfile != None:
        try:
            with open(args.pfile, 'r') as fp:
                CONSTANTS.update(json.load(fp))  # updating constants with user defined ones
        except:
            cprint('ERROR : %s is not a valid JSON file' % args.pfile, 'FAIL')
            sys.exit()

    define("port", default=8000, help="run on the given port", type=int)

    LB_HEALTHADRESS = 'tcp://' + CONSTANTS['LB_IP'] + ':' + str(CONSTANTS['LB_HCREPPORT'])
    LBReqSock = context.socket(zmq.REQ)
    setLBReqSock(LBReqSock)

    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

