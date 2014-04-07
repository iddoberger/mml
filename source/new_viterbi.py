from math import log

USE_NULL_SEGMENT = True

NULL_SEGMENT = '-'

INITIAL_STATE = 'q0'
FINAL_STATE = 'qf'


#hmm_dict: the inner states has a tuple (transitions_list, emissions_list),  INITIAL_STATE has only transitions_list,
#and FINAL_STATE is not there


hmm_dict = {'q0':  ['q2'],
            'q1': (['qf'], ['dog', 'mouse', 'professor', 'student']),
            'q2': (['q1', 'q4'], ['a', 'all', 'some', 'the']),
            'q3': (['q2'], ['adore', 'bit', 'chases', 'like', 'taught']),
            'q4': (['q1'], ['beautiful', 'big', 'handsome', 'nice', 'thin', 'thoughtful', 'ugly'])}



class HMM:
    def __init__(self, hmm_dict):
        hmm_dict_key_list = list(hmm_dict.keys())
        hmm_dict_key_list.remove(INITIAL_STATE)
        self.inner_states = hmm_dict_key_list
        initial_state_transitions = hmm_dict.pop(INITIAL_STATE)


        self.transitions = {k: v[0] for (k, v) in hmm_dict.items()}
        self.transitions[INITIAL_STATE] = initial_state_transitions

        self.emissions = {k: v[1] for (k, v) in hmm_dict.items()}

    def get_states(self):
        return [INITIAL_STATE] + self.inner_states + [FINAL_STATE]



hmm = HMM(hmm_dict)



from math import log


# A Viterbi prefix, that holds information regarding a prefix of data (for inner usage).
# Each Viterbi cell in the viterbi_seg algorithm hold a dictionary of such prefixes.
class _ViterbiPrefix:
    def __init__(self, prefix, prob, seen_length):
        self.prefix = prefix
        self.prob = prob
        self.seen_length = seen_length
        self.back_pointer = []

    def __len__(self):
        return len(self.prefix)


    def set_back_pointer(self, state, bp_prefix, column):
        self.back_pointer = [state, bp_prefix, column]

    def get_back_pointer_state(self):
        return self.back_pointer[0]

    def get_back_pointer_prefix(self):
        return self.back_pointer[1]

    def get_back_pointer_column(self):
        return self.back_pointer[2]


# A variant of Viterbi that works with unsegmented data (i.e. no separation between lexical words),
# and chooses the best possible sequence of states which reflects the best segmentation.
# Each cell contains a dictionary of relevant prefixes up to that point.
# Assumptions:
# a) obs is not the empty string.
# b) each char of obs exists in H.lexicon.
def viterbi(hmm, lexicon, observation):
    length_of_observation = len(observation)
    all_states = hmm.states + [hmm.initial_state, hmm.final_state]
    viterbi_table = {state: [{} for j in range(length_of_observation)] for state in all_states}     # Each cell hold dict of lexical entries

    # Initialize the final cell
    final_cell = _ViterbiPrefix('', float("-inf"), length_of_observation)

    start_prefixes = get_lexical_prefixes(lexicon, observation, [0])
    seen_lengths = set()

    # Initialize the first column
    for current_state in hmm.states:
        for prefix in start_prefixes:
            # if initial prob or emission prob are 0, then the probability of printing this prefix is 0.
            if hmm.initial_prob[current_state] == 0 or hmm.emission_prob[current_state][prefix] == 0:
                viterbi_table[current_state][0][prefix] = _ViterbiPrefix(prefix, 0, len(prefix))
            else:
                viterbi_table[current_state][0][prefix] = _ViterbiPrefix(prefix, log(hmm.initial_prob[current_state]) + log(hmm.emission_prob[current_state][prefix]), len(prefix))
            viterbi_table[current_state][0][prefix].set_back_pointer(hmm.initial_state, '', -1)

            seen_lengths.add(viterbi_table[current_state][0][prefix].seen_length)


    # fill out the rest of the table
    # (we can always compose the data out of basic lexical elements)
    for observation_position in range(1, length_of_observation):
        # find cell prefixes
        column_prefixes = get_lexical_prefixes(lexicon, observation, seen_lengths)
        seen_lengths.clear()

        for current_state in hmm.states:
            # fill the cell with the relevant prefixes
            for prefix in column_prefixes:
                viterbi_table[current_state][observation_position][prefix] = _ViterbiPrefix(prefix, float("-inf"), -1)

            for current_prefix in list(viterbi_table[current_state][observation_position].values()):
                for previous_state in hmm.states:
                    for previous_prefix in list(viterbi_table[previous_state][observation_position-1].values()):

                        total_chars = previous_prefix.seen_length

                        # if the prev prefix and current prefix fit the data in the corresponding place,
                        # then update the probability.
                        if previous_prefix.prefix + current_prefix.prefix == \
                                observation[total_chars - len(previous_prefix):total_chars + len(current_prefix)]:
                            if not hmm.transition_prob[previous_state][current_state] == 0 and not hmm.emission_prob[current_state][current_prefix.prefix] == 0\
                                and not previous_prefix.prob == 0:
                                probability = previous_prefix.prob + log(hmm.transition_prob[previous_state][current_state]) + log(hmm.emission_prob[current_state][current_prefix.prefix])
                                if current_prefix.prob < probability:
                                    current_prefix.prob = probability
                                    current_prefix.seen_length = (previous_prefix.seen_length + len(current_prefix))
                                    current_prefix.set_back_pointer(previous_state, previous_prefix.prefix, observation_position-1)


                # Add the length seen so far, so that next iteration could easily find proper prefixes
                seen_lengths.add(current_prefix.seen_length)

                # In case we've seen all input data, update the final cell
                if current_prefix.seen_length == length_of_observation:
                    if not hmm.transition_prob[current_state][hmm.final_state] == 0:
                        final_transition = current_prefix.prob + log(hmm.transition_prob[current_state][hmm.final_state])

                        if final_cell.prob < final_transition:
                            final_cell.prob = final_transition
                            final_cell.set_back_pointer(current_state, current_prefix.prefix, observation_position)



    if final_cell.prob == float("-inf"):
        return float("-inf"), float("-inf"), float("-inf"), float("-inf")


    # Follow backpointers to find the best path
    current_state = final_cell.get_back_pointer_state()
    current_prefix = final_cell.get_back_pointer_prefix()
    current_column = final_cell.get_back_pointer_column()

    # Paths to follow
    state_path = [hmm.final_state, current_state]
    seg_path = [current_prefix]
    prob_path = [hmm.transition_prob[current_state][hmm.final_state]]
    emission_path = [hmm.emission_prob[current_state][current_prefix]]

    while True:
        current_cell = viterbi_table[current_state][current_column][current_prefix]
        temp_state = current_state # for prob path

        current_state = current_cell.get_back_pointer_state()
        current_prefix = current_cell.get_back_pointer_prefix()
        current_column = current_cell.get_back_pointer_column()

        if current_state == hmm.initial_state:
            state_path += [hmm.initial_state]
            prob_path += [hmm.initial_prob[temp_state]]

            break

        # Since we haven't reached the initial state yet, just add the relevant
        # information to the proper list.
        state_path += [current_state]
        prob_path += [hmm.transition_prob[current_state][temp_state]]
        emission_path += [hmm.emission_prob[current_state][current_prefix]]
        seg_path += [current_prefix]


    state_path.reverse()
    prob_path.reverse()
    emission_path.reverse()
    seg_path.reverse()

    return state_path, prob_path, emission_path, seg_path


# This procedure takes a lexicon, obs and a list of starting points,
# and returns a list of all possible prefixes
# from each one of the starting points (every element in the list is unique).
def get_lexical_prefixes(lexicon, complete_observation, starting_positions):
    prefix_list = []
    lex_entries = lexicon.get_entry_values()
    longest_entry = lexicon.get_longest_entry()

    for start_position in starting_positions:
        from_start_position_length = len(complete_observation) - start_position
        maximal_block_size = min(from_start_position_length, longest_entry)
        truncated_observation = complete_observation[start_position:start_position+maximal_block_size]

        for i in range(1, len(truncated_observation)+1):
            current_prefix = truncated_observation[0:i]
            if current_prefix in lex_entries and current_prefix not in prefix_list:
                prefix_list.append(current_prefix)

    return prefix_list