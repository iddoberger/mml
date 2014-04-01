from abstractions import AbstractLexicalComponent, abstractmethod


#lexical_modifier = eval(Configuration["lexical_modifier"])()

class Lexicon(AbstractLexicalComponent):
    def __init__(self, lexical_modifier):
        self.lexical_modifier = lexical_modifier


    def get_neighbor(self):
        pass

    @abstractmethod
    def get_entries(self): pass