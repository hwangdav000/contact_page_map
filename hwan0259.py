#!/usr/bin/env python3
# See https://docs.python.org/3.x/library/socket.html
# for a description of python socket and its parameters
#
# Copyright 2019, Shaden Smith, Koorosh Vaziri,
# Niranjan Tulajapure, Ambuj Nayab,
# Akash Kulkarni, Ruofeng Liu and Daniel J. Challou
# for use by students enrolled in Csci 4131 at the University of
# Minnesota-Twin Cities only. Do not reuse or redistribute further
# without the express written consent of the authors.
#
# This is a reworked version of EchoServer to get you started.
# It responds correctly to a HEAD command.
#add the following
import socket
import os
import stat
import sys
import urllib.parse
import datetime
import re
from threading import Thread
from argparse import ArgumentParser
BUFSIZE = 4096

#add the following
CRLF = '\r\n'
#LINK1 = 'Link: <style.css>;rel= stylesheet{}{}'.format(CRLF,CRLF)
METHOD_NOT_ALLOWED = 'HTTP/1.1 405 METHOD NOT ALLOWED{}Allow: GET,HEAD, POST {}Content-Type: text/html; charset=UTF-8{}Connection: close{}{}'.format(CRLF, CRLF, CRLF, CRLF, CRLF)
SPACE = '{}{}'.format(CRLF,CRLF)
OK = 'HTTP/1.1 200 OK{}{}{}'.format(CRLF, CRLF, CRLF)
OK_GET = 'HTTP/1.1 200 OK{}Content-Type: text/html; charset=UTF-8{}{}'.format(CRLF, CRLF, CRLF)
OK_GET2 = 'HTTP/1.1 200 OK{}Content-Type: image/*{}{}'.format(CRLF, CRLF, CRLF)
OK_GET3 = 'HTTP/1.1 200 OK{}Content-Type: audio/*{}{}'.format(CRLF, CRLF, CRLF)
OK_GET4 = 'HTTP/1.1 200 OK{}Content-Type: text/css{}{}'.format(CRLF, CRLF, CRLF)
OK_GET5 = 'HTTP/1.1 200 OK{}Content-Type: */*{}{}'.format(CRLF, CRLF, CRLF)
NOT_FOUND = 'HTTP/1.1 404 NOT FOUND{}Content-Type: text/html; charset=UTF-8{}Connection:close{}{}'.format(CRLF, CRLF, CRLF, CRLF)
FORBIDDEN = 'HTTP/1.1 403 FORBIDDEN{}Content-Type: text/html; charset=UTF-8{}Connection:close{}{}'.format(CRLF, CRLF, CRLF, CRLF)
NOT_ACCEPTABLE = 'HTTP/1.1 406 NOT ACCEPTABLE{}Content-Type: text/html; charset=UTF-8{}Connection:close{}{}'.format(CRLF, CRLF, CRLF, CRLF)
MOVED_PERMANENTLY = 'HTTP/1.1 301 MOVED PERMANENTLY{}Location:https://www.youtube.com/{}Connection: close{}{}'.format(CRLF, CRLF, CRLF, CRLF)

def get_contents(fname):
    with open(fname, 'r') as f:
        return f.read()

def check_perms(resource):
    """Returns True if resource has read permissions set on
    'others'"""
    stmode = os.stat(resource).st_mode
    return (getattr(stat, 'S_IROTH') & stmode) > 0

def client_talk(client_sock, client_addr): # Not used anymore!!!!
    print('talking to {}'.format(client_addr))
    data = client_sock.recv(BUFSIZE)
    while data:
        print(data.decode('utf-8'))
        data = client_sock.recv(BUFSIZE)
    # clean up
    client_sock.shutdown(1)
    client_sock.close()
    print('connection closed.')

class HTTP_HeadServer: #A re-worked version of EchoServer
    def __init__(self, host, port):
        print('listening on port {}'.format(port))
        self.host = host
        self.port = port
        self.setup_socket()
        self.accept()
        self.sock.shutdown()
        self.sock.close()
    def setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(128)
    def accept(self):
        while True:
            (client, address) = self.sock.accept()
            #th = Thread(target=client_talk, args=(client, address))
            th = Thread(target=self.accept_request, args=(client, address))
            th.start()
    # here, we add a function belonging to the class to accept
    # and process a request
    def accept_request(self, client_sock, client_addr):
        print("accept request")
        data = client_sock.recv(BUFSIZE)
        req = data.decode('utf-8') #returns a string with http request
        #COUNT get html, image, audio
        response, x =self.process_request(req) #ret string with http response
        #once we get a response, we chop it into utf encoded bytes
        #and send it (like EchoClient)

        # send http response
        client_sock.send(bytes(response,'utf-8'))
        if (x != None):
            # if image or audio separate send
            client_sock.send(x)
            client_sock.send(bytes(SPACE,'utf-8'))
        #clean up the connection to the client
        #but leave the server socket for recieving requests open
        client_sock.shutdown(1)
        client_sock.close()
        #added method to process requests, only head is handled in this code
    def process_request(self, request):
        print('######\nREQUEST:\n{}######'.format(request))
        # regex jpg|gif|png|jpeg
        p = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:jpg|gif|png|jpeg|jfif))(?:\?([^#]*))?(?:#(.*))?')
        # regex mp3
        q = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:mp3))(?:\?([^#]*))?(?:#(.*))?')
        # css
        r = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:css))(?:\?([^#]*))?(?:#(.*))?')
        # javascript
        s = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:js))(?:\?([^#]*))?(?:#(.*))?')
        # html
        t = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:html))(?:\?([^#]*))?(?:#(.*))?')
        ico = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:ico))(?:\?([^#]*))?(?:#(.*))?')
        find_accept = re.compile('(Accept:).*')
        linelist = request.strip().split(CRLF)
        index_a = -1
        #Find index of Accept:
        for i in range(0,len(linelist)):
            if (find_accept.match(linelist[i])):
                index_a = i
        reqline = linelist[0] #get the request line
        rlwords = reqline.split() # get list of strings on request line
        if len(rlwords) == 0:
            return '', None
        if rlwords[0] == 'HEAD':
            resource = rlwords[1][1:] # skip beginning /
            return self.head_request(resource)
        # Get the resource
        elif rlwords[0] == 'GET':
            resource = rlwords[1][1:] # get the file
            accept = linelist[index_a]
            ##need to make sure accept type matches get type
            #different types of GET
            #ICO don't need pass
            if (ico.match(resource)):
                return '', None
            #image
            if (p.match(resource)):
                a_image = re.compile('.*(image|\*\/\*).*')
                #see if image type is accepted
                if (a_image.match(accept)):
                    return self.get_image(resource)
                else:
                    print("1")
                    return self.e406()
            #mp3
            elif (q.match(resource)):
                a_mp3 = re.compile('.*(audio|\*\/\*).*')
                #see if mp3 type is accepted
                if (a_mp3.match(accept)):
                    return self.get_mp3(resource)
                else:
                    print("2")
                    return self.e406()
            #css
            elif (r.match(resource)):
                a_css = re.compile('.*(text/html|application/xhtml+xml|\*\/\*).*')
                #see if css type is accepted
                if (a_css.match(accept)):
                    return self.get_css(resource)
                else:
                    print("3")
                    return self.e406()
            #js
            elif (s.match(resource)):
                a_js = re.compile('.*(text/html|application/xhtml+xml|\*\/\*).*')
                #see if js type is accepted
                if (a_js.match(accept)):
                    return self.get_js(resource)
                else:
                    print("4")
                    return self.e406()
            #html
            elif (t.match(resource)):
                a_html = re.compile('.*(text/html|application/xhtml+xml|\*\/\*).*')
                #see if html type is accepted
                if (a_html.match(accept)):
                    return self.get_request(resource)
                else:
                    print("5")
                    return self.e406()
            elif (resource == "mytube"):
                return self.get_direct()

            else:
                #only allow specified formats
                #Don't allow for user to just search directory
                return self.e404()
        elif rlwords[0] == 'POST':
            #get body message
            resource = linelist[len(linelist)-1]
            #Post
            return self.post_request(resource)
        else: #add ELIF checks for GET and POST before this else..
            return self.e405()

    def head_request(self, resource):
        """Handles HEAD requests."""
        path = os.path.join('.', resource) #look in directory where server is running
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            ret = OK
        return ret, None
    def get_request(self, resource):
        """Handles GET html requests. """
        path = os.path.join('.', resource) #look in directory to see resource exists
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            print("HANDLING GET REQUEST\n")
            ret = OK_GET
            # reads html file and appends
            with open(resource, encoding='utf-8') as f:
                str = f.read()
            ret= ret + str
        return ret, None
    def post_request(self, resource):
        name_s = re.search('name=', resource)
        email_s = re.search('email=', resource)
        address_s = re.search('address=', resource)
        place_s = re.search('place=', resource)
        url_s = re.search('url=', resource)
        #splice strings
        name = resource[name_s.start()+5:email_s.start()-1]
        email = resource[email_s.start()+6:address_s.start()-1]
        address = resource[address_s.start()+8:place_s.start()-1]
        place = resource[place_s.start()+6:url_s.start()-1]
        url = resource[url_s.start()+4:(len(resource))]
        """Handles GET html requests. """
        print("HANDLING POST REQUEST\n")
        #get vars from resource
        HTML_HEAD = urllib.parse.unquote('<!DOCTYPE html><head><title>Response Form</title><link rel="stylesheet" href="style.css"></head>')
        HTML_SUBMIT = urllib.parse.unquote('<body><h1>Following Form Data Submitted Successfully</h1><table id = "mytable" class = "table">')
        HTML_NAME = urllib.parse.unquote('<tr><td>name</td><td>{}</td></tr>'.format(name))
        HTML_EMAIL = urllib.parse.unquote('<tr><td>email</td><td>{}</td></tr>'.format(email))
        HTML_ADDRESS = urllib.parse.unquote('<tr><td>address</td><td>{}</td></tr>'.format(address))
        HTML_PLACE = urllib.parse.unquote('<tr><td>place</td><td>{}</td></tr>'.format(place))
        HTML_URL = urllib.parse.unquote('<tr><td>url</td><td>{}</td></tr></table></body></html>'.format(url))
        #REPLACE + with space
        HTML_HEAD = HTML_HEAD.replace('+', ' ')
        HTML_SUBMIT = HTML_SUBMIT.replace('+', ' ')
        HTML_NAME = HTML_NAME.replace('+', ' ')
        HTML_EMAIL = HTML_EMAIL.replace('+', ' ')
        HTML_ADDRESS = HTML_ADDRESS.replace('+', ' ')
        HTML_PLACE = HTML_PLACE.replace('+', ' ')
        HTML_URL = HTML_URL.replace('+', ' ')
        HTML_FORM = HTML_HEAD+HTML_SUBMIT+HTML_NAME+HTML_EMAIL+HTML_ADDRESS+HTML_PLACE+HTML_URL
        ret = OK_GET
        # gets html table and appends it
        ret= ret + HTML_FORM
        return ret, None

    def get_image(self, resource):
        """Handles GET image requests. """
        path = os.path.join('.', resource) #look in directory to see resource exists
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            print("HANDLING IMAGE REQUEST\n")
            ret = OK_GET2

        # reads image file and appends
        with open(resource, 'rb') as f:
            str = f.read()

        return ret, str
    def get_mp3(self, resource):
        """Handles GET mp3 requests. """
        path = os.path.join('.', resource) #look in directory to see resource exists
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            print("HANDLING AUDIO REQUEST\n")
            ret = OK_GET3

        # reads mp3 file and appends
        with open(resource, 'rb') as f:
            str = f.read()

        return ret, str
    def get_css(self, resource):
        """Handles GET css requests. """
        path = os.path.join('.', resource) #look in directory to see resource exists
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            print("HANDLING CSS REQUEST\n")
            ret = OK_GET4
            # reads css file and appends
            with open(resource, encoding='utf-8') as f:
                str = f.read()
            ret= ret + str
        return ret, None
    def get_js(self, resource):
        """Handles GET js requests. """
        path = os.path.join('.', resource) #look in directory to see resource exists
        if not os.path.exists(resource):
            return self.e404()
        elif not check_perms(resource):
            return self.e403()
        else:
            print("HANDLING JS REQUEST\n")
            ret = OK_GET5
            # reads js file and appends
            with open(resource, encoding='utf-8') as f:
                str = f.read()
            ret= ret + str
        return ret, None
    def get_direct(self):
        ret = MOVED_PERMANENTLY
        return ret, None
    # error methods
    def e403(self):
        ret = FORBIDDEN
        with open('403.html', encoding='utf-8') as f:
            str = f.read()
        ret = ret + str
        return ret, None
    def e404(self):
        ret = NOT_FOUND
        with open('404.html', encoding='utf-8') as f:
            str = f.read()
        ret = ret + str
        return ret, None
    def e405(self):
        ret = METHOD_NOT_ALLOWED
        str = '405: METHOD_NOT_ALLOWED'
        ret = ret + str
        return ret, None
    def e406(self):
        ret = NOT_ACCEPTABLE
        str = '406: NOT_ACCEPTABLE'
        ret = ret + str
        return ret, None


#to do a get request, read resource contents and append to ret value.
#(you should check types of accept lines before doing so)
# You figure out the rest
def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost',
    help='specify a host to operate on (default:localhost)')
    parser.add_argument('-p', '--port', type=int, default=9001,
    help='specify a port to operate on (default:9001)')
    args = parser.parse_args()
    return (args.host, args.port)
if __name__ == '__main__':
    (host, port) = parse_args()
    HTTP_HeadServer(host, port) #Formerly EchoServer
