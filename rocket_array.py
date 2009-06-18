#!/usr/bin/env python
import math, time

##
## TODO: A way to change a rocket's id and x,y coordinates
##

class Rocket(object):
    """x, y = coordinates on a plane
       heading = direction we're currently facing
       rocket_id = a unique identifier for identifying each rocket"""
    next_id = 0
    def __init__(self,rocket_id,(x,y),heading = 0, elevation = 15, recenter = True):
        """(x,y) coordinates, heading in degrees"""
        self.rocket_id = rocket_id
        self.x = x
        self.y = y
        self._hd = heading
        
        if recenter:
            self.center()
            self.liftTo(elevation, False)        
        else:
            self.heading = self._hd
            self.elevation = 15

    def center(self):
        self.turn(-500, False)
        self.turn(180, False)
        self.heading = self._hd
        
        self.lift(-50, False)
        self.lift(15, False)
        self.elevation = 15

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

    def liftTo(self,target_elevation, debug = True):
        if target_elevation == self.elevation:
            return
        self.lift(target_elevation - self.elevation, debug)
        self.elevation = target_elevation
    
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
            direction = radians * 180.0 / math.pi
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

    def turn(self,degrees, debug = True):
        if debug:
            print "%s (%s,%s) is turning %.02f degrees" % (self.rocket_id,
                                                        self.x,self.y, degrees)

    def lift(self,degrees, debug = True):
        if debug:
            print "%s (%s,%s) is lifting %.02f degrees" % (self.rocket_id,
                                                        self.x,self.y, degrees)

    def fire(self, num = 3, debug = True):
        print "%s (%s,%s) is FIRING!  " % (self.rocket_id, self.x, self.y),
        print "~~~>>====  " * min(num,3)
    
    def sleep(self, seconds = 1, debug = True):
        print "%s (%s,%s) is sleeping... " % (self.rocket_id, self.x, self.y),
        print "Zzz...   " * int(seconds)

class ServerRocket(Rocket):
    """Server rockets """
    def __init__(self, server, *args, **kwargs):
        self.server = server
        super(ServerRocket, self).__init__(*args, **kwargs)

    def turn(self,degrees, debug = True):
        self.server.command(self.rocket_id,"turn:%s" % degrees)
        if debug:
            super(ServerRocket, self).turn(degrees)

    def lift(self,degrees, debug = True):
        self.server.command(self.rocket_id,"elevation:%s" % degrees)
        if debug:
            super(ServerRocket, self).lift(degrees)

    def fire(self, num = 3, debug = True):
        self.server.command(self.rocket_id,"fire:%s" % num)
        if debug:
            super(ServerRocket, self).fire(num)
    
    def sleep(self, seconds = 1, debug = True):
        self.server.command(self.rocket_id,"sleep:%s" % seconds)
        if debug:
            super(ServerRocket, self).sleep(seconds)

class RocketArray(list):
    def __getitem__(self, index):
        if isinstance(index,slice) or isinstance(index,list):
            return RocketArray(list.__getitem__(self, index))
        else:
            return list.__getitem__(self, index)

    # Why do we need this?! - sruiz 2009.06.14
    def __getslice__(self, i, j):
        return RocketArray(list.__getslice__(self, i, j))

    def center(self):
        for item in self:
            item.center()
            
    def aimAt(self,x,y):
        for item in self:
            item.aimAt((x,y))
    
    def turnTo(self,target_heading):
        for item in self:
            item.turnTo(target_heading)
            
    def liftTo(self,target_elevation):
        for item in self:
            item.liftTo(target_elevation)

    def turn(self, degrees):
        for item in self:
            item.turn(degrees)
    
    def lift(self, degrees):
        for item in self:
            item.lift(degrees)
   
    def fire(self, num = 5):
        for item in self:
            item.fire(num)
    
    def sleep(self, seconds = 1):
        for item in self:
            item.sleep(seconds)

    def rollcall(self):
        self.lift(40)
        self.lift(-40)
        
        time.sleep(5)
        
        for item in self:
            item.lift(40)
            time.sleep(.5)
            item.lift(-40)
            time.sleep(.5)
            
        time.sleep(5)
        
        self.lift(15)
            
    def cancan(self):
        self.lift(-40)
        time.sleep(2)

        evens = self[::2]
        odds = self[1::2]
        
        evens.lift(40)
        time.sleep(2)

        def odds_lift(i, pause = 2):
            odds.lift(i)
            evens.lift(-i)
            time.sleep(pause)

        def odds_turn(i, pause = 2):
            odds.turn(i)
            evens.turn(-i)
            time.sleep(pause)

    	odds_lift(40)
        odds_lift(-40)
        odds_turn(20,1)
        odds_lift(40)
        odds_turn(-40)
        odds_lift(-40)
        odds_turn(40)
        odds_lift(40)
        odds_turn(-40)
        odds_lift(-40)
        odds_turn(20,1)
        odds_lift(-40)
        odds_lift(40)
        odds_lift(-40)
        self.lift(-40)

def rocket_server(host = "localhost", port = 51285):
    from SOAPpy import SOAPProxy        
    SOAPServer = SOAPProxy("http://%s:%s"% (host,port))
    return SOAPServer

def server_array(server, coords = None, rocket_type = ServerRocket, recenter = False):
    id_list = eval(server.list_rockets())

    if coords == None:
        coords = [(i,0) for i in range(len(id_list))]

    rockets = RocketArray([rocket_type(server, r_id, i, recenter=recenter) for r_id, i in zip(id_list,coords)])
    return rockets

# So...
#########
#
#     To get a list of rockets
#
# server = rocket_server()
# rockets = server_array(server)

#rs = server_array(rocket_server())


