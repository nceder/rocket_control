#!/usr/bin/python

""" rocket control

    This controls DreamCheeky rocket launchers. It will issue commands independently
    to as many launchers as are recognized on the system.
    uses the rocket_backend.py library from the pyrocket package

    Functions:
    arm_launchers() - top level function to get list of launchers on system

    Classes:
    rocket_thread - class to handle threading of commands
    Rocket - class to control launcher
       Rocket(rocket) - creates Rocket object as wrapper for rocket_backend.py's rocket class
       turn(degrees) - issues command to turn, positve for right, negative for left
       elevation(degrees) - changes elevation - positive for up...
       fire(shots) - fires shots times
       stop() - clears the command list, ending the current command thread
       send_command(command, duration) - sends command duration pair to rocket_thread
       calibrate(reps) - exercises motion and calibrates speed of movement
       precharge() - attempts to precharge with short firing sequence... mixed results
       
    """

import rocket_backend, sys, time, threading
from SOAPpy import SOAPProxy
host = "localhost"
port = 51285
if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])
server =  SOAPProxy("http://%s:%s"% (host,port))

# constants for commands
DN = 0
UP = 1
LF = 2
RT = 3
FIRE = 4
STOP = 5
CALIBRATE = 10
command_list = [DN, UP, LF, RT, FIRE, STOP]
command_names = ["DN", "UP", "LF", "RT", "FIRE", "STOP"]
# estimated degrees of travel for each command - limit to limit
degrees = [30.0,30.0,305.0,305.0]
lock = threading.Lock()
class rocket_soap_thread(threading.Thread):
    """ thread which executes rocket commands found
        in a command list of (command, duration) tuples
    """
    def __init__(self, rocket):
        threading.Thread.__init__(self)
        self.rocket = rocket
        self.id = server.register()
        # average times for each command -  limit to limit
        self.times = [1.8,1.8,14.0, 14.3]
        # seconds per degree of travel for each command
        self.degree_times = [self.times[0]/degrees[0],self.times[1]/degrees[1],self.times[2]/degrees[2],self.times[3]/degrees[3], 4, 0]

    def run(self):
        """ will run command, duration tuples from commands list until list is empty.
            thread dies after list is empty
        """
        command = 8
        while command != STOP:
            commandstr = server.get_command(self.id)
            command, duration = self.translate_command(commandstr)
##             print self.id, command, duration
            if command == CALIBRATE:
                self.calibrate(duration)
                continue
            lock.acquire()
            start_time=time.time()
            self.rocket.start_movement(command)
            lock.release()

            while start_time + duration > time.time():
                time.sleep(0.1)
                # quit timing loop if limit has been hit
                if command < FIRE and self.rocket.check_limits()[command]:
                    break
            if command == FIRE:
                lock.acquire()
                self.rocket.issue_command(DN)
                self.rocket.issue_command(UP)
                self.rocket.stop_movement()
                lock.release()
            lock.acquire()
            self.rocket.stop_movement()
            lock.release()

        server.unregister(self.id)

    def calibrate(self, reps=5):
        """ calibrates speed of travel by exercising LF/RT and elevation reps times """
        global times,  degree_times
        cmd_names=["Down", "Up", "Left", "Right"]
        for command in [DN,LF]:
            test_times = []
            self.rocket.start_movement(command+1)
            while not self.rocket.check_limits()[command+1]:
                time.sleep(.1)
            for x in range(reps):
                start_time = time.time()
                self.rocket.start_movement(command)
                while not self.rocket.check_limits()[command]:
                    time.sleep(.1)
                test_times.append(time.time()-start_time)
                start_time = time.time()
                self.rocket.start_movement(command+1)
                while not self.rocket.check_limits()[command+1]:
                    time.sleep(.1)
                test_times.append(time.time()-start_time)

            self.times[command] = sum(test_times[::2])/len(test_times[::2])
            print cmd_names[command], test_times[::2]
            self.times[command+1] = sum(test_times[1::2])/len(test_times[1::2])
            print cmd_names[command+1], test_times[1::2]
            print "Averages:", self.times[command:command+2]
            self.degree_times = [self.times[0]/degrees[0],self.times[1]/degrees[1],self.times[2]/degrees[2],self.times[3]/degrees[3],4,0]


        
    def translate_command(self, commandstr):
        try:
            command_parts = commandstr.lower().split(":")
            command = command_parts[0]
            amount = float(command_parts[1])
            if command == "elevation":
                if amount < 0:
                    command = DN
                else:
                    command = UP
            elif command == "turn":
                if amount < 0:
                    command = LF
                else:
                    command = RT
            elif command == "fire":
                command = FIRE
            elif command == "stop":
                command = STOP
            elif command == "calibrate":
                command = CALIBRATE
                return command, amount
            duration = abs(amount) * self.degree_times[command]
        except Exception, e:
            print "unable to parse commandstr:", commandstr
            print e
            command, duration = (8,0)
        return command, duration


def arm_launchers():
    """ function to acquire rockets and return a list of Rocket objects """
    lm = rocket_backend.RocketManager()
    lm.acquire_devices()
    rockets = [rocket_soap_thread(launcher) for launcher in lm.launchers]
    for rocket in rockets:
        rocket.start()
    return rockets
      
def main():

    # get list of Rocket objects 
    rockets = arm_launchers()

##     for rocket in rockets:
## ##         rocket.calibrate(1)
##         rocket.turn(-360)
##         rocket.turn(30)
##         rocket.elevation(-30)
##         rocket.elevation(29)

#    rockets[0].turn(90)
#    rockets[0].fire(1)
#    rockets[1].turn(180)
#    rockets[1].fire(2)

#    raw_input()

if __name__ == "__main__":
    main()
