#!/usr/bin/env python
import math

class Rocket():
    '''x, y = coordinates on a plane
       heading = direction we're currently facing
       rocket_id = a unique identifier for identifying each rocket'''
    next_id = 0
    def __init__(self,(x,y),heading = 0, elevation = 15):
        '''(x,y) coordinates, heading in degrees'''
        self.rocket_id = Rocket.next_id
        Rocket.next_id += 1
        self.x = x
        self.y = y

        self.center()
        self.turnTo(heading)
        self.liftTo(elevation, False)        

    def change_id_to(self, new_id):
        self.rocket_id = new_id

    def center(self):
        self.turn(-500, False)
        self.turn(180, False)
        self.heading = 0
        
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
            print "%s (%s,%s) is turning %s degrees" % (self.rocket_id,
                                                        self.x,self.y, degrees)

    def lift(self,degrees, debug = True):
        if debug:
            print "%s (%s,%s) is lifting %s degrees" % (self.rocket_id,
                                                        self.x,self.y, degrees)

    def fire(self, num = 3, debug = True):
        print "%s (%s,%s) is FIRING!  " % (self.rocket_id, self.x, self.y),
        print "~~~>>====  " * min(num,3)
    
    def sleep(self, seconds = 1, debug = True):
        print "%s (%s,%s) is sleeping... " % (self.rocket_id, self.x, self.y),
        print "ZZZzzz...   " * int(seconds)

class ServerRocket(Rocket):
    '''Server rockets '''
    def __init__(self, server, *args, **kwargs):
        self.server = server
        super(ServerRocket, self).__init__(self,*args, **kwargs)

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
    def __init__(self,*args,**kwargs):
        list.__init__(self,*args,**kwargs)

    def __getitem__(self, index):
        if isinstance(index,slice):
            return RocketArray(list.__getitem__(self, index))
        else:
            return list.__getitem__(index)

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
        
        self.sleep(5)
        
        for item in self:
            item.lift(40)
            item.sleep(.5)
            item.lift(-40)
            item.sleep(.5)
            
        self.sleep(5)
        
        self.lift(40)
        self.lift(-40)
        
        self.sleep(5)
        
        self.lift(15)
            
    def cancan(self):
        '''May not fail quite so horribly now.'''
        return # But still, it probably does...
        odds = self[1::2]
        evens = RocketArray(self[::2])

        def pause(seconds=5):
            self.sleep(seconds)
        
        self.lift(-40)
        pause()
        evens.lift(40)
        pause(1)
        for i in range(2):
            odds.lift(40)
            evens.lift(-40)
            pause(1)
        self.lift(-40)

if __name__ == "__main__":
    import sys
    from SOAPpy import SOAPProxy
    host = "192.168.2.129"
    port = 51285
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    SOAPServer = SOAPProxy("http://%s:%d" % (host,port))

    # TEST CODE HERE.
    # Text only rockets =         Rocket ((x,y),heading)
    # Special server rockets =    ServerRocket(SOAPServer,(x,y),heading)
