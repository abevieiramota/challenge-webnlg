import xml.etree.ElementTree as ET
import pandas as pd
from config import DATASETS_FILEPATHS
import networkx as nx
from matplotlib import pyplot as plt
import re


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
    
    def __init__(self, edf, odf, mdf, ldf):
        
        self.edf = edf
        self.odf = odf
        self.mdf = mdf
        self.ldf = ldf
        
        self.graph = nx.from_pandas_edgelist(self.mdf, 'm_subject', 'm_object', 'm_predicate', create_using=nx.DiGraph())

        self._str = None

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


class WebNLGCorpusIterator(object):
    
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
            
        return WebNLGEntry(edf, odf, mdf, ldf)
        

class WebNLGCorpus(object):
    
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
        
        return WebNLGCorpus(self.dataset,
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
            
        return WebNLGEntry(edf, odf, mdf, ldf)
        
    def __len__(self):
        
        return len(self.edf)
    
    def __str__(self):
        
        return self.dataset
    
    def __iter__(self):
        
        return WebNLGCorpusIterator(self)

    @staticmethod
    def load(dataset):

        if isinstance(dataset, list):

            for d in dataset:

                if d not in DATASETS_FILEPATHS:
                    raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

            filepaths = []
    
            for d in dataset:
                
                filepaths = filepaths + DATASETS_FILEPATHS[d]

            dataset_name = '_'.join(dataset)
        else:
            if dataset not in DATASETS_FILEPATHS:
                raise ValueError('It must be in {}'.format(DATASETS_FILEPATHS.keys()))

            filepaths = DATASETS_FILEPATHS[dataset]
            dataset_name = dataset

        edf, odf, mdf, ldf = WebNLGCorpus._read_file_from_paths(filepaths)

        return WebNLGCorpus(dataset_name,
                            edf, odf, mdf, ldf)



        
    @staticmethod
    def _make_entries(entries_dicts):
        
        return pd.DataFrame(entries_dicts)
    
    @staticmethod
    def _make_lexes(lexes_dicts):
        
        return pd.DataFrame(lexes_dicts)
    
    @staticmethod
    def _make_otriples(otriples_dicts):
        
        otriples_df = pd.DataFrame(otriples_dicts)
        otriples_df[['o_subject', 'o_predicate', 'o_object']] = otriples_df.otext.str.split("|", expand=True) 
        otriples_df['o_subject'] = otriples_df.o_subject.str.strip()
        otriples_df['o_predicate'] = otriples_df.o_predicate.str.strip()
        otriples_df['o_object'] = otriples_df.o_object.str.strip()
        
        return otriples_df
    
    @staticmethod
    def _make_mtriples(mtriples_dicts):
        
        mtriples_df = pd.DataFrame(mtriples_dicts)
        mtriples_df[['m_subject', 'm_predicate', 'm_object']] = mtriples_df.mtext.str.split("|", expand=True) 
        mtriples_df['m_subject'] = mtriples_df.m_subject.str.strip()
        mtriples_df['m_predicate'] = mtriples_df.m_predicate.str.strip()
        mtriples_df['m_object'] = mtriples_df.m_object.str.strip()
        
        return mtriples_df
    
    @staticmethod
    def _read_file_from_paths(filepaths):
        
        entries_dicts, otriples_dicts, mtriples_dicts, lexes_dicts = [], [], [], []
        
        for id_filepath, filepath in enumerate(filepaths):
            
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            
            for id_entry, entry in enumerate(root.iter('entry')):
                
                idx = "{}_{}".format(id_filepath, id_entry)
                
                ntriples = len(entry.find('modifiedtripleset').findall('mtriple'))
                
                entry_dict = {
                    "idx": idx,
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
                
        
        entries_df = WebNLGCorpus._make_entries(entries_dicts)
        otriples_df = WebNLGCorpus._make_otriples(otriples_dicts)
        mtriples_df = WebNLGCorpus._make_mtriples(mtriples_dicts)
        lexes_df = WebNLGCorpus._make_lexes(lexes_dicts)

        return entries_df, otriples_df, mtriples_df, lexes_df