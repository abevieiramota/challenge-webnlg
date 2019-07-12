import codecs
import subprocess
import os
import re
from webnlg_corpus import webnlg

corpus = webnlg.load('webnlg_challenge_2017')
test = corpus.subset(datasets=['test'])

MODEL_DIR = '../model'

EVALUATION_SETS = ['all-cat', 'old-cat', 'new-cat', '1size', '2size', '3size', '4size', '5size', '6size', '7size']

if not os.path.isdir(MODEL_DIR):
    os.mkdir(MODEL_DIR)


def preprocess_to_evaluate(texts_filepath, model_name):

    subprocess.run(['python', '../evaluation/webnlg2017/webnlg-automatic-evaluation-v2/evaluation_v2.py',
                    '--team_filepath', texts_filepath,
                    '--team_name', model_name,
                    '--outdir', MODEL_DIR])


BLEU_RE = re.compile(r'BLEU\ =\ ([\d\.]*),')
METEOR_RE = re.compile(r'Final score:\s+([\d\.]+)\n')
TER_RE = re.compile(r'Total\ TER:\ ([\d\.]+)\ \(')

ALL_CAT_TO_TER_FILE_RE = re.compile(r'(.*)(\.txt)')


def evaluate_texts(preprocessed_filepath, evaluation_set):

    result = {}

    with open(preprocessed_filepath, 'rb') as f:
        # bleu
        bleu_result = subprocess.run(['../evaluation/webnlg2017/webnlg-baseline-master/multi-bleu.perl',
                                 '-lc',
                                 f'../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-{evaluation_set}-reference0.lex',
                                 f'../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-{evaluation_set}-reference1.lex',
                                 f'../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-{evaluation_set}-reference2.lex'],
                                 stdout=subprocess.PIPE,
                                 input=f.read())

    result['bleu'] = float(BLEU_RE.findall(bleu_result.stdout.decode('utf-8'))[0])

    # meteor
    meteor_result = subprocess.run(['java', '-Xmx2G', '-jar',
                                    '../evaluation/webnlg2017/meteor-1.5/meteor-1.5.jar',
                                    preprocessed_filepath,
                                    f'../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-{evaluation_set}-reference-3ref.meteor',
                                    '-l', 'en', '-norm', '-r', '3', '-a',
                                    '../evaluation/webnlg2017/meteor-1.5/data/paraphrase-en.gz'],
                                    stdout=subprocess.PIPE)

    result['meteor'] = float(METEOR_RE.findall(meteor_result.stdout.decode('utf-8'))[0])

    # ter
    ter_filepath = ALL_CAT_TO_TER_FILE_RE.sub(r'\1_ter\2', preprocessed_filepath)

    ter_result = subprocess.run(['java', '-jar', '../evaluation/webnlg2017/tercom-0.7.25/tercom.7.25.jar',
                                 '-r',
                                 f'../evaluation/webnlg2017/webnlg-automatic-evaluation/references/gold-{evaluation_set}-reference-3ref.ter',
                                 '-h',
                                 ter_filepath],
                                 stdout=subprocess.PIPE)

    result['ter'] = float(TER_RE.findall(ter_result.stdout.decode('utf-8'))[0])

    return result



def evaluate_model(model, model_name, evaluation_set='all-cat'):

    texts_filepath = f'../model/{model_name}.txt'

    preprocessed_filepath = f'../model/{model_name}_{evaluation_set}.txt'

    # generate the texts

    with codecs.open(texts_filepath, 'w', 'utf-8') as f:

        for text in model.predict(test):

            f.write("{}\n".format(text))

    # generate the files needed to calculate BLEU and METEOR

    preprocess_to_evaluate(texts_filepath, model_name)

    return evaluate_texts(preprocessed_filepath, evaluation_set)