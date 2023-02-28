# -*- coding: utf-8 -*
import time
import csv
import sys
from ExtendHS4 import ExtendHS

if __name__ == "__main__":
    args = sys.argv
    keyname = args[1]
    r_bitlen = int(args[2])
    if len(args) != 3:
        print("Arguments is not correct")
        exit(1)

    readfile = "./blind_secret_key/key%s_Dp_%dbits.csv" %(keyname,r_bitlen)
    readfile2 = "./original_secret_key/key%s.txt" %(keyname)
    readfile3 = "./blind_secret_key/key%s_Dq_%dbits.csv" %(keyname,r_bitlen)

    with open(readfile, "r") as f:
        reader = csv.reader(f)
        blind_secret_data1 = [row for row in reader]

    with open(readfile3, "r") as f:
        reader = csv.reader(f)
        blind_secret_data2 = [row for row in reader]

    with open(readfile2, "r") as f:
        read_data = f.read().split("\n")
    n = int(read_data[read_data.index("n")+1],0)
    p = int(read_data[read_data.index("p")+1],0)
    q = int(read_data[read_data.index("q")+1],0)
    dp = int(read_data[read_data.index("dp")+1],0)
    dq = int(read_data[read_data.index("dq")+1],0)
    e = int(read_data[read_data.index("e")+1],0)



    # p_num = 1307
    # q_num = 2335

    # p_num = 16
    # q_num = 7

    p_num = 1307
    q_num = 7

    # 正解
    cp_bin = bin(p)[2:]
    cq_bin = bin(q)[2:]
    cdp_bin = bin(dp)[2:]
    cdq_bin = bin(dq)[2:]
    cDp_bin = bin(int(blind_secret_data1[p_num][1],0))[2:]
    cDq_bin = bin(int(blind_secret_data2[q_num][1],0))[2:]


    # デバッグ
    # print(cp_bin[-501])
    # print(cq_bin[-501])
    # print(cdp_bin[-501])
    # print(cdq_bin[-501])
    # print(cDp_bin[-501])
    # print(cDq_bin[-501])
    # exit(1)
    # print(cdp)

    # 仮定
    rp = int(blind_secret_data1[p_num][0],0)
    rq = int(blind_secret_data2[q_num][0],0)
    gp = cp_bin[:32] + "x"*(511-32) + "1"
    gq = cq_bin[:32] + "x"*(511-32) + "1"
    gDp = cDp_bin[:32] + blind_secret_data1[p_num][2][32:].replace("I","1")
    gDq = cDq_bin[:32] + blind_secret_data2[q_num][2][32:].replace("I","1")
    kp = (e*dp-1)//(p-1)
    kq = (e*dq-1)//(q-1)


    # count = 0
    # for i in range(528):
    #     if gDp[i] != "x":
    #         count += 1
    # print(count)
    # exit(1)

    # 準備
    gdp = "1" + "x"*510 + "1"
    gdq = "1" + "x"*510 + "1"

    print("recover rate")
    print("p: %lf" %((len(gp)-gp.count("x"))/len(gp)))
    print("q: %lf" %((len(gq)-gq.count("x"))/len(gq)))
    print("Dp: %lf" %((len(gDp)-gDp.count("x"))/len(gDp)))
    print("Dq:%lf" %((len(gDq)-gDq.count("x"))/len(gDq)))
    # exit(1)

    lp = kp+e*rp
    lq = kq+e*rq

    t1 = time.time()
    # ExtendHS(gp, gq, gdp, gdq, gDp, gDq, rp, rq, n, e, kp, kq, cp_bin, cq_bin, cdp_bin, cdq_bin, \
    # cDp_bin, cDq_bin)
    ExtendHS(gp, gq, gDp, gDq, lp, lq, n, e, cp_bin, cq_bin, \
    cDp_bin, cDq_bin)
    # flag = ExtendHS(p_bitseq, q_bitseq, dp_bitseq, dq_bitseq, n, e, kp, kq, cp, cq, cdp, cdq)
    t2 = time.time()
    print("processing time: %d min" %((t2-t1)//60))
