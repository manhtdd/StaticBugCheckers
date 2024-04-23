# '''

# Created on Dec. 25, 2017

# @author Andrew Habib

# '''

import os, shutil, subprocess, tempfile, json
import argparse, os
import pandas as pd
from Util import logger
from os.path import expanduser
import math

JAVA7_HOME = os.environ.get("JAVA7_HOME", expanduser("/Library/Java/JavaVirtualMachines/jdk1.7.0_80.jdk/Contents/Home"))
JAVA8_HOME = os.environ.get("JAVA8_HOME", expanduser("/Library/Java/JavaVirtualMachines/jdk1.8.0_281.jdk/Contents/Home"))
MVN_OPTS = os.environ.get("MVN_OPTS", "-Xmx4g -Xms1g -XX:MaxPermSize=512m")
INFER_PATH = "/StaticBugCheckers/static-checkers/infer-linux64-v1.0.0/bin/infer"

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

def run_infer_on_proj(dataframe, result_df, path_out_txt, path_out_json, args):
    log_capture = open(f'outputs/{"output-fixed" if args.fix else "output-buggy"}/inf_capture_log', 'a')
    log_analyze = open(f'outputs/{"output-fixed" if args.fix else "output-buggy"}/inf_analyze_log', 'a')
    row_list = []
    ran_list = result_df['vul_id'].to_list()
    
    for _, row in dataframe.iterrows():
        proj = row['vul_id']

        if proj in ran_list:
            continue

        analyze_row = {'vul_id': proj}

        print("Runnning Infer on: " + proj)
        log_capture.write("Runnning Infer on: " + proj + "\n\n")
        log_analyze.write("Runnning Infer on: " + proj + "\n\n")

        paths_dict = json.load(open(f"{args.checkout}/{proj}/VUL4J/human_patch/paths.json", 'r'))
        proj_buggy_files = list(paths_dict.values())

        proj_dir = f"{args.checkout}/{proj}"
        index_path = f"{proj_dir}/index.txt"

        # Writing to the file
        with open(index_path, 'w') as file:
            for path in proj_buggy_files:
                file.write(str(path) + '\n')

        with open(index_path, 'r') as file:
            for line in file:
                logger(line.strip())
            logger()

        infer_txt_results = []
        infer_json_results = []

        tmp_out_dir = tempfile.mkdtemp(prefix='infer-out.', dir=os.getcwd())

        java_home = JAVA7_HOME if row['compliance_level'] <= 7 else JAVA8_HOME

        package_command = 'mvn -DskipTests clean package' if row['build_system'] == 'Maven' else './gradlew clean assemble'

        cmd = """export JAVA_HOME="%s"; export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; export MAVEN_OPTS="%s"; %s capture -- %s;""" % (java_home, MVN_OPTS, INFER_PATH, package_command)

        # cmd = [f"export JAVA_HOME=\"{java_home}\";",
        #        "export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;",
        #        f"export MAVEN_OPTS=\"{MVN_OPTS}\";",
        #        f"{INFER_PATH} capture -- {package_command};"]

        cmd_options = row['cmd_options']
        if not isinstance(cmd_options, str) and not math.isnan(cmd_options):
            cmd = cmd[:-1]  # remove comma
            cmd += " " + cmd_options + ';'

        # Capture phase
        log_capture.write(cmd + "\n\n")
        
        p = subprocess.Popen(cmd, cwd=proj_dir, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, _) = p.communicate()

        analyze_row['Capture'] = "BUILD FAILURE" if "BUILD SUCCESS" not in out else "BUILD SUCCESS"

        log_capture.write(out + "\n")
        log_capture.write("*"*24 + "\n\n")

        # Analyze phase
        cmd = f"{INFER_PATH} analyze --changed-files-index index.txt"

        log_analyze.write(cmd + "\n\n")

        p = subprocess.Popen(cmd, cwd=proj_dir, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out, _) = p.communicate()

        analyze_row['Analyze'] = "No issues found" if "No issues found" in out else "There are issues"
        
        log_analyze.write(out + "\n")
        log_analyze.write("*"*24 + "\n\n")
        
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

        log_capture.write("#"*212 + "\n\n")    
        log_analyze.write("#"*212 + "\n\n")

        row_list.append(analyze_row)
        _dataframe = pd.DataFrame.from_records(row_list)
        _dataframe.to_csv("outputs/results.csv", index=None)

    log_capture.close()
    log_analyze.close()

def read_args():
    parser = argparse.ArgumentParser(description='Process JSON data.')
    parser.add_argument('-dataset', help='')
    parser.add_argument('-result', help='')
    parser.add_argument('-infer', help='')
    parser.add_argument('-checkout', help='')
    parser.add_argument('-fix', action='store_true', help='')
    return parser.parse_args()

def main():
    args = read_args()

    if args.fix:
        output_folder = 'output-fixed'
    else:
        output_folder = 'output-buggy'

    df = pd.read_csv(args.dataset)
    try:
        result_df = pd.read_csv(args.result)
    except:
        result_df = pd.DataFrame(columns=["vul_id"])

    path_out_txt = f"outputs/{output_folder}/inf_output_txt"
    if not os.path.isdir(path_out_txt):
        os.makedirs(path_out_txt)
        
    path_out_json = f"outputs/{output_folder}/inf_output_json"
    if not os.path.isdir(path_out_json):
        os.makedirs(path_out_json)

    run_infer_on_proj(df, result_df, path_out_txt, path_out_json, args)


if __name__ == "__main__":
    main()