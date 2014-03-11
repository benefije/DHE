# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 10:37:01 2014

@author: jibi
"""

import time
import threading as th
import movSword as sw
import command as cd
import eye_finder as ef
import lightsaber_segment as ls
import sharedMem
import getch

def main(robotIp):
    gt = _Getch()
    c = 'g'    
    
    shm_eye = sharedMem([0,[0.,0.],[0.,0.]])
    mutex_eye = th.Lock()
    
    shm_tar = sharedMem([0,(0.,0.,0.,0.)])
    mutex_tar = th.Lock()
    
    shm_cmd = sharedMem([0,(0.,0.,0.,0.)])
    mutex_cmd = th.Lock()
    
    eye = th.Thread(None, ef.main_eye, "Eye finder", (shm_eye, mutex_eye, robotIp), {})
    visio = th.Thread(None, ls.main, "Visio", (shm_tar, mutex_tar, robotIp, "obi"), {})
    cmd = th.Thread(None, cd.main_cmd, "Commande", (shm_eye, mutex_eye, shm_tar, mutex_tar, shm_cmd, mutex_cmd), {})
    ctrl = th.Thread(None, sw.main_ctrl, "Controle", (shm_cmd, mutex_cmd, robotIp), {})
    
    eye.start()
    visio.start()
    cmd.start()
    ctrl.start()
    
    while c!='s':
        time.sleep(4.2)
        c = gt()
    
    mutex_tar.acquire()
    shm_tar.value[-2,(0.,0.,0.,0.)]
    mutex_tar.release()
    mutex_cmd.acquire()
    shm_cmd.value[-2,(0.,0.,0.,0.)]
    mutex_cmd.release()
    mutex_eye.acquire()
    shm_eye.value[-2,[0.,0.],[0.,0.]]
    mutex_eye.release()
    
    print("That's all, folks!")
    

if __name__ == "__main__":
    robotIp = "127.0.0.1"

    if len(sys.argv) <= 1:
        print "Usage python almotion_changeposition.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]

    main(robotIp)