import xml.etree.ElementTree as ET
from config import DATASETS_FILEPATHS
import networkx as nx
from matplotlib import pyplot as plt
import re
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from itertools import chain

TRIPLE_KEYS = ['subject', 'predicate', 'object']


# BIAS: lexicalization of subject/object
# removes separators | _
unwanted_separators = re.compile(r'(\||_)')
# removes unwanted empty chars
unwanted_multiple_empty = re.compile(r'\s+')
# splits on camelcade
first_letter_in_camelcase = re.compile('(?<=[a-z])([A-Z])')
def preprocess_triple_text(s):
    
    sep_changed = unwanted_separators.sub(' ', s)
    mult_empty_removed = unwanted_multiple_empty.sub(' ', sep_changed)
    
    # remove "
    x = mult_empty_removed.replace('"', '')
    return ' '.join(first_letter_in_camelcase.sub(r' \1', x).split())


class WebNLGEntry(object):
    
    def __init__(self, entry):
        
        self.entry = entry
        

    def get_data(self, preprocessor=None):

        if preprocessor:
            return [{key: preprocessor(value) for key, value in d} for d in self.entry['mtriple']]
        else:
            return self.entry['mtriple']
        

    def draw_graph(self):
        
       # graph = nx.from_pandas_edgelist(self.mdf, 'm_subject', 'm_object', 'm_predicate', create_using=nx.DiGraph())

        _, _ = plt.subplots(1, 1, figsize=(10, 6))
        pos = nx.spring_layout(graph)
        nx.draw_networkx_edges(graph, pos)
        nx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        nx.draw_networkx_labels(graph, pos)

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

        lines.append(f"Triple info: category={self.entry['category']}\n")

        lines.append("\tModified triples:\n")
        lines.extend([m['mtext'] for m in self.entry['mtriple']])
        lines.append("\n")

        if 'lexes' in self.entry:
            lines.append("\tLexicalizations:\n")
            lines.extend([l['ltext'] for l in self.entry['lexes']])

        return "\n".join(lines)

    def __repr__(self):

        return self.__str__()


class WebNLGCorpus(object):
    
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
        subset_db.insert_multiple(db.search(query))

        return WebNLGCorpus(self.dataset_name, subset_db)
 

    def sample(self, eid=None, category=None, ntriples=None, idx=None, random_state=None):

        query = Query()

        if idx:
            query = query.idx == idx
        if eid:
            query = query.eid == eid 
        if category:
            query = query.category == category 
        if ntriples:
            query = query & (query.ntriples == ntriples)
        
        sample_entry = self.db.get(query)

        return WebNLGEntry(sample_entry)


    def __len__(self):
        
        return len(self.db)


    def __str__(self):
        
        return self.dataset


    def __iter__(self):
        
        return map(lambda entry: WebNLGEntry(entry), self.db)


    @staticmethod
    def load(dataset):

        if isinstance(dataset, list):

            for d in dataset:

                if d not in DATASETS_FILEPATHS:
                    raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

            filepaths = list(chain(*[DATASETS_FILEPATHS[d] for d in dataset]))
    
            dataset_name = '_'.join(dataset)
        else:
            if dataset not in DATASETS_FILEPATHS:
                raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

            filepaths = DATASETS_FILEPATHS[dataset]
            dataset_name = dataset

        db = WebNLGCorpus._read_file_from_paths(filepaths)

        return WebNLGCorpus(dataset_name, db)


    @staticmethod
    def _read_file_from_paths(filepaths):

        db = TinyDB(storage=MemoryStorage)
        
        entries_dicts = []
        
        for id_filepath, filepath in enumerate(filepaths):
            
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            
            for id_entry, entry in enumerate(root.iter('entry')):
                
                idx = "{}_{}".format(id_filepath, id_entry)
                
                mtriples = entry.find('modifiedtripleset').findall('mtriple')
                ntriples = len(mtriples)
                
                entry_dict = {
                    "idx": idx,
                    "category": entry.attrib['category'],
                    "eid": entry.attrib['eid'],
                    "size": entry.attrib['size'],
                    "ntriples": ntriples,
                    "content": ET.tostring(entry),
                    "otriple": [
                        dict({'idx': idx,
                             'otext': e.text},
                             **{key: value for key, value in zip(TRIPLE_KEYS, e.text.split('|'))}
                             )
                        for e in entry.find('originaltripleset').findall('otriple')
                    ],
                    "mtriple": [
                        dict({'idx': idx,
                            'mtext': e.text},
                             **{key: value for key, value in zip(TRIPLE_KEYS, e.text.split('|'))}
                             ) for e in mtriples
                    ],
                    "lexes": [
                        {'idx': idx,
                        'ltext': e.text,
                        'comment': e.attrib['comment'],
                        'lid': e.attrib['lid']} for e in entry.findall('lex')
                    ]
                }
                entries_dicts.append(entry_dict)

        db.insert_multiple(entries_dicts)

        return db