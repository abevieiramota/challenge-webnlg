import logging
from collections import defaultdict, Counter
import pickle
import re


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


REPLACE_TAG_BY_SO_RE = re.compile(r'((?P<subject>AGENT-1)|(?P<object>PATIENT-1))')
def replace_sop(m):
    
    return "{{{}}}".format(next((k for k, v in m.groupdict().items() if v)))
    

class ManualTemplateExtract:
    
    def extract(self, entries):
        
        template_db = defaultdict(Counter)
        
        for e in entries:
            
            for lexe in e.entry['lexes']:
                
                template_text = REPLACE_TAG_BY_SO_RE.sub(replace_sop, lexe['template'])
                
                template = Template(template_text)
                
                predicate = e.get_data()[0]['predicate']
                
                template_db[predicate][template] += 1
                
        return template_db
        


class TemplateExtractor():
    
    def __init__(self, data_alignment_model=None):
    
        self.data_alignment_model = data_alignment_model

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Initialized with data_alignment_model [{data_alignment_model}]")

    def extract(self, entries):

        self.logger.debug("Started fitting data.")

        template_db = defaultdict(Counter)

        n_processed = 0
        
        for e in entries:
            
            for lexe in e.lexes:

                # TODO: generalize over how the templates are indexed
                predicate = e.data[0]['predicate']
    
                template = self.extract_template(lexe, e.data[0])
    
                # add to db
                template_db[predicate][template] += 1
    
                n_processed += 1

        self.logger.debug(f"Finished fitting data. {n_processed} processed texts.")
        
        return template_db
        

    def extract_template(self, text, data):
        
        # TODO: monitor success of subj/obje alignment
        subject_span, object_span = self.data_alignment_model.align_data(text, data)

        # breaks text into char array
        text_char = list(text)

        # replaces subject text with subject placeholder
        text_char[subject_span.start_char: subject_span.end_char] = '{subject}'

        # tests if the object occurs after the subject >
        #    if it is the case, you have to adjust the indexes accordingly
        if subject_span.start_char > object_span.end_char:

            base = 0
        else:
            # adjusts the indexes
            # length of the extracted subject text
            len_subject_text = subject_span.end_char - subject_span.start_char
            # length of the placeholder minus len_subject_text
            base = len('{subject}') - len_subject_text

        # replaces object text with object placeholder
        text_char[base + object_span.start_char: base + object_span.end_char] = '{object}'

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
        


