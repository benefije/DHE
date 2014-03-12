# -*- coding: utf-8 -*-
"""
Created on Mon Mar  10 2014

@author: quentin

Controller for tests on lightsaber_segment.py
"""

import threading as th
import lightsaber_segment as ls
import sharedMem as shm
import sys
import time

def main(robotIp,enemy):
    pos = shm.sharedMem((0,0))
    mutex_pos = th.Lock()   
    ctrl = th.Thread(None, ls.main, "Vision", (pos, mutex_pos, robotIp,enemy), {})
    ctrl.start()
    while True:
        mutex_pos.acquire()
        c = pos.value
        mutex_pos.release()
        print "vision: ",c
        time.sleep(2)


if __name__ == "__main__":    
    robotIp = "172.20.11.131"
    enemy = "dark"
    if len(sys.argv) > 1:
        robotIp         = sys.argv[1]
    if len(sys.argv) > 2:
        robotIp         = sys.argv[1]
        enemy         = sys.argv[2]
    

    main(robotIp,enemy)