CATEGORIES = ['Airport', 'Astronaut', 'Building', 'City', 'ComicsCharacter', 
              'Food', 'Monument', 'SportsTeam', 'University', 'WrittenWork']

import os
import xml.etree.ElementTree as ET
import pandas as pd

FILEPATH_TEMPLATE = '../data/webnlg2017/challenge_data_train_dev/train/{0}triples/{0}triples_{1}_train_challenge.xml'

class WebNLGDataset(object):
    
    def __init__(self, ntriples, category):
        
        self.ntriples = ntriples
        self.category = category
        self.edf, self.odf, self.mdf, self.ldf = WebNLGDataset._read_files(ntriples, category)
        
    def sample(self, random_state=None):
        
        e = self.edf.sample(random_state=random_state)
        o = self.odf[self.odf.eid == e.eid.values[0]]
        m = self.mdf[self.mdf.eid == e.eid.values[0]]
        l = self.ldf[self.ldf.eid == e.eid.values[0]]
        
        return e, o, m, l
        
    @staticmethod
    def _read_files(ntriples, category):
        
        tree = ET.parse(FILEPATH_TEMPLATE.format(ntriples, category))
        root = tree.getroot()

        entries, otriples, mtriples, lexes = [], [], [], []
        
        for entry in root.iter('entry'):
            
            entry_dict = {
                "category": entry.attrib['category'],
                "eid": entry.attrib['eid'],
                "size": entry.attrib['size'],
                "ntriples": ntriples,
                "category": category
            }
            entries.append(entry_dict)
            
            otriple_dict = [
                {'eid': entry.attrib['eid'],
                 'otext': e.text,
                 'category': category,
                 'ntriples': ntriples} for e in entry.find('originaltripleset').findall('otriple')
            ]
            otriples.extend(otriple_dict)
            
            mtriple_dict = [
                {'eid': entry.attrib['eid'],
                 'mtext': e.text,
                 'category': category,
                 'ntriples': ntriples} for e in entry.find('modifiedtripleset').findall('mtriple')
            ]
            mtriples.extend(mtriple_dict)
            
            lex_dict = [
                {'eid': entry.attrib['eid'],
                 'ltext': e.text,
                 'comment': e.attrib['comment'],
                 'lid': e.attrib['lid'],
                 'category': category,
                 'ntriples': ntriples} for e in entry.findall('lex')
            ]
            lexes.extend(lex_dict)

        
        otriples_df = pd.DataFrame(otriples)
        otriples_df[['o_subject', 'o_predicate', 'o_object']] = otriples_df.otext.str.split("|", expand=True) 
        otriples_df['o_subject'] = otriples_df.o_subject.str.strip()
        otriples_df['o_predicate'] = otriples_df.o_predicate.str.strip()
        otriples_df['o_object'] = otriples_df.o_object.str.strip()
        
        mtriples_df = pd.DataFrame(mtriples)
        mtriples_df[['m_subject', 'm_predicate', 'm_object']] = mtriples_df.mtext.str.split("|", expand=True) 
        mtriples_df['m_subject'] = mtriples_df.m_subject.str.strip()
        mtriples_df['m_predicate'] = mtriples_df.m_predicate.str.strip()
        mtriples_df['m_object'] = mtriples_df.m_object.str.strip()
        
        entries_df = pd.DataFrame(entries)
        
        lexes_df = pd.DataFrame(lexes)

        return entries_df, otriples_df, mtriples_df, lexes_df
    
from IPython.core.display import display, HTML

class WebNLGEntry(object):
    
    def __init__(self, entry, otriples, mtriples, lexes):
        
        self.entry = entry
        self.otriples = otriples
        self.mtriples = mtriples
        self.lexes = lexes
        
    def display(self):
        
        display(HTML(self.mtriples[['m_subject', 'm_predicate', 'm_object']].to_html()))
        display(HTML(self.lexes[['ltext']].to_html()))

class WebNLGCorpus(object):
    
    def __init__(self, random_state=None):
        
        self.random_state = random_state
        self.datasets = []
        for category in CATEGORIES:
            
            for ntriplas in range(1, 8):
                
                try:
                    self.datasets.append(WebNLGDataset(ntriplas, category))
                except FileNotFoundError:
                    pass
                
        self.edf = pd.concat([ds.edf for ds in self.datasets])
        self.odf = pd.concat([ds.odf for ds in self.datasets])
        self.mdf = pd.concat([ds.mdf for ds in self.datasets])
        self.ldf = pd.concat([ds.ldf for ds in self.datasets])
        
        
    def datasets_size(self, **kwds):
        
        return pd.crosstab(self.edf.category, self.edf.ntriples, margins=True, **kwds)
    
    
    def sample(self, category, ntriples):
        
        e = self.edf[(self.edf.category == category) & (self.edf.ntriples == ntriples)].sample(random_state=self.random_state)
        
        return self._create_entry(e)
    
    def get(self, category, ntriples, eid):
        
        e = self.edf[(self.edf.category == category) & (self.edf.ntriples == ntriples) & (self.edf.eid == eid)]
        
        return self._create_entry(e)
    
    
    def sample_w_mtext(self, mtext):
        
        m = self.mdf[self.mdf.mtext == mtext].sample()
        e = self.edf[(self.edf.eid == m.eid.values[0]) & (self.edf.category == m.category.values[0]) & (self.edf.ntriples == m.ntriples.values[0])]
       
        return self._create_entry(e)
    
    def _create_entry(self, e):
        
        o = pd.merge(e, self.odf)
        m = pd.merge(e, self.mdf)
        l = pd.merge(e, self.ldf)
        
        return WebNLGEntry(e, o, m, l)