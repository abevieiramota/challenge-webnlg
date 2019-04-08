import xml.etree.ElementTree as ET
from config import DATASETS_FILEPATHS
import networkx as nx
import networkx.algorithms.isomorphism as iso
from matplotlib import pyplot as plt
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from itertools import chain, product
from random import Random
import pandas as pd
from collections import namedtuple
from functools import reduce
from operator import __and__


PANDAS_CONTAINER = namedtuple('PANDAS_CONTAINER', ['edf', 'odf', 'mdf', 'ldf'])


TRIPLE_KEYS = ['subject', 'predicate', 'object']

EDGE_MATCH = iso.categorical_edge_match(['predicate', 's_label', 'o_label'], [None, None, None])


def get_graph_from_triples(triples):

    graph = nx.DiGraph()

    for d in triples:

        s = d['subject']
        p = d['predicate']
        o = d['object']

        graph.add_edge(s, o, predicate=p)

    return graph


def load(dataset):

    for d in dataset:

        if d not in DATASETS_FILEPATHS:
            raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

    dataset_filepaths = [(d, DATASETS_FILEPATHS[d]) for d in dataset]
    dataset_name = '_'.join(dataset)

    db = read_file_from_paths_db(dataset_filepaths)

    return WebNLGCorpus(dataset_name, db)



def read_file_from_paths_db(dataset_filepaths):

    db = TinyDB(storage=MemoryStorage)
    
    entries_dicts = []
    
    for dataset, filepath in chain(*(product([dataset], filepaths) for dataset, filepaths in dataset_filepaths)):
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        
        for entry in root.iter('entry'):
            
            mtriples = entry.find('modifiedtripleset').findall('mtriple')
            ntriples = len(mtriples)
            
            idx = "{dataset}_{category}_{ntriples}_{eid}".format(dataset=dataset,
                   category=entry.attrib['category'],
                   ntriples=ntriples,
                   eid=entry.attrib['eid'])
            
            entry_dict = {
                "dataset": dataset,
                "idx": idx,
                "category": entry.attrib['category'],
                "eid": entry.attrib['eid'],
                "size": entry.attrib['size'],
                "ntriples": ntriples,
                "content": ET.tostring(entry),
                "otriple": [
                    dict({'otext': e.text},
                            **{key: value.strip() for key, value in zip(TRIPLE_KEYS, e.text.split('|'))}
                            )
                    for e in entry.find('originaltripleset').findall('otriple')
                ],
                "mtriple": [
                    dict({'mtext': e.text},
                            **{key: value.strip() for key, value in zip(TRIPLE_KEYS, e.text.split('|'))}
                            ) for e in mtriples
                ]
            }

            if 'v1.2' in filepath:

                entry_dict["lexes"] = [
                    {'ltext': e.findtext('text'),
                    'template': e.findtext('template', 'NOT-FOUND'),
                    'comment': e.attrib['comment'],
                    'lid': e.attrib['lid']} for e in entry.findall('lex')
                ]

                entry_dict["entity_map"] = {
                    entity.text.split('|')[0].strip(): entity.text.split('|')[1].strip() for entity in entry.find('entitymap').findall('entity')
                }
            else:
                
                entry_dict["lexes"] = [
                    {'ltext': e.text,
                    'comment': e.attrib['comment'],
                    'lid': e.attrib['lid']} for e in entry.findall('lex')
                ]
            
            entries_dicts.append(entry_dict)

    db.insert_multiple(entries_dicts)

    return db


class WebNLGEntry(object):
    
    def __init__(self, entry):
        
        self.entry = entry
        self._delexicalize_map = None
        

    def get_data(self, delexicalize=False):

        if delexicalize:

            delexicalized_data = []

            for d in self.entry['mtriple']:

                delexicalized_data.append({'subject': self.get_delexicalize_map()[d['subject']],
                                          'predicate': d['predicate'],
                                          'object': self.get_delexicalize_map()[d['object']]})
            return delexicalized_data
        else:

            return self.entry['mtriple']

    def get_delexicalize_map(self):

        if self._delexicalize_map is None:

            self._delexicalize_map = {v:k for k, v in self.entry['entity_map'].items()}

        return self._delexicalize_map


    def get_graph(self, delexicalized=False, nlp=None):

        if delexicalized and not self.entry['entity_map']:
            return None

        graph = nx.DiGraph()

        for d in self.entry['mtriple']:

            if delexicalized:

                s = self.get_delexicalize_map()[d['subject']]
                p = d['predicate']
                o = self.get_delexicalize_map()[d['object']]

            else:

                s = d['subject']
                p = d['predicate']
                o = d['object']

            s_label = None
            o_label = None

            if nlp:
                s_ent = list(nlp(s).ents)
                if s_ent:
                    s_label = s_ent[0].label_
                o_ent = list(nlp(o).ents)
                if o_ent:
                    o_label = o_ent[0].label_

            graph.add_edge(s, o, predicate=p, s_label=s_label, o_label=o_label)

        return graph


    def is_isomorphic(self, g):

        return nx.is_isomorphic(self.get_graph(), g, edge_match=EDGE_MATCH)
        

    def draw_graph(self, figsize=(15, 15), nlp=None):
        
        g = self.get_graph(nlp=nlp)
        _, _ = plt.subplots(1, 1, figsize=figsize)
        pos = nx.spring_layout(g)
        nx.draw_networkx_edges(g, pos)
        nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        nx.draw_networkx_labels(g, pos)
        nx.draw_networkx_edge_labels(g, pos)


    def lexes(self):

        return [l['ltext'] for l in self.entry['lexes']]


    def templates(self):

        return [l['template'] for l in self.entry['lexes']]


    def triples(self, kind='dict'):

        if kind == 'text':

            return [m['mtext'] for m in self.entry['mtriple']]

        if kind == 'dict':

            return self.entry['mtriple']


    def idx(self):

        return self.entry['idx']


    def __str__(self):

        lines = []

        lines.append(f"Triple info: category={self.entry['category']} eid={self.entry['eid']} idx={self.entry['idx']}\n")

        lines.append("\tModified triples:\n")
        lines.extend([m['mtext'] for m in self.entry['mtriple']])
        lines.append("\n")

        if 'lexes' in self.entry:
            lines.append("\tLexicalizations:\n")
            lines.extend(['{}\n{}\n'.format(l['ltext'], l.get('template', '')) for l in self.entry['lexes']])

        if 'entity_map' in self.entry:
            lines.append('\tEntity map:\n')
            lines.extend([f'{k} : {v}' for k, v in self.entry['entity_map'].items()])

        return "\n".join(lines)

    def __repr__(self):

        return self.__str__()


class WebNLGCorpus(object):
    
    def __init__(self, dataset_name, db):
        
        self._dataset_name = dataset_name
        self.db = db
        
    
    @property
    def dataset_name(self):
        
        return self._dataset_name
        
        
    def subset(self, ntriples=None, categories=None):
        
        if ntriples is None and categories is None:
            raise ValueError('At least one filter must be informed.')
            
        query = Query()
        
        filters = []
        
        if ntriples:
            filters.append(query.ntriples.one_of(ntriples))
            
        if categories:
            filters.append(query.category.one_of(categories))
            
        subset_db = TinyDB(storage=MemoryStorage)
        subset_db.insert_multiple(self.db.search(reduce(__and__, filters)))

        return WebNLGCorpus(self.dataset_name, subset_db)
 

    def sample(self, eid=None, category=None, ntriples=None, idx=None, seed=None):

        rg = Random()
        rg.seed(seed)
        
        query = Query()
        
        filters = []

        if eid or category or ntriples or idx:

            if idx:
                filters.append(query.idx == idx)
            if eid:
                filters.append(query.eid == eid) 
            if category:
                filters.append(query.category == category)
            if ntriples:
                filters.append(query.ntriples == ntriples)

            sample_entry = rg.choice(self.db.search(reduce(__and__, filters)))

        else:
            sample_entry = rg.choice(list(self.db))

        return WebNLGEntry(sample_entry)
    
    @property
    def edf(self):
        
        return self.as_pandas.edf
    
    @property
    def odf(self):
        
        return self.as_pandas.odf
    
    @property
    def mdf(self):
        
        return self.as_pandas.mdf
    
    @property
    def ldf(self):
        
        return self.as_pandas.ldf
    
    
    @property
    def as_pandas(self):
        
        if hasattr(self, '_pandas'):
            
            return self._pandas
        
        entries_dicts, otriples_dicts, mtriples_dicts, lexes_dicts = [], [], [], []
    
        for e in self:
            
            entry_dict = {
                "idx": e.entry['idx'],
                "dataset": e.entry['dataset'],
                "category": e.entry['category'],
                "eid": e.entry['eid'],
                "size": e.entry['size'],
                "ntriples": e.entry['ntriples'],
                "content": e.entry['content']
            }
            entries_dicts.append(entry_dict)
            
            otriple_dict = [
                {
                    'idx': e.entry['idx'], 
                    'otext': ot['otext'],
                    'object': ot['object'],
                    'predicate': ot['predicate'],
                    'subject': ot['subject']
                } for ot in e.entry['otriple']
            ]
            otriples_dicts.extend(otriple_dict)
            
            mtriple_dict = [
                {
                    'idx': e.entry['idx'],
                    'mtext': mt['mtext'],
                    'object': mt['object'],
                    'predicate': mt['predicate'],
                    'subject': mt['subject']
                } for mt in e.entry['mtriple']
            ]
            mtriples_dicts.extend(mtriple_dict)
            
            lex_dict = [
                {
                    'idx': e.entry['idx'],
                    'ltext': l['ltext'],
                    'comment': l['comment'],
                    'lid': l['lid']
                } for l in e.entry['lexes']
            ]
            lexes_dicts.extend(lex_dict)
                
        
        edf = pd.DataFrame(entries_dicts)
        odf = pd.DataFrame(otriples_dicts)
        mdf = pd.DataFrame(mtriples_dicts)
        ldf = pd.DataFrame(lexes_dicts)
        
        self._pandas = PANDAS_CONTAINER(edf=edf, odf=odf, mdf=mdf, ldf=ldf)

        return self._pandas


    def __len__(self):
        
        return len(self.db)


    def __str__(self):
        
        return self.dataset_name


    def __iter__(self):
        
        return map(lambda entry: WebNLGEntry(entry), self.db)