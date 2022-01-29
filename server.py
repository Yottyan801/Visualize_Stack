from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from http import HTTPStatus
import cgi
import os
import sys
import urllib.parse
import json
import lldbapi
import pprint
import threading
import time
import re

PORT = 8000
top_page = "html/access.html"
assign = 0


class URLstruct:
    path = ""
    query = {}


class ServerHandler(SimpleHTTPRequestHandler):
    enc = sys.getfilesystemencoding()
    debug_sign = 4
    debugger = lldbapi.lldbapi()
    thread = threading.Thread()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("GET:%s" % self.path)
        url = self.urlparse()
        # print(vars(url))
        if url.path[0] == "":
            self.send_data("text/html", file_path=top_page)
        elif url.path[0] == "favicon.ico":
            self.send_data("image/png", file_path="image/favicon.png")
        elif url.path[0] == "js":
            self.send_data("text/js", file_path="js/"+url.path[1])
        elif url.path[0] == "css":
            self.send_data("text/css", file_path="css/"+url.path[1])
        elif url.path[0] == "launch":
            self.debugger.CreateBPAtFunc()
            print("Launch:"+self.debugger.file.GetFilename())
            self.debugger.Launch()
            stackdict = self.make_dict()
            self.send_data("text/json", data=json.dumps(stackdict))

        elif url.path[0] == "skip":
            if self.debugger.thread.is_alive():
                self.send_data(
                    "text/json", data='{"thread":"false","Output":"Please wait ..."}')
            else:
                self.debugger.thread = threading.Thread(
                    target=self.debugger.Continue)
                self.debugger.thread.start()
                stackdict = self.make_dict()
                self.send_data("text/json", data=json.dumps(stackdict))
        elif url.path[0] == "continue":
            if self.debugger.thread.is_alive():
                self.send_data(
                    "text/json", data='{"thread":"false","Output":"Please wait ..."}')
            else:
                self.debugger.thread = threading.Thread(
                    target=self.debugger.AllThreadStepOver)
                self.debugger.thread.start()
                stackdict = self.make_dict()
                self.send_data("text/json", data=json.dumps(stackdict))

        elif url.path[0] == "input":
            stackdict = {}
            inputStr = url.query.get("inputStr")
            self.debugger.Input(inputStr)
            self.debugger.thread.join()

    def do_POST(self):
        url = self.urlparse()
        if url.path[0] == 'breakpoint':
            self.debugger.Create()
            length = self.headers.get('content-length')
            nbytes = int(length)
            rawPostData = self.rfile.read(nbytes)
            decodedPostData = rawPostData.decode(self.enc)
            #print(decodedPostData)
            if decodedPostData:
                bplist = [int(d) for d in decodedPostData.split(',')]
                print(bplist)
                res = self.debugger.CreateBPAtDesignatedLine(bplist)
            else:
                res = True
        else:
            length = self.headers.get('content-length')
            nbytes = int(length)
            rawPostData = self.rfile.read(nbytes)
            decodedPostData = rawPostData.decode(self.enc)
            print(decodedPostData)
            #print(self.headers)
            filename = self.headers.get('Origin')
            filename = filename.split('/')[-1]
            with open("Csource/"+filename+'.c', mode='w') as f:
                f.write(decodedPostData)

            res = self.debugger.compile("Csource/"+filename+'.c', "pthread",
                                        bin_path="Csource/bin/"+filename)
            
        if not res:
            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.end_headers()
        else:
            encoded = decodedPostData.encode(self.enc)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/plain; charset=%s" % self.enc)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()

            self.wfile.write(encoded)

    def make_dict(self):
        dictionary = {}
        dictionary['thread'] = self.debugger.stackinfo
        dictionary['Output'] = self.debugger.Output()
        dictionary['state'] = self.debugger.procState
        dictionary['module'] = self.debugger.module.GetFilename()
        # pprint.pprint(dictionary)
        return dictionary

    def send_data(self, datatype, file_path="", data=""):
        if file_path:
            f = open(file_path, "rb")
            contents = f.read()
            f.close()
        else:
            contents = data.encode(self.enc, "surrogateescape")
        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-type", "%s; charset=%s" % (datatype, self.enc))
        self.end_headers()
        self.wfile.write(contents)

    def urlparse(self):
        parse_url = urllib.parse.urlparse(self.path)
        url = URLstruct
        url.path = parse_url.path[1:].split('/')
        print(url.path)
        if parse_url.query:
            for index in parse_url.query.split("&"):
                url.query.update([tuple(index.split('='))])

        return url


def main():
    handler = ServerHandler
    httpd = HTTPServer(('', PORT), handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
