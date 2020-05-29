import sys, time, json
import requests

lst_cmd = [
            {
                "lin2go_lst":["0"],
                "cmd_lst":["ip x4"]
            },{
                "lin2go_lst":["1"],
                "cmd_lst":["fd"]
            },{
                "lin2go_lst":["2"],
                "cmd_lst":["id"]
            },{
                "lin2go_lst":["3"],
                "cmd_lst":["rf"]
            },{
                "lin2go_lst":["4"],
                "cmd_lst":["it"]
            },{
                "lin2go_lst":["5"],
                "cmd_lst":["sm"]
            }
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



