# -*- coding: utf-8 -*
# # python3.6.5
# # 観測された演算系列にビット値を知るためのルールを適用する
#
# import re
# window = 4
#
def EnzanToKnownBit(seq, w, rec=False):
    obtain_bit = preprocess(seq)
    # obtain_bit = "xxxXxxXxxxXxxxXxxxXxxxXxXxxxxxXxxxX"
    m_minus = list()
    m_plus = list()
    obtain_bit, m_minus, m_plus = DJB_linear(obtain_bit, w)
    # print(m_minus)
    # print(m_plus)
    ratio = sum([1 if s != "x" else 0 for s in obtain_bit])/len(obtain_bit)
    # print("known rate:")
    # print(str(sum([1 if s != "x" else 0 for s in obtain_bit])) + "/" + str(len(obtain_bit)))
    # print(sum([1 if s != "x" else 0 for s in obtain_bit])/len(obtain_bit))
    # print(obtain_bit)
    # obtain_bit = Rule0(obtain_bit)
    # print(obtain_bit)
    # obtain_bit = DJBRule1(obtain_bit, w)
    # xuang et.alの復元方法だとRule3しか適用できない
    # -2019/06/28-
    # print(obtain_bit)
    # obtain_bit = DJBRule2(obtain_bit,w)
    # # print(obtain_bit)
    # obtain_bit = DJBRule3(obtain_bit,w)
    # print(obtain_bit)
    # obtain_bit = DJBIA(obtain_bit,w)

    # candi_num(obtain_bit)
    #exit(1)

    # for i in range(len(obtain_bit)):
    #     if obtain_bit[i] == "I":
    #         obtain_bit = obtain_bit[:i] + "1" + obtain_bit[i+1:]
    #     elif obtain_bit[i] == "O":
    #         obtain_bit = obtain_bit[:i] + "0" + obtain_bit[i+1:]
    if rec:
        return obtain_bit, m_minus, m_plus
    return obtain_bit, m_minus, m_plus, ratio


def preprocess(seq):
    bit_pre = ""
    for i in range(len(seq)):
        if seq[i] == "s":
            bit_pre += "x"
        elif seq[i] == "m":
            bit_pre = bit_pre[:-1] + "X"
        else:
            print("error")
    return bit_pre

def DJB_linear(seq, w):
    bit_seq = seq
    multi_posi = list()
    for i in range(len(seq)):
        if seq[i] == "X":
            multi_posi.append(i)
    m_minus = [1 for i in range(len(multi_posi))]
    m_plus = [w for i in range(len(multi_posi))]

    for i in range(len(multi_posi)-2, -1, -1):
        max_num = m_minus[i+1] + multi_posi[i] - multi_posi[i+1] + w
        if m_minus[i] < max_num:
            m_minus[i] = max_num

    for i in range(1, len(multi_posi)):
        min_num = m_plus[i-1] + multi_posi[i] - multi_posi[i-1] - w
        if m_plus[i] > min_num:
            m_plus[i] = min_num

    for i in range(len(multi_posi)):
        if multi_posi[i] == 0:
            bit_seq = "1" + bit_seq[1:]

        else:
            bit_seq = bit_seq[:multi_posi[i]] + "1" + bit_seq[multi_posi[i]+1:]
            if m_minus[i] == m_plus[i]:
                target = multi_posi[i]-(m_minus[i]-1)
                bit_seq = bit_seq[:target] + "1" +bit_seq[target+1:]
                # print(bit_seq)
                # exit(1)
                # print(bit_seq)
                # exit(1)
                if i > 0:
                    for j in range(target-1, multi_posi[i-1], -1):
                        bit_seq = bit_seq[:j] + "0" + bit_seq[j+1:]
                else:
                    for j in range(target-1, -1, -1):
                        bit_seq = bit_seq[:j] + "0" + bit_seq[j+1:]
            else:
                target = multi_posi[i] - (m_plus[i] - 1)
                for j in range(target-1, multi_posi[i-1], -1):
                    bit_seq = bit_seq[:j] + "0" + bit_seq[j+1:]
    for i in multi_posi:
        bit_seq = bit_seq[:i] + "I" + bit_seq[i+1:]
    return bit_seq, m_minus, m_plus
    # exit(1)
    # print(m_minus)
    # print(m_plus)
    # exit(1)
def Rule0(bit_pre):
     bit_r0 = bit_pre.replace("X", "I")
     return bit_r0

def DJBRule1(bit_r0, w):
    bit_r1=bit_r0
    m_index = [i for i in range(len(bit_r0)) if bit_r1[i] == "I"]
    for i in range(len(m_index)-1):
        watch_bit = bit_r1[m_index[i]:m_index[i+1]+1]
        j = len(watch_bit)-2
        if j < w-1:
            watch_bit = bit_r1[m_index[i+1]+1:m_index[i+1]+(w-1-j)+1]
            if watch_bit == "x"*(w-1-j):
                watch_bit = "0"*(w-1-j)
                bit_r1 = bit_r1[:m_index[i+1]+1] + watch_bit + bit_r1[m_index[i+1]+1+(w-1-j):]
    return bit_r1

def DJBRule2(bit_r1,w):
    bit_r2=bit_r1
    m_index = [i for i in range(len(bit_r2)) if bit_r2[i] == "I"]
    for i in range(len(m_index)-1):
        if m_index[i] + 1 == m_index[i+1]:
            watch_bit = bit_r2[m_index[i]-3:m_index[i]]
            if watch_bit == "xxx":
                watch_bit = "1xx"
                bit_r2 = bit_r2[:m_index[i]-3] + watch_bit + bit_r2[m_index[i]:]
    return bit_r2

def DJBRule3(bit_r2,w):
    bit_r3=bit_r2
    m_index = [i for i in range(len(bit_r3)) if bit_r3[i] == "I"]
    for i in range(len(m_index)-1):
        watch_bit = bit_r3[m_index[i]+1:m_index[i+1]]
        j = len(watch_bit) - (w-1)
        if j > 0:
            for k in range(len(watch_bit)):
                if watch_bit[k] == "x" and k < j:
                    watch_bit = watch_bit[:k] + "O" + watch_bit[k+1:]
            bit_r3 = bit_r3[:m_index[i]+1] + watch_bit + bit_r3[m_index[i+1]:]
    return bit_r3

def DJBIA(bit_r3,w):
    bit_ia = bit_r3
    lo_index = [i for i in range(len(bit_ia)) if bit_ia[i] == "1"]
    for i in range(len(lo_index)):
        watch_lo = lo_index[i]
        tz_num = 0
        flag = 0
        while flag == 0:
            tz_num = 0
            for j in range(watch_lo-1, 0, -1):
                if bit_ia[j] == "I":
                    watch_m = j
                    flag=1
                    break
                elif bit_ia[j] == "0":
                    tz_num += 1
                elif bit_ia[j] == "O":
                    flag = 2
                    break
                else:
                    flag = 1
                    break

            if flag == 2:
                break
            if tz_num == w-1:
                flag = 0
            for k in range(1,w):
                if tz_num == -k+(w-1) and flag == 1:
                    # print("debag_a")
                    bit_ia = bit_ia[:watch_m - k] + "1"+ "x"*(k-1) + bit_ia[watch_m:]
                    flag = 0
                    # print(bit_ia)
                    break
            if flag == 0:
                watch_lo = watch_m - k
            else:
                break
    return bit_ia

def candi_num(obtain_bit):
    start = 0
    pattern = list()
    for i in range(len(obtain_bit)):
        if obtain_bit[i] == "I":
            pattern.append(obtain_bit[start:i+1])
            start = i+1
    x_num = [sub_bit.count("x") for sub_bit in pattern]
    can_num = 1
    for count in x_num:
        can_num *= 2 ** count
    # print(can_num)
    print(len(bin(can_num)))
    # print(obtain_bit)
    # print(pattern)
    # exit(1)

def XuangRule1(bit_r0, w):
    bit_r1=""
    m_index = [i for i in range(len(bit_r0)) if bit_r0[i] == "I"]
    watch_bit = bit_r0[:(w-1-m_index[0])+1]
    if watch_bit == "r"*(m_index[0])+"I"+"r"*(w-1-m_index[0]):
        watch_bit = "r"*(m_index[0])+"I"+"0"*(w-1-m_index[0])
    bit_r1 = watch_bit + bit_r0[(w-1-m_index[0])+1:]

    for i in range(len(m_index)-1):
        watch_bit = bit_r1[m_index[i]:m_index[i+1]+1]
        zero_num = 0
        for j in range(1,len(watch_bit)):
            if watch_bit[j] == "0":
                zero_num += 1
            elif watch_bit[j] == "r":
                break
        j2 = len(watch_bit) - 2
        if 0 < j2 and j2 < w:
            watch_bit = bit_r1[m_index[i]:m_index[i+1]+(w-1-j2)+1]
            watch_bit = "I" + "0"*zero_num + "x"*j2 + "I" + "0"*(w-1-j2)
            bit_r1 = bit_r1[:m_index[i]] + watch_bit + bit_r1[m_index[i+1]+(w-1-j2)+1:]

    return bit_r1

def XuangRule2(bit_r1,w):
    bit_r2 = ""
    i = len(bit_r1)-1
    while i >= 0:
        if bit_r1[i] == "1":
            if i-w < 0:
                bit_r2 = bit_r1[:i+1] + bit_r2
                break
            else:
                watch_bit = bit_r1[i-w:i+1]
            for j in range(1,w):
                if watch_bit == "x"*(w-1-j)+"I"+"0"*j+"1":
                    watch_bit = "1"+"x"*(w-j-1)+"I"+"0"*j+"1"
                    break
            i -= w
        elif bit_r1[i] == "I":
            if i-w < 0:
                bit_r2 = bit_r1[:i+1] + bit_r2
                print(bit_r2)
                break
            else:
                watch_bit = bit_r1[i-w:i+1]
            for j in range(1,w):
                if watch_bit == "r"*(w-1-j)+"I"+"0"*(w-1-j)+"I":
                    watch_bit = "1"+"r"*(j-1)+"I"+"0"*(w-1-j)+"I"
                    break
            bit_r2 = watch_bit + bit_r2
            print(bit_r2)
            i -= w
        else:
            bit_r2 = bit_r1[i] + bit_r2
            print(bit_r2)
            i -= 1
    return bit_r2

def XuangRule3(bit_r2,w):
    bit_r3 = ""
    for i in range(len(bit_r2)):
        if bit_r2[i] == "1":
            bit_r3 = "0"*i+"1" + bit_r2[i+1:]
            break
        elif bit_r2[i] == "I":
            if i >= w-1:
                bit_r3 = "0"*(i-w-1)+"r"*(w-1)+"I" + bit_r2[i+1:]
            break
    m_index = [i for i in range(len(bit_r2)) if bit_r2[i] == "I"]
    for i in range(len(m_index)-1):
        for j in range(m_index[i], len(bit_r2)):
            if bit_r2[j] == "1":
                watch_bit = bit_r2[m_index[i]:j+1]
                watch_bit = "I"+"0"*(len(watch_bit)-2)+"1"
                bit_r3 = bit_r3[:m_index[i]] + watch_bit + bit_r3[j+1:]
                break
            elif bit_r2[j] == "I":
                watch_bit = bit_r2[m_index[i]:j+1]
                for k in range(len(watch_bit)):
                    if watch_bit[k] == "x":
                        if len(watch_bit[k:])-1 > w-1:
                            watch_bit = watch_bit[:k] + "0"*(len(watch_bit[k:])-w)+"x"*(w-1)+"I"
                        break
                bit_r3 = bit_r3[:m_index[i]] + watch_bit + bit_r3[m_index[i+1]+1:]



if __name__ == "__main__":
    window = 4
    seq_test1 = "smsssssssmsmsssssm"
    seq_test2 = "ssmssssssssmssssmsssssmssssmsssmsssssmsmssssssmsssssssmssmssssssmsssmssssssssm"
    seq_test3="smssssmssssmsssssmssssmsssmssssmsssssssmsmsssssmssssssmsssssmsssmssssssssmssssmsssmssssssssmsssmsssssmssssmssssssmsssmssssssmssssssmssmsssssmsssssssmsssmssssssssmssssmsssssmssssssmsssmssssmsssssmsssssssmsssssmsssmssssmssssssssmssmsssssssmsssssmssssmssssssmsssssssmssssmssssmsssssmssmssssssmssssmssssssmsssssmsssssmsssssssmssssmssssssmssssmsssssmsssmsssssmssssssmsssssmsssssssmssssssmssssmsssmsssssssmsssmssssssmsssssmssssmsssssmsssssssmsssssmsssmsssssmsmssssssssmsssssmssssmsssmsssssmsssmssssssssmssssmsssssmssssssssmssssmssssssmssssssmssmsssssssmssssmssssssmssmssssssmsssssssmsssssmssssmsssmssssssssssmsmsssssssmssssm"
    seq_test4="smssssmssssmsssssmssssmsssmssssmsssssssmsmsssssmssssssmsssssmsssmssssssssmssssmsssmssssssssmsssmsssssmssssmssssssmsssmssssssmssssssmssmsssssmsssssssmsssmssssssssmssssmsssssmssssssmsssmssssmsssssmsssssssmsssssmsssmssssmssssssssmssmsssssssmsssssmssssmssssssmsssssssmssssmssssmsssssmssmssssssmssssmssssssmsssssmsssssmsssssssmssssmssssssmssssmsssssmsssmsssssmssssssmsssssmsssssssmssssssmssssmsssmsssssssmsssmssssssmsssssmssssmsssssmsssssssmsssssmsssmsssssmsmssssssssmsssssmssssmsssmsssssmsssmssssssssmssssmsssssmssssssssmssssmssssssmssssssmssmsssssssmssssmssssssmssmssssssmsssssssmsssssmssssmsssmssssssssssmsmsssssssmssssm"
    seq_test5="smsssssssmsssssmsssssmssssmsssssssssmssssmsssssmsmssssssssmssssmssssmsssssmssssmsssmsssssmsssssmsssssmsssssmssssmsssssmsssssssmssssmsssmsssssssssmssmsssmsssssmssssmsssssssmssssmsssssssssssmsssmssssssmsssmsssssmssssmsssssmssssmssmssssssmssmssssssssmssssmsssssssmssssmssssssmsssssmsssssmssssmsssssmssssssssssmssssmssssssssmssssmsssssmssssssmssmssssmsssssssmsssmssssssmssssmsssssssmsssssmsssmssssmssmssssmssssssssssmsssmssssssmsssmssssmsssssmsmssssssssmssssmssssmsssssssmsssssmssssmsssssmsssmsssssssssssmsssssmssssssmssmssssssmsssmsssssmsssssssmssmsssssssmsssssssmsssssmsssssssmssssmssssssmsssssssmsmsssssssmsssssssmssm"
    # print(seq_test3==seq_test4)
    result = EnzanToKnownBit(seq_test5, window)
    print(result)
    hukugen = sum([1 for s in result if s != "x"]) / len(result)
    print(hukugen)
    print("%d/%d" %(sum([1 for s in result if s != "x"]), len(result)))
