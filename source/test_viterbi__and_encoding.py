from encoding import get_encoded_lexicon_length, get_encoded_syntactic_component_length, \
                     get_encoded_data_by_grammar_length, get_symbol_length

from new_viterbi import HMM, Lexicon, INITIAL_STATE, FINAL_STATE, viterbi

def get_segments_from_data(data):
    segments_set = set()
    for datum in data:
        segments_set |= set(datum)
    return sorted(list(segments_set))

def print_hypothesis_data(hypothesis_name, hmm, lexicon, data):
    print(hypothesis_name)
    data_by_grammar_length = get_encoded_data_by_grammar_length(hmm, lexicon, data, viterbi)
    print("data by grammar length: {}".format(data_by_grammar_length))


pabiku_data = ['golatutibudopabikudaropidaropipabikupabikudaropipabiku',
               'tibudotibudodaropidaropipabikugolatu'
               'pabikudaropigolatutibudodaropi',
               'pabikudaropidaropitibudopabikudaropigolatu',
               'tibudodaropigolatupabikutibudotibudo',
               'golatudaropigolatugolatudaropipabiku',
               'daropidaropigolatutibudogolatu',
               'tibudodaropidaropidaropipabikutibudogolatupabikupabikudaropi',
               'golatugolatupabikudaropitibudotibudogolatupabikutibudo',
               'tibudotibudotibudopabikutibudotibudo']
# pabiku_data is composed out of 12 segments.
# pabiku 16, daropi 20 , tibudo 19, golatu 14
# pabikodaropi 17

pabiku_words = ['pabiku', 'daropi', 'tibudo', 'golatu']


pabiku_segments = get_segments_from_data(pabiku_data)

assert pabiku_segments == ['a', 'b', 'd', 'g', 'i', 'k', 'l', 'o', 'p', 'r', 't', 'u']


#naive
pabiku_naive_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], pabiku_segments)})
pabiku_naive_lexicon = Lexicon(pabiku_segments)
print_hypothesis_data('pabiku naive', pabiku_naive_hmm, pabiku_naive_lexicon, pabiku_data)

#target
pabiku_target_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], pabiku_words)})
pabiku_target_lexicon = Lexicon(pabiku_words)
print_hypothesis_data('pabiku target', pabiku_target_hmm, pabiku_target_lexicon, pabiku_data)


#over segmented
pabiku_over_segmented_words = pabiku_words + ['pabikodaropi']
pabiku_over_segmented_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], pabiku_over_segmented_words)})
pabiku_over_segmented_lexicon = Lexicon(pabiku_over_segmented_words)
print_hypothesis_data('pabiku over segmented', pabiku_over_segmented_hmm, pabiku_over_segmented_lexicon, pabiku_data)

#under segmented
pabiku_under_segmented_words = pabiku_words + ['pabi', 'ku']
pabiku_under_segmented_words.remove('pabiku')
pabiku_under_segmented_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], pabiku_under_segmented_words)})
pabiku_under_segmented_lexicon = Lexicon(pabiku_under_segmented_words)
print_hypothesis_data('pabiku under segmented', pabiku_under_segmented_hmm, pabiku_under_segmented_lexicon, pabiku_data)



################################################
kaliro_data = ['kalirogolatutibudopabikudaropidaropipabikupabikudaropipabiku',
               'tibudotibudodaropidaropipabikugolatu'
               'pabikudaropigolatutibudodaropi',
               'pabikudaropidaropitibudopabikudaropigolatu',
               'tibudodaropigolatupabikutibudotibudo',
               'golatudaropigolatugolatudaropipabiku',
               'daropidaropigolatutibudogolatu',
               'tibudodaropidaropidaropipabikutibudogolatupabikupabikudaropi',
               'golatugolatupabikudaropitibudotibudogolatupabikutibudo',
               'tibudotibudotibudopabikutibudotibudo']


kaliro_words = ['kaliro','pabiku', 'daropi', 'tibudo', 'golatu']
kaliro_segments = pabiku_segments

print('kaliro')


#naive
kaliro_naive_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], kaliro_segments)})
kaliro_naive_lexicon = Lexicon(kaliro_segments)
print_hypothesis_data('kaliro naive', kaliro_naive_hmm, kaliro_naive_lexicon, kaliro_data)

#target
kaliro_target_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], kaliro_words)})
kaliro_target_lexicon = Lexicon(kaliro_words)
print_hypothesis_data('kaliro target', kaliro_target_hmm, kaliro_target_lexicon, kaliro_data)


#over segmented
kaliro_over_segmented_words = kaliro_words + ['pabikodaropi']
kaliro_over_segmented_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], kaliro_over_segmented_words)})
kaliro_over_segmented_lexicon = Lexicon(kaliro_over_segmented_words)
print_hypothesis_data('kaliro over segmented', kaliro_over_segmented_hmm, kaliro_over_segmented_lexicon, kaliro_data)

#under segmented
kaliro_under_segmented_words = kaliro_words + ['pabi', 'ku']
kaliro_under_segmented_words.remove('pabiku')
kaliro_under_segmented_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], kaliro_under_segmented_words)})
kaliro_under_segmented_lexicon = Lexicon(kaliro_under_segmented_words)
print_hypothesis_data('kaliro under segmented', kaliro_under_segmented_hmm, kaliro_under_segmented_lexicon, kaliro_data)
