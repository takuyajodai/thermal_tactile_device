import random

def generate_soa_list():
    # Comment out soa_list that you don't use.
    # Pilot SOA
    #soa_list = [-1500, -1000, -600, -300, -100, 0, 100, 300, 600, 1000, 1500]

    # main SOA for cooling
    soa_list = [-1000, -700, -500, -350, -250, -200, -150, -50, 100, 300, 600]

    # main SOA for warming
    #soa_list = [-2000, -1500, -1100, -800, -600, -500, -400, -200, 100, 500, 1000]

    # 4回リピート
    soa_list *= 4

    # SOA for Practice
    #soa_list = [-2000, -1100, -600, -400, 100, 1000]



    random.shuffle(soa_list)

    #print(soa_list)

    # 添え字をつける
    new_list = [[i, soa_list[i]] for i in range(len(soa_list))]
    #print(new_list)

    return new_list
