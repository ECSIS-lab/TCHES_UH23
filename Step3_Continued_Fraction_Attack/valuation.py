# -*- coding: utf-8 -*-
from joblib import Parallel,delayed
import math

def generate_val(fai_p_can, r_bits=16, k=512, k0=4):
    val_list = []
    val_list = Parallel(n_jobs=-1)([delayed(val_function)(i, fai_p_can[i], fai_p_can[i-k0:i]+fai_p_can[i+1:i+k0+1], r_bits, k) for i in range(k0,len(fai_p_can)-5)])
    # val_list = Parallel(n_jobs=-1, verbose=1)([delayed(val_function)(i, fai_p_can[i], fai_p_can[min(0,i-4):i]+fai_p_can[i+1:min(i+5,len(fai_p_can))], r_bits, k) for i in range(len(fai_p_can)-1)])
    val_list.sort(key=lambda x:x[0])
    val_list = [row[1] for row in val_list]
    return val_list

def val_function(no, x_i, x_j_set, r_bits=16, k=512):
    # Val = 0
    # for i in range(len(x_j_set)):
        # tau = math.floor( abs(x_i-x_j_set[i]) / (2**(r_bits)) )
        # tau = (abs(x_i-x_j_set[i])) / (2**(k-2*r_bits))
        # tau = (abs(x_i-x_j_set[i])) / (2**(k-8))
        # if tau < 1:
            # val = 11/12 - (31*tau) / 60
        # elif 1 <= tau and tau < 2:
            # val = -1/12 + tau/60 + 2/(3*(tau**2))- 1/(5*(tau**4))
        # elif 2 <= tau:
            # val = 4/(3*(tau**3)) - 1 /(tau**4)
        # Val += val

    ans = [abs(x_i-x_j) / (2**(r_bits+1)) for x_j in x_j_set]
    # ans = [math.floor( abs(x_i-x_j) / (2**(r_bits+1)) ) for x_j in x_j_set]
    # ans = [math.floor( abs(x_i-x_j) / (2**(r_bits-3)) ) for x_j in x_j_set]
    ans = [calcurate(x) for x in ans]
    Val = sum(ans)
    return [no,Val]

def calcurate(tau):
    if tau < 1:
        val = 11/12 - (31*tau) / 60
    elif 1 <= tau and tau < 2:
        val = -1/12 + tau/60 + 2/(3*(tau**2))- 1/(5*(tau**4))
    elif 2 <= tau:
        val = 4/(3*(tau**3)) - 1 /(tau**4)
    return val
