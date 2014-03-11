# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 11:01:13 2014

@author: jibi
"""

class sharedMem:
    "Create a 'tank' object for inter thread simple data transfert"
    def __init__(self, val=0):
        self.value = val