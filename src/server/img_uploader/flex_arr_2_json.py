try:
    from img_uploader import img_stream_ext

except ImportError:
    import img_stream_ext


import numpy as np
from dials.array_family import flex
import json
import time
from dxtbx.model.experiment_list import ExperimentListFactory

def get_json(experiments_list_path, img_num):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)
    my_sweep = experiments.imagesets()[0]
    print("geting image #", img_num)
    data_xy_flex = my_sweep.get_raw_data(img_num)[pan_num].as_double()
    start_tm = time.time()
    str_data = img_stream_ext.img_arr_2_str(data_xy_flex)
    end_tm = time.time()
    print("C++ bit took ", end_tm - start_tm)

    return str_data


