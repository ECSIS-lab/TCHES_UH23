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

    blind_size = int(args[1])
    if len(args) != 2:
        print("Arguments is not correct")
        exit(1)

    for keyname in range(100):

        readfile = "./original_key/key%d.csv" %(keyname)
        # savefile = "./blind_secret_key/key%s_Dp_%dbits_35.csv" %(keyname,blind_size)
        # savefile = "./blind_secret_key/key%s_Dq_%dbits.csv" %(keyname,blind_size)


        with open(readfile, "r") as f:
            reader = csv.reader(f)
            read_data = [row[0] for row in reader]

        p = int(read_data[read_data.index("p")+1],0)
        dp = int(read_data[read_data.index("dp")+1],0)
        q = int(read_data[read_data.index("q")+1],0)
        dq = int(read_data[read_data.index("dq")+1],0)


        # Dpについて
        r_list = [num for num in range(2**(blind_size-1),2**blind_size)]
        Dp_list = [dp+r*(p-1) for r in r_list]


        seq_list = [KeyToSeq(bin(Dp), window=5) for Dp in Dp_list]

        subkey_list = [EnzanToKnownBit(seq, 5) for seq in seq_list]

        subkey_list = [[row[0], row[3]] for row in subkey_list]

        # 2s ビットに着目
        result = [[hex(r_list[i]), hex(Dp_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*blind_size)] for i in range(len(r_list))]
        result1 = [row for row in result if row[3] == 512+blind_size]
        result1.sort(key = lambda x: float(x[4]), reverse=True)
        result1.sort(key = lambda x: x[5], reverse=True)
        result2 =  [row for row in result if row[3] != 512+blind_size]
        result2.sort(key = lambda x: float(x[4]), reverse=True)
        result2.sort(key = lambda x: x[5], reverse=True)
        result = result1 + result2

        savefile1 = "./blind_key/key%d_Dp%d.csv" %(keyname, 2*blind_size)
        with open(savefile1, "w") as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)

        # 2s+3 ビットに着目
        result = [[hex(r_list[i]), hex(Dp_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*blind_size+3)] for i in range(len(r_list))]
        result1 = [row for row in result if row[3] == 512+blind_size]
        result1.sort(key = lambda x: float(x[4]), reverse=True)
        result1.sort(key = lambda x: x[5], reverse=True)
        result2 =  [row for row in result if row[3] != 512+blind_size]
        result2.sort(key = lambda x: float(x[4]), reverse=True)
        result2.sort(key = lambda x: x[5], reverse=True)
        result = result1 + result2

        savefile2 = "./blind_key/key%d_Dp%d.csv" %(keyname,2*blind_size+3)
        with open(savefile2, "w") as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)

        # Dqについて
        Dq_list = [dq+r*(q-1) for r in r_list]
        seq_list = [KeyToSeq(bin(Dq), window=5) for Dq in Dq_list]
        subkey_list = [EnzanToKnownBit(seq, 5) for seq in seq_list]
        subkey_list = [[row[0], row[3]] for row in subkey_list]

        # 2s ビットに着目
        result = [[hex(r_list[i]), hex(Dq_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*blind_size)] for i in range(len(r_list))]
        result1 = [row for row in result if row[3] == 512+blind_size]
        result1.sort(key = lambda x: float(x[4]), reverse=True)
        result1.sort(key = lambda x: x[5], reverse=True)
        result2 =  [row for row in result if row[3] != 512+blind_size]
        result2.sort(key = lambda x: float(x[4]), reverse=True)
        result2.sort(key = lambda x: x[5], reverse=True)
        result = result1 + result2

        savefile3 = "./blind_key/key%d_Dq%d.csv" %(keyname, 2*blind_size)
        with open(savefile3, "w") as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)

        # 2s ビットに着目
        result = [[hex(r_list[i]), hex(Dq_list[i]), subkey_list[i][0], len(subkey_list[i][0]), subkey_list[i][1], known_bit(subkey_list[i][0], 2*blind_size+3)] for i in range(len(r_list))]
        result1 = [row for row in result if row[3] == 512+blind_size]
        result1.sort(key = lambda x: float(x[4]), reverse=True)
        result1.sort(key = lambda x: x[5], reverse=True)
        result2 =  [row for row in result if row[3] != 512+blind_size]
        result2.sort(key = lambda x: float(x[4]), reverse=True)
        result2.sort(key = lambda x: x[5], reverse=True)
        result = result1 + result2

        savefile4 = "./blind_key/key%d_Dq%d.csv" %(keyname, 2*blind_size+3)
        with open(savefile4, "w") as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)
