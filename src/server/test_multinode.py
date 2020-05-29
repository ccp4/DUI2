from multi_node import Runner, str2dic

lst_cmd= [
"0 ls",
"0 ls",
"2 ls",
"1 ls",
"1 2 ls",
"5 ls",
"4 ls",
"0 ls",
"0 ls",
"0 ls",
"8 ls",
"9 ls",
"10 ls",
"11 ls",
"12 ls",
"13 ls",
"10 12 14 ls",
"6 ls",
]

lst_dic = [
{'nod_lst': [0], 'cmd_lst': [['ip', 'x4']]},
{'nod_lst': [0], 'cmd_lst': [['ip', 'x41']]},
{'nod_lst': [0], 'cmd_lst': [['ip', 'x42']]},
{'nod_lst': [1], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [2], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [3], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [4], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [5], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [6], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [7], 'cmd_lst': [['id']]},
{'nod_lst': [8], 'cmd_lst': [['id']]},
{'nod_lst': [9], 'cmd_lst': [['id']]},
{'nod_lst': [10, 11, 12], 'cmd_lst': [['ce']]},
{'nod_lst': [13], 'cmd_lst': [['rf']]},
{'nod_lst': [14], 'cmd_lst': [['it', 'nproc=3']]},
]

if __name__ == "__main__":

    cmd_tree_runner = Runner(None)

    cmd_dict = str2dic("display")
    cmd_tree_runner.run(cmd_dict)

    #for cmd_str in lst_cmd:
    for cmd_dict in lst_dic:
        cmd_tree_runner.run(cmd_dict)

        '''
        cmd_dict = str2dic(cmd_str)
        cmd_tree_runner.run(cmd_dict)
        '''

        cmd_dict = str2dic("display")
        cmd_tree_runner.run(cmd_dict)
