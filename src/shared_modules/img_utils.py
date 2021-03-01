import numpy as np

def img_arr_gen(x_size, y_size):
    arr_2d = np.zeros((x_size, y_size), dtype=np.float64)
    return arr_2d


if __name__ == "__main__":
    img_arr = img_arr_gen(80, 40)
    print("img_arr =", img_arr)
