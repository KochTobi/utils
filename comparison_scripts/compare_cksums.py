#!/usr/bin/env python3

#####
# Calaculates cksums and writes similarity result into output files
#####
import argparse
import fnmatch
import os
import subprocess
import sys

__author__ = "Tobias Koch"
__email__ = "t.koch.vs@web.de"
__copyright__ = "Tobias Koch"
__license__ = "The MIT License (MIT)"


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


parameters = argparse.ArgumentParser(description="Compare VCF files and return differences")
parameters.add_argument('folder1', type=str, nargs=1, metavar='directory')
parameters.add_argument('folder2', type=str, nargs='+', metavar='directory')
parameters.add_argument('-o', '--output', type=str, nargs=1, metavar='output', default=['cksums'])
parameters.add_argument('-p', '--pattern', type=str, nargs=1, metavar='pattern', default=['*'])


def compute_cksum(files):
    if not files:
        print('no files given: %s' % str(files))
        return []
    computed_cksum_lines = []
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


def main(argv):
    args = parameters.parse_args(argv)
    root_directories = args.folder1 + args.folder2
    output_file = args.output[0]
    pattern = args.pattern[0]

    all_files_by_root_directory = dict()
    for root_dir in root_directories:
        directory_files = find_matching_files_in_folder(pattern, root_dir)
        all_files_by_root_directory[root_dir] = directory_files

    combined_cksums_from_directories = []
    for file_list in all_files_by_root_directory.values():
        cksums_for_current_root_dir = compute_cksum(file_list)
        combined_cksums_from_directories.extend(cksums_for_current_root_dir)

    counted_cksum_dict = {}
    for i in combined_cksums_from_directories:
        curr_cksum = i[0]
        if curr_cksum in counted_cksum_dict.keys():
            counted_cksum_dict[curr_cksum] += 1
        else:
            counted_cksum_dict[curr_cksum] = 1

    matching_cksums = [curr_line[0] for curr_line in combined_cksums_from_directories if
                       counted_cksum_dict[curr_line[0]] % len(root_directories) == 0]

    failed_cksums = [curr_line[0] for curr_line in combined_cksums_from_directories if
                     counted_cksum_dict[curr_line[0]] % len(root_directories) != 0]
    identical_files_from_directories = list(
        filter(lambda line: line[0] in matching_cksums, combined_cksums_from_directories))

    different_files_from_directories = list(
        filter(lambda line: line[0] in failed_cksums, combined_cksums_from_directories))

    with open(output_file + '.identical.tsv', 'w+') as outfile:
        for line in sorted(identical_files_from_directories, key=lambda line: line[2][::-1]):
            outfile.write("%s\t%s\t%s" % (str(line[0]), str(line[1]), line[2]))
            outfile.write(os.linesep)

    with open(output_file + '.different.tsv', 'w+') as outfile:
        for line in sorted(different_files_from_directories, key=lambda line: line[2][::-1]):
            outfile.write("%s\t%s\t%s" % (str(line[0]), str(line[1]), line[2]))
            outfile.write(os.linesep)

    print('Similar files:\t%s' % len(identical_files_from_directories))
    print('Different files:\t%s' % len(different_files_from_directories))
    return


if __name__ == '__main__':
    main(sys.argv[1:])
