from encoding import get_encoded_lexicon_length, get_encoded_syntactic_component_length, \
                     get_encoded_data_by_grammar_length, get_symbol_length

from new_viterbi import HMM, Lexicon, INITIAL_STATE, FINAL_STATE, viterbi

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

def get_segments_from_data(data):
    segments_set = set()
    for datum in data:
        segments_set |= set(datum)
    return sorted(list(segments_set))

pabiku_segments = get_segments_from_data(pabiku_data)

assert pabiku_segments == ['a', 'b', 'd', 'g', 'i', 'k', 'l', 'o', 'p', 'r', 't', 'u']

pabiku_target_hmm = HMM({INITIAL_STATE: ['q1'],
                        'q1': ([FINAL_STATE, 'q1'], pabiku_words)})


pabiku_target_lexicon = Lexicon(pabiku_words)

for datum in pabiku_data:
    viterbi_result = viterbi(pabiku_target_hmm, pabiku_target_lexicon, datum)
    print(viterbi_result)