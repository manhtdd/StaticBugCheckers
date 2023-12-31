'''

Created on Nov. 23, 2017

@author Andrew Habib

'''

import json
import os

from collections import OrderedDict, namedtuple
from xml.etree import cElementTree as ET
from icecream import ic
from datetime import datetime

if not os.path.exists(f'{os.getcwd()}/logs'):
    os.makedirs(f'{os.getcwd()}/logs')

# Define a file to log IceCream output
log_file_path = os.path.join(f'{os.getcwd()}/logs', 'logs.log')

# Replace logging configuration with IceCream configuration
ic.configureOutput(prefix=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | ', outputFunction=lambda x: open(log_file_path, 'a').write(x + '\n'))


class DataReader(object):

    def __init__(self, data_paths):
        self.data_paths = data_paths
        
    def __iter__(self):
        for data_path in self.data_paths:
            name = os.path.split(data_path)[1]
            with open(data_path, 'r') as file:
                content = file.readlines()
                yield name, content

                
class XmlReader(object):

    def __init__(self, data_paths):
        self.data_paths = data_paths
        
    def __iter__(self):
        for data_path in self.data_paths:
            name = os.path.split(data_path)[1]
            with open(data_path, 'r') as file:
                yield name.replace('.xml', ''), ET.iterparse(file)


class JsonReader(object):

    def __init__(self, data_path):
        self.data_path = data_path
        
    def __iter__(self):
        with open(self.data_path, 'r') as file:
            entries = json.load(file)
            for entry in entries:
                yield entry


class JsonDataReader(object):
    
    def __init__(self, data_paths):
        self.data_paths = data_paths
        
    def __iter__(self):
        for data_path in self.data_paths:
            name = os.path.split(data_path)[1]
            if os.path.getsize(data_path) < 1:
                yield name, None
            else:
                with open(data_path, 'r') as file:
                    entries = json.load(file)
                    for entry in entries:
                        yield name, entry


def load_json_list(json_file):
    json_list = []
    for entry in JsonReader(json_file):
        json_list.append(entry)
    return json_list


def get_list_of_uniq_jsons(lst):
    uniq = []
    for new in lst:
        found = False
        for old in uniq:
            if new == old:
                found = True
                break
        if not found:
            uniq.append(new)
    return uniq


class PrettyDict(dict):

    def __str__(self):
        return "{" + ", ".join("%r: %r\n" % (key, self[key]) for key in sorted(self)) + "}"

    __repr__ = __str__


class ErrorproneMsg(object):
    
    keys = [' Proj',
            'Class',
            ' Type',
            '  Cat',
            '  Msg',
            ' Code',
            ' Mark',
            ' Line']

    def __init__(self, proj, cls, typ, cat, msg, code, mark, line):
        self.proj = proj
        self.cls = cls
        self.typ = typ
        self.cat = cat
        self.msg = msg
        self.code = code
        self.mark = mark
        self.line = int(line)
        self.values = [self.proj, self.cls, self.typ, self.cat,
                       self.msg, self.code, self.mark, self.line]

    def __str__(self):
        return("\n" + "\n".join(k + ": " + str(v) for (k, v) in zip(ErrorproneMsg.keys, self.values)) + "\n")

    __repr__ = __str__


class SpotbugsMsg(object):
    
    keys = ['    Proj',
            '   Class',
            '     Cat',
            '  Abbrev',
            '    Type',
            'Priority',
            '    Rank',
            '     Msg',
            '  Method',
            '   Field',
            '   Lines']
    
    def __init__(self, proj, cls, cat, abbrev, typ, prio, rank, msg, mth, field, lines):
        self.proj = proj
        self.cls = cls
        self.cat = cat
        self.abbrev = abbrev
        self.typ = typ
        self.prio = prio
        self.rank = rank
        self.msg = msg
        self.mth = mth
        self.field = field
        # lines could be list of tuples during serialization
        # or list of lists during deserialization
        # so construct namedtuples here instead of passing it from outside
        # so that it works during deserialization also.
        self.lines = []
        for l in lines:
            self.lines.append(SpotbugsSrcline(int(l[0]), int(l[1]), l[2]))
        self.values = [self.proj, self.cls, self.cat, self.abbrev, self.typ, self.prio,
                       self.rank, self.msg, self.mth, self.field, self.lines]
        
    def __str__(self):
        return("\n" + "\n".join(k + ": " + str(v) for (k, v) in zip(SpotbugsMsg.keys, self.values)) + "\n")

    __repr__ = __str__
    
    def unrollLines(self):
        lines = []
        for l in self.lines:
            lines.extend(range(l.start, l.end + 1))
        return list(set(lines))


SpotbugsSrcline = namedtuple('SpotbugsSrcline', ['start', 'end', 'role'])

'''
InferIssue and InferBugTrace are slightly modified to cope
with the new json format in Infer 0.15.0
'''
class InferIssue(object):
    # keys = ['bug_trace', 'bug_type', 'bug_type_hum', 'column', 'file', 'hash', 'key', 'line', 'node_key', 'procedure', 'procedure_start_line', 'qualifier', 'severity']
    keys = ['bug_trace', 'bug_type', 'bug_type_hum', 'column', 'file', 'hash', 'key', 'line', 'procedure', 'procedure_start_line', 'qualifier', 'severity']
    def __init__(self, bug_trace, bug_type, bug_type_hum, column, file, hash, key, line, procedure, procedure_start_line, qualifier, severity):
        self.bug_trace = []
        for t in bug_trace:
            self.bug_trace.append(InferBugTrace(*list(t[k] for k in InferBugTrace.keys)))
        self.bug_type = bug_type
        self.bug_type_hum = bug_type_hum
        self.column = column
        self.file = file
        self.hash = hash
        self.key = key
        self.line = line
        # self.node_key = node_key
        self.procedure = procedure
        self.procedure_start_line = procedure_start_line
        self.qualifier = qualifier
        self.severity = severity
        
        self.values = [self.bug_type, self.qualifier, self.severity, self.line, self.column, self.procedure, self.procedure_start_line, self.file, self.bug_trace, self.key, self.hash, self.bug_type_hum]
        
    def __str__(self):
        return("\n" + "\n".join(k + ": " + str(v) for (k, v) in zip(InferIssue.keys, self.values)) + "\n")
    
    __repr__ = __str__


class InferBugTrace(object):
    keys = ['level', 'filename', 'line_number', 'column_number', 'description']
    
#     def __init__(self, level, filename, line, column, desc, tags):
    def __init__(self, level, filename, line, column, desc):
        self.level = level
        self.filename = filename
        self.line = line
        self.column = column
        self.desc = desc
#         self.tags = tags
        
#         self.values = [self.level, self.filename, self.line, self.column, self.desc, self.tags]
        self.values = [self.level, self.filename, self.line, self.column, self.desc]
        
    def __str__(self):
        return("\n" + "\n".join(k + ": " + str(v) for (k, v) in zip(InferBugTrace.keys, self.values)) + "\n")
    
    __repr__ = __str__    


class InferMsg(object):
    keys = ['      Proj',
            '     Class',
            '  Bug_Type',
            '       Msg',
            '  Severity',
            '     Lines',
            ' Procedure']

    def __init__(self, proj, cls, bug_type, msg, severity, lines, procedure):
        self.proj = proj
        self.cls = cls
        self.bug_type = bug_type
        self.msg = msg
        self.severity = severity
        self.lines = lines
        self.procedure = procedure

        self.values = [self.proj, self.cls, self.bug_type, self.msg, self.severity, self.lines, self.procedure]
        
    def __str__(self):
        return("\n" + "\n".join(k + ": " + str(v) for (k, v) in zip(InferMsg.keys, self.values)))
    
    __repr__ = __str__


class FileDiff(object):

    keys = ['Project: ',
            '  Class: ',
            '  Lines: ']
    
    def __init__(self, proj, cls, lines):
        self.proj = proj
        self.cls = cls
        self.lines = set(int(i) for i in lines)
        self.values = [self.proj, self.cls, self.lines]

    def __str__(self):
        return("\n" + "\n".join(k + str(v) for (k, v) in zip(FileDiff.keys, self.values)) + "\n")

    __repr__ = __str__


class CustomEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ErrorproneMsg):
            return OrderedDict(zip(ErrorproneMsg.keys, o.values))
        elif isinstance(o, InferIssue):
            return OrderedDict(zip(InferIssue.keys, o.values))
        elif isinstance(o, InferMsg):
            return OrderedDict(zip(InferMsg.keys, o.values))
        elif isinstance(o, SpotbugsMsg):
            return OrderedDict(zip(SpotbugsMsg.keys, o.values))
        elif isinstance(o, FileDiff):
            return OrderedDict(zip(FileDiff.keys, o.values))
        elif isinstance(o, set):
            return list(o)
        else:
            json.JSONEncoder.default(self, o)


def load_parsed_diffs(diffs_file):
    diffs_ = []
    for diff in JsonReader(diffs_file):
        inst = FileDiff(*list(diff[k] for k in FileDiff.keys))
        diffs_.append(inst)
    return diffs_


def load_parsed_ep(ep_file):
    ep_res_ = []
    for msg in JsonReader(ep_file):
        inst = ErrorproneMsg(*list(msg[k] for k in ErrorproneMsg.keys))
        ep_res_.append(inst)
    return ep_res_


def load_parsed_sb(sb_file):
    sb_res_ = []
    for msg in JsonReader(sb_file):
        inst = SpotbugsMsg(*list(msg[k] for k in SpotbugsMsg.keys))
        sb_res_.append(inst)
    return sb_res_


def load_parsed_inf(inf_file):
    inf_res_ = []
    for msg in JsonReader(inf_file):
        inst = InferMsg(*list(msg[k] for k in InferMsg.keys))
        inf_res_.append(inst)
    return inf_res_


def find_msg_by_proj_and_cls(proj, cls, msgs):
    found_messages = []
    for m in msgs:
        if m.proj == proj and m.cls == cls:
            found_messages.append(m)
    return found_messages


LineMatchesToMessages = namedtuple('LineMatchesToMessages', ['lines', 'messages'])


def get_cls_name_from_file_path(cls_path):
    cls = None
    if '/com/' in cls_path:
        cls = 'com.' + cls_path.split('/com/')[1].replace('/', '.').replace('.java', '')
    elif '/org/' in cls_path:
        cls = 'org.' + cls_path.split('/org/')[1].replace('/', '.').replace('.java', '')
    return cls


def prepare_tool(path, proj):
        
    proj_dir = os.path.join(path, proj)

    try:
        with open(os.path.join(proj_dir, 'prop-source-dir')) as file:
            proj_src = file.read()
        proj_src = os.path.join(proj_dir, proj_src)
        
        with open(os.path.join(proj_dir, 'prop-compile-path')) as file:
            proj_cp = file.read()
        
        with open(os.path.join(proj_dir, 'prop-buggy-classes')) as file:
            proj_buggy_classes = file.read().splitlines()
    except Exception as e:
        ic(proj_dir)
        ic(e)
        proj_src = ''
        proj_cp = ''
        proj_buggy_classes = []
    
    try:
        with open(os.path.join(proj_dir, 'prop-exclude-classes')) as file:
            proj_exclude_classes = file.read().splitlines()
    except IOError:
        proj_exclude_classes = []
    
    proj_buggy_classes = set(proj_buggy_classes) - set(proj_exclude_classes)
    
    proj_buggy_files = map(lambda f: os.path.join(proj_src, f.replace('.', '/') + '.java'), proj_buggy_classes)
    
    try:
        with open(os.path.join(proj_dir, 'prop-javac-options')) as file:
            proj_javac_opts = file.read()
    except IOError:
        proj_javac_opts = ""
        
    return proj_src, proj_cp, proj_javac_opts, proj_buggy_files, proj_buggy_classes

NO_WARNING = "NO_WARNING"