# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 10:37:01 2014

@author: jibi
"""

import time
import threading as th
import movSword as sw
import sharedMem

def main(robotIp):
    bet = sharedMem([0.,0.,0.])
    mutex_bet = th.Lock()
    
    cmd = sharedMem([0,[0.,0.,0.,0.]])
    mutex_cmd = th.Lock()
    
    visio = th.Thread(None, "TO-DO", "Visio", (bet, mutex_bet, robotIp), {})
    cmd = th.Thread(None, "TO-DO", "Commande", (bet, cmd, mutex_bet, mutex_cmd, robotIp), {})
    ctrl = th.Thread(None, "TO-DO", "Controle", (mcd, mutex_cmd, robotIp), {})
    
    visio.start()
    cmd.start()
    ctrl.start()
    
    input("Press a key to close")
    
    visio.__stop()
    cmd.__stop()
    ctrl.__stop()
    
    print("That's all, folks!")
    

if __name__ == "__main__":
    robotIp = "127.0.0.1"

    if len(sys.argv) <= 1:
        print "Usage python almotion_changeposition.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]

    main(robotIp)