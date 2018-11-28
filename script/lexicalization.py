import logging
from sklearn.base import BaseEstimator


class FallBackLexicalize(BaseEstimator):

    def __init__(self, models):

        self.models = models 

    def fit(self, data_alignment=None):

        for model in self.models:

            model.fit(data_alignment)

    def lexicalize(self, data):

        for model in self.models:

            lexicalization = model.lexicalize(data)

            if lexicalization:

                return lexicalization

        return None



class LexicalizeAsAligned(BaseEstimator):

    def __init__(self, data_alignment=None):

        self.data_alignment = data_alignment
        self.logger = logging.getLogger(self.__class__.__name__)

    def fit(self, data_alignment=None):

        self.data_alignment = data_alignment


    def lexicalize(self, data):

        subject_lexicalization = self.data_alignment.get_subject_lexicalization(data['subject'])

        if subject_lexicalization:

            self.logger.debug(f'subject: [{data["subject"]}] lexicalized as: [{subject_lexicalization}]')

            data['subject'] = subject_lexicalization.text
        else:

            self.logger.debug(f'Failed to lexicalize subject: [{data["subject"]}]')

            return None

        object_lexicalization = self.data_alignment.get_object_lexicalization(data['object'])

        if object_lexicalization:

            self.logger.debug(f'object: [{data["object"]}] lexicalized as: [{object_lexicalization}]')

            data['object'] = object_lexicalization.text
        else:

            self.logger.debug(f'Failed to lexicalize object: [{data["object"]}]')

            return None

        return data


import re 

PARENTHESIS_RE = re.compile(r'(.*?)\((.*?)\)')
CAMELCASE_RE = re.compile(r'([a-z])([A-Z])')

def preprocess_so(so):

    parenthesis_preprocessed = PARENTHESIS_RE.sub('\g<2> \g<1>', so)
    underline_removed = parenthesis_preprocessed.replace('_', ' ')
    camelcase_preprocessed = CAMELCASE_RE.sub('\g<1> \g<2>', underline_removed)

    return camelcase_preprocessed.strip().replace('"', '')


class LexicalizePreprocessed(BaseEstimator):

    def __init__(self, preprocessor=lambda x: x):

        self.preprocessor = preprocessor

        self.logger = logging.getLogger(self.__class__.__name__)


    def fit(self, data_alignment=None):

        pass


    def lexicalize(self, data):

        return {'predicate': data['predicate'],
                'object': self.preprocessor(data['object']),
                'subject': self.preprocessor(data['subject'])}