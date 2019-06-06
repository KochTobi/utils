#!/usr/bin/env python3

#####
# Calaculates cksums and exports a csv file
#####
import argparse
import datetime
import fnmatch
import json
import os
import subprocess
import sys
import pandas as pd

__author__ = "Tobias Koch"
__email__ = "t.koch.vs@web.de"
__copyright__ = "Tobias Koch"
__license__ = "The MIT License (MIT)"


def get_simple_basename(sample):
    if type(sample) == str:
        return os.path.basename(sample).split('.')[0]

def log_command_call():
    cwd = os.getcwd()
    log_file = os.path.join(cwd, datetime.date.today().isoformat())
    log_file += "-%s-%s" % (str(datetime.datetime.today().hour), str(datetime.datetime.today().minute))
    log_file += "-%s.cmd.sh" % get_simple_basename(sys.argv[0])
    with open(log_file, 'a+') as logfile:
        logfile.write('#!/usr/bin/env bash')
        logfile.write(os.linesep)
        logfile.write("#WORKING_DIRECTORY=%s" % cwd)
        logfile.write(os.linesep)
        logfile.write("python3 "+" ".join(sys.argv))
        logfile.write(os.linesep)

def run_cmd(command):
    result = {}
    try:
        execution = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                   universal_newlines=True)
    except subprocess.CalledProcessError as err:
        print("Failed to execute cmd: %s" % err.cmd)
        result['stdout'] = err.stdout
        result['stderr'] = err.stderr
        result['returncode'] = err.returncode
        result['error'] = err
    else:
        result['stdout'] = execution.stdout
        result['stderr'] = execution.stderr
        result['returncode'] = execution.returncode
    return result


def find_matching_files_in_folder(pattern, path):
    files_found_by_pattern_search = []
    for root, dirs, files in os.walk(path):
        filenames_matching_pattern = fnmatch.filter(files, pattern)
        absolute_matched_filenames = [os.path.join(root, filename) for filename in filenames_matching_pattern]
        files_found_by_pattern_search.extend(absolute_matched_filenames)
    return files_found_by_pattern_search


parameters = argparse.ArgumentParser(description="Compute cksum and export csv file.")
parameters.add_argument('folder1', type=str, nargs=1, metavar='directory')
parameters.add_argument('folder2', type=str, nargs='+', metavar='directory')
parameters.add_argument('-o', '--output', type=str, nargs=1, metavar='output', default=['cksums'])
parameters.add_argument('-p', '--pattern', type=str, nargs=1, metavar='pattern', default=['*'])


def compute_cksum(files):
    if not files:
        print('No files given: %s' % str(files))
        return []
    computed_cksum_lines = []
    filename_cksum_dict = dict()
    cmd = ["cksum"]
    cmd.extend(files)
    cmd = ' '.join(cmd)
    result = run_cmd(cmd)
    if result.get('returncode') > 0:
        raise subprocess.SubprocessError('Command execution failed: %s' % result.get('stderr'))
    output = result.get('stdout').splitlines()
    for line in output:
        cksum, bytecount, filename = line.split()
        computed_cksum_lines.append([int(cksum), int(bytecount), str(filename)])
    return computed_cksum_lines

def cksums2csv(cksums_dict,filename):
    data_frame = pd.DataFrame({key:pd.Series(value) for key, value in cksums_dict.items()})
    data_frame.to_csv(filename, sep=',', encoding='utf-8', index=False)


def main(argv):
    args = parameters.parse_args(argv)
    root_directories = args.folder1 + args.folder2
    output_file = args.output[0]
    pattern = args.pattern[0]

    number_of_directories = len(root_directories)

    all_files_by_root_directory = dict()
    for root_dir in root_directories:
        directory_files = find_matching_files_in_folder(pattern, root_dir)
        all_files_by_root_directory[root_dir] = directory_files

    all_cksums_by_root_directory = dict()
    combined_cksums_from_directories = []

    for root_dir, file_list in all_files_by_root_directory.items():
        cksums_for_current_root_dir = compute_cksum(file_list)
        all_cksums_by_root_directory[root_dir] = [x[0] for x in cksums_for_current_root_dir]
        combined_cksums_from_directories.extend(cksums_for_current_root_dir)

    with open(output_file + '.full_cksum_output.tsv', 'w+') as outfile:
        for value in combined_cksums_from_directories:
            outfile.write("%s\t%s\t%s" % (value[0], value[1], value[2]))
            outfile.write(os.linesep)
    cksums2csv(all_cksums_by_root_directory, output_file + '.csv')
    return


if __name__ == '__main__':
    main(sys.argv[1:])
    log_command_call()
