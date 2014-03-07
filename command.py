# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 17:32:30 2014

@author: jibi
"""

import math as m
import sys

"""Compute the target position for the sword from the opponent sword position"""
def target(pos):
    return [-1,[0.,0.,0.,0.]]

def main_cmd(shm_tar, shm_cmd, mutex_tar, mutex_cmd):
    while True:        
        mutex_tar.acquire()
        n = shm_tar.value[0]
        mutex_tar.release()
        if n==-1:
            print "Fail in target mem zone tar. Exit" , n
            break
        elif n==-2:
            print "Terminated by parent"
            break
            
        mutex_cmd.acquire()
        n = shm_cmd.value[0]
        mutex_cmd.release()
        if n==-1:
            print "Fail in target mem zone cmd. Exit" , n
            break
        elif n==-2:
            print "Terminated by parent"
            break
            
        mutex_tar.acquire()
        pos = shm_tar.value[1]
        mutex_tar.release()
        
        cmd = target(pos)
        
        mutex_cmd.acquire()
        shm_cmd.value = cmd
        mutex_cmd.release()