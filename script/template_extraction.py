import spacy
import logging
from collections import defaultdict
import pickle

te_logger = logging.getLogger("TemplateExtractor")

class Template:

    def __init__(self, str_template):

        self.str_template = str_template

    def fill(self, data):

        return self.str_template.format(**data)

    def __str__(self):

        return self.str_template

    def __repr__(self):

        return self.__str__()

    def __eq__(self, other):

        return self.str_template == other.str_template

    def __hash__(self):

        return self.str_template.__hash__()


class TemplateExtractor:
    
    def __init__(self, data_alignment_model=None):
    
        self.data_alignment_model = data_alignment_model
        self.template_db = None

        te_logger.debug("Initialized with data_alignment_model [%s]", data_alignment_model)


    def fit(self, texts, datas):

        te_logger.debug("Started fitting data.")

        self.template_db = defaultdict(lambda: defaultdict(list))

        n_processed = 0

        for text, data in zip(texts, datas):

            # TODO: generalize over how the templates are indexed
            predicate = data['m_predicate']

            template = self.extract_template(text, data)

            # add to db
            self.template_db[predicate][template].append((text, data))

            n_processed += 1

        te_logger.debug("Finished fitting data. %d processed texts.", n_processed)
        

    def extract_template(self, text, data):
        
        # TODO: monitor success of subj/obje alignment
        m_subject_span, m_object_span = self.data_alignment_model.align_data(text, data)

        # breaks text into char array
        text_char = list(text)

        # replaces subject text with m_subject placeholder
        text_char[m_subject_span.start_char: m_subject_span.end_char] = '{m_subject}'

        # tests if the object occurs after the subject >
        #    if it is the case, you have to adjust the indexes accordingly
        if m_subject_span.start_char > m_object_span.end_char:

            base = 0
        else:
            # adjustes the indexes
            # length of the extracted subject text
            len_subject_text = m_subject_span.end_char - m_subject_span.start_char
            # length of the placeholder minus len_subject_text
            base = len('{m_subject}') - len_subject_text

        # replaces object text with m_object placeholder
        text_char[base + m_object_span.start_char: base + m_object_span.end_char] = '{m_object}'

        # build template using the char array
        return Template(''.join(text_char))

    @staticmethod
    def save(te, path):

        with open(path, 'wb') as f:
            pickle.dump(dict(te.template_db), f)

    @staticmethod
    def load(path):

        with open(path, 'rb') as f:
            template_db = pickle.load(f)
        
        te = TemplateExtractor()
        te.template_db = template_db 

        return te
        


