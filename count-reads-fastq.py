#!/usr/bin/env python3
# With help from:
#   https://codereview.stackexchange.com/questions/69261/counting-the-lines-of-a-compressed-file

import argparse
import bz2
import gzip
import os
import sys
import re
from progress.spinner import LineSpinner


class UnsupportedCompressionException(Exception):
    pass


class UnexpectedLineCountException(Exception):
    pass


class CompressedFastqFile:
    fileCompressionToolMap = {".gz": gzip.open, ".bz2": bz2.open}

    def __init__(self, filepath):
        extension = os.path.splitext(filepath)[1].lower()
        if extension not in self.fileCompressionToolMap:
            raise UnsupportedCompressionException(
                "Unrecognized file extension. Please provide a .bz2 or .gz compressed file."
            )
        self.filepath = filepath
        self.fileCompressionTool = self.fileCompressionToolMap[extension]
        print("Successfully created CompressedFastqFile for " + filepath)

    def count_reads(self):
        with LineSpinner('Reading file ') as spinner:
            with self.fileCompressionTool(self.filepath) as fileHandler:
                line_count = 0
                lines_with_only_plus = 0
                for line in fileHandler:
                    spinner.next()
                    line_count += 1
                    if (re.match('\+', line.decode())):
                        lines_with_only_plus += 1

                if (line_count % 4 != 0):
                    raise UnexpectedLineCountException( "Number of lines(" + str(line_count) + ") not a multiple of 4.")
                elif (line_count / 4 != lines_with_only_plus):
                    raise UnexpectedLineCountException( "Number of lines/4 (" + str(line_count / 4) +") and number of reads(" + str(lines_with_only_plus) + ") disagree.")
                else:
                    return lines_with_only_plus

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count reads in fastq file.")
    parser.add_argument("--file", nargs='+', help="a .bz2 or .gz compressed fastq file")

    args = parser.parse_args()
    for file_path in args.file:
        try:
                compressed_file = CompressedFastqFile(file_path)
                print(file_path + ":\t" + str(compressed_file.count_reads()))
        except (UnsupportedCompressionException, UnexpectedLineCountException) as e:
            print(file_path + ":\t" + str(e), file=sys.stderr)
