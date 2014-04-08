from collections import OrderedDict
from math import log2, ceil
from io import StringIO
from copy import copy


from unittest.mock import MagicMock


class SyntacticComponent():
    pass


alphabet_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'y']
words_list = ['a', 'adore', 'all', 'beautiful', 'big', 'bit', 'chases', 'dog', 'handsome', 'like', 'mouse', 'nice', 'professor', 'some', 'student', 'taught', 'the', 'thin', 'thoughtful', 'ugly']
states_list = ["q0", "q1", "q2", "q3", "q4", "qf"]

mock_transition_dict = {'q0': ['q2'], 'q1': ['qf'], 'q2': ['q1', 'q4'], 'q3': ['q2'], 'q4': ['q1'], 'qf': []}
transition_dict_no_nulls = {'q0': ['q2'], 'q1': ['qf'], 'q2': ['q1', 'q4'], 'q3': ['q2'], 'q4': ['q1']}

mock_emission_dict = {'q0': [],
                      'q1': ['dog', 'mouse', 'professor', 'student'],
                      'q2': ['a', 'all', 'some', 'the'],
                      'q3': ['adore', 'bit', 'chases', 'like', 'taught'],
                      'q4': ['beautiful', 'big', 'handsome', 'nice', 'thin', 'thoughtful', 'ugly'],
                      'qf': []}

emission_dict_no_nulls = {'q1': ['dog', 'mouse', 'professor', 'student'],
                          'q2': ['a', 'all', 'some', 'the'],
                          'q3': ['adore', 'bit', 'chases', 'like', 'taught'],
                          'q4': ['beautiful', 'big', 'handsome', 'nice', 'thin', 'thoughtful', 'ugly']}



def mock_transition(arg):
    return mock_transition_dict.get(arg, [])


def mock_emission(arg):
    return mock_emission_dict.get(arg, [])

syntactic_component = SyntacticComponent()

syntactic_component.get_outgoing_states = MagicMock(side_effect=mock_transition)

syntactic_component.get_emissions = MagicMock(side_effect=mock_emission)


def get_binary_by_item(list_, item):
    if not list_:
        raise ValueError("list is Empty")
    if len(list_) == 1:
        return ''
    symbol_length = get_symbol_length(list_)
    return get_binary_string(list_.index(item), symbol_length)


def get_item_by_binary(list_, binary):
    return list_[int(binary, 2)]

big_list = [str(x) for x in range(20)]


def get_binary_enumeration(list_):
    list_ = copy(list_)
    list_.insert(0, "#")
    symbol_length = get_symbol_length(list_)
    enumeration = OrderedDict()
    for i in range(len(list_)):
        enumeration[list_[i]] = get_binary_string(i, symbol_length)

    return enumeration, symbol_length


def get_symbol_length(list_):
    return ceil(log2(len(list_)))


def get_binary_string(number, log_length):
    return str(bin(number))[2:].zfill(log_length)

assert get_binary_by_item(big_list, '13') == "01101"
assert get_item_by_binary(big_list, "01101") == '13'

alphabet_enumeration, alphabet_symbol_length = get_binary_enumeration(alphabet_list)
inverse_alphabet_enumeration = {v: k for k, v in alphabet_enumeration.items()}
assert alphabet_enumeration["a"] == "00001"
assert alphabet_enumeration["y"] == "10100"
assert inverse_alphabet_enumeration["00000"] == "#"


states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
inverse_states_enumeration = {v: k for k, v in states_enumeration.items()}
assert states_enumeration["q0"] == "001"
assert states_enumeration["qf"] == "110"
assert inverse_states_enumeration["000"] == "#"

words_enumeration, words_symbol_length = get_binary_enumeration(words_list)
inverse_words_enumeration = {v: k for k, v in words_enumeration.items()}



##### Lexicon #####

def encode_lexicon(alphabet_list, words_list):    # with 0*1 prefix, ## ending
    str_io = StringIO()
    alphabet_enumeration, alphabet_symbol_length = get_binary_enumeration(alphabet_list)
    print('0'*alphabet_symbol_length + '1', end="", file=str_io)
    for word in words_list:
        for char in word:
            print(alphabet_enumeration[char], end="", file=str_io)
        print(alphabet_enumeration["#"], end="", file=str_io)
    print(alphabet_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()


def decode_lexicon(encoded_lexicon_string):
    first_one_index = encoded_lexicon_string.index('1')
    number_of_repr_bits = first_one_index
    encoded_lexicon_string = encoded_lexicon_string[first_one_index+1:]

    lexicon_string = ''
    i = 0
    while True:
        bits = encoded_lexicon_string[i:i+number_of_repr_bits]
        i += number_of_repr_bits
        lexicon_string += inverse_alphabet_enumeration[bits]
        if lexicon_string.endswith("##"):
            break

    words_list = lexicon_string[:-2].split('#')
    return words_list


def get_encoded_lexicon_length(alphabet_symbol_length, words_list):
    delimiter_usage = (len(words_list) + 1) * alphabet_symbol_length
    words_usage = sum([len(word) for word in words_list]) * alphabet_symbol_length
    num_bits = alphabet_symbol_length + 1
    encoding_length = delimiter_usage + words_usage + num_bits
    return encoding_length

encoded_lexicon_string = encode_lexicon(alphabet_list, words_list)
encode_lexicon_length = get_encoded_lexicon_length(alphabet_symbol_length, words_list)


assert encode_lexicon_length == 616
assert len(encoded_lexicon_string) == encode_lexicon_length
assert decode_lexicon(encoded_lexicon_string) == words_list

##### Syntactic Component #####

def encode_syntactic_component(syntactic_component, states_list, words_list):  # with 0*1 prefix,
    str_io = StringIO()                                                        # double state's # after transitions
    #transitions                                                               # double word's #  at ending (after emissions)
    states_enumeration, states_symbol_length = get_binary_enumeration(states_list)
    print('0'*states_symbol_length + '1', end="", file=str_io)
    for state in states_list:
        if syntactic_component.get_outgoing_states(state):  # print only states with the have outgoing link i.e no qf
            print(states_enumeration[state], end="", file=str_io)
            for outgoing_state in syntactic_component.get_outgoing_states(state):
                print(states_enumeration[outgoing_state], end="", file=str_io)
            print(states_enumeration["#"], end="", file=str_io)

    print(states_enumeration["#"], end="", file=str_io)
    #emissions
    words_enumeration, words_symbol_length = get_binary_enumeration(words_list)
    for state in states_list:
        if syntactic_component.get_emissions(state):  # print only states with emissions
            print(states_enumeration[state], end="", file=str_io)
            for emission in syntactic_component.get_emissions(state):
                print(words_enumeration[emission], end="", file=str_io)
            print(words_enumeration["#"], end="", file=str_io)
    print(words_enumeration["#"], end="", file=str_io)
    return str_io.getvalue()


def decode_syntactic_component(encoded_syntactic_component_string):
    first_one_index = encoded_syntactic_component_string.index('1')
    number_of_repr_bits = first_one_index
    encoded_transitions_string = encoded_syntactic_component_string[first_one_index+1:]
    #transitions
    transitions_dict = dict()
    transitions_lists = []
    i = 0
    while True:
        bits = encoded_transitions_string[i:i+number_of_repr_bits]
        i += number_of_repr_bits
        transitions_lists.append(inverse_states_enumeration[bits])
        if transitions_lists[-2:] == ['#', '#']:
            i += number_of_repr_bits
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

    encoded_syntactic_component_string = encoded_syntactic_component_string[i+1:]

    #emissons
    emissions_dict = dict()
    i = 0
    while True:
        state_bits = encoded_syntactic_component_string[i:i+states_symbol_length]
        i += states_symbol_length
        current_state = inverse_states_enumeration[state_bits]
        emissions_dict[current_state] = list()
        while True:
            word_bits = encoded_syntactic_component_string[i:i+words_symbol_length]
            i += words_symbol_length
            if inverse_words_enumeration[word_bits] == '#':
                break
            else:
                current_word = inverse_words_enumeration[word_bits]
                emissions_dict[current_state].append(current_word)

        word_bits = encoded_syntactic_component_string[i:i+words_symbol_length]
        if inverse_words_enumeration[word_bits] == '#':
            break

    return transitions_dict, emissions_dict


def get_encoded_syntactic_component_length(syntactic_component, states_list, words_symbol_length):
    #transitions
    states_symbol_length = get_symbol_length(states_list)
    state_symbols_in_transitions = 0
    states_with_outgoing = 0
    for state in states_list:
        if len(syntactic_component.get_outgoing_states(state)) > 0:
            state_symbols_in_transitions += len(syntactic_component.get_outgoing_states(state)) + 1  # +1 indicate the origin state
            states_with_outgoing += 1

    delimiter_usage = states_symbol_length * (states_with_outgoing + 1)  # +1 indicate the final extra delimiter
    states_usage = state_symbols_in_transitions * states_symbol_length
    num_bits = states_symbol_length + 1
    transition_length = num_bits + delimiter_usage + states_usage

    #emissions
    num_of_emissions = 0
    states_with_emissions = 0
    for state in states_list:
        if len(syntactic_component.get_emissions(state)) > 0:
            states_with_emissions += 1
            num_of_emissions += len(syntactic_component.get_emissions(state))


    delimiter_usage = (states_with_emissions + 1) * words_symbol_length   # +1 indicate the final extra delimiter
    emission_usage = states_with_emissions * states_symbol_length + (words_symbol_length * num_of_emissions)
    emissions_length = delimiter_usage + emission_usage

    encoded_syntactic_component_length = transition_length + emissions_length

    return encoded_syntactic_component_length



def get_encoded_syntactic_component_length_v2(syntactic_component, states_list, words_symbol_length):
    states_symbol_length = get_symbol_length(states_list)
    state_symbols_in_transitions = 0
    num_of_emissions = 0
    for state in states_list:
        if len(syntactic_component.get_outgoing_states(state)) > 0:
            state_symbols_in_transitions += len(syntactic_component.get_outgoing_states(state)) + 1  # +1 indicate the origin state
            num_of_emissions += len(syntactic_component.get_emissions(state))

    content_usage = (state_symbols_in_transitions * states_symbol_length) + (num_of_emissions * words_symbol_length)
    delimiter_usage = (len(states_list) * words_symbol_length) + ((len(states_list) + 1) * states_symbol_length)
    num_bits = states_symbol_length + 1
    encoded_syntactic_component_length = num_bits + delimiter_usage + content_usage


    return encoded_syntactic_component_length


encoded_syntactic_component_string = encode_syntactic_component(syntactic_component, states_list, words_list)
encoded_syntactic_component_length = get_encoded_syntactic_component_length(syntactic_component, states_list, words_symbol_length)

assert encoded_syntactic_component_length == 192
#print(get_encoded_syntactic_component_length_v2(syntactic_component, states_list, words_symbol_length))
assert len(encoded_syntactic_component_string) == encoded_syntactic_component_length
assert decode_syntactic_component(encoded_syntactic_component_string) == (transition_dict_no_nulls, emission_dict_no_nulls)




##### Data by Grammar #####

data = ["athindog","theuglymouse"]
mock_viterbi_dict = {"athindog": (['q0', 'q2', 'q4', 'q1', 'qf'],['a', 'thin', 'dog']),
                     "theuglymouse": (['q0', 'q2', 'q4', 'q1', 'qf'], ['the', 'ugly', 'mouse'])}

def mock_viterbi(syntactic_component, lexicon, datum):
    return mock_viterbi_dict[datum]

viterbi = MagicMock(side_effect=mock_viterbi)

def encode_data_by_grammar(syntactic_component, lexicon, data, viterbi):   #no prefix, no delimiter at all
    str_io = StringIO()
    for datum in data:
        states_path, emissions_path = viterbi(syntactic_component, lexicon, datum)
        states_index = 0
        segmentation_index = 0
        while True:
            current_state = states_path[states_index]
            transition_table = syntactic_component.get_outgoing_states(current_state)
            states_index += 1
            next_state = states_path[states_index]
            transition_binary = get_binary_by_item(transition_table, next_state)
            print(transition_binary, end="", file=str_io)
            if states_index >= len(states_path) - 1:
                break
            emission_table = syntactic_component.get_emissions(next_state)
            emission_value = emissions_path[segmentation_index]
            emission_binary = get_binary_by_item(emission_table, emission_value)
            print(emission_binary, end="", file=str_io)
            segmentation_index += 1

    return str_io.getvalue()

def decode_data(encoded_data_string):
    def get_item_by_binary_with_truncate(list_, full_binary_string):
        symbol_length = get_symbol_length(list_)
        if not symbol_length:
            return list_[0], full_binary_string
        needed_binary = full_binary_string[0:symbol_length]
        return list_[int(needed_binary, 2)], full_binary_string[symbol_length:]

    data = []
    while True:
        str_io = StringIO()
        current_state = "q0"
        while True:
            transition_table = syntactic_component.get_outgoing_states(current_state)
            current_state, encoded_data_string = get_item_by_binary_with_truncate(transition_table, encoded_data_string)
            if current_state == "qf":
                data.append(str_io.getvalue())
                break
            emission_table = syntactic_component.get_emissions(current_state)
            emission_value, encoded_data_string = get_item_by_binary_with_truncate(emission_table, encoded_data_string)
            print(emission_value, end='', file=str_io)


        if not encoded_data_string:
            break

    return data



def get_encoded_data_by_grammar_length(syntactic_component, lexicon, data, viterbi):
    data_by_grammar_length = 0
    for datum in data:
        viterbi_result = viterbi(syntactic_component, lexicon, datum)
        if not viterbi_result:
            return float("-INF")
        else:
            viterbi_path = viterbi_result[0]
        viterbi_index = 0
        current_state = viterbi_path[viterbi_index]
        while True:
            transitions_list = syntactic_component.get_outgoing_states(current_state)
            data_by_grammar_length += get_symbol_length(transitions_list)
            viterbi_index += 1
            current_state = viterbi_path[viterbi_index]
            if viterbi_index >= len(viterbi_path) - 1:
               break
            emissions_list = syntactic_component.get_emissions(current_state)
            data_by_grammar_length += get_symbol_length(emissions_list)

    return data_by_grammar_length


encoded_string = encode_data_by_grammar(syntactic_component, words_list, data, viterbi)


assert len(encoded_string) == 16
assert get_encoded_data_by_grammar_length(syntactic_component, words_list, data, viterbi) == len(encoded_string)
assert decode_data(encoded_string) == data

