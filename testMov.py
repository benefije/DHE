# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 15:58:01 2014

@author: jibi

Controller for tests on movSword.py
"""

import threading as th
import movSword as msw
import sharedMem as shm
import sys
import time

def main(robotIp,positions):
    cmd = shm.sharedMem([0,[0.,0.,0.,0.]])
    mutex_cmd = th.Lock()
    
    ctrl = th.Thread(None, msw.main_ctrl, "Controle", (cmd, mutex_cmd, robotIp), {})
    ctrl.start()
    
    raw_input("Press a key1")
    mutex_cmd.acquire()
    cmd.value = [5,position]
    mutex_cmd.release()
    
    time.sleep(20)

    mutex_cmd.acquire()
    cmd.value = [-2,[0.,0.,0.,0.]]
    mutex_cmd.release()
    print "Done"

if __name__ == "__main__":    
    robotIp = "172.20.10.90"
    
    if len(sys.argv) <= 1:
        position         = [0.1,0.0,0.25,-1.57]

    else:
       position = eval('['+sys.argv[1]+']')

    main(robotIp,position)