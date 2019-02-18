import logging
from sklearn.base import BaseEstimator
from collections import defaultdict, Counter
import re

PARENTHESIS_RE = re.compile(r'(.*?)\((.*?)\)')
CAMELCASE_RE = re.compile(r'([a-z])([A-Z])')

def preprocess_so(so):

    parenthesis_preprocessed = PARENTHESIS_RE.sub('\g<2> \g<1>', so)
    underline_removed = parenthesis_preprocessed.replace('_', ' ')
    camelcase_preprocessed = CAMELCASE_RE.sub('\g<1> \g<2>', underline_removed)

    return camelcase_preprocessed.strip().replace('"', '')


REMOVE_SPACE_BEFORE_DOT_RE = re.compile(r"(.*?)(\s*)([\.,'!])")
def remove_space_before_dot(s):
    
    return REMOVE_SPACE_BEFORE_DOT_RE.sub(r'\1\3', s)


REPLACE_TAG_BY_SO_RE = re.compile(r'((?P<subject>agent\\-1)|(?P<object>patient\\-1))')
def replace_sop(m):
    
    return "(?P<{}>.*?)".format(next((k for k, v in m.groupdict().items() if v)))

transtab = str.maketrans("’", "'")
def normalize_text(s):
    
    return s.translate(transtab).lower().replace('`` ', '').replace(" '' ", '')


class LexicalizeAsAligned(BaseEstimator):
    
    def __init__(self, fallback_preprocessing=preprocess_so):
        
        self.fallback_preprocessing = fallback_preprocessing
        
    
    def fit(self, X, y=None):
        
        self.subject_lexicalization = defaultdict(Counter)
        self.object_lexicalization = defaultdict(Counter)
        self.not_matched_templates = []
        self.errors = []
        self.cant_find_subject = []
        self.cant_find_object = []
        self.without_template = []
        
        for e in X:
            
            triple = e.get_data()[0]
            
            for lex in e.entry['lexes']:
                
                if not lex['template']:
                    
                    self.without_template.append(lex)
                    continue
                
                text = normalize_text(lex['ltext'])
                template = normalize_text(lex['template'])
                template = remove_space_before_dot(template)
                
                try:
                    nr = re.compile(REPLACE_TAG_BY_SO_RE.sub(replace_sop, re.escape(template))) 
                except:
                    self.errors.append(lex)
                
                m = nr.match(text)
                
                if m:
                    d = m.groupdict()
                    
                    if 'subject' in d:
                        self.subject_lexicalization[triple['subject']][d['subject']] += 1
                    else:
                        self.cant_find_subject.append(lex)
                        
                    if 'object' in d:
                        self.object_lexicalization[triple['object']][d['object']] += 1
                    else:
                        self.cant_find_object.append(lex)
                else:
                    self.not_matched_templates.append((e, lex))
                    
                    
    def lexicalize(self, triples):
        
        already_seen = set()
        
        lexicalizations = []
        
        for triple in triples:
        
            if triple['subject'] in already_seen:
                subject_lexi = ','
            else:
                if triple['subject'] in self.subject_lexicalization:
                    subject_lexi = self.subject_lexicalization[triple['subject']].most_common(1)[0][0]
                else:
                    subject_lexi = self.fallback_preprocessing(triple['subject'])
                    
                already_seen.add(triple['subject'])
                
            if triple['object'] in already_seen:
                object_lexi = ','
            else:
                if triple['object'] in self.object_lexicalization:
                    object_lexi = self.object_lexicalization[triple['object']].most_common(1)[0][0]
                else:
                    object_lexi = self.fallback_preprocessing(triple['object'])
                already_seen.add(triple['object'])
            
            lexicalized_triple = dict(subject=subject_lexi,
                                     object=object_lexi,
                                     predicate=triple['predicate'])
            
            lexicalizations.append(lexicalized_triple)
            
        return lexicalizations


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



class LexicalizeAsAligned2(BaseEstimator):

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