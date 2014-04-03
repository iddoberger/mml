from collections import OrderedDict,defaultdict
from math import log2, ceil
from io import StringIO
from copy import copy


from unittest.mock import MagicMock, Mock

class HHM():
    pass


alphabet_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'y']
words_list = ['a', 'adore', 'all', 'beautiful', 'big', 'bit', 'chases', 'dog', 'handsome', 'like', 'mouse', 'nice', 'professor', 'some', 'student', 'taught', 'the', 'thin', 'thoughtful', 'ugly']
states_list = ["q0", "q1", "q2", "q3", "q4", "qf"]

mock_transition_dict = {'q0': ['q2'], 'q2': ['q1', 'q4'], 'q4': ['q1'], 'q1': ['qf'], 'q3': ['q2']}

mock_emission_dict = {'q2': ['a', 'all', 'some', 'the'],
                      'q4': ['beautiful', 'big', 'handsome', 'nice', 'thin', 'thoughtful', 'ugly'],
                      'q1': ['dog', 'mouse', 'professor', 'student'],
                      'q3': ['adore', 'bit', 'chases', 'like', 'taught']}

def mock_transition(arg):
    return mock_transition_dict.get(arg, [])

def mock_emission(arg):
    return mock_emission_dict.get(arg, [])

hmm = HHM()

hmm.get_outgoing_states = MagicMock(side_effect=mock_transition)

hmm.get_emissions = MagicMock(side_effect=mock_emission)



def get_binary_by_item(list_, item):
    symbol_length = get_symbol_length(list_)
    return get_binary_string(list_.index(item), symbol_length)

def get_item_by_binary(list_, binary):
    return list_[int(binary, 2)]

big_list = [str(x) for x in range(20)]


def get_binary_enumeration(list_):
    list_ = copy(list_)
    list_.append("#")
    symbol_length = get_symbol_length(list_)
    enumeration = OrderedDict()
    for i in range(len(list_)):
        enumeration[list_[i]] = get_binary_string(i, symbol_length)

    return enumeration, symbol_length


def get_symbol_length(list_):
    return max(1, ceil(log2(len(list_))))   # log2 1 sould be 1 in this case

def get_binary_string(number, log_length):
    return str(bin(number))[2:].zfill(log_length)

assert get_binary_by_item(big_list, '13') == "01101"
assert get_item_by_binary(big_list, "01101") == '13'

alphabet_enumeration, alphabet_symbol_length = get_binary_enumeration(alphabet_list)
inverse_alphabet_enumeration = {v: k for k, v in alphabet_enumeration.items()}
assert alphabet_enumeration["a"] == "00000"
assert inverse_alphabet_enumeration["10100"] == "#"


states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
inverse_states_enumeration = {v: k for k, v in states_enumeration.items()}
assert states_enumeration["q0"] == "000"
assert inverse_states_enumeration["110"] == "#"


states_and_words_enumeration, states_and_words_symbol_length = get_binary_enumeration(states_list+words_list)
inverse_states_and_words_enumeration = {v: k for k, v in states_and_words_enumeration.items()}

assert states_and_words_enumeration["q2"] == "00010"
assert states_and_words_enumeration["adore"] == "00111"
assert inverse_states_and_words_enumeration["11010"] == "#"

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

    return lexicon_string, encoded_hypothesis_string[i:]   #TODO return list of words

def get_encoded_lexicon_length(alphabet_list, words_list):
    alphabet_symbol_length = get_binary_enumeration(alphabet_list)[1]
    delimiter_usage = (len(words_list) + 1) * alphabet_symbol_length
    words_usage = sum([len(word) for word in words_list]) * alphabet_symbol_length
    num_bits = alphabet_symbol_length + 1
    encoding_length = delimiter_usage + words_usage + num_bits
    return encoding_length

encoded_lexicon_string = encode_lexicon(alphabet_list, words_list)
encode_lexicon_length = get_encoded_lexicon_length(alphabet_list, words_list)


assert encode_lexicon_length == 616
assert len(encoded_lexicon_string) == encode_lexicon_length
assert decode_lexicon(encoded_lexicon_string)[0] == "a#adore#all#beautiful#big#bit#chases#dog#handsome#like#mouse#nice#professor#some#student#taught#the#thin#thoughtful#ugly##"


def encode_transitions(hmm, states_list):
    str_io = StringIO()
    states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
    print('0'*states_symbol_length + '1', end="", file=str_io)
    for state in states_list:
        if hmm.get_outgoing_states(state):  # print only states with the have outgoing link i.e no qf
            print(states_enumeration[state], end="", file=str_io)
            for outgoing_state in hmm.get_outgoing_states(state):
                print(states_enumeration[outgoing_state], end="", file=str_io)
            print(states_enumeration["#"], end="", file=str_io)

    print(states_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()



def decode_transitions(encoded_hypothesis_string):
    transitions_dict = dict()
    first_one_index = encoded_hypothesis_string.index('1')
    number_of_repr_bits = first_one_index
    encoded_hypothesis_string = encoded_hypothesis_string[first_one_index+1:]
    transitions_lists = []
    i = 0
    while True:
        bits = encoded_hypothesis_string[i:i+number_of_repr_bits]
        i += number_of_repr_bits
        transitions_lists.append(inverse_states_enumeration[bits])
        if transitions_lists[-2:] == ['#', '#']:
            break

    temp_list = []
    transitions_lists = transitions_lists[:-1]
    while '#' in transitions_lists:
        delimiter_index = transitions_lists.index('#')
        temp_list.append(transitions_lists[:delimiter_index])
        transitions_lists = transitions_lists[delimiter_index+1:]

    transitions_lists = temp_list

    for transitions in transitions_lists:
        transitions_dict[transitions[0]] = list()
        transitions_dict[transitions[0]].extend(transitions[1:])

    return transitions_dict, encoded_hypothesis_string[i:]

def get_encoded_transitions_length(hmm, states_list):
    state_symbols_in_strings = 0
    states_with_outgoing = 0
    for state in states_list:
        if len(hmm.get_outgoing_states(state)) > 0:
            state_symbols_in_strings += len(hmm.get_outgoing_states(state)) + 1  # +1 indicate the origin state
            states_with_outgoing += 1

    delimiter_usage = states_symbol_length * (states_with_outgoing + 1)  # +1 indicate the final extra delimiter
    states_usage = state_symbols_in_strings * states_symbol_length
    num_bits = states_symbol_length + 1
    transition_length = num_bits + delimiter_usage + states_usage

    return transition_length

encode_transitions_length = get_encoded_transitions_length(hmm, states_list)
encoded_transitions_string = encode_transitions(hmm, states_list)

assert encode_transitions_length == 55
assert len(encoded_transitions_string) == encode_transitions_length
assert decode_transitions(encoded_transitions_string)[0] == mock_transition_dict


def encode_emissions_old(hmm, states_list, words_list):
    str_io = StringIO()  # TODO sould not work
    states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
    words_enumeration, words_symbol_length = get_binary_enumeration(words_list)
    print('0'*words_symbol_length + '1', end="", file=str_io)
    for state in states_list:
        if hmm.get_emissions(state):  # print only states with emissions
            print(states_enumeration[state], end="", file=str_io)
            for emission in hmm.get_emissions(state):
                print(words_enumeration[emission], end="", file=str_io)
            print(words_enumeration["#"], end="", file=str_io)

    print(words_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()



# def decode_emissions_old(encoded_hypothesis_string):
#     emissions_dict = dict()
#     first_one_index = encoded_hypothesis_string.index('1')
#     words_number_of_repr_bits = first_one_index
#     encoded_hypothesis_string = encoded_hypothesis_string[first_one_index+1:]
#     i = 0
#     while True:
#         state_bits = encoded_hypothesis_string[i:i+states_symbol_length]
#         i += states_symbol_length
#         print(inverse_states_enumeration[state_bits])
#         while True:
#             word_bits = encoded_hypothesis_string[i:i+words_symbol_length]
#             i += words_symbol_length
#             if inverse_words_enumeration[word_bits] == '#':
#                 break
#             else:
#                 print(inverse_words_enumeration[word_bits])
#
#          # TODO finish me
#
#
#         break


    return emissions_dict, encoded_hypothesis_string[i:]
    # transitions_lists = []
    # i = 0
    # while True:
    #     bits = encoded_hypothesis_string[i:i+number_of_repr_bits]
    #     i += number_of_repr_bits
    #     transitions_lists.append(inverse_states_enumeration[bits])
    #     if transitions_lists[-2:] == ['#', '#']:
    #         break
    #
    # temp_list = []
    # transitions_lists = transitions_lists[:-1]
    # while '#' in transitions_lists:
    #     delimiter_index = transitions_lists.index('#')
    #     temp_list.append(transitions_lists[:delimiter_index])
    #     transitions_lists = transitions_lists[delimiter_index+1:]
    #
    # transitions_lists = temp_list
    #
    # for transitions in transitions_lists:
    #     transitions_dict[transitions[0]] = list()
    #     transitions_dict[transitions[0]].extend(transitions[1:])
    #
    # return transitions_dict, encoded_hypothesis_string[i:]

def get_encoded_emissions_length(hmm, states_list, words_list):
    pass


def encode_emissions(hmm, states_list, words_list):
    str_io = StringIO()
    states_and_words_list = states_list + words_list
    states_and_words_enumeration, states_and_words_symbol_length = get_binary_enumeration(states_and_words_list)
    print('0'*states_and_words_symbol_length + '1', end="", file=str_io)
    for state in states_list:
        if hmm.get_emissions(state):  # print only states with emissions
            print(states_and_words_enumeration[state], end="", file=str_io)
            for emission in hmm.get_emissions(state):
                print(states_and_words_enumeration[emission], end="", file=str_io)
            print(states_and_words_enumeration["#"], end="", file=str_io)

    print(states_and_words_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()



# # print(encode_emissions_raw(hmm, states_list, words_list))
#
# # encode_emissions_length = get_encoded_emissions_length(hmm, states_list, words_list)
# ##encoded_emissions_string = encode_emissions(hmm, states_list, words_list)
# print(len(encoded_emissions_string))
# print(decode_emissions(encoded_emissions_string)[0])
# #
# # assert encode_emissions_length ==
# # assert len(encoded_emissions_string) == encode_emissions_length
# # assert decode_emissions(encoded_emissions_string)[0] == mock_emission_dict


data = ["athindog","theuglymouse"]
mock_viterbi_dict = {"athindog": (['q0', 'q2', 'q4', 'q1', 'qf'],['a', 'thin', 'dog']),
                     "theuglymouse": (['q0', 'q2', 'q4', 'q1', 'qf'], ['the', 'ugly', 'mouse'])}

def mock_viterbi(arg):
    return mock_viterbi_dict[arg]

hmm.parse = MagicMock(side_effect=mock_viterbi)

def encode_data_by_grammar(hmm, data):
    str_io = StringIO()
    for datum in data:
        viterbi_path, segmentation_path = hmm.parse(datum)
        viterbi_index = 0
        seg_index = 0
        while True:
            current_state = viterbi_path[viterbi_index]
            transition_table = hmm.get_outgoing_states(current_state)
            viterbi_index += 1
            next_state = viterbi_path[viterbi_index]
            transition_binary = get_binary_by_item(transition_table, next_state)
            print(transition_binary, end="", file=str_io)
            if viterbi_index >= len(viterbi_path) - 1:
                break
            emission_table = hmm.get_emissions(next_state)
            emission_value = segmentation_path[seg_index]
            emission_binary = get_binary_by_item(emission_table, emission_value)
            print(emission_binary, end="", file=str_io)
            seg_index += 1

    return str_io.getvalue()

def decode_data(encoded_data_string):
    def get_item_by_binary_with_truncate(list_, binary):
        symbol_length = get_symbol_length(list_)
        needed_binary = binary[0:symbol_length]
        return list_[int(needed_binary, 2)], binary[symbol_length:]

    data = []
    while True:
        str_io = StringIO()
        current_state = "q0"
        while True:
            transition_table = hmm.get_outgoing_states(current_state)
            current_state, encoded_data_string = get_item_by_binary_with_truncate(transition_table, encoded_data_string)
            if current_state == "qf":
                data.append(str_io.getvalue())
                break
            emission_table = hmm.get_emissions(current_state)
            emission_value, encoded_data_string = get_item_by_binary_with_truncate(emission_table, encoded_data_string)
            print(emission_value, end='', file=str_io)


        if not encoded_data_string:
            break

    return data



def get_encoded_data_by_grammar_length(hmm, data):
    data_by_grammar_length = 0
    for datum in data:
        viterbi_path, seg = hmm.parse(datum)
        viterbi_index = 0
        current_state = viterbi_path[viterbi_index]
        while True:
            transition_table = hmm.get_outgoing_states(current_state)
            data_by_grammar_length += get_symbol_length(transition_table)
            viterbi_index += 1
            current_state = viterbi_path[viterbi_index]
            if viterbi_index >= len(viterbi_path) - 1:
               break
            emission_table = hmm.get_emissions(current_state)
            data_by_grammar_length += get_symbol_length(emission_table)

    return data_by_grammar_length


encoded_string = encode_data_by_grammar(hmm, data)
assert len(encoded_string) == 22
assert get_encoded_data_by_grammar_length(hmm, data) == len(encoded_string)
assert decode_data(encoded_string) == data



#########

def decode_transitions_to_raw_string(encoded_hypothesis_string):
    first_one_index = encoded_hypothesis_string.index('1')
    number_of_repr_bits = first_one_index
    encoded_hypothesis_string = encoded_hypothesis_string[first_one_index+1:]

    transitions_string = ''
    i = 0
    while True:
        bits = encoded_hypothesis_string[i:i+number_of_repr_bits]
        i += number_of_repr_bits
        transitions_string += inverse_states_enumeration[bits]
        if transitions_string.endswith("##"):
            break

    return transitions_string, encoded_hypothesis_string[i:]



# def encode_emissions_raw(hmm, states_list, words_list):
#     str_io = StringIO()
#     states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
#     words_enumeration, words_symbol_length = get_binary_enumeration(words_list)
#     print('0'*words_symbol_length + '1', end="", file=str_io)
#     for state in states_list:
#         if hmm.get_emissions(state):  # print only states with emissions
#             print(state, end="", file=str_io)
#             for emission in hmm.get_emissions(state):
#                 print(emission, end="", file=str_io)
#             print('#', end="", file=str_io)
#
#     print("#", end="", file=str_io)
#     return str_io.getvalue()
