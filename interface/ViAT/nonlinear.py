#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 14:41:25 2019

@author: jfochoa
"""
import numpy as np;

def hampelFilter(signal, Thresh):
    """
    Procedure to implement the Hampel filter
    """
    ref = np.median(signal)
    
    AbsDev = [abs(r - ref) for r in signal]
    MAD = 1.4826 * np.median(AbsDev);
    TestVal = abs(signal - ref)
    
#    print("changing");
#    numero = np.sum((TestVal > Thresh * MAD)==True)
#    print(numero)
#    
    signal[TestVal > Thresh * MAD] = ref
    
        
    return signal