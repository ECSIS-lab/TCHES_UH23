# coding: utf-8
# pおよびqの値を演算系列に直す

import os
import sys
sys.path.append('../../')

from libs import slidingwindow as sw


key_dir = "./test_key/"

def KeyToSeq(key, window=4):
    # key = format(int(key, 16), 'b') # 16進数(文字型) -> 2進数(文字型)
    seq="sm"
    seq = seq + sw.bin2seq_for_libgcrypt(key[2:], window)
    return seq

if __name__ == "__main__":
    load_key = key_dir + "key777.txt"
    with open(load_key, "r") as f:
        data = f.read()
    data = data.split("\n")
    p = data[1]
    q = data[3]

    # print("p: %s" %(sw.bin2seq_for_libgcrypt(p, 4)))
    # print("q: %s" %(sw.bin2seq_for_libgcrypt(q, 4)))
