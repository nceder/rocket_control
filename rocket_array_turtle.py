#!/usr/bin/env python
from rocket_array import *
import turtle

screen = turtle.Screen()
screen.setup(width = 0.5, height = 0.5)
screen.mode("logo")
screen.setworldcoordinates(-4,-4,4,4)


class TurtleRocket(Rocket):
    '''Turtle rockets. Barely started...'''
    def __init__(self, (x,y), heading = 0, *args, **kwargs):
        self.turtle = turtle.Turtle()
        self.turtle.goto(x,y)
        super(TurtleRocket, self).__init__((x,y), heading, *args, **kwargs)

    #def turn(self,degrees, debug = True):
    #    self.server.command(self.rocket_id,"turn:%s" % degrees)
    #    if debug:
    #        super(ServerRocket, self).turn(degrees)

rs = RocketArray([TurtleRocket((i,0)) for i in range(-2,3)])
