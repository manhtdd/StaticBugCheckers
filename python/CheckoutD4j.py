'''

Created on Dec. 15, 2017

@author Andrew Habib

'''

import os
import subprocess
import sys
from Util import ic

def exec_cmd(cmd):
    p = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd_out, cmd_err = p.communicate()
    ic(cmd_out)
    ic(cmd_err)

def check_out_each_project(d4j_binary, dist, proj, ver, ver_type):
    ic("Checking out:", proj, ver, ver_type)
    ver = str(ver)
    proj_dist = os.path.join(dist, f'{proj}-{ver}')
    
    if not os.path.exists(proj_dist):
        cmd = [d4j_binary, 'checkout', '-p', proj, '-v', ver + ver_type, '-w', proj_dist]
        exec_cmd(cmd)
    else:
        ic(f'{proj_dist} is existed')
    
    ic("Getting properties:", proj, ver, ver_type)
    os.chdir(proj_dist)

    prop_buggy_classes = 'prop-buggy-classes'
    prop_source_dir = 'prop-source-dir'
    prop_compile_path = 'prop-compile-path'
    
    if not os.path.exists(prop_buggy_classes):
        cmd = [d4j_binary, 'export', '-p', 'classes.modified', '-o', prop_buggy_classes]
        exec_cmd(cmd)
    else:
        ic(f'{prop_buggy_classes} is existed')

    if not os.path.exists(prop_source_dir):
        cmd = [d4j_binary, 'export', '-p', 'dir.src.classes', '-o', prop_source_dir]
        exec_cmd(cmd)
    else:
        ic(f'{prop_source_dir} is existed')

    if not os.path.exists(prop_compile_path):
        cmd = [d4j_binary, 'export', '-p', 'cp.compile', '-o', prop_compile_path]
        exec_cmd(cmd)
    else:
        ic(f'{prop_compile_path} is existed')

    ic("Compiling:", proj, ver, ver_type)
    cmd = [d4j_binary, 'compile']
    exec_cmd(cmd)

if __name__ == '__main__':
    
    path_d4j = sys.argv[1] if sys.argv[1].startswith("/") else os.path.join(os.getcwd(), sys.argv[1])
    ver_type = sys.argv[2]
    
    d4j_binary = os.path.join(path_d4j, 'framework/bin/defects4j')
    dist = os.path.join(path_d4j, 'projects', ver_type)
    
    print(dist)
    if not os.path.isdir(dist):
        os.makedirs(dist)
        
    projects = {
        'Chart': [1]
    }

    for proj, list_ids in projects.items():
        for ver in list_ids:
            check_out_each_project(d4j_binary, dist, proj, ver, ver_type)

    print('Done')
