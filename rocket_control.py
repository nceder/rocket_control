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

# constants for commands
DN = 0
UP = 1
LF = 2
RT = 3
FIRE = 4
command_list = [DN, UP, LF, RT, FIRE]
# average times for each command -  limit to limit
times = [1.8,1.8,14.0, 14.3]
# estimated degrees of travel for each command - limit to limit
degrees = [30.0,30.0,315.0,315.0]
# seconds per degree of travel for each command
degree_times = [times[0]/degrees[0],times[1]/degrees[1],times[2]/degrees[2],times[3]/degrees[3]]

class rocket_thread(threading.Thread):
    """ thread which executes rocket commands found
        in a command list of (command, duration) tuples
    """
    def __init__(self, rocket, commands):
        threading.Thread.__init__(self)
        self.rocket = rocket
        self.commands = commands[:]

    def run(self):
        """ will run command, duration tuples from commands list until list is empty.
            thread dies after list is empty
        """
        while self.commands:
            command, duration = self.commands.pop(0)
            start_time=time.time()
            self.rocket.start_movement(command)
            while start_time + duration > time.time():
                time.sleep(0.1)
                # quit timing loop if limit has been hit
                if command < FIRE and self.rocket.check_limits()[command]:
                    break

            if command == FIRE:
                self.rocket.issue_command(DN)
                self.rocket.issue_command(UP)
                self.rocket.stop_movement()

class Rocket(object):
    """Class which creates a thread to manage a rocket's commands"""
    counter = 1
    def __init__(self, rocket):
        self.rocket = rocket
        self.rocket_id = Rocket.counter
        Rocket.counter += 1
        self.rocket.id = self.rocket_id
        self.thread = None
        print "Rocket launcher #%d armed" % self.rocket_id

    def turn(self, degrees):
        """turns turret - negative degrees for left"""
        if degrees < 0:
            degrees = -degrees
            direction = LF
            time = degrees * degree_times[direction]
        else:
            direction = RT
            time = degrees * degree_times[direction]
        self.send_command(direction, time)

    def elevation(self, degrees):
        """adjusts elevation - positive degrees for up """
        if degrees < 0:
            degrees = -degrees
            direction = DN
            time = degrees * degree_times[direction]
        else:
            direction = UP
            time = degrees * degree_times[direction]
        self.send_command(direction, time)

    def fire(self, shots=3):
        """Runs fire command long enough to fire shots"""
        self.send_command(FIRE, shots* 4 + 0.2)

    def precharge(self):
        """ attempts to pre-charge with short fire cycle """
        self.send_command(FIRE, 2.7)
        
    def stop(self):
        """clears commands list """
        if self.thread.is_alive():
            self.thread.commands = []

    def send_command(self, command, duration):
        if self.thread and self.thread.commands:
            self.thread.commands.append((command,duration))
        else:
            self.thread = rocket_thread(self.rocket, [(command,duration), (8,1)])
            self.thread.start()
            
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

            times[command] = sum(test_times[::2])/len(test_times[::2])
            print cmd_names[command], test_times[::2]
            times[command+1] = sum(test_times[1::2])/len(test_times[1::2])
            print cmd_names[command+1], test_times[1::2]
            print "Averages:", times[command:command+2]
            degree_times = [times[0]/degrees[0],times[1]/degrees[1],times[2]/degrees[2],times[3]/degrees[3]]

def arm_launchers():
    """ function to acquire rockets and return a list of Rocket objects """
    lm = rocket_backend.RocketManager()
    lm.acquire_devices()
    rockets = [Rocket(launcher) for launcher in lm.launchers]
    return rockets
    
def main():

    # get list of Rocket objects 
    rockets = arm_launchers()

    for rocket in rockets:
##         rocket.calibrate(1
        rocket.elevation(-10)
        rocket.elevation(30)
        rocket.fire(1)

#    rockets[0].turn(90)
#    rockets[0].fire(1)
#    rockets[1].turn(180)
#    rockets[1].fire(2)

#    raw_input()

if __name__ == "__main__":
    main()
