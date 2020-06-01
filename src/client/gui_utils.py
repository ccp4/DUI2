old_graph = '''
status: (R)eady  (B)usy  (F)ailed  (S)ucceeded
 |
 |  line number
 |   |
 |   |    command --->
--------------------------
 S   \_(0)                                   | Root
 S       \_(1)                               | ls
 S       |   \_(4)                           | ls
 S       |       \_(7) ``\```\```\           | ls
 S       |       \_(10)``\```\```\           | ls
 S       |       \_(11)  :   :   :           | ls
 S       |       \_(12)  :   :   :           | ls
 S       \_(2)           :   :   :           | ls
 S       |   \_(5)       :   :   :           | ls
 S       |       \_(8) ``\```\```\           | ls
 S       |       \_(13)``\```\```\           | ls
 S       |       \_(14)  :   :   :           | ls
 S       \_(3)           :   :   :           | ls
 S       |   \_(6)       :   :   :           | ls
 S       |       \_(9)   :   :   :           | ls
 S       |       \_(15)  :   :   :           | ls
 S       |           \_(16)  :   :           | ls,  parents:[7, 10, 8, 13, 15]
 S       |           \_____(17)  :           | ls,  parents:[7, 10, 8, 13, 15]
 S       |           \_________(18)          | ls,  parents:[15, 13, 8, 10, 7]
 F       \_(19)                              | 0
 R       \_(20)                              | None
----------------------------------------------------
'''

nod_lst = [
{"lin_num": 0, "status": "Succeeded", "cmd2show": ["Root"], "child_node_lst": [1, 2, 3, 19, 20], "parent_node_lst": []},
{"lin_num": 1, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [4], "parent_node_lst": [0]},
{"lin_num": 2, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [5], "parent_node_lst": [0]},
{"lin_num": 3, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [6], "parent_node_lst": [0]},
{"lin_num": 4, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [7, 10, 11, 12], "parent_node_lst": [1]},
{"lin_num": 5, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [8, 13, 14], "parent_node_lst": [2]},
{"lin_num": 6, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [9, 15], "parent_node_lst": [3]},
{"lin_num": 7, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 8, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 9, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [6]},
{"lin_num": 10, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 11, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 12, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 13, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 14, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [5]},
{"lin_num": 15, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [6]},
{"lin_num": 16, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 17, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 18, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [15, 13, 8, 10, 7]},
{"lin_num": 19, "status": "Failed", "cmd2show": ["0", "ls"], "child_node_lst": [], "parent_node_lst": [0]},
{"lin_num": 20, "status": "Ready", "cmd2show": ["None"], "child_node_lst": [], "parent_node_lst": [0]}
]

if __name__ == "__main__":
    for node in nod_lst:
        print(node)

