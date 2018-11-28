import logging
from sklearn.base import BaseEstimator


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

        object_lexicalization = self.data_alignment.get_object_lexicalization(data['object'])

        if object_lexicalization:

            self.logger.debug(f'object: [{data["object"]}] lexicalized as: [{object_lexicalization}]')

            data['object'] = object_lexicalization.text
        else:

            self.logger.debug(f'Failed to lexicalize object: [{data["object"]}]')

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

    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)


    def fit(self, data_alignment=None):

        self.data_alignment = data_alignment


    def lexicalize(self, data):

        return {'predicate': data['predicate'],
                'object': preprocess_so(data['object']),
                'subject': preprocess_so(data['subject'])}