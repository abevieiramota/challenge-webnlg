from spacy import displacy
from spacy_util import overlaps, get_span, as_span
import logging
from textacy import extract

rda_logger = logging.getLogger('RootDataAlignmentModel')
# TODO: aligning only sentence with triple > align whole text with tripleset
class RootDataAlignmentModel:
    
    def __init__(self, similarity_metric=None, nlp=None):

        if similarity_metric is None:
            raise ValueError("similarity_metric mustn't be not None")

        if nlp is None:
            raise ValueError("nlp mustn't be not None")
        
        self.similarity_metric = similarity_metric
        self.nlp = nlp

        rda_logger.debug("Initialized with similarity_metric [%s], nlp = [%s]", 
                    similarity_metric, nlp)


    def align_data(self, text, data):

        # TODO: work with multiple types
        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text

        rda_logger.debug("Aligning [%s] with [%s]", text, data)
        
        similarities = self.get_similarities(doc, data)

        rda_logger.debug("similarities \n%s", similarities)
        
        # subject extraction
        # BIAS: subject wins priority over distances tie
        m_subject_span, sim_subject = max(similarities['m_subject'], key=lambda x: x[1])

        rda_logger.debug("Selected m_subject_span [%s] with similarity [%f] for [%s]", 
                         m_subject_span, sim_subject, data['m_subject'])

        m_object_span = None
        
        # object extraction
        # search for the best span for object, different from the subject one
        for span, sim in sorted(similarities['m_object'], key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, m_subject_span):

                rda_logger.debug("Span [%s] overlaps m_subject_span [%s]",
                                span.text, m_subject_span.text)
                continue
                
            m_object_span = span

            rda_logger.debug("Selected m_object_span [%s] with similarity [%f] for [%s]", 
                             m_object_span.text, sim, data['m_object'])
            break

        if m_object_span is None:

            rda_logger.warning("I can't extract m_object_span.")
            
        return m_subject_span, m_object_span
    
    def render_aligned(self, text, data):

        if type(text) == str:
            doc = self.nlp(text)
        else:
            doc = text
        
        m_subject_span, m_object_span = self.align_data(doc, data)

        spans = [('m_subject: {}'.format(data['m_subject']), m_subject_span), 
                                  ('m_object: : {}'.format(data['m_object']), m_object_span)]

        # BUG: bug in displacy.render? if the ents aren't ordered by start_char, it renders duplicated texts
        spans = sorted(spans, key=lambda s: s[1].start_char)
        
        render_data =  {
            'text': doc.text,
            'ents': [{
                'start': span.start_char,
                'end': span.end_char,
                'label': label
            } for label, span in spans],
            'title': None
        }
    
        displacy.render(render_data, style='ent', manual=True, jupyter=True)
        

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


ngram_logger = logging.getLogger("NGramDataAlignmentModel")
class NGramDataAlignmentModel:

    def __init__(self, max_n=4, similarity_metric=None, nlp=None):

        if similarity_metric is None:
            raise ValueError("similarity_metric mustn't be not None")

        if nlp is None:
            raise ValueError("nlp mustn't be not None")

        self.max_n = max_n 
        self.nlp = nlp
        self.similarity_metric = similarity_metric
        self.m_subject_align = {}
        self.m_object_align = {}

    def align_data(self, text, data):

        doc = self.nlp(text)

        ngrams = []
        n_punct = len([token for token in doc if token.is_punct])
        for n in range(1, min(self.max_n+1, len(doc) - n_punct)):
            
            ngrams.extend(extract.ngrams(doc, n))

        subject_sims = [(ngram, self.similarity_metric(ngram.text, data['m_subject'])) for ngram in ngrams]
       
        ngram_logger.debug("Similarities from m_subject %s", list(zip(ngrams, subject_sims)))

        subject_span, subject_sim = max(subject_sims, key=lambda x: x[1])

        ngram_logger.debug("Selected m_subject_span [%s] with similarity [%f] for [%s]", 
                         subject_span, subject_sim, data['m_subject'])

        object_sims = [(ngram, self.similarity_metric(ngram.text, data['m_object'])) for ngram in ngrams]

        ngram_logger.debug("Similarities from m_object %s", list(zip(ngrams, object_sims)))

        for span, sim in sorted(object_sims, key=lambda x: x[1], reverse=True):

            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, subject_span):

                ngram_logger.debug("Span [%s] overlaps m_subject_span [%s]",
                                span.text, subject_span.text)
                continue

            object_span = span

            ngram_logger.debug("Selected m_object_span [%s] with similarity [%f] for [%s]", 
                             object_span.text, sim, data['m_object'])
            break
        
        if object_span is None:

            ngram_logger.warning("I can't extract m_object_span.")

        # TODO: add this schema to other aligner
        self.m_subject_align[data['m_subject']] = subject_span
        self.m_object_align[data['m_object']] = object_span

        return subject_span, object_span
