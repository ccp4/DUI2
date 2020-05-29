from multi_node import Runner, str2dic

lst_cmd1= [
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

lst_cmd2 = [
"0 ip x4",
"0 ip x41",
"0 ip x42",
"1 fd nproc=9",
"2 fd nproc=9",
"3 fd nproc=9",
"4 id",
"5 id",
"6 id",
"7 rf",
"8 rf",
"9 rf",
"10 11 12 ce",
"13 it nproc=4",
"14 sm",
]

lst_dic = [
{'lin2go_lst': [0], 'cmd_lst': [['ip', 'x4']]},
{'lin2go_lst': [0], 'cmd_lst': [['ip', 'x41']]},
{'lin2go_lst': [0], 'cmd_lst': [['ip', 'x42']]},
{'lin2go_lst': [1], 'cmd_lst': [['dials.generate_mask', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['dials.apply_mask', 'input.mask=tmp_mask.pickle']]},
{'lin2go_lst': [2], 'cmd_lst': [['dials.generate_mask', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['dials.apply_mask', 'input.mask=tmp_mask.pickle']]},
{'lin2go_lst': [3], 'cmd_lst': [['dials.generate_mask', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['dials.apply_mask', 'input.mask=tmp_mask.pickle']]},
{'lin2go_lst': [4], 'cmd_lst': [['fd', 'nproc=9']]},
{'lin2go_lst': [5], 'cmd_lst': [['fd', 'nproc=9']]},
{'lin2go_lst': [6], 'cmd_lst': [['fd', 'nproc=9']]},
{'lin2go_lst': [7], 'cmd_lst': [['id']]},
{'lin2go_lst': [8], 'cmd_lst': [['id']]},
{'lin2go_lst': [9], 'cmd_lst': [['id']]},
{'lin2go_lst': [10, 11, 12], 'cmd_lst': [['ce']]},
{'lin2go_lst': [13], 'cmd_lst': [['rf']]},
{'lin2go_lst': [14], 'cmd_lst': [['it', 'nproc=3']]},
]

#{'lin2go_lst': [], 'cmd_lst': [['display']]}

if __name__ == "__main__":

    cmd_tree_runner = Runner(None)

    cmd_dict = str2dic("display")
    cmd_tree_runner.run(cmd_dict)

    # swap lst_cmd1 with lst_cmd2 to select test
    #for cmd_str in lst_cmd2:
    for cmd_dict in lst_dic:
        cmd_tree_runner.run(cmd_dict)

        '''
        cmd_dict = str2dic(cmd_str)
        cmd_tree_runner.run(cmd_dict)
        '''

        cmd_dict = str2dic("display")
        cmd_tree_runner.run(cmd_dict)
