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


def load(dataset, structure='db'):

    for d in dataset:

        if d not in DATASETS_FILEPATHS:
            raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

    dataset_filepaths = [(d, DATASETS_FILEPATHS[d]) for d in dataset]
    dataset_name = '_'.join(dataset)

    if structure == 'db':

        db = read_file_from_paths_db(dataset_filepaths)

        return WebNLGCorpusDb(dataset_name, db)

    elif structure == 'pandas':

        edf, odf, mdf, ldf = read_file_from_paths_pandas(dataset_filepaths)

        return WebNLGCorpusPandas(dataset_name,
                            edf, odf, mdf, ldf)



def read_file_from_paths_db(dataset_filepaths):

    db = TinyDB(storage=MemoryStorage)
    
    entries_dicts = []
    
    for dataset, filepath in chain(*(product([dataset], filepaths) for dataset, filepaths in dataset_filepaths)):
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        
        for entry in root.iter('entry'):
            
            mtriples = entry.find('modifiedtripleset').findall('mtriple')
            ntriples = len(mtriples)
            
            entry_dict = {
                "dataset": dataset,
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


def make_entries(entries_dicts):
    
    return pd.DataFrame(entries_dicts)


def make_lexes(lexes_dicts):
    
    return pd.DataFrame(lexes_dicts)


def make_otriples(otriples_dicts):
    
    otriples_df = pd.DataFrame(otriples_dicts)
    otriples_df[['o_subject', 'o_predicate', 'o_object']] = otriples_df.otext.str.split("|", expand=True) 
    otriples_df['o_subject'] = otriples_df.o_subject.str.strip()
    otriples_df['o_predicate'] = otriples_df.o_predicate.str.strip()
    otriples_df['o_object'] = otriples_df.o_object.str.strip()
    
    return otriples_df


def make_mtriples(mtriples_dicts):
    
    mtriples_df = pd.DataFrame(mtriples_dicts)
    mtriples_df[['m_subject', 'm_predicate', 'm_object']] = mtriples_df.mtext.str.split("|", expand=True) 
    mtriples_df['m_subject'] = mtriples_df.m_subject.str.strip()
    mtriples_df['m_predicate'] = mtriples_df.m_predicate.str.strip()
    mtriples_df['m_object'] = mtriples_df.m_object.str.strip()
    
    return mtriples_df


def read_file_from_paths_pandas(dataset_filepaths):
    
    entries_dicts, otriples_dicts, mtriples_dicts, lexes_dicts = [], [], [], []
    
    for dataset, filepath in chain(*(product([dataset], filepaths) for dataset, filepaths in dataset_filepaths)):
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        
        for entry in root.iter('entry'):
            
            ntriples = len(entry.find('modifiedtripleset').findall('mtriple'))
            idx = "{}_{}_{}_{}".format(dataset, entry.attrib['category'], ntriples, entry.attrib['eid'])
            
            entry_dict = {
                "idx": idx,
                "dataset": dataset,
                "category": entry.attrib['category'],
                "eid": entry.attrib['eid'],
                "size": entry.attrib['size'],
                "ntriples": ntriples,
                "content": ET.tostring(entry)
            }
            entries_dicts.append(entry_dict)
            
            otriple_dict = [
                {'idx': idx,
                    'otext': e.text
                    } for e in entry.find('originaltripleset').findall('otriple')
            ]
            otriples_dicts.extend(otriple_dict)
            
            mtriple_dict = [
                {'idx': idx,
                    'mtext': e.text} for e in entry.find('modifiedtripleset').findall('mtriple')
            ]
            mtriples_dicts.extend(mtriple_dict)
            
            lex_dict = [
                {'idx': idx,
                    'ltext': e.text,
                    'comment': e.attrib['comment'],
                    'lid': e.attrib['lid']} for e in entry.findall('lex')
            ]
            lexes_dicts.extend(lex_dict)
            
    
    entries_df = make_entries(entries_dicts)
    otriples_df = make_otriples(otriples_dicts)
    mtriples_df = make_mtriples(mtriples_dicts)
    lexes_df = make_lexes(lexes_dicts)

    return entries_df, otriples_df, mtriples_df, lexes_df


class WebNLGEntryDb(object):
    
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


    def triples(self, kind='dict'):

        if kind == 'text':

            return [m['mtext'] for m in self.entry['mtriple']]

        if kind == 'dict':

            return self.entry['mtriple']


    def idx(self):

        return self.entry['idx']


    def __str__(self):

        lines = []

        lines.append(f"Triple info: category={self.entry['category']} eid={self.entry['eid']}\n")

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


class WebNLGCorpusDb(object):
    
    def __init__(self, dataset_name, db):
        
        self.dataset_name = dataset_name
        self.db = db
        
        
    def subset(self, ntriples, categories=None):

        query = Query()

        if ntriples:
            query = query & (query.ntriples == ntriples)
        if categories:
            query = query & (query.category.any(categories))
        
        subset_db = TinyDB(storage=MemoryStorage)
        subset_db.insert_multiple(self.db.search(query))

        return WebNLGCorpusDb(self.dataset_name, subset_db)
 

    def sample(self, eid=None, category=None, ntriples=None, idx=None, seed=None):

        rg = Random()
        rg.seed(seed)

        if eid or category or ntriples or idx:

            query = Query()

            if idx:
                query = query.idx == idx
            if eid:
                query = query.eid == eid 
            if category:
                query = query & (query.category == category)
            if ntriples:
                query = query & (query.ntriples == ntriples)

            sample_entry = rg.choice(self.db.search(query))

        else:
            sample_entry = rg.choice(list(self.db))

        return WebNLGEntryDb(sample_entry)


    def __len__(self):
        
        return len(self.db)


    def __str__(self):
        
        return self.dataset_name


    def __iter__(self):
        
        return map(lambda entry: WebNLGEntryDb(entry), self.db)



# WebNLG as pandas DataFrame

class WebNLGEntryPandas(object):
    
    def __init__(self, edf, odf, mdf, ldf):
        
        self.edf = edf
        self.odf = odf
        self.mdf = mdf
        self.ldf = ldf
        self._str = None
        self._graph = None

    @property
    def graph(self):

        if self._graph is None:
            self._graph = nx.from_pandas_edgelist(self.mdf, 'm_subject', 'm_object', 'm_predicate', create_using=nx.DiGraph())

        return self._graph


    @graph.setter
    def graph(self, graph):

        self._graph = graph


    def get_data(self, preprocessor=None):

        if preprocessor:
            return self.mdf[['m_subject', 'm_predicate', 'm_object']].applymap(preprocessor).to_dict(orient='records')
        else:
            return self.mdf[['m_subject', 'm_predicate', 'm_object']].to_dict(orient='records')
        

    def draw_graph(self):

        _, _ = plt.subplots(1, 1, figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        nx.draw_networkx_labels(self.graph, pos)


    def lexes(self):

        return self.ldf.ltext.tolist()


    def triples(self, kind='dict'):

        if kind == 'text':

            return self.mdf.mtext.tolist()

        if kind == 'dict':

            return self.mdf[['m_object', 'm_predicate', 'm_subject']].to_dict(orient='record')


    def idx(self):

        return self.edf.idx.values[0]


    def __str__(self):

        if not self._str:

            lines = []

            lines.append("Triple info: {}\n".format(self.edf[['category', 'eid', 'idx', 'ntriples']].to_dict(orient='records')[0]))

            lines.append("\tModified triples:\n")
            lines.extend(self.mdf.mtext.tolist())
            lines.append("\n")

            if self.ldf is not None:
                lines.append("\tLexicalizations:\n")
                lines.extend(self.ldf.ltext.tolist())

            self._str = "\n".join(lines)

        return self._str


    def __repr__(self):

        return self.__str__()


class WebNLGCorpusPandasIterator(object):
    
    def __init__(self, corpus):
        
        self.corpus = corpus
        self.idx_iter = corpus.edf.idx.values.__iter__()
        

    def __iter__(self):
        
        return self
        

    def __next__(self):
        
        idx = next(self.idx_iter)
        
        edf = self.corpus.edf[self.corpus.edf.idx == idx]
        odf = self.corpus.odf[self.corpus.odf.idx == idx]
        mdf = self.corpus.mdf[self.corpus.mdf.idx == idx]
        ldf = self.corpus.ldf[self.corpus.ldf.idx == idx]\
                if len(self.corpus.ldf) else None
            
        return WebNLGEntryPandas(edf, odf, mdf, ldf)
        

class WebNLGCorpusPandas(object):
    
    def __init__(self, dataset, edf, odf, mdf, ldf):
        
        self.dataset = dataset
        self.edf = edf
        self.odf = odf
        self.mdf = mdf
        self.ldf = ldf
        
        
    def subset(self, ntriples, categories=None):

        filter_ = True
        if ntriples:
            filter_ = filter_ & (self.edf.ntriples.isin(ntriples))
        if categories:
            filter_ = filter_ & (self.edf.category.isin(categories))
        
        edf = self.edf[filter_]
        odf = self.odf[self.odf.idx.isin(edf.idx)]
        mdf = self.mdf[self.mdf.idx.isin(edf.idx)]
        ldf = self.ldf[self.ldf.idx.isin(edf.idx)]
        
        return WebNLGCorpusPandas(self.dataset,
                            edf, odf, mdf, ldf)
 

    def sample(self, eid=None, category=None, ntriples=None, idx=None, random_state=None):
        
        if not idx:
            ds = self.edf
            if category:
                ds = ds[ds.category == category]
            if ntriples:
                ds = ds[ds.ntriples == ntriples]
            
            if not len(ds):
                raise ValueError('No entries for category {} and ntriples {}'.format(
                        category, ntriples))
            
            idx = ds.sample(random_state=random_state).idx.values[0]

        if eid:

            idx = ds[ds.eid == eid].idx.values[0]
        
        edf = self.edf[self.edf.idx == idx]
        odf = self.odf[self.odf.idx == idx]
        mdf = self.mdf[self.mdf.idx == idx]
        ldf = self.ldf[self.ldf.idx == idx] if len(self.ldf) else None
            
        return WebNLGEntryPandas(edf, odf, mdf, ldf)
        

    def __len__(self):
        
        return len(self.edf)
    

    def __str__(self):
        
        return self.dataset
    

    def __iter__(self):
        
        return WebNLGCorpusPandasIterator(self)