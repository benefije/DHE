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
import math as m
from naoqi import ALProxy
from naoqi import motion

global position

"""Convert a set of coordinates for the sword into a set of coordinates
for the NAO's hand.
No rotations along y-axis nor z-axis.
l-parameter is the sword length"""
def sw_coord(pos, l):
    al = pos[3]
    px = pos[0]
    py = pos[1]+l*m.cos(al)
    pz = pos[2]+l*m.sin(al)
    
    return [px,py,pz,al,0.,0.]

"""Returns the highest error for regards to the destination"""    
def max_error(pos, dest):  
    return max(abs(pos[0]-dest[0]),abs(pos[1]-dest[1]),abs(pos[2]-dest[2]),abs(pos[3]-dest[3]))

"""Compute the cartesian movement to make the sword to reach the target position
Parameters:
    robotIP: IP address of the NAO controlled;
    position: 6-coordinates target position;
    go: sharedMem object containing command flag;
Returns:
    0 if movement completed;
    1 if interrupted;
    -1 if position unreached
"""
def move(robotIP, go, mutex_cmd):    
    global position    
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
    fail_th = 1. #Threshold fo maximum acceptable error
    l = 0.2 #length of the sword
    beh = 5 #Behaviour flag
    
    while err>eps and beh==5:
        target = sw_coord(position,l)        
        
        motionProxy.setPosition(chainName, space, target, fractionMaxSpeed, axisMask)
        time.sleep(1)
        current = motionProxy.getPosition(chainName, space, useSensor)
        err_1 = err;
        err = max_error(target,current)
        print [position,' ',current,' ',err]    
        print ''
        
        #stop if no movement
        if abs(err-err_1)<0.005:
            err = 0
        
        #Is there new instruction
        mutex_cmd.acquire()
        beh = go.value[0]
        mutex_cmd.release()
    
    #interrupt pending cartesian movement
    motionProxy.setPosition(chainName, space, current, fractionMaxSpeed, axisMask)
 
    if beh!=5:      #Interrupted
        return 1
    elif err_1>fail_th:     #Movement blocked and not tolerable
        return -1
    else:                   #Movement achieved within the margin of tolerance
        return 0

"""Returns coordinates for the prime posture"""        
def pos_prime():
    return [0.1,0.1,0.,0.6] #TO DO
    
"""Returns coordinates for the seconde posture"""        
def pos_seconde():
    return [0.2,-0.05,0.,0.4] #TO DO
    
"""Returns coordinates for the tierce posture"""        
def pos_tierce():
    return [0.15,-0.1,0.1,-0.5] #TO DO
    
"""Returns coordinates for the quarte posture"""        
def pos_quarte():
    return [0.1,0.025,0.1,-0.2] #TO DO
    
def main_ctrl(shm_cmd,mutex_cmd,robotIP):
    global position
    position = [0.1,0.0,0.25,-1.57]
    cur_behav = 0 #Current behaviour of the NAO
    
    while True:
        #Behaviour selection
        mutex_cmd.acquire()
        n = shm_cmd.value[0]
        mutex_cmd.release()
        
        print "cur", n
        
        if n==0:            #no movement
            cur_behav = 0
            continue
        elif n==1:          #Base position: prime
            position = pos_prime()
        elif n==2:          #Base position: seconde
            position = pos_seconde()
        elif n==3:          #Base position: tierce
            position = pos_tierce()
        elif n==4:          #Base position: quarte
            position = pos_quarte()
        elif n==5:          #Controlled movement
            mutex_cmd.acquire()
            position = shm_cmd.value[1]
            mutex_cmd.release()
        elif n==-2:
            print "Ended by parent"
            break
        else:
            print "Failure on behaviour. Exit", n
            break
        
        #Movement execution if new behaviour or controlled movement
        if cur_behav!=n or n==5:
            cur_behav = n
            move(robotIP,shm_cmd,mutex_cmd)
            n = 0
        
    print "End of movements"