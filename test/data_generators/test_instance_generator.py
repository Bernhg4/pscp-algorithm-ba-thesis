from source.models.baseModels import RoundInstance, PSCP_Instance, Demand


def gen_tiny_instance1():
    num_carriers = 3
    num_colors = 3
    history_color = 1
    demands = [
        Demand(6,1,2,2),
        Demand(2,2,3,2)
    ]

    ri_1 = RoundInstance([1, 1, 2, 2 ])
    ri_2 = RoundInstance([1, 1, 1, 1])
    #ri_3 = RoundInstance([1, 1, 2])

    rounds = [ri_1,ri_2]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

def gen_tiny_instance2():
    num_carriers = 2
    num_colors = 3
    history_color = 1
    demands = [
        Demand(2,1,2,1),
        Demand(2,2,3,1)
    ]

    ri_1 = RoundInstance([1, 1, 2, 2])

    rounds = [ri_1]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

def gen_small_instance1():
    num_carriers = 3
    num_colors = 3
    history_color = 1
    demands = [
        Demand(4, 1, 2, 1),
        Demand(3, 2, 1, 1)
    ]

    ri_1 = RoundInstance([1, 1, 2, 2, 2, 1, 1])

    rounds = [ri_1]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

def gen_medium_instance1():
    num_carriers = 3
    num_colors = 3
    history_color = 1
    demands = [
        Demand(10, 1, 1, 3),
        Demand(8, 2, 2, 3),
        Demand(7,3 , 3, 3)
    ]

    ri_1 = RoundInstance([1, 1, 2, 2, 2, 1, 1])
    ri_2 = RoundInstance([1, 1, 3, 3, 3, 3, 1, 2 ,2])
    ri_3 = RoundInstance([2, 2, 2, 1, 3, 3, 3, 1 ,1])

    rounds = [ri_1, ri_2, ri_3]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

def gen_big_instance1():
    num_carriers = 5
    num_colors = 5
    history_color = 1
    demands = [
        Demand(10, 1, 1, 3),
        Demand(8, 2, 2, 3),
        Demand(7,3 , 3, 3),
        Demand(8,4 , 4, 5),
        Demand(7,5 , 5, 5)
    ]

    ri_1 = RoundInstance([1, 1, 2, 2, 2, 1, 1])
    ri_2 = RoundInstance([1, 1, 3, 3, 3, 3, 1, 2 ,2])
    ri_3 = RoundInstance([2, 2, 2, 1, 3, 3, 3, 1 ,1])
    ri_4 = RoundInstance([4, 4, 4, 4, 4, 5, 5, 5])
    ri_5 = RoundInstance([4, 4, 4, 5, 5, 5, 5])

    rounds = [ri_1, ri_2, ri_3, ri_4, ri_5]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)
