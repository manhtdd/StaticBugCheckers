import argparse, subprocess, shutil, os, json
import pandas as pd
from Util import copy_files, logger
import subprocess

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', help='')
    return parser.parse_args()

def main():
    args = read_args()

    df = pd.read_csv(args.dataset)
    vul4j_ids = df['vul_id'].tolist()

    for id in vul4j_ids:
        cmd = ["vul4j", "checkout", "--id", id, "-d", f"/tmp/vul4j/vul/{id}"]
        subprocess.run(cmd)

    if not os.path.exists("/tmp/vul4j/fix"):
        shutil.copytree("/tmp/vul4j/vul", "/tmp/vul4j/fix")

    # Iterate over directories in /tmp/vul4j/fix/*/VUL4J/human_patch
    for root, dirs, files in os.walk("/tmp/vul4j/fix"):
        for dir_name in dirs:
            logger(dir_name)
            human_patch_dir = os.path.join(root, dir_name, 'VUL4J', 'human_patch')
            paths_json_file = os.path.join(human_patch_dir, 'paths.json')
            
            # Check if paths.json exists
            if os.path.exists(paths_json_file):
                # Read paths.json
                paths_dict = json.load(open(paths_json_file, 'r'))
                
                # Copy files
                copy_files(human_patch_dir, f"/tmp/vul4j/fix/{dir_name}", paths_dict)
        break

if __name__ == "__main__":
    main()