from sklearn.base import clone
import numpy as np
import codecs
import subprocess
from itertools import product
import pandas as pd
import os
import re

from webnlg import WebNLGCorpus

test = WebNLGCorpus.load("test_with_lex")

X_test = np.array([t.get_data() for t in test])
y_test = np.array([t.lexes() for t in test])


def preprocess_to_evaluate(texts_filepath, team_name, out_dirpath):
    
    subprocess.run(['mkdir', '-p', out_dirpath])
        
    subprocess.run(['python', '../evaluation/webnlg2017/webnlg-automatic-evaluation-v2/evaluation_v2.py',
                    '--team_filepath', texts_filepath,
                    '--team_name', team_name,
                    '--outdir', out_dirpath])


BLEU_RE = re.compile(r'BLEU\ =\ ([\d\.]*),')
METEOR_RE = re.compile(r'Final score:\s+([\d\.]+)\n')


def evaluate_texts(all_cat_filepath):
    
    result = {}
    
    with open(all_cat_filepath, 'rb') as f:
        # bleu
        bleu_result = subprocess.run(['../evaluation/webnlg2017/webnlg-baseline-master/multi-bleu.perl', 
                                 '-lc',
                                 '../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-all-cat-reference0.lex',
                                 '../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-all-cat-reference1.lex',
                                 '../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-all-cat-reference2.lex'],
                                 stdout=subprocess.PIPE,
                                 input=f.read())

    result['bleu'] = float(BLEU_RE.findall(bleu_result.stdout.decode('utf-8'))[0])

    # meteor
    meteor_result = subprocess.run(['java', '-Xmx2G', '-jar',
                                    '../evaluation/webnlg2017/meteor-1.5/meteor-1.5.jar',
                                    all_cat_filepath,
                                    '../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-all-cat-reference-3ref.meteor',
                                    '-l', 'en', '-norm', '-r', '3', '-a', 
                                    '../evaluation/webnlg2017/meteor-1.5/data/paraphrase-en.gz'],
                                    stdout=subprocess.PIPE)

    result['meteor'] = float(METEOR_RE.findall(meteor_result.stdout.decode('utf-8'))[0])
                  
    return result


def evaluate_model(model, model_name):
    
    texts_filepath = f'../data/models/{model_name}.txt'
    preprocessed_texts_dirpath = f'../tmp/{model_name}'
    all_cat_filepath = f'../tmp/{model_name}/{model_name}_all-cat.txt'

    # generate the texts

    with codecs.open(texts_filepath, 'w', 'utf-8') as f:

        for text in model.predict(X_test):

            f.write("{}\n".format(text))

    # generate the files needed to calculate BLEU and METEOR

    preprocess_to_evaluate(texts_filepath, model_name, preprocessed_texts_dirpath)

    return evaluate_texts(all_cat_filepath)



def evaluate_grid(base_model, param_grid):
    
    results = []
    
    for i, params in enumerate(product(*param_grid.values())):
        
        model_name = f'{i}'
        
        model = clone(base_model)
        
        params = dict(zip(param_grid.keys(), params))
        model.set_params(**params)
        
        result = dict(params)
        results.append(result)
        
        evaluation_result = evaluate_model(model, model_name)
        
        result.update(evaluation_result)
                  
    return pd.DataFrame.from_records(results)