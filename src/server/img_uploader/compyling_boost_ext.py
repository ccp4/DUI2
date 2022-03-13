#from subprocess import call as shell_call

from subprocess import PIPE, run

from distutils import sysconfig
import scitbx

obj_name = "img_stream_ext"
py_inc_path = sysconfig.get_python_inc()
print("\n sysconfig.get_python_inc() =", py_inc_path)
for pos, single_shar in enumerate(py_inc_path):
    if(single_shar == "/" ):
        cut_py_inc_path = py_inc_path[0:pos]

scitbx_path = scitbx.__path__[0]
print("\n scitbx_path =", scitbx_path)
cut_scitbx_path = scitbx_path[0:-6]
print("cut_scitbx_path =", cut_scitbx_path)

dict_conf_vars = sysconfig.get_config_vars()
print("\n", dict_conf_vars["prefix"])
prefix_path = dict_conf_vars["prefix"]
cut_prefix = prefix_path[0:-10]
print("cut_prefix =", cut_prefix)
inc_path = cut_prefix + "build/include"
print("inc_path =", inc_path)

com_lin_01 = "g++ -I" + py_inc_path \
    + " -I" + cut_py_inc_path +  " -fPIC -c " \
    + " -I" + cut_scitbx_path \
    + " -I" + inc_path \
    + " " + obj_name + ".cpp"

lib_path = sysconfig.get_python_lib()

for pos, single_shar in enumerate(lib_path):
    if(single_shar == "/" ):
        cut_lib_path = lib_path[0:pos]

for pos, single_shar in enumerate(cut_lib_path):
    if(single_shar == "/" ):
        cut_cut_lib_path = cut_lib_path[0:pos]

python_3_p_8 = '''
com_lin_02 = "g++ -shared " + obj_name + ".o -L" +   \
    cut_cut_lib_path + " -lboost_python38 -L" +      \
    cut_lib_path + "/config -lpython3.8 -o " + obj_name + ".so"
'''

com_lin_02 = "g++ -shared " + obj_name + ".o -L" +   \
    cut_cut_lib_path + " -lboost_python39 -L" +      \
    cut_lib_path + "/config -lpython3.9 -o " + obj_name + ".so"

print("\n Compiling Line 1:")
print("cmd =", com_lin_01)

result1 = run(
    com_lin_01, shell=True,
    stdout=PIPE, stderr=PIPE,
    universal_newlines=True
)
print("\n Line 1 (returncode) =", result1.returncode)

#################################################################

print("\n Compiling Line 2:")
print("cmd =", com_lin_02)

result2 = run(
    com_lin_02, shell=True,
    stdout=PIPE, stderr=PIPE,
    universal_newlines=True
)
print("\n Line 2 (returncode) =", result2.returncode)

if(result1.returncode != 0 or result2.returncode !=0 ):

    print("\n result1.stdout =", result1.stdout)
    print("\n result1.stderr =", result1.stderr)

    print("\n result2.stdout =", result2.stdout)
    print("\n result2.stderr =", result2.stderr)
    print("\n")
    print("*********************************************")
    print("*                                           *")
    print("*                  ERROR                    *")
    print("*   Failed to compile some C++ extensions   *")
    print("*                                           *")
    print("*********************************************")
    print("\n")

else:
    print("\n Done compiling")
