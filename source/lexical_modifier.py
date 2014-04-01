from abstractions import AbstractLexicalModifier
from random import choice, randint


class LexicalModifier(AbstractLexicalModifier):
    def modify_lexicon(self, entries, alphabet):
        pass


    def remove_segment_from_entry(self, entries, alphabet):
         while True:
            chosen_entry = choice(entries)
            entry_length = len(chosen_entry)
            chosen_position = randint(0, entry_length)
            new_entry = chosen_entry[0:chosen_position] + chosen_entry[chosen_position+1:]
            if new_entry not in entries:
                entries.append(new_entry)
                entries.remove(chosen_entry)
                return [new_entry], [chosen_entry]

    def add_segment_to_entry(self, entries, alphabet):
        while True:
            chosen_entry = choice(entries)
            entry_length = len(chosen_entry)
            chosen_segment = choice(alphabet)
            chosen_position = randint(0, entry_length)

            new_entry = chosen_entry[:chosen_position] + chosen_segment + chosen_entry[chosen_position:]
            if new_entry not in entries:
                entries.append(new_entry)
                return [new_entry], []


class SillyLexicalModifier(AbstractLexicalModifier):
    def modify_lexicon(self, entries, alphabet):
        pass

    def add_two_segment_to_end_of_entry(self, entries, alphabet):
        while True:
            chosen_entry = choice(entries)
            new_entry = chosen_entry + choice(alphabet) + choice(alphabet)
            if new_entry not in entries:
                entries.append(new_entry)
                entries.remove(chosen_entry)
                return [new_entry], [chosen_entry]