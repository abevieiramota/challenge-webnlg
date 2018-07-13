import xml.etree.ElementTree as ET
import pandas as pd
from config import DATASETS_FILEPATHS
import networkx as nx
from matplotlib import pyplot as plt

class WebNLGEntry(object):
    
    def __init__(self, edf, odf, mdf, ldf):
        
        self.edf = edf
        self.odf = odf
        self.mdf = mdf
        self.ldf = ldf
        
        self.graph = nx.from_pandas_edgelist(self.mdf, 'm_subject', 'm_object', 'm_predicate', create_using=nx.DiGraph())
        
    def draw_graph(self):
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        nx.draw_networkx_labels(self.graph, pos)


class WebNLGCorpus(object):
    
    def __init__(self, dataset=None):
        
        if dataset not in DATASETS_FILEPATHS:
            
            raise ValueError('It must be train or dev')
            
        self.name = dataset
            
        filepaths = DATASETS_FILEPATHS[dataset]
        self.edf, self.odf, self.mdf, self.ldf = self._read_file_from_paths(filepaths)
 

    def sample(self, category=None, ntriples=None, idx=None, random_state=None):
        
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
        
        edf = self.edf[self.edf.idx == idx]
        odf = self.odf[self.odf.idx == idx]
        mdf = self.mdf[self.mdf.idx == idx]
        ldf = self.ldf[self.ldf.idx == idx] if len(self.ldf) else None
            
        return WebNLGEntry(edf, odf, mdf, ldf)
        
    def __len__(self):
        
        return len(self.edf)
    
    def __str__(self):
        
        return self.name

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