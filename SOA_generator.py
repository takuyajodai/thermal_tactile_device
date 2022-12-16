import random

def generate_soa_list():
    # パイロットのSOA
    soa_list = [-2000, -1600, -1200, -800, -400, 0, 400, 800, 1200, 1600, 2000]

    # 4回リピート
    soa_list = soa_list * 4

    random.shuffle(soa_list)
    #print(soa_list)

    # 添え字をつける
    new_list = [[i, soa_list[i]] for i in range(len(soa_list))]
    print(new_list)

    return new_list
