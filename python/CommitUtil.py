import uuid, re
from pydriller import Repository
from Util import logger

def clean_string(signature):
    return signature.strip().replace(' ', '')

def get_method_code(source_code, start_line, end_line):
    try:
        if source_code is not None:
            code = ('\n'.join(source_code.split('\n')[int(start_line) - 1: int(end_line)]))
            return code
        else:
            return None
    except Exception as e:
        logger(f'Problem while extracting method code from the changed file contents: {e}')
        pass

def changed_methods_both(file):
    """
    Return the list of methods that were changed.
    :return: list of methods
    """
    new_methods = file.methods
    old_methods = file.methods_before
    added = file.diff_parsed["added"]
    deleted = file.diff_parsed["deleted"]

    methods_changed_new = {
        y
        for x in added
        for y in new_methods
        if y.start_line <= x[0] <= y.end_line
    }
    methods_changed_old = {
        y
        for x in deleted
        for y in old_methods
        if y.start_line <= x[0] <= y.end_line
    }
    return methods_changed_new, methods_changed_old

# --------------------------------------------------------------------------------------------------------
# extracting method_change data
def get_methods(file, file_change_id):
    """
    returns the list of methods in the file.
    """
    file_methods = []
    try:
        if file.changed_methods:
            # for m in file.methods:
            #     if m.name != '(anonymous)':
            #         logger(m.long_name)

            # for mb in file.methods_before:
            #     if mb.name != '(anonymous)':
            #         logger(mb.long_name)

            # for mc in file.changed_methods:
            #     if mc.name != '(anonymous)':
            #         logger(mc.long_name)

            if file.changed_methods:
                methods_after, methods_before = changed_methods_both(file)  # in source_code_after/_before
                if methods_before:
                    for mb in methods_before:
                        # filtering out code not existing, and (anonymous)
                        # because lizard API classifies the code part not as a correct function.
                        # Since, we did some manual test, (anonymous) function are not function code.
                        # They are also not listed in the changed functions.
                        if file.source_code_before is not None and mb.name != '(anonymous)':
                            method_before_code = get_method_code(file.source_code_before, mb.start_line, mb.end_line)
                            method_before_row = {
                                'method_change_id': uuid.uuid4().fields[-1],
                                'file_change_id': file_change_id,
                                'name': mb.name,
                                'signature': mb.long_name,
                                'parameters': mb.parameters,
                                'start_line': mb.start_line,
                                'end_line': mb.end_line,
                                'code': method_before_code,
                                'nloc': mb.nloc,
                                'complexity': mb.complexity,
                                'token_count': mb.token_count,
                                'top_nesting_level': mb.top_nesting_level,
                                'before_change': 'True',
                            }
                            file_methods.append(method_before_row)

                if methods_after:
                    for mc in methods_after:
                        if file.source_code is not None and mc.name != '(anonymous)':
                            changed_method_code = get_method_code(file.source_code, mc.start_line, mc.end_line)
                            changed_method_row = {
                                'method_change_id': uuid.uuid4().fields[-1],
                                'file_change_id': file_change_id,
                                'name': mc.name,
                                'signature': mc.long_name,
                                'parameters': mc.parameters,
                                'start_line': mc.start_line,
                                'end_line': mc.end_line,
                                'code': changed_method_code,
                                'nloc': mc.nloc,
                                'complexity': mc.complexity,
                                'token_count': mc.token_count,
                                'top_nesting_level': mc.top_nesting_level,
                                'before_change': 'False',
                            }
                            file_methods.append(changed_method_row)

        if file_methods:
            return file_methods
        else:
            return None

    except Exception as e:
        logger(f'Problem while fetching the methods: {e}')
        pass

# ---------------------------------------------------------------------------------------------------------
# extracting file_change data of each commit
def get_files(commit):
    """
    returns the list of files of the commit.
    """
    commit_files = []
    commit_methods = []
    try:
        logger(f'Extracting files for {commit.hash}')
        if commit.modified_files:
            for file in commit.modified_files:
                logger(f'Processing file {file.filename} in {commit.hash}')
                # programming_language = (file.filename.rsplit(".')[-1] if '.' in file.filename else None)
                file_change_id = uuid.uuid4().fields[-1]

                file_row = {
                    'file_change_id': file_change_id,       # filename: primary key
                    'hash': commit.hash,                    # hash: foreign key
                    'filename': file.filename,
                    'old_path': file.old_path,
                    'new_path': file.new_path,
                    'change_type': file.change_type,        # i.e. added, deleted, modified or renamed
                    'diff_parsed': file.diff_parsed,        # diff parsed in a dict containing added and deleted lines lines
                    'num_lines_added': file.added_lines,        # number of lines added
                    'num_lines_deleted': file.deleted_lines,    # number of lines removed
                    'code_after': file.source_code,
                    'code_before': file.source_code_before,
                    'nloc': file.nloc,
                    'complexity': file.complexity,
                    'token_count': file.token_count
                }
                commit_files.append(file_row)
                file_methods = get_methods(file, file_change_id)

                if file_methods is not None:
                    commit_methods.extend(file_methods)
        else:
            logger('The list of modified_files is empty')

        return commit_files, commit_methods

    except Exception as e:
        logger(f'Problem while fetching the files: {e}')
        pass


def extract_commits(repo_url: str, commits, user_token):
    """This function extract git commit information of only the hashes list that were specified in the
    commit URL. All the commit_fields of the corresponding commit have been obtained.
    Every git commit hash can be associated with one or more modified/manipulated files.
    One vulnerability with same hash can be fixed in multiple files so we have created a dataset of modified files
    as 'df_file' of a project.
    :param repo_url: list of url links of all the projects.
    :param hashes: list of hashes of the commits to collect
    :return dataframes: at commit level and file level.
    """
    repo_commits = []
    repo_files = []
    repo_methods = []

    # ----------------------------------------------------------------------------------------------------------------
    # extracting commit-level data
    repo_url = f"https://{user_token['user']}:{user_token['token']}@github.com/{repo_url}.git"

    logger(f'Extracting commits for {repo_url} with {4} worker(s) looking for the following hashes:')

    # giving first priority to 'single' parameter for single hash because
    # it has been tested that 'single' gets commit information in some cases where 'only_commits' does not,
    # for example: https://github.com/hedgedoc/hedgedoc.git/35b0d39a12aa35f27fba8c1f50b1886706e7efef
    single_hash = None
    if len(commits) == 1:
        single_hash = commits[0]
        hashes = None
    else:
        hashes = []
        for commit in commits:
            hashes.append(commit)

    for commit in Repository(path_to_repo=repo_url, only_commits=hashes, single=single_hash, num_workers=4).traverse_commits():
        logger(f'Processing {commit.hash}')
        try:
            commit_row = {
                'hash': commit.hash,
                'repo_url': f"https://github.com/{repo_url}.git",
                'author': commit.author.name,
                'committer': commit.committer.name,
                'msg': commit.msg,
                'merge': commit.merge,
                'parents': commit.parents,
                'num_lines_added': commit.insertions,
                'num_lines_deleted': commit.deletions
            }
            commit_files, commit_methods = get_files(commit)
            repo_commits.append(commit_row)
            repo_files.extend(commit_files)
            repo_methods.extend(commit_methods)
        except Exception as e:
            logger(f'Problem while fetching the commits: {e}')
            pass

    return repo_commits, repo_files, repo_methods

def extract_repo_commit_from_commit_link(link):
    pattern = r"https://github.com/([^/]+)/([^/]+)/commit/([^/]+)"
    match = re.match(pattern, link)
    if match:
        repo = match.group(1) + "/" + match.group(2)
        commit_hash = match.group(3)
        print("Repository:", repo)
        print("Commit hash:", commit_hash)
        return repo, commit_hash
    else:
        logger(f"Invalid GitHub commit {link}")