#!/usr/bin/env python
from rocket_array import *
import turtle

def toLogo(heading):
    if heading > 90:
        return 360 - (heading - 90)
    return 90 - heading

class TurtleRocket(ServerRocket):
    '''Turtle rockets. Barely started...'''
    def __init__(self, server, rocket_id,(x,y), heading = 0, *args, **kwargs):
        self.turtle = turtle.Turtle()
        super(TurtleRocket, self).__init__(server, rocket_id,(x,y),
                                           heading = heading, *args, **kwargs)
        self.turtle.shape("arrow")
        self.turtle.penup()
        self.turtle.goto(x,y)
        self.turtle.setheading(toLogo(heading))

    def turn(self,degrees, debug = True):
        if -180 < degrees < 0:
            self.turtle.left(abs(degrees))
        elif 0 < degrees < 180:
            self.turtle.right(degrees)
        super(TurtleRocket, self).turn(degrees)
    
    def center(self):
        self.turtle.setheading(toLogo(self._hd))
        super(TurtleRocket, self).center()

screen = turtle.Screen()
screen.mode("logo")
screen.setup(width = 0.5, height = 0.5)
screen.title("Turtle Rockets!")
screen.setworldcoordinates(-2,-2,4,4)

#    (id, (x,y), heading)
rocket_info = ((0,(0,0),0),
               (1,(1,0),0),
               (2,(2,0),0))

server = rocket_server()

rs = RocketArray([TurtleRocket(server, r_id, loc, head, recenter=False)
                  for r_id, loc, head in rocket_info])
