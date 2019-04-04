#!/usr/bin/env python3

#####
# Compares vcf files using vcftools compare and cksum
#####
import argparse
import sys
import subprocess

__author__ = "Tobias Koch"
__email__ = "t.koch.vs@web.de"
__copyright__ = "Tobias Koch"
__license__ = "The MIT License (MIT)"

parameters = argparse.ArgumentParser(description="Compare VCF files and return differences")
parameters.add_argument('file1', type=str, nargs=1, metavar='file')
parameters.add_argument('file2', type=str, nargs='+', metavar='file')
parameters.add_argument('-o', '--output', type=str, nargs=1, metavar='output')


def main(argv):
    args = parameters.parse_args(argv)
    files = args.file1 + args.file2
    print(files)
    return


if __name__ == '__main__':
    main(sys.argv[1:])
