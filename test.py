# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 14:24:58 2014

@author: jibi
"""
from math import *
from numpy import *
from reverK import *
import sys
from naoqi import ALProxy
import time

def main(robotIP, position):
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    motionProxy.setStiffnesses("Body", 1.0)

    # Example showing how to set angles, using a fraction of max speed
    names  = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
    angles  = exe_revK(position)
    print angles
    fractionMaxSpeed  = 0.2
    motionProxy.angleInterpolationWithSpeed(names, angles, fractionMaxSpeed)

    time.sleep(3.0)
    print "end"


if __name__ == "__main__":
    robotIp = "172.20.12.26"

    if len(sys.argv) <= 1:
        print "Usage python almotion_setposition.py robotIP (optional default: 127.0.0.1)"
        position         = [0.,0., 0.0, 0.0, 0.0, 0.0]

    else:
        #robotIp = sys.argv[1]
        position = eval('['+sys.argv[1]+']')

    main(robotIp, position)