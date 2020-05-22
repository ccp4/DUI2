from multi_node import Runner

if __name__ == "__main__":
    lst_cmd = [
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
    "13 it nproc=4"
    ]

    cmd_tree_runner = Runner(None)
    cmd_tree_runner.run("display")

    for cmd_str in lst_cmd:
        cmd_tree_runner.run(cmd_str)
        cmd_tree_runner.run("display")
