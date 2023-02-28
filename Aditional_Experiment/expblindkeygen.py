import csv
import sys
from keytoseq import KeyToSeq
from enzan_rule import EnzanToKnownBit

def known_bit(seq,focus):
    count = 0
    for i in range(focus):
        if seq[i] != "x":
            count += 1
    return count

# 入力に乱数のビットサイズを入れる
# 2*乱数サイズ-2のビット数まで着目
if __name__ == "__main__":
    args = sys.argv
    r_bitlen = int(args[1])
    keyname = int(args[2])
    if len(args) != 3:
        print("Arguments is not correct")
        exit(1)

    readfile = "./RSA2048key/key%d.csv" %(keyname)
    savefile_Dp = "./expblindkey/Dp_%dbitsmask_key%d.csv" %(r_bitlen, keyname)
    savefile_Dq = "./expblindkey/Dq_%dbitsmask_key%d.csv" %(r_bitlen, keyname)

    # dpについて作成
    with open(readfile, "r") as f:
        read_data = f.read().split("\n")
    p = int(read_data[read_data.index("p")+1],0)
    dp = int(read_data[read_data.index("dp")+1],0)

    r_list = [num for num in range(2**15,2**16)]
    Dp_list = [dp+r*(p-1) for r in r_list]


    seq_list = [KeyToSeq(bin(Dp), window=5) for Dp in Dp_list]

    subkey_list = [EnzanToKnownBit(seq, 5) for seq in seq_list]

    subkey_list = [[row[0], row[3]] for row in subkey_list]

    result = [[hex(r_list[i]), hex(Dp_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*r_bitlen-2)] for i in range(len(r_list))]
    result1 = [row for row in result if row[3] == 1024+r_bitlen]
    result1.sort(key = lambda x: float(x[4]), reverse=True)
    result1.sort(key = lambda x: x[5], reverse=True)
    result2 =  [row for row in result if row[3] != 1024+r_bitlen]
    result2.sort(key = lambda x: float(x[4]), reverse=True)
    result2.sort(key = lambda x: x[5], reverse=True)
    result = result1 + result2

    with open(savefile_Dp, "w") as f:
        writer = csv.writer(f)
        # writer.writerow(["乱数", "Dp", "smから復元した系列", "演算系列の長さ", "復元率", "2*乱数サイズ-2のうち既知のビット数"])
        for row in result:
            writer.writerow(row)


    # dqについて作成
    with open(readfile, "r") as f:
        read_data = f.read().split("\n")
    q = int(read_data[read_data.index("q")+1],0)
    dq = int(read_data[read_data.index("dq")+1],0)

    r2_list = [num for num in range(2**15,2**16)]
    Dq_list = [dq+r*(q-1) for r in r2_list]


    seq_list_Dq = [KeyToSeq(bin(Dq), window=5) for Dq in Dq_list]

    subkey_list_Dq = [EnzanToKnownBit(seq, 5) for seq in seq_list_Dq]

    subkey_list_Dq = [[row[0], row[3]] for row in subkey_list_Dq]

    result_Dq = [[hex(r2_list[i]), hex(Dq_list[i]), subkey_list_Dq[i][0], len(subkey_list_Dq[i][0]), subkey_list_Dq[i][1], known_bit(subkey_list_Dq[i][0], 2*r_bitlen-2)] for i in range(len(r2_list))]
    result1_Dq = [row for row in result_Dq if row[3] == 1024+r_bitlen]
    result1_Dq.sort(key = lambda x: float(x[4]), reverse=True)
    result1_Dq.sort(key = lambda x: x[5], reverse=True)
    result2_Dq =  [row for row in result_Dq if row[3] != 1024+r_bitlen]
    result2_Dq.sort(key = lambda x: float(x[4]), reverse=True)
    result2_Dq.sort(key = lambda x: x[5], reverse=True)
    result_Dq = result1_Dq + result2_Dq

    with open(savefile_Dq, "w") as f:
        writer = csv.writer(f)
        # writer.writerow(["乱数", "Dq", "smから復元した系列", "演算系列の長さ", "復元率", "2*乱数サイズ-2のうち既知のビット数"])
        for row in result_Dq:
            writer.writerow(row)
