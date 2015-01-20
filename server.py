import pdb
import os
import json
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool, WebSocket

cherrypy.config.update({'server.socket_port': 9000})
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

if os.path.isfile("points.json"):
    f = open("points.json", "r")
    points = json.loads(f.read())
    f.close()
else:
    points = []

class Root(object):
    @cherrypy.expose
    def index(self):
        return "HI"

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler

class WebWorker(WebSocket):
    def received_message(self, msg):
        global points

        if msg.is_binary:
            return

        if str(msg) == "new":
            self.send(json.dumps(points))
            return

        if str(msg) == "clear":
            points = []
            cherrypy.engine.publish("websocket-broadcast", "clear");

        p = str(msg).split(",")
        if len(p) != 2:
            return

        try:
            px = int(p[0])
            py = int(p[1])
        except:
            return

        points.append(tuple(p))
        cherrypy.engine.publish("websocket-broadcast", json.dumps([[px,py]]))

        f = open("points.json", "w")
        f.write(json.dumps(points))
        f.close()

cherrypy.quickstart(Root(), config={'/ws': {'tools.websocket.on': True, 'tools.websocket.handler_cls': WebWorker}})
