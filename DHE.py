# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 10:37:01 2014

@author: jibi
"""

import time
import threading as th
import movSword as sw
import sharedMem
import getch

def main(robotIp):
    gt = _Getch()
    c = 'g'    
    
    shm_tar = sharedMem([0,(0.,0.,0.,0.)])
    mutex_tar = th.Lock()
    
    shm_cmd = sharedMem([0,(0.,0.,0.,0.)])
    mutex_cmd = th.Lock()
    
    visio = th.Thread(None, "TO-DO", "Visio", (shm_tar, mutex_bet, robotIp), {})
    cmd = th.Thread(None, "TO-DO", "Commande", (shm_tar, cmd, mutex_tar, mutex_cmd, robotIp), {})
    ctrl = th.Thread(None, "TO-DO", "Controle", (mcd, mutex_cmd, robotIp), {})
    
    visio.start()
    cmd.start()
    ctrl.start()
    
    while c!='s':
        time.sleep(4.2)
        c = gt()
    
    shm_tar.value[-2,[0.,0.,0.]]
    shm_cmd.value[-2,[0.,0.,0.,0.]]
    
    print("That's all, folks!")
    

if __name__ == "__main__":
    robotIp = "127.0.0.1"

    if len(sys.argv) <= 1:
        print "Usage python almotion_changeposition.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]

    main(robotIp)