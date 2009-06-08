#!/usr/bin/python

from SOAPpy import SOAPProxy
import rocket_control
import sys
helpstr = """Commands take the form of

        rocket_list|command:amount
        
    where rocket_list is a rocket_id, a comma separated list of rocket_ids, or "all"
    and command is one of:
        elevation, turn, fire, stop
    and amount is either degrees (negative for left and down) or shots.
        (for stop, the amount is ignored)

           examples:
              all|turn:30        - all rockets turn 30 degrees right
              0|elevation:-5     - first rocket down 5 degrees
              all|fire:3         - fire all rockets 3 times
              0,2,4|calibrate:2  - calibrate rockets 0,2, and 4 two cycles
              all|stop           - stops all rocket threads, ends remote programs

    Other commands:
        quit - ends this program
        reset - resets server
        help or ? - prints this message
        """
host = "localhost"
port = 51285
if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])
server =  SOAPProxy("http://%s:%d" % (host,port))
print """Interactive rocket launcher console...\n"""
print helpstr
num_rockets = 0
inputstr = "|"
while inputstr != "quit":
    if num_rockets != server.num_rockets():
        num_rockets = server.num_rockets()
        print num_rockets, "rockets found"
    if inputstr in ["?", "help"]:
        print helpstr
        inputstr = "|"
    elif inputstr == "reset":
        server.server_reset()
        inputstr = "|"
    elif inputstr == "register":
        server.register()
        inputstr = "|"
    elif inputstr[:10] == "unregister":
        server.unregister(int(inputstr.split(":")[-1]))
        inputstr = "|"
    elif inputstr == "list":
        print server.list_rockets()
        inputstr = "|"
        
    rocket_str, commandstr = inputstr.split("|")
    if rocket_str == "all":
        rockets = eval(server.list_rockets())
    else:
        rockets = eval("["+rocket_str+"]")
    for rocket in rockets:
        try:
            command = server.command(rocket,commandstr)
        except Exception, e:
            print e
    inputstr = raw_input("-->").lower().strip()
    if not inputstr:
        inputstr = "|"
    
    
