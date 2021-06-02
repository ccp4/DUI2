import img_stream_ext
import numpy as np
from dials.array_family import flex
from matplotlib import pyplot as plt
import json
import time
from dxtbx.model.experiment_list import ExperimentListFactory


def draw_pyplot(img_arr):
    plt.imshow(img_arr, interpolation = "nearest")
    plt.show()

def save_json_w_str(flex_array_in):
    d1, d2 = flex_array_in.all()
    print("d1, d2 =", d1, d2)
    start_tm = time.time()
    str_data = img_stream_ext.img_arr_2_str(flex_array_in)
    end_tm = time.time()
    print("C++ bit took ", end_tm - start_tm)

    #print("str_data =", str_data)
    arr_dic = {"d1": d1, "d2": d2, "str_data": str_data}
    #print("\narr_dic =", arr_dic)

    print("saving in json file")
    with open("arr_img.json", "w") as fp:
        json.dump(arr_dic, fp, indent=4)

if __name__ == "__main__":
    experiments_path = "/scratch/dui_tst/dui_server_run/run1/imported.expt"
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)
    my_sweep = experiments.imagesets()[0]
    data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
    print("type(data_xy_flex) =", type(data_xy_flex))
    print("data_xy_flex.all() =", data_xy_flex.all())

    save_json_w_str(data_xy_flex)


