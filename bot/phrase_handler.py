import random

import phrases
import phrase_types


class PhraseHandler:
    def __init__(self):
        self._phrases = phrases.phrases

    def get_phrase(self, phrase_type: phrase_types.PhraseTypes):
        return random.choice(self._phrases[phrase_type])
