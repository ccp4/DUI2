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


def generate_ini_n_steps(n_times):
    lst_ini_stp = []
    for times in range(n_times):
        step = 2 ** (times + 1)
        ini = int(step / 2)
        ini_stp = (ini, step)
        lst_ini_stp.append(ini_stp)

    lst_ini_stp.reverse()
    print("lst_ini_stp:", lst_ini_stp)
    return lst_ini_stp

def generate_bunches(arr_in, lst_ini_stp):
    lst_data_out = []
    x_size = len(arr_in[:,0])
    y_size = len(arr_in[0,:])
    #print("x_size, y_size: ", (x_size, y_size))
    lst_data_out.append("x_size, y_size: " + str((x_size, y_size)) )
    new_arr_2d = np.zeros(
            (x_size, y_size), dtype=np.float64, order='C'
        )

    # This connected loops need to be reproduced
    # just identically in the client side
    for ini_stp in lst_ini_stp:
        #print("ini_stp:", ini_stp)
        lst_data_out.append("ini_stp:" + str(ini_stp))
        arr_str = "I(x,y):["
        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]
                arr_str += str(arr_in[x, y]) + ","

        arr_str += "]"
        #print(arr_str)
        lst_data_out.append(arr_str)

        #print("ini_stp:", ini_stp)
        lst_data_out.append("ini_stp:" + str(ini_stp))
        arr_str = "I(x-u/2,y):["
        for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]
                arr_str += str(arr_in[x, y]) + ","

        arr_str += "]"
        #print(arr_str)
        lst_data_out.append(arr_str)

        #print("ini_stp:", ini_stp)
        lst_data_out.append("ini_stp:" + str(ini_stp))
        arr_str = "I(x,y-u/2):["
        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                new_arr_2d[x, y] = arr_in[x, y]
                arr_str += str(arr_in[x, y]) + ","

        arr_str += "]"
        #print(arr_str)
        lst_data_out.append(arr_str)

        #plt.imshow(new_arr_2d, interpolation = "nearest")
        #plt.show()

    y_row = arr_in[0, 0:y_size]
    print("y_row =", y_row)
    new_arr_2d[0, 0:y_size] = y_row
    x_col = arr_in[0:x_size, 0]
    print("x_col =", x_col)
    new_arr_2d[0:x_size, 0] = x_col
    #plt.imshow(new_arr_2d, interpolation = "nearest")
    #plt.show()
    return lst_data_out


def from_stream_to_arr(lst_data_in):
    print("#" * 72 + "\n")
    for lin_str in lst_data_in:
        print(lin_str, "\n")

if __name__ == "__main__":
    img_arr = img_arr_gen(25, 50)
    print("img_arr =\n", img_arr)
    plt.imshow(img_arr, interpolation = "nearest")
    plt.show()

    lst_ini_stp = generate_ini_n_steps(5)
    lst_bun = generate_bunches(img_arr, lst_ini_stp)
    from_stream_to_arr(lst_bun)

