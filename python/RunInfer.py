# '''

# Created on Dec. 25, 2017

# @author Andrew Habib

# '''

# import os, shutil, subprocess, sys, tempfile
# from Util import prepare_tool

# def run_infer_on_proj(proj, path, path_out_txt, path_out_json, path_infer):
#     log = open(os.path.join(os.getcwd(), 'inf_log'), 'a')

#     log.write("Runnning Infer on: " + proj + "\n\n")
    
#     _, proj_cp, proj_javac_opts, proj_buggy_files, _ = prepare_tool(path, proj)
    
#     infer_txt_results = []
#     infer_json_results = []
    
#     tmp_out_dir = tempfile.mkdtemp(prefix='infer-out.', dir=os.getcwd())
    
#     for buggy_f in proj_buggy_files:
#         cmd = [path_infer, 'run', '-o', tmp_out_dir, '--keep-going', '--', 'javac']
#         if proj_javac_opts: 
#             cmd = cmd + proj_javac_opts.split(' ') + ['-cp', proj_cp, buggy_f] 
#         else: 
#             cmd = cmd + ['-cp', proj_cp, buggy_f]
               
#         log.write(" ".join(cmd) + "\n\n")
        
#         p = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         (out, _) = p.communicate()
        
#         log.write(out + "\n")
#         log.write("*"*24 + "\n\n")
        
#         try:
#             with open(os.path.join(os.getcwd(), tmp_out_dir + '/bugs.txt'), 'r') as file:
#                 infer_txt_results.append(file.read())
#         except IOError:
#             pass

#         try:
#             with open(os.path.join(os.getcwd(), tmp_out_dir + '/report.json'), 'r') as file:
#                 infer_json_results.append(file.read().strip("\n"))
#         except IOError:
#             pass            

#     shutil.rmtree(tmp_out_dir)
    
#     with open(os.path.join(path_out_txt, proj), 'w') as file:
#         file.write("\n".join(res for res in infer_txt_results))
    
#     with open(os.path.join(path_out_json, proj), 'w') as file:
#         file.write(manual_merge_json(infer_json_results))
     
#     log.write("#"*212 + "\n\n")
#     log.close()

# def manual_merge_json(json_strings):
#     json_strings = [x for x in json_strings if x != "" and x != '[]']
#     length = len(json_strings)
    
#     if length == 1:
#         return json_strings[0]
    
#     if length > 1:
#         for i in range(1, length):
#             json_strings[i] = json_strings[i][1:-1]
#         json_strings[0] = json_strings[0][:-1]
#         json_strings[length - 1] = json_strings[length - 1] + ']'
#         return ",".join(s for s in json_strings)
    
#     return ""
        
# if __name__ == '__main__':
#     path_infer = os.path.join(os.getcwd(), sys.argv[1])
#     path_d4j_projects = os.path.join(os.getcwd(), sys.argv[2])
    
#     path_out_txt = os.path.join(os.getcwd(), 'inf_output_txt')
#     if not os.path.isdir(path_out_txt):
#         os.makedirs(path_out_txt)
        
#     path_out_json = os.path.join(os.getcwd(), 'inf_output_json')
#     if not os.path.isdir(path_out_json):
#         os.makedirs(path_out_json)
    
#     projects = sorted(os.listdir(path_d4j_projects))
    
#     # Use a cmd is_filter to debug specific projects
#     is_filter = False
#     if len(sys.argv) > 4:
#         is_filter = True
#         with open(sys.argv[4]) as file:
#             filter_list = file.read().splitlines()
#     if is_filter:
#         projects = sorted(list(i for i in projects if i in filter_list))
        
#     for p in projects:
#         run_infer_on_proj(p, path_d4j_projects, path_out_txt, path_out_json, path_infer)
    
import argparse, json, pickle
import pandas as pd
from CommitUtil import extract_commits, extract_repo_commit_from_commit_link
from Util import logger

def read_args():
    parser = argparse.ArgumentParser(description='Process JSON data.')
    parser.add_argument('-dataset', help='')
    parser.add_argument('-infer', help='')
    parser.add_argument('-github', help='')
    return parser.parse_args()

def main():
    args = read_args()

    df = pd.read_csv(args.dataset)
    commits = df['human_patch'].tolist()
    user_token = json.load(open(args.github, "r"))
    
    file_level_infos = []
    for commit in commits:
        try:
            repo, _commit = extract_repo_commit_from_commit_link(commit)
            _, repo_files, _ = extract_commits(repo, [_commit], user_token)
            file_level_infos.append((commit, repo_files))
            
        except Exception as e:
            logger(f"Problem while traverse through {repo}: {e}")

    pickle.dump(file_level_infos, open("../outputs/file_level_infos.pkl", 'wb'))

if __name__ == "__main__":
    main()