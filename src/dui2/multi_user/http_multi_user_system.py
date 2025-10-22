from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler#, HTTPServer

import http.server, socketserver


import json, sys

from dui2 import only_server
from dui2.multi_user.sever_side import AuthSystem

""" The HTTP request handler """
class RequestHandler(BaseHTTPRequestHandler):
    auth = AuthSystem()
    lst_dui2_servers = []
    def _send_cors_headers(self):
        ''' Sets headers required for CORS '''
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def send_ok_dict(self, body = None):
        '''used by both, GET or POST,'''
        response = {}
        response["connection status"] = "OK"
        response["body"] = body
        print("response =", response)

        self.wfile.write(bytes(json.dumps(response), "utf8"))

    def do_POST(self):
        print("do_POST")
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        dataLength = int(self.headers["Content-Length"])
        print("dataLength =", dataLength)
        data = self.rfile.read(dataLength)

        body_str = str(data.decode('utf-8'))

        print("body_str =", body_str)
        url_dict = json.loads(body_str)
        command = url_dict["command"]
        print("command =", command)

        username = url_dict["data_user"]
        password = url_dict["data_pass"]

        if command == 'register':
            success, message = self.auth.create_user(username, password)
            print(f"Result: {message}")

        elif command == 'login':
            success, message = self.auth.login(username, password)
            if success:
                print(f"Login successful! Your token: {message}")
                #TODO: consider launching a separated process only if you can
                #TODO: get or pass the token, instead of the next line
                new_dui2_server = only_server.main(do_join = False)
                self.lst_dui2_servers.append(new_dui2_server)

            else:
                print(f"Login failed: {message}")

        try:
            resp_dict = {"success":success, "message":message}

        except UnboundLocalError:
            resp_dict = {"success":False, "message":"command not found"}

        self.send_ok_dict(body = resp_dict)

    def do_GET(self):
        print("do_GET")
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

        url_path = self.path
        url_dict = parse_qs(urlparse(url_path).query)

        print("url_path =", url_path)
        print("url_dict =", url_dict)
        try:
            command = url_dict['command'][0]
            token = url_dict['token'][0]

            if command == 'validate':
                success, message = auth.validate(token)

            elif command == 'logout':
                success, message = auth.logout(token)

            try:
                resp_dict = {"success":success, "message":message}

            except UnboundLocalError:
                resp_dict = {"success":False, "message":"command not found"}

        except KeyError:
            resp_dict = {"success":False, "message":"Key not found"}

        self.send_ok_dict(body = resp_dict)


def main():
    ip_adr = "127.0.0.1"
    port_num = 34567

    socketserver.ThreadingTCPServer.allow_reuse_address = True

    with socketserver.ThreadingTCPServer(
        (ip_adr, port_num), RequestHandler
    ) as httpd:
        print("Hosting server on: \n http://" + ip_adr + ":" + str(port_num))
        try:
            httpd.serve_forever()

        except KeyboardInterrupt:
            print(" Interrupted with Keyboard ")
            httpd.server_close()




