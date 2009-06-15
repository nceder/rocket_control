#!/usr/bin/env python
from rocket_array import *
import turtle

screen = turtle.Screen()
screen.mode("logo")
screen.setup(width = 0.5, height = 0.5)
screen.title("Turtle Rockets!")
screen.setworldcoordinates(-4,-4,4,4)

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

    #def turn(self,degrees, debug = True):
    #    self.server.command(self.rocket_id,"turn:%s" % degrees)
    #    if debug:
    #        super(ServerRocket, self).turn(degrees)
    
rs = server_array(rocket_server(), ((-2,-2),(0,2),(2,-2)) , rocket_type = TurtleRocket, recenter = False)
