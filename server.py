#!/usr/bin/env python

import SOAPpy
import Queue
import sys

rockets = []

def register():
    rockets.append(Queue.Queue())
    print len(rockets)
    return len(rockets)-1
 
def unregister(pos):
    global rockets
    rockets[pos] = None

def command(pos, command):
    if command.lower() == "stop":
        command = "stop:0"
    print "put", pos, command
    rockets[pos].put(command)

def get_command(pos):
    return rockets[pos].get()

def num_rockets():
    return len(rockets)

def list_rockets():
    return repr([rockets.index(x) for x in rockets if x])

def server_reset():
    global rockets
    rockets=[]
    print "Server Reset!"

if __name__ == "__main__":
    ip="10.0.0.133"
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
 
        
