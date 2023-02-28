import re
# バイナリ系列を Sliding Window で演算系列に変換する関数
# binary : 入力バイナリ系列
# window : SlidingWindw の 窓幅
def bin2seq_for_libgcrypt(binary, window):
    seq=''
    i=0


    # libgcrypt 処理系に乗算回数をそろえている
    binary = binary[1:]


    while len(binary) > 0:
        i+=1
        # 先頭文字列の取り出し
        match_nzero_OB = re.match(r'1.{0,%s}1|1' % (window - 2), binary) # window size
        match_zero_OB = re.match(r'0+', binary)



        # non-zero digit
        if match_nzero_OB:
            digits = match_nzero_OB.group()
            digitslen = len(digits)
            index = match_nzero_OB.end()
            seq = seq + 's' * digitslen + 'm'
            binary = binary[index:]



        # zero digit
        elif match_zero_OB:
            digits = match_zero_OB.group()
            digitslen = len(digits)
            index = match_zero_OB.end()
            seq = seq + 's' * digitslen
            binary = binary[index:]



        # 終了
        else:
            break


    #
    return seq