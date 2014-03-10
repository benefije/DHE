# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 15:58:01 2014

@author: jibi

Controller for tests on movSword.py
"""

import threading as th
import lightsaber_segment as ls
import sharedMem as shm
import sys
import time

def main(robotIp,positions):
    pos = shm.sharedMem((0,0))
    mutex_pos = th.Lock()
    
    ctrl = th.Thread(None, ls.main, "Controle", (pos, mutex_pos, robotIp), {})
    ctrl.start()
    

    mutex_cmd.acquire()
    mutex_cmd.release()
    print "in mutex",pos.value


if __name__ == "__main__":    
    robotIp = "172.20.10.90"
    
    if len(sys.argv) <= 1:
        position         = [0.1,0.0,0.25,-1.57]

    else:
       position = eval('['+sys.argv[1]+']')

    main(robotIp,position)