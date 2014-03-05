# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 09:18:59 2014

@author: jibi
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 16:05:40 2014

@author: jibi
"""
# -*- encoding: UTF-8 -*-

import sys
import time
from math import *
from naoqi import ALProxy
from naoqi import motion

"""Convert a set of coordinates for the sword into a set of coordinates
for the NAO's hand.
No rotations along y-axis nor z-axis.
l-parameter is the sword length"""
def sw_coord(pos, l):
    al = pos[3]
    px = pos[0]
    py = pos[1]+l*cos(al)
    pz = pos[2]+l*sin(al)
    
    return [px,py,pz,al,0.,0.]

def main(robotIP, position):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e


    # Example showing how to set LArm Position, using a fraction of max speed
    chainName = "LArm"
    space     = motion.FRAME_TORSO
    useSensor = False

    fractionMaxSpeed = 0.5
    axisMask         = 7 # total control
    
    motionProxy.setPosition(chainName, space, position, fractionMaxSpeed, axisMask)
    time.sleep(3)
    current = motionProxy.getPosition(chainName, space, useSensor)
    print position     
    print current
    print "end"



if __name__ == "__main__":
    robotIp = "172.20.11.131"

    if len(sys.argv) <= 1:
        position         = [0.1,-0.2,0.1,0.]

    else:
        #robotIp = sys.argv[1]
        position = eval('['+sys.argv[1]+']')

    main(robotIp, sw_coord(position,0.2))