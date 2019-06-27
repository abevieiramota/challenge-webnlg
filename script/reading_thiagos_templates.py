import xml.etree.ElementTree as ET
import re
from template_based import *
from collections import defaultdict, Counter
import glob


PLACE_ENTITY_TAG = re.compile('((?:AGENT-.)|(?:PATIENT-.)|(?:BRIDGE-.))')


TRIPLE_KEYS = ['subject', 'predicate', 'object']


def make_dict_from_triple(triple_text):

    triple_dict = {}

    for triple_key, part in zip(TRIPLE_KEYS, triple_text.split('|')):

        stripped_part = part.strip()

        triple_dict[triple_key] = stripped_part

    return triple_dict


def extract_entity_value(entities):

    entity_dict = {}

    for entity in entities:

        entity_placeholder, entity_value = entity.text.split('|')

        entity_dict[entity_value.strip()] = entity_placeholder.strip()

    return entity_dict


def read_thiagos_templates():

    template_db = defaultdict(Counter)

    for filepath in  glob.glob('../../webnlg/data/delexicalized/v1.2/train/**/*.xml', recursive=True):

        tree = ET.parse(filepath)
        root = tree.getroot()

        for entry in root.iter('entry'):

            category = entry.attrib['category']

            entity_map = extract_entity_value(entry.find('entitymap').findall('entity'))

            for triple in entry.find('modifiedtripleset').findall('mtriple'):

                triple = make_dict_from_triple(triple.text)

                o0 = Slot(entity_map[triple['object']], [])
                p0 = Predicate(triple['predicate'], [o0])
                s0 = Slot(entity_map[triple['subject']], [p0])

                s = Structure(s0)

                for e in entry.findall('lex'):

                    template_text = PLACE_ENTITY_TAG.sub(r'{\1}', e.findtext('template', 'NOT-FOUND'))

                    try:
                        t = Template(s, template_text)
                    except:
                        continue

                    template_db[s][t] += 1

    return dict(template_db)
