# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 14:11:38 2014

@author: benefije
@descript: Matrices and angles for the nao's left arm's reverse kinematics
"""

from math import *
from numpy import *
import numpy.linalg as nl


"""Denavit-Hartenberg Matrix"""
def DH_mat(r, al, d, th):
    T1 = array([[cos(th), -sin(th)*cos(al), sin(th)*sin(al), r*cos(th)]])
    T2 = array([[sin(th), cos(th)*cos(al), -cos(th)*sin(al), r*sin(th)]])
    T3 = array([[0., sin(al), cos(al), d]])    
    T4 = array([[0.,0.,0.,1.]])
    
    T = concatenate((T1, T2, T3, T4))
    
    return T

"""Base transformation matrix, from target position and angle"""
def T_mat(p):
    px = p[0]
    py = p[1]
    pz = p[2] 
    
    ax = p[3]
    ay = p[4]
    az = p[5]    
    
    Rx = array([[1.,0.,0.],[0.,cos(ax),-sin(ax)],[0.,sin(ax),cos(ay)]])
    Ry = array([[cos(ay),0.,sin(ay)],[0.,1.,0.],[-sin(ay),0.,cos(ay)]])
    Rz = array([[cos(az),-sin(az),0.],[sin(az),cos(az),0.],[0.,0.,1.]])

    R = dot(dot(Rx,Ry),Rz)
    y = array([[px],[py],[pz]])
    T0 = array([[0,0,0,1]])
    T1 = concatenate((R,y),axis=1)

    T = concatenate((T1,T0),axis=0)
    return T

"""return the first intermediary matrix"""    
def Tp_mat(T):
    """Transformation matrices for base and end of the chain.
   Parameters provided by Aldebaran, except for the length of the sword
   in A4->End (2,4)"""
    a0b = array([[1.,0.,0.,0.],[0.,1.,0.,0.113],[0.,0.,1.,0.1],[0.,0.,0.,1.]])
    ae4 = array([[1.,0.,0.,0.1137],[0.,1.,0.,0.],[0.,0.,1.,0.1],[0.,0.,0.,1.]])
    
    rz = array([[cos(pi/2),-sin(pi/2),0.,0.],[sin(pi/2),cos(pi/2),0.,0.],
                    [0.,0.,1.,0.],[0.,0.,0.,1.]])
    
    a0b_1 = nl.inv(a0b);
    ae4_1 = nl.inv(ae4)
    rz_1 = nl.inv(rz)
    
    Tp = dot(a0b_1,dot(T,dot(ae4_1,rz_1)))
    return Tp

"""Compute the reverse kinematics for a given position;
return the five angles of the left arm chain"""
def exe_revK(pos):
    l1 = 0.105
    l2 = 0.015
    
    T = T_mat(pos)
    Tp = Tp_mat(T)
    
    th1 = atan2(-Tp[2,3], Tp[0,3])
    T01 = DH_mat(0.,-pi/2,0.,th1)
    Tpp = dot(nl.inv(T01),Tp)
    
    th2 = acos((l2*Tpp[0,3]-l1*Tp[2,3])/(l2*l2-l1*l1))
    T12 = DH_mat(0.,pi/2,0.,th2-pi/2) #/!\ th2-pi/2
    Tppp = dot(nl.inv(T12),Tpp)
    
    th3 = atan2(Tppp[2,2],Tppp[0,2])
    T23 = DH_mat(0.,-pi/2,0.105,th3) 
    Tpppp = dot(nl.inv(T23),Tppp)
    
    th4 = atan2(Tpppp[0,2],Tpppp[2,2])
    th5 = atan2(Tpppp[1,0],Tpppp[1,1])
    
    th = [th1,th2,th3,th4,th5]
    return th