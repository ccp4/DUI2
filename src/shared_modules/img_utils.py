import numpy as np
from matplotlib import pyplot as plt
def img_arr_gen(x_size, y_size):
    arr_2d = np.zeros((x_size, y_size), dtype=np.float64, order='C')
    xmid = x_size / 2
    ymid = y_size / 2
    for x in range(x_size):
        for y in range(y_size):
            h = abs(xmid - x) + abs(ymid - y)
            arr_2d[x, y] = h

    arr_2d[
        int(x_size / 10):int(x_size - x_size / 10),
        int(y_size / 10):int(y_size / 5)
    ] = 5

    return arr_2d


def generate_bunches(arr_in, n_times):
    step_lst = []
    for times in range(n_times):
        local_step = times + 1
        step_lst.append(2 ** local_step)

    step_lst.reverse()

    print(step_lst)

    lst_ini_stp = []
    ini = 0
    for pos, loop_step in enumerate(step_lst):
        ini_stp = (ini, loop_step)
        lst_ini_stp.append(ini_stp)
        ini = ini + int(loop_step / 2)
        ini_stp = (ini, loop_step)
        lst_ini_stp.append(ini_stp)
        ini = int(ini / 2)

    print(lst_ini_stp)

    new_arr_2d = np.zeros(
            (len(arr_in[:,0]), len(arr_in[0,:])),
            dtype=np.float64, order='C'
        )

    print("new_arr_2d =\n", new_arr_2d)

    for ini_stp in lst_ini_stp:
        print("ini_stp", ini_stp)



if __name__ == "__main__":

    img_arr = img_arr_gen(18, 14)
    print("img_arr =\n", img_arr)
    #plt.imshow(img_arr, interpolation = "nearest")
    #plt.show()
    generate_bunches(img_arr, 5)


