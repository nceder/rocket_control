#!/usr/bin/env python

# Math stuff for heading calculations
import math
def toRadians(degrees):
    return degrees * math.pi / 180.0
def toDegrees(radians):
    return radians * 180.0 / math.pi

import sys
import time
from SOAPpy import SOAPProxy
import rocket_control_soap
host = "192.168.2.129"
port = 51285
if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])

class ArrayNode():
    server = SOAPProxy("http://%s:%d" % (host,port))
    next_id = 0
    def __init__(self,(x,y),heading = 0, elevation = 0):
        '''(x,y) coordinates, heading in degrees'''
        self.rocket_id = ArrayNode.next_id
        ArrayNode.next_id += 1

        self.x = x
        self.y = y

        self.center()
        self.turnTo(heading)
        self.lift(elevation)        
           
    def turn(self,degrees, debug = True):
        ArrayNode.server.command(self.rocket_id,"turn:%s" % degrees)
        #if debug:
        #    print "%s (%s,%s) is turning %s degrees" % (self.rocket_id, self.x,self.y, degrees)

    def turnTo(self,target_heading):
        if target_heading == self.heading:
            return
        rT = (target_heading - self.heading) % 360
        lT = (self.heading - target_heading) % 360
        if rT < lT:
            self.turn(rT)
        else:
            self.turn(-lT)
        self.heading = target_heading
        
    def lift(self,degrees, debug = False):
        ArrayNode.server.command(self.rocket_id,"elevation:%s" % degrees)
        if debug:
            print "%s (%s,%s) is lifting %s degrees" % (self.rocket_id, self.x,self.y, degrees)

    def liftTo(self,target_elevation):
        if target_elevation == self.elevation:
            return
        self.lift(target_elevation - self.elevation)
        self.elevation = target_elevation

    def center(self):
        self.turn(-500, False)
        self.turn(180, False)
        self.heading = 0
        
        self.lift(-50, False)
        self.lift(15, False)
        self.elevation = 15
    
    def calculate_heading(self,dx,dy):
        target_heading = None
        if dx and not dy:
            if dx > 0:
                target_heading = 90
            else:
                target_heading = 270
        elif dy and not dx:
            if dy > 0:
                target_heading = 0
            else:
                target_heading = 180
        elif dx and dy:
            radians = math.atan(float(dy) / float(dx))
            direction = toDegrees(radians)
            if dx > 0:
                direction -= 90
            if dx < 0:
                direction += 90
            direction %= 360
            target_heading = 360 - direction
        if target_heading == None:
            target_heading = self.heading
        return target_heading

    def aimAt(self,(x,y)):
        dx = float(x) - float(self.x)
        dy = float(y) - float(self.y)
        target_heading = self.calculate_heading(dx,dy)
        self.turnTo(target_heading)

    def fire(self, num = 5, debug = True):
        ArrayNode.server.command(self.rocket_id,"fire:%s" % num)
        if debug:
            print "%s (%s,%s) is FIRING!  " % (self.rocket_id, self.x,self.y),
            print "~~~>>====  " * min(num,3)
    
    def sleep()

class RocketArray(list):
    def __init__(self,arr*):
        list.__init__(self, arr)

    def __getitem__(self, index):
        if isinstance(index,slice):
            return RocketArray(list.__getitem__(index))
        else:
            return list.__getitem__(index)

    def turn(self, degrees):
        for item in self:
            item.turn(degrees)
    
    def lift(self, degrees):
        for item in self:
            item.lift(degrees)

    def center(self):
        for item in self:
            item.center()
            
    def aimAt(self,x,y):
        for item in self:
            item.aimAt((x,y))
   
    def fire(self, num = 5):
        for item in self:
            item.fire(num)def pause(seconds=5):
    time.sleep(seconds)


    def rollcall(self):
        self.allLift(40)
        self.allLift(-40)
        
        time.sleep(5)
        
        for item in self:
            item.lift(40)
            time.sleep(.5)
            item.lift(-40)
            time.sleep(.5)
            
        time.sleep(5)
        
        self.allLift(40)
        self.allLift(-40)
        
        time.sleep(5)
        
        self.allLift(15)
            
    def cancan(self):
        def pause(seconds=5):
            time.sleep(seconds)

        '''Fails horribly.'''
        return # seriously, it doesn't work.
        odds = self[1::2]
        evens = RocketArray(self[::2])
        
        self.allLift(-40)
        pause()
        evens.allLift(40)
        pause(1)
        for i in range(2):
            odds.allLift(40)
            evens.allLift(-40)
            pause(1)
        self.allLift(-40)
