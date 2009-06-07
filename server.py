#!/usr/bin/env python

import SOAPpy
import Queue
import sys

rockets = []

def register():
    global rockets
    rockets.append(Queue.Queue())
    print len(rockets)
    return len(rockets)-1
 
def unregister(pos):
    global rockets
    rockets[pos] = None

def command(pos, command):
    global rockets
    if command.lower() == "stop":
        command = "stop:0"
    print "put", pos, command
    rockets[pos].put(command)

def get_command(pos):
    global rockets
    return rockets[pos].get()

def num_rockets():
    global rockets
    return len(rockets)

def server_reset():
    global rockets
    rockets=[]
    print "Server Reset!"


if __name__ == "__main__":
    ip="localhost"
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
    server.serve_forever()
 
        
