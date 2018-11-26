from collections import defaultdict
import networkx as nx
from sklearn.base import BaseEstimator

class MostFrequentFirstDiscourseStructuring(BaseEstimator):

    def __init__(self, template_model=None):

        self.predicate_frequency = defaultdict(int)


    def fit(self, template_model=None):

        for predicate, templates_dicts in template_model.template_db.items():

            freq = sum((len(examples) for examples in templates_dicts.values()))

            self.predicate_frequency[predicate] = freq


    def sort(self, data):

        sorted_sentences = sorted(data, 
                                  key=lambda d: self.predicate_frequency[d['m_predicate']],
                                  reverse=True)
        
        return sorted_sentences


class ChainDiscourseStructuring(BaseEstimator):

    def sort(self, data):

        G = nx.DiGraph()

        for tripleset in data:
            
            G.add_edge(tripleset['m_subject'], tripleset['m_object'], m_predicate=tripleset['m_predicate'])

        # node without in edges
        source = list(set(G.nodes()).difference(set([n[1] for n in G.in_edges()])))[0]

        sorted_edges = nx.bfs_edges(G, source)

        sorted_data = []

        for edge in sorted_edges:

            m_predicate = G.get_edge_data(*edge)['m_predicate']

            d = {'m_subject': edge[0],
                 'm_predicate': m_predicate,
                 'm_object': edge[1]}
            sorted_data.append(d)

        return sorted_data

