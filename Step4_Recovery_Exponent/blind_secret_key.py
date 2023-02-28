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

if __name__ == "__main__":
    args = sys.argv
    keyname = args[1]
    r_bitlen = int(args[2])
    if len(args) != 3:
        print("Arguments is not correct")
        exit(1)

    readfile = "./original_secret_key/key%s.txt" %(keyname)
    savefile = "./blind_secret_key/key%s_Dq_%dbits.csv" %(keyname,r_bitlen)


    with open(readfile, "r") as f:
        read_data = f.read().split("\n")
    p = int(read_data[read_data.index("q")+1],0)
    dp = int(read_data[read_data.index("dq")+1],0)

    r_list = [num for num in range(2**15,2**16)]
    Dp_list = [dp+r*(p-1) for r in r_list]


    seq_list = [KeyToSeq(bin(Dp), window=5) for Dp in Dp_list]

    subkey_list = [EnzanToKnownBit(seq, 5) for seq in seq_list]

    subkey_list = [[row[0], row[3]] for row in subkey_list]

    result = [[hex(r_list[i]), hex(Dp_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*r_bitlen)] for i in range(len(r_list))]
    result1 = [row for row in result if row[3] == 512+r_bitlen]
    result1.sort(key = lambda x: float(x[4]), reverse=True)
    result1.sort(key = lambda x: x[5], reverse=True)
    result2 =  [row for row in result if row[3] != 512+r_bitlen]
    result2.sort(key = lambda x: float(x[4]), reverse=True)
    result2.sort(key = lambda x: x[5], reverse=True)
    result = result1 + result2

    with open(savefile, "w") as f:
        writer = csv.writer(f)
        for row in result:
            writer.writerow(row)
