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
                                  key=lambda d: self.predicate_frequency[d['predicate']],
                                  reverse=True)
        
        return sorted_sentences


class ChainDiscourseStructuring(BaseEstimator):

    def fit(self, template_model):

        pass


    def sort(self, data):

        G = nx.DiGraph()

        for tripleset in data:
            
            G.add_edge(tripleset['subject'], tripleset['object'], predicate=tripleset['predicate'])

        # node without in edges
        nodes_wo_in_edges = list(set(G.nodes()).difference(set([n[1] for n in G.in_edges()])))

        # TODO: not found
        if not nodes_wo_in_edges:

            return data

        # chooses the first -> random
        source = nodes_wo_in_edges[0]

        sorted_edges = nx.bfs_edges(G, source)

        sorted_data = []

        for edge in sorted_edges:

            predicate = G.get_edge_data(*edge)['predicate']

            d = {'subject': edge[0],
                 'predicate': predicate,
                 'object': edge[1]}
            sorted_data.append(d)

        return sorted_data

