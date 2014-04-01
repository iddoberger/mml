from abc import ABCMeta, abstractmethod


class AbstractLexicalComponent(metaclass=ABCMeta):
    @abstractmethod
    def get_neighbor(self): pass

    @abstractmethod
    def get_entries(self): pass


class AbstractLexicalModifier(metaclass=ABCMeta):
    @abstractmethod
    def modify_lexicon(self, entries, alphabet): pass




