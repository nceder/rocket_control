#!/usr/bin/env python

import SOAPpy
import Queue
import sys

rockets = {}

def register(id):
    global rockets
    rockets[id]=Queue.Queue()
    print id
 
def unregister(pos):
    global rockets
    rockets.pop(pos)

def command(pos, command):
    if command.lower() == "stop":
        command = "stop:0"
    print "put", pos, command
    rockets[pos].put(command)

def get_command(id):
    return rockets[id].get()

def num_rockets():
    return len(rockets)

def list_rockets():
    #return repr([rockets.index(x) for x in rockets if x])
    global rockets
    return repr(rockets.keys())

def server_reset():
    global rockets
    rockets={}
    print "Server Reset!"

if __name__ == "__main__":
    ip="127.0.0.1"
    port=51285
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    server = SOAPpy.ThreadingSOAPServer((ip, port))
    server.registerFunction(register)
    server.registerFunction(unregister)
    server.registerFunction(command)
    server.registerFunction(num_rockets)
    server.registerFunction(get_command)
    server.registerFunction(server_reset)
    server.registerFunction(list_rockets)
    server.serve_forever()
 
        
