from spacy import displacy
from spacy_util import overlaps, get_span, as_span
import logging
from textacy import extract

# TODO: lexicalization must be serialized
class DataAlignmentModel:

    def render_aligned(self, text, data):

        m_subject_span, m_object_span = self.align_data(text, data)

        spans = [('m_subject', m_subject_span), ('m_object', m_object_span)]

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

    
    def get_subject_lexicalization(self, m_subject):

        return self.m_subject_align.get(m_subject, None)

    def get_object_lexicalization(self, m_object):

        return self.m_object_align.get(m_object, None)

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

    
    def get_subject_lexicalization(self, m_subject):

        for model in self.models:

            result = model.get_subject_lexicalization(m_subject)

            if result:

                return result
        
        return None

    def get_object_lexicalization(self, m_object):

        for model in self.models:

            result = model.get_object_lexicalization(m_object)

            if result:

                return result
        
        return None


class SPODataAlignmentModel(DataAlignmentModel):

    def __init__(self, nlp=None):

        if nlp is None:
            raise ValueError("nlp mustn't be None")

        self.nlp = nlp
        self.m_subject_align = {}
        self.m_object_align = {}

    
    def align_data(self, text, data):

        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        from textacy import extract

        spo = list(extract.subject_verb_object_triples(doc))

        if not spo:

            return None

        s, p, o = spo[0]

        self.m_subject_align[data['m_subject']] = s 
        self.m_object_align[data['m_object']] = o 

        return s, o


# TODO: aligning only sentence with triple > align whole text with tripleset
class RootDataAlignmentModel(DataAlignmentModel):
    
    def __init__(self, similarity_metric=None, nlp=None):

        DataAlignmentModel.__init__(self)

        if similarity_metric is None:
            raise ValueError("similarity_metric mustn't be None")

        if nlp is None:
            raise ValueError("nlp mustn't be None")
        
        self.similarity_metric = similarity_metric
        self.nlp = nlp
        self.m_subject_align = {}
        self.m_object_align = {}
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
        m_subject_span, sim_subject = max(similarities['m_subject'], key=lambda x: x[1])

        self.logger.debug(f"Selected m_subject_span [{m_subject_span}] with similarity [{sim_subject}] for [{data['m_subject']}]")

        m_object_span = None
        
        # object extraction
        # search for the best span for object, different from the subject one
        for span, sim in sorted(similarities['m_object'], key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, m_subject_span):

                self.logger.debug(f"Span [{span.text}] overlaps m_subject_span [{m_subject_span.text}]")
                continue
                
            m_object_span = span

            self.logger.debug(f"Selected m_object_span [{m_object_span.text}] with similarity [{sim}] for [{data['m_object']}]")
            break

        if m_object_span is None:

            self.logger.warning("I can't extract m_object_span.")

        self.m_subject_align[data['m_subject']] = m_subject_span
        self.m_object_align[data['m_object']] = m_object_span
            
        return m_subject_span, m_object_span
    
    def get_similarities(self, doc, data):

        spans, roots = [], []

        similarities = {k:[] for k in data.keys()}

        # dependency trees' roots > discards first level, the whole sentence
        # you can't match m_subject or m_object with the whole sentence
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
        self.m_subject_align = {}
        self.m_object_align = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def align_data(self, text, data):

        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        ngrams = []
        n_punct = len([token for token in doc if token.is_punct])
        for n in range(1, min(self.max_n+1, len(doc) - n_punct)):
            
            ngrams.extend(extract.ngrams(doc, n))

        subject_sims = [(ngram, self.similarity_metric(ngram.text, data['m_subject'])) for ngram in ngrams]
       
        self.logger.debug("Similarities from m_subject %s", list(zip(ngrams, subject_sims)))

        subject_span, subject_sim = max(subject_sims, key=lambda x: x[1])

        self.logger.debug(f"Selected m_subject_span [{subject_span}] with similarity [{subject_sim}] for [{data['m_subject']}]")

        object_sims = [(ngram, self.similarity_metric(ngram.text, data['m_object'])) for ngram in ngrams]

        self.logger.debug("Similarities from m_object %s", list(zip(ngrams, object_sims)))

        for span, sim in sorted(object_sims, key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, subject_span):

                self.logger.debug(f"Span [{span.text}] overlaps m_subject_span [{subject_span.text}]")
                continue

            object_span = span

            self.logger.debug(f"Selected m_object_span [{object_span.text}] with similarity [{sim}] for [{data['m_object']}]")
            break
        
        if object_span is None:

            self.logger.warning("I can't extract m_object_span.")

        # TODO: add this schema to other aligner
        self.m_subject_align[data['m_subject']] = subject_span
        self.m_object_align[data['m_object']] = object_span

        return subject_span, object_span
