import logging


class LexicalizeAsAligned:

    def __init__(self, data_alignment=None):

        self.data_alignment = data_alignment
        self.logger = logging.getLogger(self.__class__.__name__)


    def lexicalize(self, data):

        subject_lexicalization = self.data_alignment.get_subject_lexicalization(data['m_subject'])

        if subject_lexicalization:

            self.logger.debug(f'm_subject: [{data["m_subject"]}] lexicalized as: [{subject_lexicalization}]')

            data['m_subject'] = subject_lexicalization.text
        else:

            self.logger.debug(f'Failed to lexicalize m_subject: [{data["m_subject"]}]')

        object_lexicalization = self.data_alignment.get_object_lexicalization(data['m_object'])

        if object_lexicalization:

            self.logger.debug(f'm_object: [{data["m_object"]}] lexicalized as: [{object_lexicalization}]')

            data['m_object'] = object_lexicalization.text
        else:

            self.logger.debug(f'Failed to lexicalize m_object: [{data["m_object"]}]')

        return data


import re 

PARENTHESIS_RE = re.compile(r'(.*?)\((.*?)\)')
CAMELCASE_RE = re.compile(r'([a-z])([A-Z])')


def preprocess_so(so):

    parenthesis_preprocessed = PARENTHESIS_RE.sub('\g<2> \g<1>', so)
    underline_removed = parenthesis_preprocessed.replace('_', ' ')
    camelcase_preprocessed = CAMELCASE_RE.sub('\g<1> \g<2>', underline_removed)

    return camelcase_preprocessed.strip().replace('"', '')


class LexicalizePreprocessed:

    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)

    def lexicalize(self, data):

        return {'m_predicate': data['m_predicate'],
                'm_object': preprocess_so(data['m_object']),
                'm_subject': preprocess_so(data['m_subject'])}