import random

def generate_soa_list():
    # パイロットのSOA
    soa_list = [-1500, -1000, -600, -300, -100, 0, 100, 300, 600, 1000, 1500]

    # 4回リピート
    soa_list *= 4
    #for i in range(4):
    #    temp_list = random.sample(soa_list, len(soa_list))
    #    temp_list += temp_list

    random.shuffle(soa_list)

    #print(soa_list)

    # 添え字をつける
    new_list = [[i, soa_list[i]] for i in range(len(soa_list))]
    #print(new_list)

    return new_list
