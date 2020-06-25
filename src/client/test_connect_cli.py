import sys, time, json
import requests

lst_cmd = [
            {"nod_lst":["0"], "cmd_lst":["ip x4"]},
            {"nod_lst":["0"], "cmd_lst":["ip x41"]},
            {"nod_lst":["0"], "cmd_lst":["ip x42"]},
            {'nod_lst': [1], 'cmd_lst':
                 [['gm untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['am input.mask=tmp_mask.pickle']]},
            {'nod_lst': [2], 'cmd_lst':
                 [['gm untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['am input.mask=tmp_mask.pickle']]},
            {'nod_lst': [3], 'cmd_lst':
                 [['gm untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['am input.mask=tmp_mask.pickle']]},
            {"nod_lst":[""], "cmd_lst":["d"]},
            {"nod_lst":["4"], "cmd_lst":["fd nproc=9"]},
            {"nod_lst":["5"], "cmd_lst":["fd nproc=9"]},
            {"nod_lst":["6"], "cmd_lst":["fd nproc=9"]},
            {"nod_lst":[""], "cmd_lst":["d"]},
            {"nod_lst":["7"], "cmd_lst":["id"]},
            {"nod_lst":["8"], "cmd_lst":["id"]},
            {"nod_lst":["9"], "cmd_lst":["id"]},
            {"nod_lst":[""], "cmd_lst":["d"]},
            {"nod_lst":["10","11","12"], "cmd_lst":["ce"]},
            {"nod_lst":["13"], "cmd_lst":["rf"]},
            {"nod_lst":[""], "cmd_lst":["d"]},
            {"nod_lst":["14"], "cmd_lst":["it nproc=3"]},
            {"nod_lst":[""], "cmd_lst":["d"]},
          ]


if __name__ == "__main__":
    for cmd in lst_cmd:
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)
        line_str = ''
        while True:
            tmp_dat = req_get.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                print(line_str[:-1])
                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                print('>>  /*EOF*/  <<')
                break



