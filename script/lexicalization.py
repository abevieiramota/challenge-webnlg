class LexicalizeAsAligned:

    def __init__(self, data_alignment=None):

        self.data_alignment = data_alignment


    def lexicalize(self, data):

        if data['m_subject'] in self.data_alignment.m_subject_align:

            data['m_subject'] = self.data_alignment.m_subject_align.get(data['m_subject']).text
        
        if data['m_object'] in self.data_alignment.m_object_align:
            data['m_object'] = self.data_alignment.m_object_align.get(data['m_object']).text

        return data
