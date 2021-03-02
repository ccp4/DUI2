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
    lst_ini_stp = []
    for times in range(n_times):
        step = 2 ** (times + 1)
        ini = int(step / 2)
        ini_stp = (ini, step)
        lst_ini_stp.append(ini_stp)

    lst_ini_stp.reverse()
    print("lst_ini_stp:", lst_ini_stp)

    x_size = len(arr_in[:,0])
    y_size = len(arr_in[0,:])
    new_arr_2d = np.zeros(
            (x_size, y_size), dtype=np.float64, order='C'
        )
    print("new_arr_2d =\n", new_arr_2d)

    for ini_stp in lst_ini_stp:
        print("ini_stp", ini_stp)
        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]

        for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]

        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]

        plt.imshow(new_arr_2d, interpolation = "nearest")
        plt.show()

    y_row = arr_in[0, 0:y_size]
    print("y_row =", y_row)
    new_arr_2d[0, 0:y_size] = y_row
    x_col = arr_in[0:x_size, 0]
    print("x_col =", x_col)
    new_arr_2d[0:x_size, 0] = x_col
    plt.imshow(new_arr_2d, interpolation = "nearest")
    plt.show()


if __name__ == "__main__":
    img_arr = img_arr_gen(25, 50)
    print("img_arr =\n", img_arr)
    plt.imshow(img_arr, interpolation = "nearest")
    plt.show()
    generate_bunches(img_arr, 5)

