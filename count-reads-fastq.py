#!/usr/bin/env python3
# Credits go to:
#   https://codereview.stackexchange.com/questions/69261/counting-the-lines-of-a-compressed-file

import argparse
import bz2
import gzip
import os
import sys

class UnsupportedCompressionException(Exception):
    pass

class UnexpectedLineCountException(Exception):
    pass

class CompressedFastqFile:
    fileCompressionToolMap = {".gz":gzip.open, ".bz2":bz2.open}
    def __init__(self, filepath):
        extension = os.path.splitext(filepath)[1].lower()
        if extension not in self.fileCompressionToolMap:
            raise  UnsupportedCompressionException("Unrecognized file extension. Please provide a .bz2 or .gz compressed file.")
        self.filepath = filepath
        self.fileCompressionTool = self.fileCompressionToolMap[extension]

    def count_reads(self):
        line_count = self.count_lines()
        if line_count%4 == 0:
            return line_count/4
        else:
            raise UnexpectedLineCountException("Number of lines " + str(line_count) + " not a multiple of 4.")
        

    def count_lines(self):
        with self.fileCompressionTool(self.filepath) as fileHandler:
            lines = 0
            for _ in fileHandler:
                lines += 1
            return lines
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count reads in fastq file.')
    parser.add_argument('--file', nargs=1, help='a .bz2 or .gz compressed fastq file')

    args = parser.parse_args()
    try:
        compressed_file = CompressedFastqFile(args.file[0])
        print(compressed_file.count_reads())
    except (UnsupportedCompressionException, UnexpectedLineCountException) as e:
        print (e)
        exit(1)
