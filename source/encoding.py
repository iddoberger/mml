from collections import OrderedDict
from math import log2, ceil
from io import StringIO
from copy import copy

alphabet_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'y']
words_list = ['a', 'adore', 'all', 'beautiful', 'big', 'bit', 'chases', 'dog', 'handsome', 'like', 'mouse', 'nice', 'professor', 'some', 'student', 'taught', 'the', 'thin', 'thoughtful', 'ugly']
states_list = ["q0", "q1", "q2", "q3", "q4", "qf"]




def get_binary_enumeration(list_):
    def get_binary_string(number, log_length):
        return str(bin(number))[2:].zfill(log_length)
    list_ = copy(list_)
    list_.sort()  # sort for good measure (the list can arrive sorted already
    list_.append("#")
    symbol_length = get_symbol_length(list_)
    enumeration = OrderedDict()
    for i in range(len(list_)):
        enumeration[list_[i]] = get_binary_string(i, symbol_length)

    return enumeration, symbol_length

def get_symbol_length(list_):
    return ceil(log2(len(list_)))

alphabet_enumeration, alphabet_symbol_length = get_binary_enumeration(alphabet_list)
inverse_alphabet_enumeration = {v:k for k, v in alphabet_enumeration.items()}
assert alphabet_enumeration["a"] == "00000"
assert inverse_alphabet_enumeration["10100"] == "#"

def encode_lexicon(alphabet_list, words_list):
    str_io = StringIO()
    alphabet_enumeration, alphabet_symbol_length = get_binary_enumeration(alphabet_list)
    print('0'*alphabet_symbol_length + '1', end="", file=str_io)
    for word in words_list:
        for char in word:
            print(alphabet_enumeration[char], end="", file=str_io)
        print(alphabet_enumeration["#"], end="", file=str_io)
    print(alphabet_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()

def encode_lexicon_length(alphabet_list, words_list):
    alphabet_symbol_length = get_binary_enumeration(alphabet_list)[1]
    delimiter_usage = (len(words_list) + 1) * alphabet_symbol_length
    words_usage = sum([len(word) for word in words_list]) * alphabet_symbol_length
    num_bits = alphabet_symbol_length + 1
    encoding_length = delimiter_usage + words_usage + num_bits
    return encoding_length

def decode_lexicon(encoded_hypothesis_string):
    first_one_index = encoded_hypothesis_string.index('1')
    number_of_repr_bits = first_one_index
    encoded_hypothesis_string = encoded_hypothesis_string[first_one_index+1:]

    lexicon_string = ''
    i = 0
    while True:
        bits = encoded_hypothesis_string[i:i+number_of_repr_bits]
        i += number_of_repr_bits
        lexicon_string += inverse_alphabet_enumeration[bits]
        if lexicon_string.endswith("##"):
            break

    return lexicon_string, encoded_hypothesis_string[i:]


encoded_lexicon_string = encode_lexicon(alphabet_list, words_list)
encode_lexicon_length = encode_lexicon_length(alphabet_list, words_list)

assert encode_lexicon_length == 616
assert len(encoded_lexicon_string) == encode_lexicon_length
assert decode_lexicon(encoded_lexicon_string)[0] == "a#adore#all#beautiful#big#bit#chases#dog#handsome#like#mouse#nice#professor#some#student#taught#the#thin#thoughtful#ugly##"