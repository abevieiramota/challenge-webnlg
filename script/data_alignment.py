from spacy import displacy
from spacy_util import overlaps, get_span, as_span
import logging
from textacy import extract
from sklearn.base import BaseEstimator

# TODO: lexicalization must be serialized
class DataAlignmentModel(BaseEstimator):

    def render_aligned(self, text, data):

        subject_span, object_span = self.align_data(text, data)

        spans = [('subject', subject_span), ('object', object_span)]

        # BUG: bug in displacy.render? if the ents aren't ordered by start_char, it renders duplicated texts
        spans = sorted(spans, key=lambda s: s[1].start_char)
        
        render_data =  {
            'text': text,
            'ents': [{
                'start': span.start_char,
                'end': span.end_char,
                'label': label
            } for label, span in spans],
            'title': None
        }
    
        displacy.render(render_data, style='ent', manual=True, jupyter=True)

    
    def get_subject_lexicalization(self, subject):

        return self.subject_align.get(subject, None)


    def get_object_lexicalization(self, object):

        return self.object_align.get(object, None)


    def align_data(self, text, data):
        pass 


class FallBackDataAlignmentModel(DataAlignmentModel):

    def __init__(self, models):

        self.models = models


    def align_data(self, text, data):

        for model in self.models:

            result = model.align_data(text, data)

            if result:

                return result

        return None

    
    def get_subject_lexicalization(self, subject):

        for model in self.models:

            result = model.get_subject_lexicalization(subject)

            if result:

                return result
        
        return None


    def get_object_lexicalization(self, object):

        for model in self.models:

            result = model.get_object_lexicalization(object)

            if result:

                return result
        
        return None


class SPODataAlignmentModel(DataAlignmentModel):

    def __init__(self, nlp=None):

        if nlp is None:
            raise ValueError("nlp mustn't be None")

        self.nlp = nlp
        self.subject_align = {}
        self.object_align = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    
    def align_data(self, text, data):

        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        from textacy import extract

        spo = list(extract.subject_verb_object_triples(doc))

        if not spo:

            self.logger.warning('No (subject, predicate, object) identified.')

            return None

        s, p, o = spo[0]

        self.logger.debug(f'Identified subject = [{s}], predicate = [{p}], object = [{o}]')

        self.subject_align[data['subject']] = s 
        self.object_align[data['object']] = o 

        return s, o


# TODO: aligning only sentence with triple > align whole text with tripleset
class RootDataAlignmentModel(DataAlignmentModel):
    
    def __init__(self, similarity_metric=None, nlp=None):

        if similarity_metric is None:
            raise ValueError("similarity_metric mustn't be None")

        if nlp is None:
            raise ValueError("nlp mustn't be None")
        
        self.similarity_metric = similarity_metric
        self.nlp = nlp
        self.subject_align = {}
        self.object_align = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug("Initialized with similarity_metric [%s], nlp = [%s]", 
                    similarity_metric, nlp)


    def align_data(self, text, data):

        # TODO: work with multiple types
        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        self.logger.debug(f"Aligning [{text}] with [{data}]")
        
        similarities = self.get_similarities(doc, data)

        self.logger.debug(f"similarities \n{similarities}")
        
        # subject extraction
        # BIAS: subject wins priority over distances tie
        subject_span, sim_subject = max(similarities['subject'], key=lambda x: x[1])

        self.logger.debug(f"Selected subject_span [{subject_span}] with similarity [{sim_subject}] for [{data['subject']}]")

        object_span = None
        
        # object extraction
        # search for the best span for object, different from the subject one
        for span, sim in sorted(similarities['object'], key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, subject_span):

                self.logger.debug(f"Span [{span.text}] overlaps subject_span [{subject_span.text}]")
                continue
                
            object_span = span

            self.logger.debug(f"Selected object_span [{object_span.text}] with similarity [{sim}] for [{data['object']}]")
            break

        if object_span is None:

            self.logger.warning("I can't extract object_span.")

        self.subject_align[data['subject']] = subject_span
        self.object_align[data['object']] = object_span
            
        return subject_span, object_span
    
    def get_similarities(self, doc, data):

        spans, roots = [], []

        similarities = {k:[] for k in data.keys()}

        # dependency trees' roots > discards first level, the whole sentence
        # you can't match subject or object with the whole sentence
        for upper_root in [token for token in doc if token.head == token]:

            roots.extend(upper_root.lefts)
            roots.extend(upper_root.rights)

        # BIAS: parts of the tree
        # breadth-first
        for root in roots:

            # root subtree
            # BIAS: parts of the tree
            root_span = get_span(doc, root)
            root_itself = as_span(doc, root)

            for span in set([root_span, root_itself]):

                spans.append(span)

                # for each structured data, calculate similarity
                for k, d in data.items():

                    similarities[k].append((span, self.similarity_metric(d, span.text)))

            # add children
            roots.extend(root.lefts)
            roots.extend(root.rights)

        return similarities


class NGramDataAlignmentModel(DataAlignmentModel):

    def __init__(self, max_n=4, similarity_metric=None, nlp=None):

        DataAlignmentModel.__init__(self)

        if similarity_metric is None:
            raise ValueError("similarity_metric mustn't be None")

        if nlp is None:
            raise ValueError("nlp mustn't be None")

        self.max_n = max_n 
        self.nlp = nlp
        self.similarity_metric = similarity_metric
        self.subject_align = {}
        self.object_align = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug("Initialized with similarity_metric [%s], max_n = [%s]", 
                    similarity_metric, max_n)


    def align_data(self, text, data):

        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        ngrams = []
        # n_punct = len([token for token in doc if token.is_punct])
        
        for n in range(1, min(self.max_n+1, len(doc))):
            
            ngrams.extend(extract.ngrams(doc, n))

        subject_sims = [(ngram, self.similarity_metric(ngram.text, data['subject'])) for ngram in ngrams]
       
        self.logger.debug("Similarities from subject %s", list(zip(ngrams, subject_sims)))

        subject_span, subject_sim = max(subject_sims, key=lambda x: x[1])

        self.logger.debug(f"Selected subject_span [{subject_span}] with similarity [{subject_sim}] for [{data['subject']}]")

        object_sims = [(ngram, self.similarity_metric(ngram.text, data['object'])) for ngram in ngrams]

        self.logger.debug("Similarities from object %s", list(zip(ngrams, object_sims)))

        object_span = None

        for span, sim in sorted(object_sims, key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, subject_span):

                self.logger.debug(f"Span [{span.text}] overlaps subject_span [{subject_span.text}]")
                continue

            object_span = span

            self.logger.debug(f"Selected object_span [{object_span.text}] with similarity [{sim}] for [{data['object']}]")
            break
        
        if object_span is None:

            self.logger.warning("I can't extract object_span.")

        self.subject_align[data['subject']] = subject_span
        self.object_align[data['object']] = object_span

        return subject_span, object_span
