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

global backup

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
    
def max_error(pos, dest):  
    return max(abs(pos[0]-dest[0]),abs(pos[1]-dest[1]),abs(pos[2]-dest[2]),abs(pos[3]-dest[3]))

def main(robotIP, position):
    global backup
    
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



    chainName = "LArm"
    space     = motion.FRAME_TORSO
    useSensor = False

    fractionMaxSpeed = 0.5
    axisMask         = 15 # x,y,z,ax
    err = 42;
    err_1 = 42;
    eps = 0.001 #error limit
    
    while err>eps:
        motionProxy.setPosition(chainName, space, position, fractionMaxSpeed, axisMask)
        time.sleep(1)
        current = motionProxy.getPosition(chainName, space, useSensor)
        err_1 = err;
        err = max_error(position,current)
        print [position,' ',current,' ',err]    
        print ''
        
        #stop if no movement
        if abs(err-err_1)<0.005:
            err = 0
    
    #interrupt pending cartesian movement
    motionProxy.setPosition(chainName, space, current, fractionMaxSpeed, axisMask)
    
    #if in an unreachable position, back to reference position and try again
    #if that havec ever occured, back to position and standing by
    if err_1>1:
        print "back to a better position"
        main(robotIP,sw_coord([0.1,0.0,0.25,-1.57],0.2))
    if backup==0:
        print "try again
        main(robotIp, sw_coord(position,0.2))
        backup = 1


if __name__ == "__main__":
    global backup
    
    robotIp = "172.20.11.131"
    backup = 0

    if len(sys.argv) <= 1:
        position         = [0.1,0.0,0.25,-1.57]

    else:
        position = eval('['+sys.argv[1]+']')

    main(robotIp, sw_coord(position,0.2))