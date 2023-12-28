import argparse
import json
from Util import ic
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        ic(f"Error: File not found at path '{file_path}'")
    except json.JSONDecodeError:
        ic(f"Error: Invalid JSON format in file '{file_path}'")

def read_args():
    parser = argparse.ArgumentParser(description='Load JSON file from a given path.')

    parser.add_argument('-ep_diffs_warnings', type=str, help='Path to the JSON file')
    parser.add_argument('-inf_diffs_warnings', type=str, help='Path to the JSON file')
    parser.add_argument('-sb_diffs_warnings', type=str, help='Path to the JSON file')

    parser.add_argument('-ep_removed_warnings', type=str, help='Path to the JSON file')
    parser.add_argument('-inf_removed_warnings', type=str, help='Path to the JSON file')
    parser.add_argument('-sb_removed_warnings', type=str, help='Path to the JSON file')

    args = parser.parse_args()
    return args

def get_detected_bugs(diff_warnings, removed_warnings, proj_key, warning_key):
    detected_bugs = {}
    no_warnings = []

    for warning in diff_warnings:

        if warning[proj_key] in detected_bugs:
            detected_bugs[warning[proj_key]].append(warning)
        else:
            detected_bugs[warning[proj_key]] = [warning]

    for warning in removed_warnings:

        if warning[warning_key] == "NO_WARNING":
            no_warnings.append(warning)
        else:
            if warning[proj_key] in detected_bugs:
                detected_bugs[warning[proj_key]].append(warning)
            else:
                detected_bugs[warning[proj_key]] = [warning]

    return detected_bugs, no_warnings

def keys_intersect(*dictionaries):
    if not all(isinstance(d, dict) for d in dictionaries):
        raise ValueError("All arguments must be dictionaries.")

    # Get the keys of each dictionary
    keys_sets = [set(d.keys()) for d in dictionaries]

    # Find the intersection of key sets
    intersection_keys = set.intersection(*keys_sets)

    return intersection_keys

def plot_venn(*sets, set_labels=None, title=None, filename=None):
    if len(sets) < 2 or len(sets) > 3:
        raise ValueError("This function supports 2 or 3 sets only.")

    if not all(isinstance(s, set) for s in sets):
        raise ValueError("All arguments must be sets.")

    if set_labels is None:
        set_labels = [f"Set {i+1}" for i in range(len(sets))]

    if title is None:
        title = f"Venn Diagram for {len(sets)} Sets"

    if len(sets) == 2:
        venn_function = venn2
    else:
        venn_function = venn3

    venn_function(subsets=tuple(sets), set_labels=set_labels)

    plt.title(title)

    if filename:
        plt.savefig(filename)
    else:
        plt.show()


def main():
    args = read_args()

    ep_diffs_warnings = load_json(args.ep_diffs_warnings)
    inf_diffs_warnings = load_json(args.inf_diffs_warnings)
    sb_diffs_warnings = load_json(args.sb_diffs_warnings)

    ep_removed_warnings = load_json(args.ep_removed_warnings)
    inf_removed_warnings = load_json(args.inf_removed_warnings)
    sb_removed_warnings = load_json(args.sb_removed_warnings)

    ep_detected_bugs, ep_no_warnings = get_detected_bugs(ep_diffs_warnings, ep_removed_warnings, " Proj", "  Cat")
    inf_detected_bugs, inf_no_warnings = get_detected_bugs(inf_diffs_warnings, inf_removed_warnings, "      Proj", "  Bug_Type")
    sb_detected_bugs, sb_no_warnings = get_detected_bugs(sb_diffs_warnings, sb_removed_warnings, "    Proj", "    Type")

    ic(len(ep_detected_bugs.keys()))
    ic(len(inf_detected_bugs.keys()))
    ic(len(sb_detected_bugs.keys()))

    ic(len(ep_no_warnings))
    ic(len(inf_no_warnings))
    ic(len(sb_no_warnings))

    ep_inf = keys_intersect(ep_detected_bugs, inf_detected_bugs)
    sb_inf = keys_intersect(sb_detected_bugs, inf_detected_bugs)
    ep_sb = keys_intersect(ep_detected_bugs, sb_detected_bugs)

    ep_inf_sb = keys_intersect(ep_detected_bugs, sb_detected_bugs, inf_detected_bugs)

    ic(len(ep_inf))
    ic(len(sb_inf))
    ic(len(ep_sb))
    ic(len(ep_inf_sb))

    plot_venn(set(ep_detected_bugs.keys()),
              set(inf_detected_bugs.keys()),
              set(sb_detected_bugs.keys()),
              set_labels=('Error Prone', 'Infer', 'SpotBugs'),
              title="Total number of bugs found by all three static checkers and their overlap",
              filename='results_no_warning')

if __name__ == "__main__":
    main()
