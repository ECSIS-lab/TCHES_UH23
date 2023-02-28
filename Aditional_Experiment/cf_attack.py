import csv
import gc
import math
import numpy as np
import pandas as pd
import os
import random
import re
import sys



from joblib import Parallel,delayed
from keytoseq import KeyToSeq
from enzan_rule import EnzanToKnownBit

def known_bit(seq,focus):
    count = 0
    for i in range(focus):
        if seq[i] != "x":
            count += 1
    return count

def known_rate_after(seq,blind_size):
    # blind_size2 = 2 * blind_size
    blute_size = 2*blind_size - 2
    return (blute_size+(len(seq[blute_size:])-seq[blute_size:].count("x")))/ (1024+blind_size)

# def rank_start_judge(df_p,df_q,blind_size,used_wave):
#     p_sig = ( (df_p["known_bit_2r+3"] > (2*blind_size+3)-10) & \
#               (df_p["key_len"] == 1024+blind_size) ).sum() >= used_wave
#     q_sig =  ( (df_q["known_bit_2r+3"] > (2*blind_size+3)-10) & \
#               (df_q["key_len"] == 1024+blind_size) ).sum() >= used_wave
#     return (p_sig and q_sig)

def cf_attack_cal_rank(partseq_list,p_bin,blind_size,used_wave,brute_size,ck_list):
    blind_size2 = 2*blind_size
    index_list = [[j,k,l] for j in range(used_wave-2) for k in range(j+1, used_wave-1) for l in range(k+1,used_wave)]
    p_can = []
    res = 0
    # df_p_can = pd.DataFrame(index=[], \
    # columns=["set_no", "pro_no", "p_guess", "valuation"])

    for set_no, [first, second, third] in enumerate(index_list):
        subkey1 = partseq_list[first].replace("I","1")
        subkey2 = partseq_list[second].replace("I","1")
        subkey3 = partseq_list[third].replace("I","1")

        v1_list = exponent_brute(subkey1, brute_size)
        v2_list = exponent_brute(subkey2, brute_size)
        v3_list = exponent_brute(subkey3, brute_size)

        v1_list = [hex(int(v1,2)) for v1 in v1_list]
        v2_list = [hex(int(v2,2)) for v2 in v2_list]
        v3_list = [hex(int(v3,2)) for v3 in v3_list]

        cf_res = []
        cf_res = Parallel(n_jobs=-1)( [delayed(cf_attack)(hex(v1_i)+hex(v2_i)+hex(v3_i), int(v1,0), int(v2,0), int(v3,0), blind_size) for v1_i, v1 in enumerate(v1_list) \
                                        for v2_i, v2 in enumerate(v2_list) for v3_i, v3 in enumerate(v3_list) ])
        cf_res = [ [set_no] + x for x in cf_res if x[1] != -1]
        # print(cf_res[:5])
        # exit(1)

        df_cf_res = pd.DataFrame(cf_res, columns=["set_no", "pro_no", "p_guess"])

        # print(df_cf_res)
        # exit(1)

        if set_no == 0:
            df_p_can = df_cf_res
        else:
            df_p_can = pd.concat( [df_p_can, df_cf_res] )
            df_p_can = df_p_can.drop_duplicates(keep="first", subset=["p_guess"])
        # p_can = list(set(p_can) | set(cf_res))
        # p_can = sorted(p_can)

        del cf_res
        del v1_list
        del v2_list
        del v3_list
        del df_cf_res
        gc.collect()

    df_p_can = df_p_can.sort_values(["p_guess"])

    # L = [ coincidence(bin(x)[2:], p_bin) for x in p_can]
    # L_index = [i for i,x in enumerate(L) if x >= blind_size2]
    # if len(L_index) == 0:
        # res = -1
    if False:
        print("OK")

    else:
        print("calculate valuation")
        val_list = []
        exp = -brute_size + blind_size * 3
        val_list = generate_val([df_p_can["p_guess"].iloc[i] for i in range(len(df_p_can))], exp)
        df_p_can["valuation"] = val_list
        df_p_can = df_p_can.sort_values(["valuation"], ascending=False)
        df_p_can = df_p_can[:2000000]
        df_p_can["p_match"] = [ coincidence( bin(df_p_can["p_guess"].iloc[i])[2:], p_bin) \
                                for i in range(len(df_p_can)) ]
        df_p_can["rank"] = [i+1 for i in range(len(df_p_can))]
        # sort_val_list = sorted(val_list, reverse=True)
        # ok_index_list = []
        # for i in L_index:
            # ok_index_list.append(sort_val_list.index(val_list[i-4]))
        # res = min(ok_index_list)+1

        # del val_list
        # del sort_val_list
        # del ok_index_list

    del p_can
    # del L
    # del L_index
    gc.collect()
    # print(df_p_can[df_p_can["p_match"]>=20])
    # print(len(df_p_can))
    df_p_can = df_p_can[ df_p_can["p_match"]>=brute_size-2]
    # print(df_p_can)
    # exit(1)


    if len(df_p_can) == 0:
        return [-1, -1, -1, -1]
    # print(df_p_can[ df_p_can["p_match"]>=blind_size2-4 ])
    # exit(1)

    for select in range(len(df_p_can)):
        set = df_p_can["set_no"].iloc[select]
        v1_pro, v2_pro, v3_pro = re.split( "0x", ( df_p_can["pro_no"].iloc[select] )[2:] )
        v1_pro = "0x"+v1_pro
        v2_pro = "0x"+v2_pro
        v3_pro = "0x"+v3_pro
    # print(v1_pro)
    # print(v2_pro)
    # print(v3_pro)
    # print(set)
    # print(index_list[set])
    # exit(1)
        first, second, third = index_list[set]
        subkey1 = partseq_list[first].replace("I","1")
        subkey2 = partseq_list[second].replace("I","1")
    # subkey3 = partseq_list[third].replace("I","1")

        v1_list = exponent_brute_last(subkey1, brute_size)
        v2_list = exponent_brute_last(subkey2, brute_size)
    # v3_list = exponent_brute(subkey3, brute_size)
        rec_v1 = v1_list[int(v1_pro,0)]
        rec_v2 = v2_list[int(v2_pro,0)]

        if coincidence(rec_v1, bin(int(ck_list[first],0))[2:]) >= brute_size:
            return [df_p_can["rank"].iloc[select], rec_v1, rec_v2, hex(df_p_can["p_guess"].iloc[select]) ]
    return [-1, -1, -1, -1]
    # rec_v3 = v3_list[int(v3_pro,0)]
    # print(df_p_can[:1])


def cf_attack(pro_no, v1, v2, v3, r_bits):
    p_myu_zero, q_myu_zero = my_expand_to_continuous_fraction(abs(v1 - v2), abs(v1 - v3), r_bits)

    if q_myu_zero >= p_myu_zero:
        if q_myu_zero == 0:
            x = -1
        else:
            # x = math.floor(abs(v1 - v3) / (q_myu_zero))
            x = abs(v1 - v3) // (q_myu_zero)
        myu = q_myu_zero

    else:
        # x = math.floor(abs(v1 - v2) / (p_myu_zero))
        x = abs(v1 - v2) // (p_myu_zero)
        myu = p_myu_zero

    if 2**1023 < x and x < 2**1024:
        return [pro_no, int(bin(x)[:3*r_bits+2],0)]
        # return hex(x)
    else:
        return [pro_no,-1]

def exponent_brute(subkey1, brute_size):
    end = brute_size
    stack = []
    stack.append([subkey1, 0])
    v1_list = []
    while len(stack) > 0:
        v1, focus_bit = stack.pop(0)
        if focus_bit == end:
             # v1_list.append(v1.replace("x","1"))
             v1_list.append(v1.replace("x","0"))
        elif v1[focus_bit] == "x":
            stack.append([v1[:focus_bit] + "0" + v1[focus_bit+1:], focus_bit+1])
            stack.append([v1[:focus_bit] + "1" + v1[focus_bit+1:], focus_bit+1])
        else:
            stack.append([v1, focus_bit+1])
    return v1_list

def exponent_brute_last(subkey1, brute_size):
    end = brute_size
    stack = []
    stack.append([subkey1, 0])
    v1_list = []
    while len(stack) > 0:
        v1, focus_bit = stack.pop(0)
        if focus_bit == end:
            v1_list.append(v1)
        elif v1[focus_bit] == "x":
            stack.append([v1[:focus_bit] + "0" + v1[focus_bit+1:], focus_bit+1])
            stack.append([v1[:focus_bit] + "1" + v1[focus_bit+1:], focus_bit+1])
        else:
            stack.append([v1, focus_bit+1])
    return v1_list

def my_expand_to_continuous_fraction(a, b, R=16):
    answer = []
    next_a = a
    next_b = b
    c = 0
    while True:
        c_a = next_a
        c_b = next_b
        if c_b == 0:
            break
        current_num = c_a // c_b

        answer.append(current_num)
        if len(answer) > 1:
            p, q = my_contract_from_continuous_fraction(answer)
            if p > (2**(R-1)) or q > (2**(R-1)):
                answer.pop(-1)
                break
        temp_next_a = c_a - current_num*c_b

        next_a = c_b
        next_b = temp_next_a
        c += 1
    if len(answer) == 0:
        return [0,0]

    p, q =my_contract_from_continuous_fraction(answer)
    return [p,q]

#連分数展開した結果をもとに、それをp/qという分数の形にしていく
def my_contract_from_continuous_fraction(list_expanded_continuous_fraction):
    l_p =[1, list_expanded_continuous_fraction[0]]
    l_q =[0, 1]
    for ind_c_a, c_a  in enumerate(list_expanded_continuous_fraction[1:]):
        ind_pq = ind_c_a + 2
        l_p.append(c_a * l_p[ind_pq -1] + l_p[ind_pq -2])
        l_q.append(c_a * l_q[ind_pq -1] + l_q[ind_pq -2])
    answer = [l_p[-1], l_q[-1]]
    return [l_p[-1], l_q[-1]]

def generate_val(fai_p_can, exp, k=1024, k0=4):
    val_list = []
    val_list = Parallel(n_jobs=-1)([delayed(val_function)(i, fai_p_can[i], fai_p_can[i-k0:i]+fai_p_can[i+1:i+k0+1], exp, k) for i in range(k0,len(fai_p_can)-k0)])
    val_list.sort(key=lambda x:x[0])
    val_list = [row[1] for row in val_list]
    val_list = [0 for i in range(k0)] + val_list + [0 for i in range(k0)]

    return val_list

def val_function(no, x_i, x_j_set, exp, k=1024):
    # ans = [abs(x_i-x_j) / (2**(r_bits+1)) for x_j in x_j_set]
    ans = [abs(x_i-x_j) / (2**exp) for x_j in x_j_set]
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

def coincidence(p0_bin, p_bin):
    count = 0
    for i in range(len(p0_bin)):
        if p0_bin[i] == p_bin[i]:
            count += 1
        else:
            break
    return count

def cf_attack_again(partseq_list,p_bin,blind_size,brute_size):
    blind_size2 = 2*blind_size
    p_can = []
    res = 0
    df_p_can = pd.DataFrame(index=[], \
    columns=["pro_no","p_guess"])

    # for set_no, [first, second, third] in enumerate(index_list):
    subkey1 = partseq_list[0].replace("I","1")
    subkey2 = partseq_list[1].replace("I","1")
    subkey3 = partseq_list[2].replace("I","1")

    # v1_list = exponent_brute(subkey1, brute_size)
    # v2_list = exponent_brute(subkey2, brute_size)
    v3_list = exponent_brute(subkey3, brute_size)

    # v1_list = [hex(int(v1,2)) for v1 in v1_list]
    # v2_list = [hex(int(v2,2)) for v2 in v2_list]
    v1 = subkey1.replace("x","0")
    v2 = subkey2.replace("x","0")
    v3_list = [hex(int(v3,2)) for v3 in v3_list]

    cf_res = []
    cf_res = Parallel(n_jobs=-1)( [ delayed(cf_attack) (v3_i, int(v1,2), int(v2,2), int(v3,0), blind_size) \
     for v3_i, v3 in enumerate(v3_list) ] )
    cf_res = [ x for x in cf_res if x[1] != -1]
    # print(cf_res[:5])
    # exit(1)

    df_cf_res = pd.DataFrame(cf_res, columns=["pro_no", "p_guess"])

    # print(df_cf_res)
    # exit(1)

    # if set_no == 0:
    df_p_can = df_cf_res
    # else:
        # df_p_can = pd.concat( [df_p_can, df_cf_res] )
        # df_p_can = df_p_can.drop_duplicates(keep="first", subset=["p_guess"])
    # p_can = list(set(p_can) | set(cf_res))
    # p_can = sorted(p_can)

    del cf_res
    # del v1_list
    # del v2_list
    # del v3_list
    del df_cf_res
    gc.collect()


    # df_p_can = df_p_can.sort_values(["p_guess"])
# L = [ coincidence(bin(x)[2:], p_bin) for x in p_can]
# L_index = [i for i,x in enumerate(L) if x >= blind_size2]
# if len(L_index) == 0:
    # res = -1
# if False:
    # print("OK")

# else:
    # print("calculate valuation")
    # val_list = []
    # val_list = generate_val([df_p_can["p_guess"].iloc[i] for i in range(len(df_p_can))])
    # df_p_can["valuation"] = val_list
    # df_p_can = df_p_can.sort_values(["valuation"], ascending=False)
    # df_p_can = df_p_can[:5000]
    if len(df_p_can) == 0:
        return [-1,-1]
    df_p_can["p_match"] = [ coincidence( bin(df_p_can["p_guess"].iloc[i])[2:], p_bin) \
                            for i in range(len(df_p_can)) ]
    # df_p_can["rank"] = [i for i in range(len(df_p_can))]
        # sort_val_list = sorted(val_list, reverse=True)
        # ok_index_list = []
        # for i in L_index:
            # ok_index_list.append(sort_val_list.index(val_list[i-4]))
        # res = min(ok_index_list)+1

        # del val_list
        # del sort_val_list
        # del ok_index_list

    del p_can
    # del L
    # del L_index
    gc.collect()
    # print(df_p_can[df_p_can["p_match"]>=20])
    # df_p_can = df_p_can[ df_p_can["p_match"]>=blind_size2-4 ]
    # print(df_p_can[ df_p_can["p_match"]>=blind_size2-4 ])
    # exit(1)
    # set = df_p_can["set_no"].iloc[0]
    # v1_pro, v2_pro, v3_pro = re.split( "0x", ( df_p_can["pro_no"].iloc[0] )[2:] )
    df_p_can = df_p_can.sort_values(["p_match"], ascending=False)

    if df_p_can["p_match"].iloc[0] >= brute_size-2:
        v3_pro = df_p_can["pro_no"].iloc[0]
        # print(df_p_can[:5])
    # first, second, third = index_list[set]
    # subkey1 = partseq_list[first].replace("I","1")
    # subkey2 = partseq_list[second].replace("I","1")
    # subkey3 = partseq_list[third].replace("I","1")

    # v1_list = exponent_brute_last(subkey1, brute_size)
    # v2_list = exponent_brute_last(subkey2, brute_size)
    # v3_list = exponent_brute(subkey3, brute_size)
    # print(df_p_can[:5])
    # rec_v1 = v1_list[int(v1_pro,16)]
    # rec_v2 = v2_list[int(v2_pro,16)]
        rec_v3 = v3_list[v3_pro]
    # print(len(bin(int(rec_v3,0)))-2)
    # print(len(p_bin))
    # print(len(bin(int(rec_v3,0))))
    # exit(1)
    # x = (int(p_bin,2)*(2**(512-3*blind_size)))
    # x = int(rec_v3,0)
    # print(len(bin(x)))
    # exit(1)
        r3 = math.floor( int(rec_v3,0) / (int(p_bin,2)*(2**(1024-3*blind_size))))



        rec_v3 = bin(int(rec_v3,0))[2:brute_size+2] + (partseq_list[2].replace("I","1"))[brute_size:]
    # rec_v3 = v3_list[int(v3_pro,16)]
    # print(rec_v3)
    # print(r3)
    # exit(1)
    else:
        rec_v3 = -1
        r3 = -1


    return [rec_v3, r3]

    # return [df_p_can["rank"].iloc[0], rec_v1, rec_v2, hex(df_p_can["p_guess"].iloc[0]) ]


if __name__ == "__main__":
    args = sys.argv
    # print(args)
    # exit(1)
    if len(args) != 5:
        print("argument error")
        sys.exit(1)
    keyname = args[1]
    blind_size = int(args[2])
    used_wave = int(args[3])
    symbol = args[4]
    # trace_num = 32768

    if symbol != "p" and symbol != "q":
        print("Symbol Error")
        sys.exit(1)

    #debag用
    # keyname = 7
    # blind_size = 16
    # used_wave = 10
    # trace_num = 30000

    brute_size = (2*blind_size) - 2

    readfile1 = "./RSA2048key/key%s.csv" %(keyname)
    with open(readfile1, "r") as f:
        reader = csv.reader(f)
        r_data = [row[0] for row in reader]

    p_ori = r_data[r_data.index(symbol)+1]
    # q_ori = r_data[r_data.index("q")+1]
    dp_ori = r_data[r_data.index("d"+symbol)+1]
    # dq_ori = r_data[r_data.index("dq")+1]


    # seed値の固定
    # random.seed(0)
    # 10000~はなし




    df_p = pd.DataFrame(index=[], \
    columns=["no","random_num","correct_key","partial_key", "key_len", "known_rate", "known_bit_2r-2", "known_rate_after"])

    # df_q = pd.DataFrame(index=[], \
    # columns=["random_num","partial_key", "key_len", "known_rate", "known_bit_2r"])

    start = True
    rp_list = [x for x in range(2**15,2**16)]
    # rq_list = []
    for i in range(len(rp_list)):
        # rp = random.randrange(2**(blind_size-1), 2**(blind_size))
        # if start == False:
        #     while hex(rp) in rp_list:
        #         rp = random.randrange(2**(blind_size-1), 2**(blind_size))
        # rp_list.append(hex(rp))
        rp = rp_list[i]
        Dp = rp*(int(p_ori,0) - 1) + int(dp_ori,0)
        seq_Dp = KeyToSeq(bin(Dp), window=5)
        trans_res  = EnzanToKnownBit(seq_Dp, 5)
        par_Dp = trans_res[0]
        known_rate = trans_res[3]

        # df_p = df_p.append( {"no":i,"random_num":hex(rp), "partial_key":par_Dp, \
        #                      "correct_key":hex(Dp),"key_len":len(par_Dp), "known_rate":known_rate, \
        #                      "known_bit_2r-2":known_bit(par_Dp,brute_size), "known_rate_after":known_rate_after(par_Dp,brute_size)}, ignore_index=True )
        
        df_p = pd.concat( [df_p, pd.DataFrame({"no":i,"random_num":hex(rp), "partial_key":par_Dp, \
                             "correct_key":hex(Dp),"key_len":len(par_Dp), "known_rate":known_rate, \
                             "known_bit_2r-2":known_bit(par_Dp,brute_size), "known_rate_after":known_rate_after(par_Dp,blind_size)}, index=[0])], ignore_index=True)
        
        start = False

    df_p_s = df_p[df_p["key_len"]==1024+blind_size].sort_values(["known_bit_2r-2","known_rate","known_rate_after"],ascending=False)
    # df_p_s = df_p_s[:10]
    # df_p_50 = df_p[used_wave:]
    df_p_50 = df_p_s[ df_p_s["known_rate_after"] >= 0.5].sort_values(["known_bit_2r-2"], ascending=False)
    # print(len(df_p_50))
    # exit(1)

    if len(df_p_s) >= used_wave and len(df_p_50) > 0:
        df_p_s = df_p_s.set_index(["no"])
        # print(df_p_s[:10])
        # exit(1)
        # df_p_50とdf_p_sと異なるデータを使った場合を想定
        print("cf_attack_first")
        result = cf_attack_cal_rank(partseq_list=[df_p_s["partial_key"].iloc[i] for i in range(used_wave)],p_bin=bin(int(p_ori,0))[2:],\
                           blind_size=blind_size,used_wave=used_wave,brute_size=brute_size, ck_list=[df_p_s["correct_key"].iloc[i] for i in range(used_wave)])

        # v1_c = int(df_p_s["random_num"].iloc[4],0) * (int(p_ori,0) - 1) + int(dp_ori,0)
        # print(bin(v1_c)[2:34])/
        # print(result[1])

        # v2_c = int(df_p_s["random_num"].iloc[7],0) * (int(p_ori,0) - 1) + int(dp_ori,0)
        # print(bin(v2_c)[2:34])
        # print(result[2])
        # exit(1)

        if result[0] == -1:
            savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
            if symbol == "p":
                with open(savefile, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["keyname"])
                    writer.writerow([keyname])
                    writer.writerow(["rank"])
                    writer.writerow([result[0]])
                    writer.writerow(["rp"])
                    writer.writerow([result[1]])
                    writer.writerow(["Dp"])
                    writer.writerow([result[2]])
                    writer.writerow(["correct_rp"])
                    writer.writerow([-1])
            else:
                with open(savefile, "a") as f:
                    writer = csv.writer(f)
                    writer.writerow(["rank"])
                    writer.writerow([result[0]])
                    writer.writerow(["rq"])
                    writer.writerow([result[1]])
                    writer.writerow(["Dq"])
                    writer.writerow([result[2]])
                    writer.writerow(["correct_rq"])
                    writer.writerow([-1])
            sys.exit(0)

        print("cf_attack_second")
        v3, r3 = cf_attack_again( partseq_list=[result[1], result[2], df_p_50["partial_key"].iloc[0]], p_bin=bin(int(result[-1],0))[2:],\
                           blind_size=blind_size,brute_size=brute_size)


        index = 0
        if r3 == int(df_p_50["random_num"].iloc[index],0) and \
        coincidence(v3,bin(int(df_p_50["correct_key"].iloc[index],0))[2:]) >= brute_size:
            savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
            if symbol == "p":
                with open(savefile, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["keyname"])
                    writer.writerow([keyname])
                    writer.writerow(["rank"])
                    writer.writerow([result[0]])
                    writer.writerow(["rp"])
                    writer.writerow([hex(r3)])
                    writer.writerow(["Dp"])
                    writer.writerow([v3])
                    writer.writerow(["correct_rp"])
                    writer.writerow([df_p_50["random_num"].iloc[0]])
            else:
                with open(savefile, "a") as f:
                    writer = csv.writer(f)
                    writer.writerow(["rank"])
                    writer.writerow([result[0]])
                    writer.writerow(["rq"])
                    writer.writerow([hex(r3)])
                    writer.writerow(["Dq"])
                    writer.writerow([v3])
                    writer.writerow(["correct_rq"])
                    writer.writerow([df_p_50["random_num"].iloc[0]])
            sys.exit(0)

        elif index + 1 == len(df_p_50):
            # 終了
            savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
            if symbol == "p":
                with open(savefile, "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["keyname"])
                    writer.writerow([keyname])
                    writer.writerow(["rank"])
                    writer.writerow([-1])
                    writer.writerow(["rp"])
                    writer.writerow([-1])
                    writer.writerow(["Dp"])
                    writer.writerow([-1])
                    writer.writerow(["correct_rp"])
                    writer.writerow([-1])
            else:
                with open(savefile, "a") as f:
                    writer = csv.writer(f)
                    writer.writerow(["rank"])
                    writer.writerow([-1])
                    writer.writerow(["rq"])
                    writer.writerow([-1])
                    writer.writerow(["Dq"])
                    writer.writerow([-1])
                    writer.writerow(["correct_rq"])
                    writer.writerow([-1])
            sys.exit(0)
        
        # print(r3)
        # print(int(df_p_50["random_num"].iloc[index],0))
        # print("\n")
        while v3 == -1 or \
        r3 != int(df_p_50["random_num"].iloc[index],0) or \
        coincidence(v3,bin(int(df_p_50["correct_key"].iloc[index],0))[2:]) < brute_size:
            index += 1
            v3, r3 = cf_attack_again( partseq_list=[result[1], result[2], df_p_50["partial_key"].iloc[index]], p_bin=bin(int(result[-1],0))[2:],\
                               blind_size=blind_size,brute_size=brute_size)
            # print(r3)
            # print(int(df_p_50["random_num"].iloc[index],0))
            # print("\n")
            # exit(1)
            if r3 == int(df_p_50["random_num"].iloc[index],0) and \
        coincidence(v3,bin(int(df_p_50["correct_key"].iloc[index],0))[2:]) >= brute_size:
                savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
                if symbol == "p":
                    with open(savefile, "w") as f:
                        writer = csv.writer(f)
                        writer.writerow(["keyname"])
                        writer.writerow([keyname])
                        writer.writerow(["rank"])
                        writer.writerow([result[0]])
                        writer.writerow(["rp"])
                        writer.writerow([hex(r3)])
                        writer.writerow(["Dp"])
                        writer.writerow([v3])
                        writer.writerow(["correct_rp"])
                        writer.writerow([df_p_50["random_num"].iloc[index]])
                else:
                    with open(savefile, "a") as f:
                        writer = csv.writer(f)
                        writer.writerow(["rank"])
                        writer.writerow([result[0]])
                        writer.writerow(["rq"])
                        writer.writerow([hex(r3)])
                        writer.writerow(["Dq"])
                        writer.writerow([v3])
                        writer.writerow(["correct_rq"])
                        writer.writerow([df_p_50["random_num"].iloc[index]])
                sys.exit(0)

            elif index + 1 == len(df_p_50):
                # 終了
                savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
                if symbol == "p":
                    with open(savefile, "w") as f:
                        writer = csv.writer(f)
                        writer.writerow(["keyname"])
                        writer.writerow([keyname])
                        writer.writerow(["rank"])
                        writer.writerow([-1])
                        writer.writerow(["rp"])
                        writer.writerow([-1])
                        writer.writerow(["Dp"])
                        writer.writerow([-1])
                        writer.writerow(["correct_rp"])
                        writer.writerow([-1])
                else:
                    with open(savefile, "a") as f:
                        writer = csv.writer(f)
                        writer.writerow(["rank"])
                        writer.writerow([-1])
                        writer.writerow(["rq"])
                        writer.writerow([-1])
                        writer.writerow(["Dq"])
                        writer.writerow([-1])
                        writer.writerow(["correct_rq"])
                        writer.writerow([-1])
                sys.exit(0)



        #     if index + 1 == len(df_p_50):
        #         savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
        #         if symbol == "p":
        #             with open(savefile, "w") as f:
        #                 writer = csv.writer(f)
        #                 writer.writerow(["keyname"])
        #                 writer.writerow([keyname])
        #                 writer.writerow(["rank"])
        #                 writer.writerow([result[0]])
        #                 writer.writerow(["rp"])
        #                 writer.writerow([-1])
        #                 writer.writerow(["Dp"])
        #                 writer.writerow([-1])
        #                 writer.writerow(["correct_rp"])
        #                 writer.writerow([-1])
        #         else:
        #             with open(savefile, "a") as f:
        #                 writer = csv.writer(f)
        #                 writer.writerow(["rank"])
        #                 writer.writerow([result[0]])
        #                 writer.writerow(["rq"])
        #                 writer.writerow([-1])
        #                 writer.writerow(["Dq"])
        #                 writer.writerow([-1])
        #                 writer.writerow(["correct_rq"])
        #                 writer.writerow([-1])
        #         sys.exit(0)

        # savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
        # if symbol == "p":
        #     with open(savefile, "w") as f:
        #         writer = csv.writer(f)
        #         writer.writerow(["keyname"])
        #         writer.writerow([keyname])
        #         writer.writerow(["rank"])
        #         writer.writerow([result[0]])
        #         writer.writerow(["rp"])
        #         writer.writerow([hex(r3)])
        #         writer.writerow(["Dp"])
        #         writer.writerow([v3])
        #         writer.writerow(["correct_rp"])
        #         writer.writerow([df_p_50["random_num"].iloc[0]])
        # else:
        #     with open(savefile, "a") as f:
        #         writer = csv.writer(f)
        #         writer.writerow(["rank"])
        #         writer.writerow([result[0]])
        #         writer.writerow(["rq"])
        #         writer.writerow([hex(r3)])
        #         writer.writerow(["Dq"])
        #         writer.writerow([v3])
        #         writer.writerow(["correct_rq"])
        #         writer.writerow([df_p_50["random_num"].iloc[0]])
    else:
        savefile = "./cf_attack_data/cf_attack_data_key%s_blind%dbits_%dused.csv" %(keyname, blind_size, used_wave)
        if symbol == "p":
            with open(savefile, "w") as f:
                writer = csv.writer(f)
                writer.writerow(["keyname"])
                writer.writerow([keyname])
                writer.writerow(["rank"])
                writer.writerow([-1])
                writer.writerow(["rp"])
                writer.writerow([-1])
                writer.writerow(["Dp"])
                writer.writerow([-1])
                writer.writerow(["correct_rp"])
                writer.writerow([-1])
        else:
            with open(savefile, "a") as f:
                writer = csv.writer(f)
                writer.writerow(["rank"])
                writer.writerow([-1])
                writer.writerow(["rq"])
                writer.writerow([-1])
                writer.writerow(["Dq"])
                writer.writerow([-1])
                writer.writerow(["correct_rq"])
                writer.writerow([-1])
        sys.exit(0)