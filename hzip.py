#!/usr/bin/env python3
'''
usage: hzip.py [-h] [-o OUTFILE] [-s SUFFIX] [-f] [-l LEVEL] [-a] infile

Compress files using the hzlib module.

positional arguments:
  infile

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        Name of output file
  -s SUFFIX, --suffix SUFFIX
                        Suffix to use instead of .hz
  -f, --force           Force compression and overwrite output file if it
                        exists
  -l LEVEL, --level LEVEL
                        Maximum levels of compression
  -a, --alwayscompress  Compress to max level even if it would make output
                        larger

Format of saved file is the following:
The string of bytes MAGIC from hzlib, followed by one byte containing the
compression level of the data, followed by the data.

Compression level 0 is the raw input. The data used in compression level
n+1 is the result of compressing the result provided by compression
level n. Note that each level includes its codebook in its data, but does
not include the magic number.
'''
from hzlib import MAGIC, compress, build_codebook, build_canonical_codebook, \
    symbol_count, pad, join, make_huffman_tree
from struct import pack, unpack
# import _collections
DEFAULT_EXTENSION = '.hz'
MAX_COMPRESSION_LEVEL = 255
MIN_COMPRESSION_LEVEL = 0
DEFAULT_FILE_NAME = 'NEW_ZIP'


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Compress files using the hzlib module.')
    parser.add_argument("infile")
    parser.add_argument("-o", "--outfile", type=str, default=None,
                        help='Name of output file')
    parser.add_argument("-s", "--suffix", type=str, default=DEFAULT_EXTENSION,
                        help=('Suffix to use instead of ' +
                              DEFAULT_EXTENSION))
    parser.add_argument("-f", "--force", action='store_true',
                        help=('Force compression and overwrite output ' +
                              'file if it exists'))
    parser.add_argument("-l", "--level", type=int,
                        default=MAX_COMPRESSION_LEVEL,
                        help='Maximum levels of compression')
    parser.add_argument("-a", "--alwayscompress", action='store_true',
                        help=('Compress to max level even if it would ' +
                              'make output larger'))
    args = parser.parse_args()
    # print(args, args.force)

    if args.force == True:
        writing_mode = 'wb'
    else:
        writing_mode = 'xb'

    if args.outfile is not None:
        output_file = args.outfile + args.suffix
    else:
        output_file = args.infile + args.suffix

    decoded_stream = []
    encoded_stream = ""

    input_file = args.infile
    compression_level = args.level

    with open(input_file, 'rb') as decoded_file:
        for line in decoded_file:
            decoded_stream += line

        decoded_stream_size = len(decoded_stream)
        for rounds in range(0, compression_level):
            if encoded_stream != "":
                decoded_stream = encoded_stream
            symbol_dict = symbol_count(decoded_stream)
            huffman_tree = make_huffman_tree(symbol_dict)
            code_book = build_codebook(huffman_tree)
            cannonical_code_book = build_canonical_codebook(code_book)
            compressed_stream = compress(decoded_stream, cannonical_code_book)
            paded_stream = pad(compressed_stream)
            encoded_stream = join(paded_stream, cannonical_code_book)

            # if len(encoded_stream)>decoded_stream_size and args
            # .alwayscompare:
            #     compression_level=rounds
            #     break
        if compression_level == 0:
            encoded_stream = decoded_stream



    with open(output_file, writing_mode) as encoded_file:
        encoded_file.write(MAGIC)
        encoded_file.write(bytes(pack('H',rounds + 1)))
        # import array
        # g=array.array(encoded_stream)

        # print(g)
        for i in encoded_stream:
            print(bytes(i))
        encoded_stream_2=bytes(encoded_stream)
        # for bit in encoded_stream:
        #     encoded_stream_2+=bytes(pack('H',bit))
        encoded_file.write(encoded_stream_2)

    return None

if __name__ == '__main__':
    main()
