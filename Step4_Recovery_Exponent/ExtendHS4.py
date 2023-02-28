
from joblib import Parallel, delayed
import sys
import gc

max_process = 32 * 3
key_poss = [ [str(i), str(j), str(k), str(l)]  for i in range(2) for j in range(2) for k in range(2) for l in range(2)]

def ExtendHS(gp, gq, gDp, gDq, lp, lq, n, e, \
cp_bin, cq_bin, cDp_bin, cDq_bin):
    Q = []
    # [gDq, gDp, gq, gp, depth]
    Q.append([1, gp, gq, gDp, gDq])
    count = 0
    flag = 1
    poss_count = 0
    kp_bits = ext_bit(bin(lp))
    kq_bits = ext_bit(bin(lq))
    # depth_control = 1
    # 深さ優先探索のループ
    while len(Q) > 0:
        count += 1
        if count == 100000:
            print(len(Q))
            count %= 100000
        # データをprocess数分取り出すループ
        depth, p_bin, q_bin, Dp_bin, Dq_bin = Q.pop()

        # if p_bin[-depth:] == cp_bin[-depth:] and q_bin[-depth:] == cq_bin[-depth:] and \
        # Dp_bin[-depth:] == cDp_bin[-depth:] and Dq_bin[-depth:] == cDq_bin[-depth:]:
        #     print(depth)
        # else:
        #     continue

        if depth == 512:
            if p_bin[-depth:] == cp_bin[-depth:] and q_bin[-depth:] == cq_bin[-depth:] and \
            Dp_bin[-depth:] == cDp_bin[-depth:] and Dq_bin[-depth:] == cDq_bin[-depth:]:
                poss_count += 1
                print("find_key")
                print("now: %d"  %(poss_count))
                continue
                # return 0
                flag = 0
            else:
                poss_count += 1
                print("now: %d"  %(poss_count))
                continue

        Q += Process2(depth, p_bin, q_bin, Dp_bin, Dq_bin, lp, lq, n, e, kp_bits, kq_bits)

    print("candidate: %d" %(poss_count))
    return flag


def ext_bit(u):
    if u[-1] == "1":
        return 0
    else:
        count = 0
        while u[-count-1] == "0":
            count += 1
        return count

def Process(depth, p_bin_in, q_bin_in, Dp_bin_in, Dq_bin_in, \
            lp, lq, n, e, kp_bits, kq_bits):
    # print("process depth=%d" %(depth))
    Q = list()
    result = list()
    ori_p_bin = p_bin_in
    ori_q_bin = q_bin_in
    ori_Dp_bin = Dp_bin_in
    ori_Dq_bin = Dq_bin_in

    Dp_eff = ori_Dp_bin[-(depth+1+kp_bits)]
    Dq_eff = ori_Dq_bin[-(depth+1+kq_bits)]

    is_poss = [1 for i in range(len(key_poss))]


    j = 0
    for p_i, q_i, Dp_i, Dq_i in key_poss:



        if ori_p_bin[-depth-1] != "x" and ori_p_bin[-depth-1] != p_i:
            is_poss[j] = 0
            j += 1
            continue


        if ori_q_bin[-depth-1] != "x" and ori_q_bin[-depth-1] != q_i:
            is_poss[j] = 0
            j += 1
            continue

        if ori_Dp_bin[-depth-1] != "x" and ori_Dp_bin[-depth-1] != Dp_i:
            is_poss[j] = 0
            j += 1
            continue

        if ori_Dq_bin[-depth-1] != "x" and ori_Dq_bin[-depth-1] != Dq_i:
            is_poss[j] = 0
            j += 1
            continue

        # if depth == 500:
        #     if p_i == "0" and q_i == "1" and dp_i == "1"and dq_i == "1" and Dp_i == "1" and Dq_i == "0":
        #         print("OK")
        #         exit(1)


        p_bin = ori_p_bin[:-depth-1] + p_i + ori_p_bin[-depth:]
        q_bin = ori_q_bin[:-depth-1] + q_i + ori_q_bin[-depth:]
        Dp_bin = ori_Dp_bin[:-depth-1] + Dp_i + ori_Dp_bin[-depth:]
        Dq_bin = ori_Dq_bin[:-depth-1] + Dq_i + ori_Dq_bin[-depth:]

        # pq = N
        pq = int(p_bin[-depth-1:], 2) * int(q_bin[-depth-1:], 2)
        if pq % (2**(depth+1)) != n % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue


        eDp_1 = (e* int(Dp_bin[-depth-1:], 2)) - 1
        kpp_erp = lp  * (int(p_bin[-depth-1:], 2) - 1)
        if eDp_1 % (2**(depth+1)) != kpp_erp % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue

        effect = []


        kpp_eDp = lp*(int(p_bin[-depth:], 2) - 1) + 1 - e*int(Dp_bin[-depth:], 2)
        c3 = kpp_eDp % (2**(depth+1+kp_bits))
        c3 = c3 >> (kp_bits+depth)
        if c3 == 0:
            if Dp_eff != "x":
                if p_i != Dp_eff:
                    j += 1
                    continue
            # dp and p must agree at bit i
            effect.append(p_i)
        else:
            if Dp_eff != "x":
                if p_i == Dp_eff:
                    j += 1
                    continue
             # dp and p must *dis*agree at bit i
            effect.append(str(1 ^ int(p_i)))



        eDq_1 = (e* int(Dq_bin[-depth-1:], 2)) - 1
        kqq_erq = lq  * (int(q_bin[-depth-1:], 2) - 1)
        if eDq_1 % (2**(depth+1)) != kqq_erq % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue

        kqq_eDq = lq*(int(q_bin[-depth:], 2) - 1) + 1 - e*int(Dq_bin[-depth:], 2)
        c4 = kqq_eDq % (2**(depth+1+kq_bits))
        c4 = c4 >> (kq_bits+depth)
        if c4 == 0:
            if Dq_eff != "x":
                if Dq_eff != q_i:
                    j += 1
                    continue
            # dq1 and q must agree at bit i
            effect.append(q_i)
        else:
            if Dq_eff != "x":
                if Dq_eff == q_i:
                    j += 1
                    continue
            # dq1 and q must *dis*agree at bit i
            effect.append(str(1 ^ int(q_i)))

        Dq_ef = effect.pop()
        Dq_out = Dq_bin[:-(depth+kq_bits)-1] + Dq_ef + Dq_bin[-(depth+kq_bits):]
        Dp_ef = effect.pop()
        Dp_out = Dp_bin[:-(depth+kp_bits)-1] + Dp_ef + Dp_bin[-(depth+kp_bits):]


        p_out = p_bin[:-depth-1] +key_poss[j][0] + p_bin[-depth:]
        q_out = q_bin[:-depth-1] + key_poss[j][1] + q_bin[-depth:]
        Dp_out = Dp_out[:-depth-1] + key_poss[j][2] + Dp_out[-depth:]
        Dq_out = Dq_out[:-depth-1] + key_poss[j][3] + Dq_out[-depth:]

        depth_out = depth+1
        result += [Dq_out, Dp_out, q_out, p_out, depth_out]
        j += 1

    return result

def Process2(depth, p_bin_in, q_bin_in, Dp_bin_in, Dq_bin_in, \
            lp, lq, n, e, kp_bits, kq_bits):

    result = []
    ori_p_bin = p_bin_in
    ori_q_bin = q_bin_in
    ori_Dp_bin = Dp_bin_in
    ori_Dq_bin = Dq_bin_in

    Dp_eff = ori_Dp_bin[-(depth+1+kp_bits)]
    Dq_eff = ori_Dq_bin[-(depth+1+kq_bits)]

    is_poss = [1 for i in range(16)]


    j = 0
    for p_i, q_i, Dp_i, Dq_i in key_poss:



        if ori_p_bin[-depth-1] != "x" and ori_p_bin[-depth-1] != p_i:
            is_poss[j] = 0
            j += 1
            continue


        if ori_q_bin[-depth-1] != "x" and ori_q_bin[-depth-1] != q_i:
            is_poss[j] = 0
            j += 1
            continue

        if ori_Dp_bin[-depth-1] != "x" and ori_Dp_bin[-depth-1] != Dp_i:
            is_poss[j] = 0
            j += 1
            continue

        if ori_Dq_bin[-depth-1] != "x" and ori_Dq_bin[-depth-1] != Dq_i:
            is_poss[j] = 0
            j += 1
            continue

        p_bin = ori_p_bin[:-depth-1] + p_i + ori_p_bin[-depth:]
        q_bin = ori_q_bin[:-depth-1] + q_i + ori_q_bin[-depth:]
        Dp_bin = ori_Dp_bin[:-depth-1] + Dp_i + ori_Dp_bin[-depth:]
        Dq_bin = ori_Dq_bin[:-depth-1] + Dq_i + ori_Dq_bin[-depth:]

        # pq = N
        pq = int(p_bin[-depth-1:], 2) * int(q_bin[-depth-1:], 2)
        if pq % (2**(depth+1)) != n % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue


        eDp_1 = (e* int(Dp_bin[-depth-1:], 2)) - 1
        kpp_erp = lp  * (int(p_bin[-depth-1:], 2) - 1)
        if eDp_1 % (2**(depth+1)) != kpp_erp % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue

        kpp_eDp = lp*(int(p_bin[-depth:], 2) - 1) + 1 - e*int(Dp_bin[-depth:], 2)
        c3 = kpp_eDp % (2**(depth+1+kp_bits))
        c3 = c3 >> (kp_bits+depth)
        if c3 == 0:
            if Dp_eff != "x" and p_i != Dp_eff:
                j += 1
                continue
            # dp and p must agree at bit i
            Dp_ef = p_i
            # effect.append(p_i)
        else:
            if Dp_eff != "x" and  p_i == Dp_eff:
                j += 1
                continue
             # dp and p must *dis*agree at bit i
            Dp_ef = str(1^int(p_i))
            # effect.append(str(1 ^ int(p_i)))



        eDq_1 = (e* int(Dq_bin[-depth-1:], 2)) - 1
        kqq_erq = lq  * (int(q_bin[-depth-1:], 2) - 1)
        if eDq_1 % (2**(depth+1)) != kqq_erq % (2**(depth+1)):
            is_poss[j] = 0
            j += 1
            continue

        kqq_eDq = lq*(int(q_bin[-depth:], 2) - 1) + 1 - e*int(Dq_bin[-depth:], 2)
        c4 = kqq_eDq % (2**(depth+1+kq_bits))
        c4 = c4 >> (kq_bits+depth)
        if c4 == 0:
            if Dq_eff != "x" and Dq_eff != q_i:
                j += 1
                continue
            # dq1 and q must agree at bit i
            Dq_ef = q_i
            # effect.append(q_i)
        else:
            if Dq_eff != "x" and Dq_eff == q_i:
                j += 1
                continue
            # dq1 and q must *dis*agree at bit i
            Dq_ef = str(1^int(q_i))
            # effect.append(str(1 ^ int(q_i)))

        # Dq_ef = effect.pop()
        Dq_out = Dq_bin[:-(depth+kq_bits)-1] + Dq_ef + Dq_bin[-(depth+kq_bits):]
        # Dp_ef = effect.pop()
        Dp_out = Dp_bin[:-(depth+kp_bits)-1] + Dp_ef + Dp_bin[-(depth+kp_bits):]


        p_out = p_bin[:-depth-1] +key_poss[j][0] + p_bin[-depth:]
        q_out = q_bin[:-depth-1] + key_poss[j][1] + q_bin[-depth:]
        Dp_out = Dp_out[:-depth-1] + key_poss[j][2] + Dp_out[-depth:]
        Dq_out = Dq_out[:-depth-1] + key_poss[j][3] + Dq_out[-depth:]

        depth_out = depth+1
        result.append([depth_out, p_out, q_out, Dp_out, Dq_out])
        j += 1

    return result
