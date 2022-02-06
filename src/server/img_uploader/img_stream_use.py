import img_stream_ext
import numpy as np
from dials.array_family import flex
from matplotlib import pyplot as plt
import json
import time
import zlib
import pickle

from dxtbx.datablock import DataBlockFactory
from dxtbx.model import Experiment, ExperimentList
from dxtbx.model.experiment_list import (
    ExperimentListFactory,
    InvalidExperimentListError,
)

def draw_pyplot(img_arr):
    plt.imshow(img_arr, interpolation = "nearest")
    plt.show()


def save_json_w_str(flex_array_in, inv_scale, x1, y1, x2, y2):
    start_tm = time.time()
    str_data = img_stream_ext.slice_mask_2_str(
        flex_array_in, inv_scale, x1, y1, x2, y2
    )
    byt_data = bytes(str_data.encode('utf-8'))
    byt_data = zlib.compress(byt_data)
    end_tm = time.time()
    print("C++ and compressing took ", end_tm - start_tm)
    print("str_data[0:80] =", str_data[0:80])
    print("str_data[-80:] =", str_data[-80:])

    with open("arr_img.json.zip", 'wb') as file_out:
        file_out.write(byt_data)


def load_json_w_str():
    with open("arr_img.json.zip", 'rb') as json_file:
        compresed = json_file.read()

    dic_str = zlib.decompress(compresed)
    arr_dic = json.loads(dic_str)

    d1 = arr_dic["d1"]
    d2 = arr_dic["d2"]
    str_data = arr_dic["str_data"]
    print("d1, d2 =", d1, d2)

    n_tup = tuple(str_data)
    arr_1d = np.asarray(n_tup, dtype = 'float')

    np_array_out = arr_1d.reshape(d1, d2)
    return np_array_out


if __name__ == "__main__":

    experiments_path = "/scratch/dui_tst/dui_server_run/run2/masked.expt"
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

    imageset_tmp = experiments.imagesets()[0]
    mask_file = imageset_tmp.external_lookup.mask.filename

    pick_file = open(mask_file, "rb")
    mask_tup_obj = pickle.load(pick_file)
    pick_file.close()

    mask_flex = mask_tup_obj[0]
    save_json_w_str(mask_flex, 5, 850, 1000, 950, 1200)

    loaded_array = load_json_w_str()
    print("drawing")
    draw_pyplot(loaded_array)





