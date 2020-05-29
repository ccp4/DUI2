import sys, time, json
import requests

lst_cmd = [
            {"lin2go_lst":["0"], "cmd_lst":["ip x4"]},
            {"lin2go_lst":["0"], "cmd_lst":["ip x41"]},
            {"lin2go_lst":["0"], "cmd_lst":["ip x42"]},
            {'lin2go_lst': [1], 'cmd_lst':
                 [['dials.generate_mask untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['dials.apply_mask input.mask=tmp_mask.pickle']]},
            {'lin2go_lst': [2], 'cmd_lst':
                 [['dials.generate_mask untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['dials.apply_mask input.mask=tmp_mask.pickle']]},
            {'lin2go_lst': [3], 'cmd_lst':
                 [['dials.generate_mask untrusted.rectangle=0,1421,1258,1312 output.mask=tmp_mask.pickle'],
                  ['dials.apply_mask input.mask=tmp_mask.pickle']]},
            {"lin2go_lst":[""], "cmd_lst":["d"]},
            {"lin2go_lst":["4"], "cmd_lst":["fd nproc=9"]},
            {"lin2go_lst":["5"], "cmd_lst":["fd nproc=9"]},
            {"lin2go_lst":["6"], "cmd_lst":["fd nproc=9"]},
            {"lin2go_lst":[""], "cmd_lst":["d"]},
            {"lin2go_lst":["7"], "cmd_lst":["id"]},
            {"lin2go_lst":["8"], "cmd_lst":["id"]},
            {"lin2go_lst":["9"], "cmd_lst":["id"]},
            {"lin2go_lst":[""], "cmd_lst":["d"]},
            {"lin2go_lst":["10","11","12"], "cmd_lst":["ce"]},
            {"lin2go_lst":["13"], "cmd_lst":["rf"]},
            {"lin2go_lst":[""], "cmd_lst":["d"]},
            {"lin2go_lst":["14"], "cmd_lst":["it nproc=3"]},
          ]


if __name__ == "__main__":
    for cmd in lst_cmd:
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)
        str_lst = []
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



