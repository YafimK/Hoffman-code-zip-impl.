'''
This module contains several function for compress and decompress data, using
the Huffman code algorithm.
'''
from collections import Counter
from operator import itemgetter
import bisect

MAGIC = b"i2cshcfv1"


def symbol_count(data):
    """
    Runs on the supplied data and coutns the occurrences of each symbol/char.
    :param data: the information to be dissected and symbol counted
    :return: counter container which keys are are the different chars and the
    values is their count.
    """
    return Counter(data)


def make_huffman_tree(counter):
    """
    first sorts the symbol counter container by their their key and then
    by their occurences.
    then starts marging them to create a tree represented by tuples- each
    two leafs are gathered to sub-tree/branch till
    there are no more left a main tree in created (if one is left he is
    considered to be a leaf).
    :param counter: the container with symbols and their count in the data
    :return: a huffman tree in tuples
    """
    #defaultive numbers used in the functions and can be changed
    pop_item_placement = 0 #the placement of the item to pop during the
    # sorting process - if entered a diffrent list-these should change.
    symbol_key_list_placement = 0 #accouns for the place of the symbol
    symbol_frequency_list_placement = 1 #accounts for the place of frequency
    # of the symbol
    first_sort_crieteria = 0 #first sorting crit. is the key
    second_sort_crieteria = 1 #second sorting crit. is the value

    # if no counter is supplied or counter is empty then return None
    if counter is None or not len(counter):
        return None
        # sorts the lsit by their length and symbols value
    sorted_hoffman_container = sorted(sorted(counter.items(),
                                             key=itemgetter(
                                                 first_sort_crieteria),
                                             reverse=True),
                                      key=itemgetter(second_sort_crieteria))

    while len(sorted_hoffman_container) > 1:
        # extract the two symbols which are the less frequent chars int the
        # symbol count
        symbol_a = sorted_hoffman_container.pop(
            pop_item_placement) #least frequent char
        symbol_b = sorted_hoffman_container.pop(
            pop_item_placement) # second-least frequent char
        # create a parent of the two extracted sorted_hoffman_container -
        # separated from the
        # insertion for readability
        new_node = ((symbol_b[symbol_key_list_placement],
                     symbol_a[symbol_key_list_placement]),
                    symbol_a[symbol_frequency_list_placement] + symbol_b[
                        symbol_frequency_list_placement])
        # finds the proper insertion index for the parent and inserts it -
        # separated for readability
        char_frequency_list = [char[symbol_frequency_list_placement] for char
                               in sorted_hoffman_container]
        insertion_index = bisect.bisect(char_frequency_list, new_node[
            symbol_frequency_list_placement])
        sorted_hoffman_container.insert(insertion_index, new_node)
    return sorted_hoffman_container[0][0]


def build_codebook(huff_tree):
    """
    Takes the tuppled sorted huffman tree- runs on it recursively till it
    gets to the leaf of and inserts the value to the code book. while going
    for the leaf it counts the branches past(0 for left, 1 for right) (
    subtrees) to find binary
    representation (according to it's number of occurences).
    inserts a value for each symbol which includs the length of the binary
    value and it's value.
    :param huff_tree: a tuppled sorted huffman tree which represents a tree
    sorted by symbol occrurences
    :return: code book which has the symbols with their binary value and
    length
    """
    default_leaf_prefix = '0'
    code_book = {}

    def binary_value_finder(node, prefix=""):
        if type(node) == tuple and len(node) == 2:
            binary_value_finder(node[0], prefix + '0')
            binary_value_finder(node[1], prefix + '1')
        else:
            #if it's a sole leaf - puts a defaultive 0
            if prefix == "":
                prefix = default_leaf_prefix
            code_book[node] = (len(prefix), int(prefix, 2))

            #if the huffman tree supplied is not None - run the recursive
            # function

    if huff_tree is not None:
        binary_value_finder(huff_tree)
    return code_book


def build_canonical_codebook(codebook):
    """
    takes the codebook and sorts it cannonicly by their binary lengths and
    key value and index them accoringly.
    :param codebook:
    :return: sorted cannoicly codebook
    """
    #first sorts the codebook first by binary value length and then by
    # their keys value.
    sorted_nodes = sorted(codebook.items(),
                          key=lambda node: (node[1][0], node[0]))
    new_binary_value = 0
    for counter in range(len(sorted_nodes)):
        #calculate the new binary value by the key's position in the
        # codebook, and adds zero according to the diffrence in length
        # between this key and the key before it (adds zero for each 1 in
        # delta lengths).
        new_binary_value = bin(new_binary_value)[2:] + '0' * (abs(
            sorted_nodes[counter - 1][1][0] - sorted_nodes[counter][1][0]))
        #inserts the new key with new value and older length
        sorted_nodes[counter] = (sorted_nodes[counter][0], (
            sorted_nodes[counter][1][0], int(new_binary_value, 2)))
        #incement the value counter after updating with current value-which
        # could have rise since since the adjustment of zeros
        new_binary_value = int(new_binary_value, 2) + 1
    return dict(sorted_nodes)


def build_decodebook(codebook):
    """
    transfers the codebook supplied to a dictionery which the keys are the
    binary length and value of the compatible symbol/char in the file and
    the compatible symbol/char as value
    :param codebook: encoding table
    :return: dictionery eith mapping of bytes length and value matching
    symbols/chars
    """
    decode_book = {}
    for item in codebook.items():
        decode_book[item[1]] = item[0]
    return decode_book


def compress(corpus, codebook):
    """
    Compresses a the data supplied using the codebook(huffman Tree).
    :param corpus: the data to be compressed
    :param codebook: the huffman tree used to compress
    return an iterator which runs over the bits of the encoded data
    """

    for bit in corpus:
        binary_value = '0' * abs(
            len(bin(codebook[bit][1])[2:]) - codebook[bit][0]) + bin(
            codebook[bit][1])[2:]
        for value in binary_value:
            yield int(value)


def decompress(bits, decodebook):
    """
    The opposite of compress, going through the bits supplied and decompress it
    using the the decodebook.
    :param bits: iterable binery data
    :param decodebook: dictionary that maps chars - binary
    code length and its value to each char of the huffman tree.
    :return: iterator which runs over the uncompressed data
    """
    if bits is None or decodebook is None:
        return None
        #converts the data to string
    bit_string = ''.join(map(str, bits))
    count_cutter = 1
    start_mark = 0

    #over the bits and tries to find a matching key in the decoding book
    #each found key is yielded.
    #uses the slice functionelity to move to increase the "search" range if
    # a match not found.
    for counter in range(len(bit_string)):
        checking_key = (len(bit_string[start_mark:count_cutter]),
                        int(bit_string[start_mark:count_cutter], 2))
        if checking_key in decodebook:
            yield decodebook[checking_key]
            #if a match is found restart the search indexes
            start_mark = count_cutter
            count_cutter += 1
        else:
            count_cutter += 1


def pad(bits):
    """
    Takes a bit sequence and adds bits so it divisable by 8.
    goes through the bits 8th' and converts them into bytes.
    :param bits: iterable composed of binary data (1,0)
    :return: iterator which goes through the bytes values
    """
    if type(bits) != list:
        bits = list(bits)

    # add 1 to the list as requested:
    bits.append(1)
    #converts the list to string
    bits = ''.join(map(str, bits))

    # iterate over the string:
    while len(bits) // 8:
        new_bits = int(bits[:8], 2)
        bits = bits[8:len(bits)]
        yield new_bits
    else:
        if 0 < len(bits) < 8:
            # add "0" to complete the last value for 8 digits:
            new_bits = bits
            # take the binary value:
            new_bits = int(new_bits + '0' * (8 - (len(bits) % 8)), 2)
            yield new_bits


def unpad(byteseq):
    """
    Takes byte sequence, goes through the bytes, get their bit representation
    and removes "artificel" padding of 1s and zeros.
    :param byteseq: byte sequence
    :return iterator which runs over the unpaded bits
    """
    bits = [str(bin(byte)[2:]) for byte in byteseq]
    new_bits = []
    for byte in bits:
        if len(byte) < 8:
            byte = '0' * (8 - len(byte)) + byte
        new_bits.append(byte)

    new_bits = ''.join(new_bits).rstrip('0')[:-1]
    for bit in new_bits:
        yield int(bit)


def join(data, codebook):
    """
    Joins the codebook and the data so it will be ready for the writing
    to the file. This by first going on the dictionery and appending it to
    the list by bits and adds the data to the end.
    :param data:compressed data
    :param codebook: huffman codebook
    :return iterator which goes through the concated codebook and data
    """
    default_no_codebook_value = 0
    default_placement_length_codebook = 0
    default_table_size = 256
    conecatated_data = []

    for index in range(default_table_size):
        if codebook.__contains__(index):
            conecatated_data.append(
                codebook[index][default_placement_length_codebook])
        else:
            conecatated_data.append(default_no_codebook_value)
    conecatated_data += data
    for item in conecatated_data:
        yield item


def split(byteseq):
    '''
    As oopsite to join splits the concated compressed data and huffman
    codebook.
    :param byteseq: concated compreseed data and huffman codebook
    :return: huffman codebook and an iterator which runs over the compressed
    data
    '''
    default_table_size = 256

    byte_dict = {}
    #if byte seq is not in list format-converts it
    if type(byteseq) != list:
        byteseq = list(byteseq)
        #recreates the codebook
    for index in range(default_table_size):
        if byteseq[index] != 0:
            byte_dict[index] = (byteseq[index], 0)

    #new iterator which runs over the compressed data
    def byte_iterator():
        for index in range(default_table_size, len(byteseq)):
            yield byteseq[index]

    return byte_iterator(), build_canonical_codebook(byte_dict)
    
