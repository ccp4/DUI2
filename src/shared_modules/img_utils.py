import numpy as np
from matplotlib import pyplot as plt
def img_arr_gen(x_size, y_size):
    arr_2d = np.zeros((x_size, y_size), dtype=np.float64)
    xmid = x_size / 2
    ymid = y_size / 2
    for x in range(x_size):
        for y in range(y_size):
            h = abs(xmid - x) + abs(ymid - y)
            arr_2d[x, y] = h

    return arr_2d


if __name__ == "__main__":
    img_arr = img_arr_gen(800, 400)
    print("img_arr =", img_arr)
    plt.imshow(img_arr , interpolation = "nearest")
    plt.show()
