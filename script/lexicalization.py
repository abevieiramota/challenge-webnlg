import logging

le_logger = logging.getLogger("LexicalizeAsAligned")

class LexicalizeAsAligned:

    def __init__(self, data_alignment=None):

        self.data_alignment = data_alignment


    def lexicalize(self, data):

        subject_lexicalization = self.data_alignment.get_subject_lexicalization(data['m_subject'])

        if subject_lexicalization:

            le_logger.debug('m_subject: [%s] lexicalized as: [%s]', data['m_subject'], subject_lexicalization)

            data['m_subject'] = subject_lexicalization.text
        else:

            le_logger.debug('Failed to lexicalize m_subject: [%s]', data['m_subject'])

        object_lexicalization = self.data_alignment.get_object_lexicalization(data['m_object'])

        if object_lexicalization:

            le_logger.debug('m_object: [%s] lexicalized as: [%s]', data['m_object'], object_lexicalization)

            data['m_object'] = object_lexicalization.text
        else:

            le_logger.debug('Failed to lexicalize m_object: [%s]', data['m_object'])

        return data
