from sklearn.base import BaseEstimator, RegressorMixin
import re


SPO_ORDER = ['subject', 'predicate', 'object']
OPS_ORDER = ['object', 'predicate', 'subject']

def as_is(x):
    
    return x

def simple_ops_sort(spo):
    
    return reversed(simple_spo_sort(spo))


PARENTHESIS_RE = re.compile(r'(.*?)\((.*?)\)')
CAMELCASE_RE = re.compile(r'([a-z])([A-Z])')

def remove_and_invert_parenthesis(x):
    
    return PARENTHESIS_RE.sub('\g<2> \g<1>', x)

def remove_underline(x):
    
    return x.replace('_', ' ')

def camelcase_to_normal(x):
    
    return CAMELCASE_RE.sub('\g<1> \g<2>', x)

def parenthesis_underline(x):
    
    return remove_underline(\
                            remove_and_invert_parenthesis(x))

def parenthesis_underline_camelcase(x):
    
    return camelcase_to_normal(\
                              remove_underline(\
                                              remove_and_invert_parenthesis(x)))
    


class JustJoinGenerator(BaseEstimator, RegressorMixin):
    
    def __init__(self, 
                 spo_sep=' ', 
                 sen_sep=',', 
                 spo_order=SPO_ORDER, 
                 sen_sort=as_is,
                 preprocess_subject=as_is,
                 preprocess_predicate=as_is,
                 preprocess_object=as_is):
        
        self.spo_sep = spo_sep
        self.sen_sep = sen_sep
        self.spo_order = spo_order
        self.sen_sort = sen_sort
        self.preprocess_subject = preprocess_subject
        self.preprocess_predicate = preprocess_predicate
        self.preprocess_object = preprocess_object
        
    
    # there isn't any training step, as it's all rule-based        
    def fit(self, X, y=None):
        pass
    
    # generating text for an entry
    def predict_entry(self, x):
        
        sens = []
        
        for t in self.sen_sort(x):
            
            t_preprocessed = {'subject': self.preprocess_subject(t['subject']),
                              'predicate': self.preprocess_predicate(t['predicate']),
                              'object': self.preprocess_object(t['object'])}
            
            t_sorted = [t_preprocessed[field] for field in self.spo_order]
            
            sen = self.spo_sep.join(t_sorted)
            
            sens.append(sen)
        
        text = self.sen_sep.join(sens)
            
        return text
    
    
    def predict(self, X, y=None):
        
        # for each entry, generate a text
        return [self.predict_entry(x) for x in X]