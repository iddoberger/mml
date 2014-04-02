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

mock_transition_dict = {'q0': ['q2'], 'q2': ['q1', 'q4'], 'q4': ['q1'], 'q1': ['qf'], 'q1': ['q3'], 'q3': ['q2']}

mock_emission_dict = {'q2': ['a', 'all', 'some', 'the'],
                      'q4': ['beautiful', 'big', 'handsome', 'nice', 'thin', 'thoughtful', 'ugly'],
                      'q1': ['dog', 'mouse', 'professor', 'student'],
                      'q3': ['adore', 'bit', 'chases', 'like', 'taught']}

def mock_transition(arg):
    return mock_transition_dict.get(arg, [])

def mock_emission(arg):
    return mock_emission_dict.get(arg, default=[])

hmm = HHM()

hmm.get_outgoing_states = MagicMock(side_effect=mock_transition)

hmm.get_emission = MagicMock(side_effect=mock_emission)


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
inverse_alphabet_enumeration = {v: k for k, v in alphabet_enumeration.items()}
assert alphabet_enumeration["a"] == "00000"
assert inverse_alphabet_enumeration["10100"] == "#"

words_enumeration, words_symbol_length = get_binary_enumeration(words_list)
inverse_words_enumeration = {v: k for k, v in words_enumeration.items()}
assert words_enumeration["adore"] == "00001"
assert inverse_words_enumeration["10100"] == "#"

states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
inverse_states_enumeration = {v: k for k, v in states_enumeration.items()}
assert states_enumeration["q0"] == "000"
assert inverse_states_enumeration["110"] == "#"

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

    return lexicon_string, encoded_hypothesis_string[i:]

def encode_lexicon_length(alphabet_list, words_list):
    alphabet_symbol_length = get_binary_enumeration(alphabet_list)[1]
    delimiter_usage = (len(words_list) + 1) * alphabet_symbol_length
    words_usage = sum([len(word) for word in words_list]) * alphabet_symbol_length
    num_bits = alphabet_symbol_length + 1
    encoding_length = delimiter_usage + words_usage + num_bits
    return encoding_length

encoded_lexicon_string = encode_lexicon(alphabet_list, words_list)
encode_lexicon_length = encode_lexicon_length(alphabet_list, words_list)

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




def encode_transitions_length(hmm, states_list):
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


encoded_transitions_string = encode_transitions(hmm, states_list)


encode_transitions_length = encode_transitions_length(hmm, states_list)
encoded_transitions_string = encode_transitions(hmm, states_list)


assert encode_transitions_length == 55
assert len(encoded_transitions_string) == encode_transitions_length
assert decode_transitions(encoded_transitions_string)[0] == mock_transition_dict





viterbi_path = ['q0', 'q2', 'q4', 'q1', 'qf']
seg = ['a', 'thin', 'dog']

combined_list = viterbi_path[:1] + [x for t in zip(viterbi_path[1:-1], seg) for x in t] + viterbi_path[-1:]






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
