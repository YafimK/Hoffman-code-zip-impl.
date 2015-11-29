#!/usr/bin/env python3
'''
usage: hunzip.py [-h] [-o OUTFILE] [-s SUFFIX] [-S OUTSUFFIX] [-f] infile

Decompress files using the hzlib module.

positional arguments:
  infile

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Name of output file
  -s SUFFIX, --suffix SUFFIX
                        Default suffix to remove instead of .hz
  -S OUTSUFFIX, --outsuffix OUTSUFFIX
                        Default suffix to add if instead of .out
  -f, --force           Force decompression and overwrite output file if it
                        exists
'''

from hzlib import MAGIC,split

DEFAULT_IN_EXTENSION = '.hz'
DEFAULT_OUT_EXTENSION = '.out'

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Decompress files using the hzlib module.')
    parser.add_argument("infile")
    parser.add_argument("-o", "--outfile", type=str, default=None, 
                        help='Name of output file')
    parser.add_argument("-s", "--suffix", type=str,
                        default=DEFAULT_IN_EXTENSION,
                        help=('Default suffix to remove instead of ' +
                              DEFAULT_IN_EXTENSION))
    parser.add_argument("-S", "--outsuffix", type=str,
                        default=DEFAULT_OUT_EXTENSION,
                        help=('Default suffix to add if instead of ' +
                              DEFAULT_OUT_EXTENSION))
    parser.add_argument("-f", "--force", action='store_true',
                        help=('Force decompression and overwrite output ' +
                              'file if it exists'))
    args = parser.parse_args()
    print(args)
    input_file= args.infile

    if args.outfile is None:
        output_file=input_file+args.outsuffix
    else:
        output_file=args.outfile+args.outsuffix

    if args.force==True:
        mode='wb'
    else:
        mode='xb'

    from struct import unpack
    with open(input_file,'rb') as in_file:
        #first check the MAGIC
        if MAGIC!=in_file.read(len(MAGIC)):
            raise TypeError
        comperession_levels=list(in_file.read(1))
        print(comperession_levels)
        encoded_stream=(in_file.readlines())
        print(encoded_stream)
        # encoded_stream=in_file.readlines()
        # print(encoded_stream)


if __name__ == '__main__':
    main()
