from new_viterbi import HMM, Lexicon, INITIAL_STATE, FINAL_STATE, NULL_SEGMENT, USE_NULL_SEGMENT
from math import log
from collections import namedtuple

# A Viterbi prefix, that holds information regarding a prefix of data (for inner usage).
# Each Viterbi cell in the viterbi_seg algorithm hold a dictionary of such prefixes.
class _ViterbiPrefix:
    def __init__(self, prefix_string, probability, position):
        self.prefix_string = prefix_string
        self.probability = probability
        self.position = position
        self.back_pointer = []

    def __len__(self):
        return len(self.prefix_string)

    def __str__(self):
        return self.prefix_string

    def set_back_pointers(self, state, prefix_string, column):
        self.back_pointer = [state, prefix_string, column]

    def get_state_back_pointer(self):
        return self.back_pointer[0]

    def get_prefix_back_pointer(self):
        return self.back_pointer[1]

    def get_column_back_pointer(self):
        return self.back_pointer[2]


ViterbiResult = namedtuple('ViterbiResult', ['states_path', 'emissions_path'])

# A variant of Viterbi that works with unsegmented data (i.e. no separation between lexical words),
# and chooses the best possible sequence of states which reflects the best segmentation.
# Each cell contains a dictionary of relevant prefixes up to that point.
# Assumptions:
# a) obs is not the empty string.
# b) each char of obs exists in H.lexicon.
def viterbi(hmm, lexicon, observation):
    observation_length = len(observation)
    viterbi_table = {state: [{} for _ in range(observation_length)] for state in hmm.get_states()}  # Each cell holds a
                                                                                                    # dict of lexical entries
    # Initialize the final cell
    final_cell = _ViterbiPrefix('', float("-inf"), observation_length)

    initial_prefix_strings = get_lexical_prefixes(lexicon, observation, [0])   # maybe get only emission availabe to the states
    seen_positions = set()

    # Initialize the first column
    for current_state in hmm.inner_states:
        for prefix_string in initial_prefix_strings:
            # if initial prob or emission prob are 0, then the probability of printing this prefix is 0.
            if not hmm.get_transition_probability(INITIAL_STATE, current_state) or \
               not hmm.get_emission_probability(current_state, prefix_string):
                viterbi_table[current_state][0][prefix_string] = _ViterbiPrefix(prefix_string, 0, len(prefix_string))
            else:
                log_probability = log(hmm.get_transition_probability(INITIAL_STATE, current_state)) + \
                                  log(hmm.get_emission_probability(current_state, prefix_string))
                viterbi_table[current_state][0][prefix_string] = _ViterbiPrefix(prefix_string, log_probability,
                                                                                len(prefix_string))

            viterbi_table[current_state][0][prefix_string].set_back_pointers(INITIAL_STATE, '', -1)

            seen_positions.add(viterbi_table[current_state][0][prefix_string].position)


    # fill out the rest of the table
    # (we can always compose the data out of basic lexical elements)
    for observation_position in range(1, observation_length):
        # find cell prefixes
        column_prefix_strings = get_lexical_prefixes(lexicon, observation, seen_positions)
        seen_positions.clear()

        for current_state in hmm.inner_states:
            # fill the cell with the relevant prefixes
            for prefix_string in column_prefix_strings:
                viterbi_table[current_state][observation_position][prefix_string] = _ViterbiPrefix(prefix_string,
                                                                                                   float("-inf"), -1)

            for current_viterbi_prefix in viterbi_table[current_state][observation_position].values():
                for previous_state in hmm.inner_states:
                    for previous_viterbi_prefix in viterbi_table[previous_state][observation_position-1].values():
                        previous_position = previous_viterbi_prefix.position

                        # if the previous prefix and current prefix fit the data in the corresponding place,
                        # then update the probability.
                        combined_prefixes = str(previous_viterbi_prefix) + str(current_viterbi_prefix)
                        start_index = previous_position - len(previous_viterbi_prefix)
                        end_index = previous_position + len(current_viterbi_prefix)
                        #print(observation[start_index:end_index])
                        if combined_prefixes == observation[start_index:end_index]:
                            if hmm.get_transition_probability(previous_state, current_state) \
                                    and hmm.get_emission_probability(current_state, str(current_viterbi_prefix)) \
                                    and previous_viterbi_prefix.probability:

                                probability = previous_viterbi_prefix.probability + \
                                              log(hmm.get_transition_probability(previous_state, current_state)) + \
                                              log(hmm.get_emission_probability(current_state, str(current_viterbi_prefix)))

                                if current_viterbi_prefix.probability < probability:
                                    current_viterbi_prefix.probability = probability
                                    current_viterbi_prefix.position = (previous_viterbi_prefix.position + len(current_viterbi_prefix))
                                    current_viterbi_prefix.set_back_pointers(previous_state, str(previous_viterbi_prefix),
                                                                             observation_position-1)

                # Add the length seen so far, so that next iteration could easily find proper prefixes
                seen_positions.add(current_viterbi_prefix.position)

                # In case we've seen all input data, update the final cell
                if current_viterbi_prefix.position == observation_length:
                    if hmm.get_transition_probability(current_state, FINAL_STATE):
                        final_transition = current_viterbi_prefix.probability + \
                                           log(hmm.get_transition_probability(current_state, FINAL_STATE))

                        if final_cell.probability < final_transition:
                            final_cell.probability = final_transition
                            final_cell.set_back_pointers(current_state, str(current_viterbi_prefix), observation_position)

    if final_cell.probability == float("-inf"):
        return None

    # Follow back pointers to find the best path
    current_state = final_cell.get_state_back_pointer()
    current_viterbi_prefix = final_cell.get_prefix_back_pointer()
    current_column = final_cell.get_column_back_pointer()

    # Paths to follow
    backward_states_path = [FINAL_STATE, current_state]
    backward_emissions_path = [current_viterbi_prefix]

    while True:
        current_cell = viterbi_table[current_state][current_column][current_viterbi_prefix]

        current_state = current_cell.get_state_back_pointer()
        current_viterbi_prefix = current_cell.get_prefix_back_pointer()
        current_column = current_cell.get_column_back_pointer()

        if current_state == INITIAL_STATE:
            backward_states_path += [INITIAL_STATE]
            break

        backward_states_path += [current_state]
        backward_emissions_path += [current_viterbi_prefix]

    return ViterbiResult(list(reversed(backward_states_path)), list(reversed(backward_emissions_path)))


# This procedure takes a lexicon, obs and a list of starting points,
# and returns a list of all possible prefixes
# from each one of the starting points (every element in the list is unique).
def get_lexical_prefixes(lexicon, complete_observation, starting_positions):
    prefix_list = []
    longest_entry = lexicon.get_maximal_entry_length()

    for start_position in starting_positions:
        from_start_position_length = len(complete_observation) - start_position
        maximal_block_size = min(from_start_position_length, longest_entry)
        truncated_observation = complete_observation[start_position:start_position+maximal_block_size]

        for i in range(1, len(truncated_observation)+1):
            current_prefix = truncated_observation[0:i]
            if current_prefix in lexicon.entries and current_prefix not in prefix_list:
                prefix_list.append(current_prefix)

    if NULL_SEGMENT in lexicon.entries:
        prefix_list.append(NULL_SEGMENT)

    return prefix_list




##############

hmm = HMM({INITIAL_STATE: ['q1'],
          'q1': (['q1', 'q2'], ['cat', 'dog']),
          'q2': (['q2', FINAL_STATE], ['s', NULL_SEGMENT])})


lexicon = Lexicon(['cat', 'dog', 's', NULL_SEGMENT])

assert viterbi(hmm, lexicon, 'cat').emissions_path == ['cat', NULL_SEGMENT]
assert viterbi(hmm, lexicon, 'cats').emissions_path == ['cat', 's']



hmm = HMM({INITIAL_STATE: ['q1'],
          'q1': (['q1', 'q2'], ['cat', 'dog']),
          'q2': (['q2', 'q3'], ['s', NULL_SEGMENT]),
          'q3': (['q3', FINAL_STATE], ['full', NULL_SEGMENT])})


lexicon = Lexicon(['cat', 'dog', 's', 'full', NULL_SEGMENT])


assert viterbi(hmm, lexicon, 'catfull').emissions_path == ['cat', NULL_SEGMENT, 'full']
assert viterbi(hmm, lexicon, 'cat').emissions_path == ['cat', NULL_SEGMENT, NULL_SEGMENT]
