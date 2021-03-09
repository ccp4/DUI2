import numpy as np
from matplotlib import pyplot as plt

import time


def img_arr_gen(x_size, y_size):
    arr_2d = np.zeros((x_size, y_size), dtype=np.float64, order='C')
    xmid = x_size / 2
    ymid = y_size / 2
    for x in range(x_size):
        for y in range(y_size):
            h = abs(xmid - x) + abs(ymid - y)
            arr_2d[x, y] = h * 5

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
    arr_str = "x_size, y_size=" + str( (x_size, y_size) )
    lst_data_out.append(arr_str)
    lst_data_out.append("len(lst_ini_stp)=" + str(len(lst_ini_stp)))

    start = time.time()

    #old timing =  2.291943073272705 ############################################

    # mocking loops just to count size of array
    lst_ini_stp_arr = []
    first_loop = True
    for ini_stp in lst_ini_stp:
        ini_stp_arr_s = [ini_stp[0], ini_stp[1]]
        size = 0
        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                size += 1

        ini_stp_arr_s.append(
            np.zeros(size, dtype=np.float64, order='C')
        )

        size = 0
        for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
            for y in range(ini_stp[0], y_size, ini_stp[1]):
                size += 1

        ini_stp_arr_s.append(
            np.zeros(size, dtype=np.float64, order='C')
        )

        size = 0
        for x in range(ini_stp[0], x_size, ini_stp[1]):
            for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                size += 1

        ini_stp_arr_s.append(
            np.zeros(size, dtype=np.float64, order='C')
        )

        size = 0
        if first_loop:
            first_loop = False
            for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
                for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                    size += 1

            ini_stp_arr_s.append(
                np.zeros(size, dtype=np.float64, order='C')
            )
            print("len(ini_stp_arr_s) =", len(ini_stp_arr_s))
        else:
            ini_stp_arr_s.append(None)

        lst_ini_stp_arr.append(ini_stp_arr_s)
    print("len(lst_ini_stp_arr[0]) =", len(lst_ini_stp_arr[0]))
    #print("\n\n lst_ini_stp_arr =", lst_ini_stp_arr, "\n\n")
    #############################################################################

    for ini_stp_arr in lst_ini_stp_arr:
        lst_data_out.append("ini_stp=" + str(ini_stp_arr[0:2]))
        lst_data_out.append("I(x,y)=")
        # This 4 double connected loops need to be reproduced
        # just identically in the client side
        pos = 0
        for x in range(ini_stp_arr[0], x_size, ini_stp_arr[1]):
            for y in range(ini_stp_arr[0], y_size, ini_stp_arr[1]):
                ini_stp_arr[2][pos] = arr_in[x, y]
                pos += 1

        lst_data_out.append(ini_stp_arr[2])

        lst_data_out.append("ini_stp=" + str(ini_stp_arr[0:2]))
        lst_data_out.append("I(x+u/2,y)=")
        pos = 0
        for x in range(int(ini_stp_arr[0] * 2), x_size, ini_stp_arr[1]):
            for y in range(ini_stp_arr[0], y_size, ini_stp_arr[1]):
                ini_stp_arr[3][pos] = arr_in[x, y]
                pos += 1

        lst_data_out.append(ini_stp_arr[3])

        lst_data_out.append("ini_stp=" + str(ini_stp_arr[0:2]))
        lst_data_out.append("I(x,y+u/2)=")
        pos = 0
        for x in range(ini_stp_arr[0], x_size, ini_stp_arr[1]):
            for y in range(int(ini_stp_arr[0] * 2), y_size, ini_stp_arr[1]):
                ini_stp_arr[4][pos] = arr_in[x, y]
                pos += 1

        lst_data_out.append(ini_stp_arr[4])

        if ini_stp_arr[5] is not None:
            lst_data_out.append("ini_stp=" + str(ini_stp_arr[0:2]))
            lst_data_out.append("I(x+u/2,y+u/2)=")
            pos = 0
            for x in range(int(ini_stp_arr[0] * 2), x_size, ini_stp_arr[1]):
                for y in range(int(ini_stp_arr[0] * 2), y_size, ini_stp_arr[1]):
                    ini_stp_arr[5][pos] = arr_in[x, y]
                    pos += 1

            lst_data_out.append(ini_stp_arr[5])

        else:
            lst_data_out.append("I(x+u/2,y+u/2)=None")

    y_row = arr_in[0, 0:y_size]
    x_col = arr_in[0:x_size, 0]

    lst_data_out.append("I(0,:)=")
    lst_data_out.append(y_row)

    lst_data_out.append("I(:,0)=")
    lst_data_out.append(x_col)

    end = time.time()
    print("timing = ", end - start)

    '''
    print("\n *********** \n lst_data_out =\n")
    for single_line in lst_data_out:
        print(single_line)
    '''

    return lst_data_out


def str2tup(str_in):
    cut_str = str_in[1:-1]
    #print("str_in(cut) =", cut_str)
    lst_str = cut_str.split(",")
    tmp_lst_num = []
    for singl_str in lst_str:
        tmp_lst_num.append(int(singl_str))

    return tuple(tmp_lst_num)


def from_stream_to_arr(lst_data_in):
    print("#" * 72 + "\n")
    #for lin_str in lst_data_in:
    #    print(lin_str, "\n")

    print("#" * 72 + "\n")

    lin1 = lst_data_in[0]
    if lin1[0:15] == "x_size, y_size=":
        print("lin1 OK")
        tup_str = lin1[15:]
        print("tup_str =", tup_str)
        tup_dat = str2tup(tup_str)
        x_size = tup_dat[0]
        y_size = tup_dat[1]
        img_i_2d = np.zeros(
                (x_size, y_size), dtype=np.float64, order='C'
            )

    else:
        print(" *** ERROR #1 *** ")
        print("lin1 =", lin1)
        return

    lin2 = lst_data_in[1]
    if lin2[0:17] == "len(lst_ini_stp)=":
        lst_len = int(lin2[17:])
        pos_lst = 2
        for times in range(lst_len):
            print("times =", times)
            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            if lin_n_str[0:9] == "ini_stp=[":
                ini_stp = str2tup(lin_n_str[8:])

            else:
                print(" *** ERROR #3 *** ")
                print("lin_n_str =", lin_n_str)
                return

            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            #print("lin_n_str =", lin_n_str)
            if lin_n_str == "I(x,y)=":
                dat_arr = lst_data_in[pos_lst]
                pos_lst += 1

            else:
                print(" *** ERROR #4 *** ")
                print("lin_n_str =", lin_n_str)
                return

            if len(dat_arr) > 0:
                arr_pos = 0
                for x in range(ini_stp[0], x_size, ini_stp[1]):
                    for y in range(ini_stp[0], y_size, ini_stp[1]):
                        i = float(dat_arr[arr_pos])
                        arr_pos += 1
                        img_i_2d[x-ini_stp[0] + 1:x + 1, y-ini_stp[0] + 1:y + 1] = i

            ########################################################################
            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            if lin_n_str[0:9] == "ini_stp=[":
                #print("lin_n_str =", lin_n_str)
                ini_stp = str2tup(lin_n_str[8:])

            else:
                print(" *** ERROR #5 *** ")
                print("lin_n_str =", lin_n_str)
                return

            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            #print("lin_n_str =", lin_n_str)
            if lin_n_str == "I(x+u/2,y)=":
                dat_arr = lst_data_in[pos_lst]
                pos_lst += 1

            else:
                print(" *** ERROR #6 *** ")
                print("lin_n_str =", lin_n_str)
                return

            if len(dat_arr) > 0:
                arr_pos = 0
                for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
                    for y in range(ini_stp[0], y_size, ini_stp[1]):
                        i = float(dat_arr[arr_pos])
                        arr_pos += 1
                        img_i_2d[x-ini_stp[0] + 1:x + 1, y-ini_stp[0] + 1:y + 1] = i

            #######################################################################
            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            if lin_n_str[0:9] == "ini_stp=[":
                #print("lin_n_str =", lin_n_str)
                ini_stp = str2tup(lin_n_str[8:])

            else:
                print(" *** ERROR #7 *** ")
                print("lin_n_str =", lin_n_str)
                return

            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            #print("lin_n_str =", lin_n_str)
            if lin_n_str == "I(x,y+u/2)=":
                dat_arr = lst_data_in[pos_lst]
                pos_lst += 1

            else:
                print(" *** ERROR #8 *** ")
                print("lin_n_str =", lin_n_str)
                return

            if len(dat_arr) > 0:
                arr_pos = 0
                for x in range(ini_stp[0], x_size, ini_stp[1]):
                    for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                        i = float(dat_arr[arr_pos])
                        arr_pos += 1
                        img_i_2d[x-ini_stp[0] + 1:x + 1, y-ini_stp[0] + 1:y + 1] = i

            #######################################################################

            lin_n_str = lst_data_in[pos_lst]
            pos_lst += 1
            if lin_n_str[0:9] == "ini_stp=[":
                #print("lin_n_str =", lin_n_str)
                ini_stp = str2tup(lin_n_str[8:])

                lin_n_str = lst_data_in[pos_lst]
                pos_lst += 1
                #print("lin_n_str =", lin_n_str)
                if lin_n_str == "I(x+u/2,y+u/2)=":
                    dat_arr = lst_data_in[pos_lst]
                    pos_lst += 1

                else:
                    print(" *** ERROR #9 *** ")
                    print("lin_n_str =", lin_n_str)
                    return

                if len(dat_arr) > 0:
                    arr_pos = 0
                    for x in range(int(ini_stp[0] * 2), x_size, ini_stp[1]):
                        for y in range(int(ini_stp[0] * 2), y_size, ini_stp[1]):
                            i = float(dat_arr[arr_pos])
                            arr_pos += 1
                            img_i_2d[x-ini_stp[0] + 1:x + 1, y-ini_stp[0] + 1:y + 1] = i

            elif lin_n_str == "I(x+u/2,y+u/2)=None":
                print("skipping I(x+u/2,y+u/2)")

            else:
                print(" *** ERROR #7 *** ")
                print("lin_n_str =", lin_n_str)
                return

            #######################################################################

            plt.imshow(img_i_2d, interpolation = "nearest")
            plt.show()

        lin_n_str = lst_data_in[pos_lst]
        pos_lst += 1
        if lin_n_str == "I(0,:)=":
            dat_arr = lst_data_in[pos_lst]
            pos_lst += 1

        for y, i in enumerate(dat_arr):
            img_i_2d[0, y] = float(i)

        lin_n_str = lst_data_in[pos_lst]
        pos_lst += 1
        if lin_n_str == "I(:,0)=":
            dat_arr = lst_data_in[pos_lst]
            pos_lst += 1

        for x, i in enumerate(dat_arr):
            img_i_2d[x, 0] = float(i)

        plt.imshow(img_i_2d, interpolation = "nearest")
        plt.show()

    else:
        print(" *** ERROR #2 *** ")
        print("lin2 =", lin2)
        return


if __name__ == "__main__":
    img_arr = img_arr_gen(250, 350)
    #img_arr = img_arr_gen(1500, 3500)
    plt.imshow(img_arr, interpolation = "nearest")
    plt.show()
    lst_ini_stp = generate_ini_n_steps(6)
    lst_bun = generate_bunches(img_arr, lst_ini_stp)
    from_stream_to_arr(lst_bun)

