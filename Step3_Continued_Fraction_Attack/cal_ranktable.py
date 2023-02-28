import numpy as np
from joblib import delayed, Parallel
import sys
import csv
import math
from valuation import generate_val
import gc

def coincidence(p0_bin, p_bin):
    # p = "0xca6ac0540f9b704c5d247badc2d49a25c673af54a8fe23288c52a1ed0533644d3a41ba6ef894314442773c97c9dbacb9aadbaa44208e49b5645f76fe99543303"
    # p_bin = bin(int(p[2:],16))[2:]
    count = 0
    for i in range(len(p0_bin)):
        if p0_bin[i] == p_bin[i]:
            count += 1
        else:
            break
    return count


def cf_attack(v1, v2, v3, r_bits):
    p_myu_zero, q_myu_zero = my_expand_to_continuous_fraction(abs(v1 - v2), abs(v1 - v3), r_bits)

    if q_myu_zero >= p_myu_zero:
        x = math.floor(abs(v1 - v3) / (q_myu_zero))
        myu = q_myu_zero

    else:
        x = math.floor(abs(v1 - v2) / (p_myu_zero))
        myu = p_myu_zero

    # x = math.floor(abs(v1 - v2) / (p_myu_zero))
    # myu = p_myu_zero

    # return bin(x)[2:2*int(r_bits)+2]
    if 2**511 < x and x < 2**512:
        return int(bin(x)[:3*r_bits+2],0)
    else:
        return -1

def exponent_brute(subkey1, r_bitlen):
    # end = 2*r_bitlen
    end = 2*r_bitlen+3
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


if __name__ == "__main__":
    args = sys.argv
    blind_size= int(args[1])
    max_val = int(args[2])
    keyname = int(args[3])
    if len(args) != 4:
        print("Arguments is not correct")
        exit(1)
    # key_num = 100
    result = [0 for i in range(3)]
    blind_size2 = 2*blind_size
    index_list = [[j,k,l] for j in range(max_val-2) for k in range(j+1, max_val-1) for l in range(k+1,max_val)]

    p_can = []
    q_can = []
    print("key no. %d" %keyname)
    readfile1 = "./original_key/key%d.csv" %(keyname)
    readfile2 = "./blind_key/key%d_Dp%d.csv" %(keyname, blind_size2+3)
    readfile3 = "./blind_key/key%d_Dq%d.csv" %(keyname, blind_size2+3)

    with open(readfile1, "r") as f:
        reader = csv.reader(f)
        read_data = [row[0] for row in reader]
    p_bin = bin(int(read_data[read_data.index("p")+1],0))[2:]
    q_bin = bin(int(read_data[read_data.index("q")+1],0))[2:]

    # readfile = "../blind_secret_key/key%s_Dp_%dbits.csv" %(keyname,r_bitlen)
    # readfile = "../blind_secret_key/key%s_Dp_%dbits_32.csv" %(keyname,r_bitlen)
    # readfile = "../blind_secret_key/key%s_Dp_%dbits_35.csv" %(keyname,r_bitlen)

    # result = []

    with open(readfile2, "r") as f:
        reader = csv.reader(f)
        # blind_secret_data : [r(0x), Dp(0x), subkey]
        blind_data = [row[:3] for row in reader]

    blind_data = blind_data[:max_val]

    print("p calculate")
    for first, second, third in index_list:
        subkey1 = blind_data[first][2].replace("I","1")
        subkey2 = blind_data[second][2].replace("I","1")
        subkey3 = blind_data[third][2].replace("I","1")
        # cv1 = bin(int(blind_data[first][1],0))[2:]

        v1_list = exponent_brute(subkey1, blind_size)
        v2_list = exponent_brute(subkey2, blind_size)
        v3_list = exponent_brute(subkey3, blind_size)

        v1_list = [int(v1,2) for v1 in v1_list]
        v2_list = [int(v2,2) for v2 in v2_list]
        v3_list = [int(v3,2) for v3 in v3_list]

        cf_res = []
        cf_res = Parallel(n_jobs=-1)( [delayed(cf_attack)(v1, v2, v3, blind_size) for v1 in v1_list for v2 in v2_list for v3 in v3_list ])
        cf_res = [x for x in cf_res if x != -1]
        p_can = list(set(p_can) | set(cf_res))
        p_can = sorted(p_can)

        del cf_res
        del v1_list
        del v2_list
        del v3_list
        gc.collect()

    L = [ coincidence(bin(x)[2:], p_bin) for x in p_can]
    L_index = [i for i,x in enumerate(L) if x >= blind_size2]
    if len(L_index) == 0:
        result[0] = -1

        # exit(1)
    else:
        print("calculate valuation")
        val_list = []
        val_list = generate_val(p_can)
        sort_val_list = sorted(val_list, reverse=True)
        ok_index_list = []
        for i in L_index:
            ok_index_list.append(sort_val_list.index(val_list[i-4]))
        result[0] = min(ok_index_list)+1

        del val_list
        del sort_val_list
        del ok_index_list

    del p_can
    del L
    del L_index
    gc.collect()

    with open(readfile3, "r") as f:
        reader = csv.reader(f)
        # blind_secret_data : [r(0x), Dp(0x), subkey]
        blind_data = [row[:3] for row in reader]

    blind_data = blind_data[:max_val]


    print("q calculate")
    for first, second, third in index_list:
        subkey1 = blind_data[first][2].replace("I","1")
        subkey2 = blind_data[second][2].replace("I","1")
        subkey3 = blind_data[third][2].replace("I","1")
        # cv1 = bin(int(blind_data[first][1],0))[2:]

        v1_list = exponent_brute(subkey1, blind_size)
        v2_list = exponent_brute(subkey2, blind_size)
        v3_list = exponent_brute(subkey3, blind_size)

        v1_list = [int(v1,2) for v1 in v1_list]
        v2_list = [int(v2,2) for v2 in v2_list]
        v3_list = [int(v3,2) for v3 in v3_list]

        cf_res = []
        cf_res = Parallel(n_jobs=-1)( [delayed(cf_attack)(v1, v2, v3, blind_size) for v1 in v1_list for v2 in v2_list for v3 in v3_list ])
        cf_res = [x for x in cf_res if x != -1]
        q_can = list(set(q_can) | set(cf_res))
        q_can = sorted(q_can)
        del cf_res
        del v1_list
        del v2_list
        del v3_list
        gc.collect()


    L = [ coincidence(bin(x)[2:], q_bin) for x in q_can]

    L_index = [i for i,x in enumerate(L) if x >= blind_size2]
    if len(L_index) == 0:
        result[1] = -1
        # print("Not Found")
        # exit(1)
    else:
        print("calculate valuation")
        # print(val_list[:3])
        val_list = []
        val_list = generate_val(q_can)
        # print(val_list[:3])
        # exit(1)
        sort_val_list = sorted(val_list, reverse=True)
        ok_index_list = []
        for i in L_index:
            ok_index_list.append(sort_val_list.index(val_list[i-4]))

        result[1] = min(ok_index_list)+1
        del val_list
        del sort_val_list
        del ok_index_list

    del q_can
    del L
    del L_index
    gc.collect()

    if -1 in result:
        result[2] = -1
    else:
        result[2] = result[0] * result[1]
    # print(result[:3])

savefile = "./rank_table/rank_table_%d_choice%d.csv" %(blind_size2, max_val)
if keyname == 0:
    with open(savefile, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["key_no", "p_rank", "q_rank", "p_rank * q_rank"])
        writer.writerow([keyname] + result)
else:
    with open(savefile, "a") as f:
        writer = csv.writer(f)
        writer.writerow([keyname] + result)
    # for keyname in range(27,key_num):
    #     if keyname == 28:
    #         exit(1)
    #     p_can = []
    #     q_can = []
    #     print("key no. %d" %keyname)
    #     readfile1 = "./original_key/key%d.csv" %(keyname)
    #     readfile2 = "./blind_key/key%d_Dp%d.csv" %(keyname, blind_size2+3)
    #     readfile3 = "./blind_key/key%d_Dq%d.csv" %(keyname, blind_size2+3)
    #
    #     with open(readfile1, "r") as f:
    #         reader = csv.reader(f)
    #         read_data = [row[0] for row in reader]
    #     p_bin = bin(int(read_data[read_data.index("p")+1],0))[2:]
    #     q_bin = bin(int(read_data[read_data.index("q")+1],0))[2:]
    #
    #     # readfile = "../blind_secret_key/key%s_Dp_%dbits.csv" %(keyname,r_bitlen)
    #     # readfile = "../blind_secret_key/key%s_Dp_%dbits_32.csv" %(keyname,r_bitlen)
    #     # readfile = "../blind_secret_key/key%s_Dp_%dbits_35.csv" %(keyname,r_bitlen)
    #
    #     # result = []
    #
    #     with open(readfile2, "r") as f:
    #         reader = csv.reader(f)
    #         # blind_secret_data : [r(0x), Dp(0x), subkey]
    #         blind_data = [row[:3] for row in reader]
    #
    #     blind_data = blind_data[:max_val]
    #
    #     print("p calculate")
    #     for first, second, third in index_list:
    #         subkey1 = blind_data[first][2].replace("I","1")
    #         subkey2 = blind_data[second][2].replace("I","1")
    #         subkey3 = blind_data[third][2].replace("I","1")
    #         # cv1 = bin(int(blind_data[first][1],0))[2:]
    #
    #         v1_list = exponent_brute(subkey1, blind_size)
    #         v2_list = exponent_brute(subkey2, blind_size)
    #         v3_list = exponent_brute(subkey3, blind_size)
    #
    #         v1_list = [int(v1,2) for v1 in v1_list]
    #         v2_list = [int(v2,2) for v2 in v2_list]
    #         v3_list = [int(v3,2) for v3 in v3_list]
    #
    #         cf_res = []
    #         cf_res = Parallel(n_jobs=-1)( [delayed(cf_attack)(v1, v2, v3, blind_size) for v1 in v1_list for v2 in v2_list for v3 in v3_list ])
    #         cf_res = [x for x in cf_res if x != -1]
    #         p_can = list(set(p_can) | set(cf_res))
    #         p_can = sorted(p_can)
    #
    #         del cf_res
    #         del v1_list
    #         del v2_list
    #         del v3_list
    #         gc.collect()
    #
    #     L = [ coincidence(bin(x)[2:], p_bin) for x in p_can]
    #     L_index = [i for i,x in enumerate(L) if x >= blind_size2]
    #     if len(L_index) == 0:
    #         result[keyname].append(-1)
    #
    #         # exit(1)
    #     else:
    #         print("calculate valuation")
    #         val_list = []
    #         val_list = generate_val(p_can)
    #         sort_val_list = sorted(val_list, reverse=True)
    #         ok_index_list = []
    #         for i in L_index:
    #             ok_index_list.append(sort_val_list.index(val_list[i-4]))
    #         result[keyname].append(min(ok_index_list)+1)
    #
    #         del val_list
    #         del sort_val_list
    #         del ok_index_list
    #
    #     del p_can
    #     del L
    #     del L_index
    #     gc.collect()
    #
    #     with open(readfile3, "r") as f:
    #         reader = csv.reader(f)
    #         # blind_secret_data : [r(0x), Dp(0x), subkey]
    #         blind_data = [row[:3] for row in reader]
    #
    #     blind_data = blind_data[:max_val]
    #
    #
    #     print("q calculate")
    #     for first, second, third in index_list:
    #         subkey1 = blind_data[first][2].replace("I","1")
    #         subkey2 = blind_data[second][2].replace("I","1")
    #         subkey3 = blind_data[third][2].replace("I","1")
    #         # cv1 = bin(int(blind_data[first][1],0))[2:]
    #
    #         v1_list = exponent_brute(subkey1, blind_size)
    #         v2_list = exponent_brute(subkey2, blind_size)
    #         v3_list = exponent_brute(subkey3, blind_size)
    #
    #         v1_list = [int(v1,2) for v1 in v1_list]
    #         v2_list = [int(v2,2) for v2 in v2_list]
    #         v3_list = [int(v3,2) for v3 in v3_list]
    #
    #         cf_res = []
    #         cf_res = Parallel(n_jobs=-1)( [delayed(cf_attack)(v1, v2, v3, blind_size) for v1 in v1_list for v2 in v2_list for v3 in v3_list ])
    #         cf_res = [x for x in cf_res if x != -1]
    #         q_can = list(set(q_can) | set(cf_res))
    #         q_can = sorted(q_can)
    #         del cf_res
    #         del v1_list
    #         del v2_list
    #         del v3_list
    #         gc.collect()
    #
    #
    #     L = [ coincidence(bin(x)[2:], q_bin) for x in q_can]
    #
    #     L_index = [i for i,x in enumerate(L) if x >= blind_size2]
    #     if len(L_index) == 0:
    #         result[keyname].append(-1)
    #         # print("Not Found")
    #         # exit(1)
    #     else:
    #         print("calculate valuation")
    #         # print(val_list[:3])
    #         val_list = []
    #         val_list = generate_val(q_can)
    #         # print(val_list[:3])
    #         # exit(1)
    #         sort_val_list = sorted(val_list, reverse=True)
    #         ok_index_list = []
    #         for i in L_index:
    #             ok_index_list.append(sort_val_list.index(val_list[i-4]))
    #
    #         result[keyname].append(min(ok_index_list)+1)
    #         del val_list
    #         del sort_val_list
    #         del ok_index_list
    #
    #     if -1 in result[keyname]:
    #         result[keyname].append(-1)
    #     else:
    #         result[keyname].append(result[keyname][0]*result[keyname][1])
    #     # print(result[:3])
    #     del q_can
    #     del L
    #     del L_index
    #     gc.collect()
    #
    # result.append( [ min([row[0] for row in result if row[0] > 0]), min([row[1] for row in result if row[1] > -1]), min([row[2] for row in result if row[2] > -1]) ] )
    # result.append( [ max([row[0] for row in result[:-1] if row[0] > 0]), max([row[1] for row in result[:-1] if row[1] > -1]), max([row[2] for row in result[:-1] if row[2] > -1])] )
    #
    # sub_res = []
    # for i in range(3):
    #     sub_cal = [row[i] for row in result[:-2] if row[i] > 0]
    #     sub_res.append(sum(sub_cal) / len(sub_cal))
    # result.append(sub_res)
    #
    # savefile = "./rank_table/rank_table_%d_choice%d.csv" %(blind_size2, max_val)
    # with open(savefile, "w") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["key_no", "p_rank", "q_rank", "p_rank * q_rank"])
    #     for i in range(len(result[:-3])):
    #         writer.writerow([i] + result[i])
    #     writer.writerow(["min"] + result[-3])
    #     writer.writerow(["max"] + result[-2])
    #     writer.writerow(["ave"] + result[-1])
    # # print(result)
    #     # exit(1)
    #     # match_index = L_index[index_list.index(min_index)]
