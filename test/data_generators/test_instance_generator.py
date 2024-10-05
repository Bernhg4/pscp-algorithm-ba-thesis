from source.models.baseModels import RoundInstance, PSCP_Instance


def gen_small_instance1():
    num_carriers = 3
    num_colors = 3
    history_color = 1
    demands = []

    ri_1 = RoundInstance([1, 1, 2, 2, 2, 1, 1])

    rounds = [ri_1]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

def gen_medium_instance1():
    num_carriers = 3
    num_colors = 3
    history_color = 1
    demands = []

    ri_1 = RoundInstance([1, 1, 2, 2, 2, 1, 1])
    ri_2 = RoundInstance([1, 1, 3, 3, 3, 3, 1, 2 ,2])
    ri_3 = RoundInstance([2, 2, 2, 1, 3, 3, 3, 1 ,1])

    rounds = [ri_1, ri_2, ri_3]

    return PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)
