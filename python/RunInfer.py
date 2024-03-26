# '''

# Created on Dec. 25, 2017

# @author Andrew Habib

# '''

import os, shutil, subprocess, tempfile
import argparse, os
import pandas as pd
from Util import logger, prepare_tool

def manual_merge_json(json_strings):
    json_strings = [x for x in json_strings if x != "" and x != '[]']
    length = len(json_strings)
    
    if length == 1:
        return json_strings[0]
    
    if length > 1:
        for i in range(1, length):
            json_strings[i] = json_strings[i][1:-1]
        json_strings[0] = json_strings[0][:-1]
        json_strings[length - 1] = json_strings[length - 1] + ']'
        return ",".join(s for s in json_strings)
    
    return ""

def run_infer_on_proj(proj, path, path_out_txt, path_out_json, path_infer):
    log = open('../outputs/inf_log', 'a')

    log.write("Runnning Infer on: " + proj + "\n\n")
    
    _, proj_cp, proj_javac_opts, proj_buggy_files, _ = prepare_tool(path, proj)
    
    infer_txt_results = []
    infer_json_results = []
    
    tmp_out_dir = tempfile.mkdtemp(prefix='infer-out.', dir=os.getcwd())
    
    for buggy_f in proj_buggy_files:
        cmd = [path_infer, 'run', '-o', tmp_out_dir, '--keep-going', '--', 'javac']
        if proj_javac_opts: 
            cmd = cmd + proj_javac_opts.split(' ') + ['-cp', proj_cp, buggy_f] 
        else: 
            cmd = cmd + ['-cp', proj_cp, buggy_f]
               
        log.write(" ".join(cmd) + "\n\n")
        
        p = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, _) = p.communicate()
        
        log.write(out + "\n")
        log.write("*"*24 + "\n\n")
        
        try:
            with open(os.path.join(os.getcwd(), tmp_out_dir + '/bugs.txt'), 'r') as file:
                infer_txt_results.append(file.read())
        except IOError:
            pass

        try:
            with open(os.path.join(os.getcwd(), tmp_out_dir + '/report.json'), 'r') as file:
                infer_json_results.append(file.read().strip("\n"))
        except IOError:
            pass            

    shutil.rmtree(tmp_out_dir)
    
    with open(os.path.join(path_out_txt, proj), 'w') as file:
        file.write("\n".join(res for res in infer_txt_results))
    
    with open(os.path.join(path_out_json, proj), 'w') as file:
        file.write(manual_merge_json(infer_json_results))
     
    log.write("#"*212 + "\n\n")
    log.close()

def read_args():
    parser = argparse.ArgumentParser(description='Process JSON data.')
    parser.add_argument('-dataset', help='')
    parser.add_argument('-infer', help='')
    parser.add_argument('-checkout', help='')
    return parser.parse_args()

def main():
    args = read_args()

    df = pd.read_csv(args.dataset)
    vul_ids = df['vul_id'].tolist()

    path_out_txt = "../outputs/inf_output_txt"
    if not os.path.isdir(path_out_txt):
        os.makedirs(path_out_txt)
        
    path_out_json = "../outputs/inf_output_json"
    if not os.path.isdir(path_out_json):
        os.makedirs(path_out_json)

    for id in vul_ids:
        run_infer_on_proj(id, args.checkout, "../outputs/inf_output_txt", "../outputs/inf_output_json", args.infer)


if __name__ == "__main__":
    main()