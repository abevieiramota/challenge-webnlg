from spacy import displacy
import pandas as pd
import spacy
from textacy import similarity

# tests if two spans overlaps
# TODO: move to spacy_util
def overlaps(span1, span2):

    return max(0, min(span1.end_char, span2.end_char) - max(span1.start_char, span2.start_char)) > 0


def get_span(doc, node):

    return doc[node.left_edge.i: node.right_edge.i + 1]

def get_left_span(doc, node):

    return doc[node.left_edge.i: node.i + 1]

def get_right_span(doc, node):

    return doc[node.i: node.right_edge.i + 1]

def as_span(doc, node):

    return doc[node.i: node.i + 1]


class RootDataAlignmentModel:
    
    def __init__(self, similarity_metric):
        
        self.similarity_metric = similarity_metric
        
    def align_data(self, doc, data):
        
        df = self.get_distances(doc, data)
        
        # subject extraction
        # BIAS: subject wins priority over distances tie
        m_subject_span = df.m_subject.nlargest(1).index.values[0]

        m_object_span = None
        
        # object extraction
        # search for the best span for object, different from the subject one
        for span in df.m_object.sort_values(ascending=False).index.values:
            
            # tests if the current span doesn't overlaps the subject one
            if overlaps(span, m_subject_span):

                continue
                
            m_object_span = span
            break
            
        return m_subject_span, m_object_span
    
    def render_aligned(self, doc, data):
        
        m_subject_span, m_object_span = self.align_data(doc, data)
        
        data =  {
            'text': doc.text,
            'ents': [{
                'start': span.start_char,
                'end': span.end_char,
                'label': label
            } for label, span in [('m_subject: {}'.format(data['m_subject']), m_subject_span), 
                                  ('m_object: : {}'.format(data['m_object']), m_object_span)]],
            'title': None
        }
    
        displacy.render(data, style='ent', manual=True, jupyter=True)
        

    def get_distances(self, doc, data):

        distances, spans = [], []

        # dependency trees' roots
        roots = [token for token in doc if token.head == token]

        # BIAS: parts of the tree
        # breadth-first
        for root in roots:

            # root subtree
            # BIAS: parts of the tree
            root_span = get_span(doc, root)
            # root left subtree
            root_left_span = get_left_span(doc, root)
            # root right subtree
            root_right_span = get_right_span(doc, root)
            # root node
            only_root = as_span(doc, root)

            # test agains the node and its subtree
            for span in set((only_root, root_span, root_left_span, root_right_span)):

                spans.append(span)

                distances_span = []

                # for each structured data, calculate similarity
                for d in data.values():

                    distances_span.append(self.similarity_metric(d, span.text))

                distances.append(distances_span)
            
            # add children
            roots.extend(root.lefts)
            roots.extend(root.rights)

        return pd.DataFrame(distances, index=spans, columns=data.keys())