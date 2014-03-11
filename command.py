# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 17:32:30 2014

@author: jibi
"""

import math as m
import sys

global cur_pos

"""Check if a point (x,y) is in a box around a target (X,Y)"""
def isInInterval(x,y,X,Y,th):
    lo = 0.05
    la = 0.015
    
    x0 = x - X #Switching to a frame which X,Y is the center
    y0 = y - Y
    
    a = -m.tan(th) #Calcultaing cartesian parameters of the line including X,Y, with an agle theta
    d = abs(a*x+y)/m.sqrt(a*a+1) #Computing the distance from x,y to the line
    
    if d<la and abs(x)<lo: #if in a rectangle with legnth lo and width la, centered on X,Y
        return True
    else:
        return False
    

"""Compute the dynamic target position for the sword from the opponent sword position"""
def target(pos_ls):
    global cur_pos
    
    if isInInterval(cur_pos[1],cur_pos[2],pos_ls[1],pos_ls[2],pos_ls[3]):
        return cur_pos
    else:
        new_pos = ()
        xp = 1
        if cur_pos[0]>0.175:
            xp = -1
        elif cur_pos[0]<0.1:
            xp = 1
            
        nx = cur_pos[0] + xp*0.001
        new_pos.__add__(nx,cur_pos[1],cur_pos[2],cur_pos[3])
        
        return new_pos
    
"""Define the behaviour of the robot from the offensor position"""
def behav(pos_ls):
    bubble = 0.5 #in meters, threshold from which the defensor start parrying
    
    x = pos_ls[1][0]
    y = pos_ls[1][1]
    z = pos_ls[1][2]
    
    a = -1
    t = (-10.,10.,-10.,-10.)
    
    if x>bubble:
        t = (0.,10.,-10.,-10.)
        if z>=0:
            if y>=0:
                a = 3   #Quarte
            else:
                a = 4   #Tierce
        else:
            if y<=0:
                a = 2   #Seconde
            else:
                a = 1   #Prime
    else:
        a = 5           #Free movement
        t = target(pos_ls)
    
    return [a,t]

"""Loop for summoning the calculation function.
Includes reading and writing the shared memory zones"""
def main_cmd(shm_tar, shm_cmd, mutex_tar, mutex_cmd):
    global cur_pos
    cur_pos = (-10.,10.,-10.)
    
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
        pos_ls = shm_tar.value[1]
        mutex_tar.release()
        
        cmd = behav(pos_ls)
        
        mutex_cmd.acquire()
        shm_cmd.value = cmd
        mutex_cmd.release()