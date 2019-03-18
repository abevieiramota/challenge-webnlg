from collections import defaultdict
import networkx as nx
from sklearn.base import BaseEstimator


class DoesntSortDiscourseStructuring(BaseEstimator):

    def fit(self, template_model=None):
        pass 


    def structure(self, data):

        return data



class MostFrequentFirstDiscourseStructuring(BaseEstimator):


    def fit(self, template_db):
        
        self.predicate_frequency = defaultdict(int)

        for predicate, templates_counter in template_db.items():

            self.predicate_frequency[predicate] = sum(templates_counter.values())


    def structure(self, data):

        sorted_sentences = sorted(data, 
                                  key=lambda d: self.predicate_frequency[d['predicate']],
                                  reverse=True)
        
        return sorted_sentences



class ChainDiscourseStructuring:
    
    def structure(self, e):

        G = e.get_graph()

        # node without in edges
        nodes_wo_in_edges = list(set(G.nodes()).difference(set([n[1] for n in G.in_edges()])))

        # TODO: not found
        if not nodes_wo_in_edges:

            return None

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

