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

if __name__ == "__main__":

    cmd_tree_runner = Runner(None)

    cmd_dict = str2dic("display")
    cmd_tree_runner.run(cmd_dict)

    # swap lst_cmd1 with lst_cmd2 to select test
    for cmd_str in lst_cmd2:

        cmd_dict = str2dic(cmd_str)
        cmd_tree_runner.run(cmd_dict)

        cmd_dict = str2dic("display")
        cmd_tree_runner.run(cmd_dict)
