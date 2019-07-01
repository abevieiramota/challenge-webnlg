import xml.etree.ElementTree as ET
import re
from template_based import *
from collections import defaultdict, Counter
import glob


PLACE_ENTITY_TAG = re.compile('((?:AGENT-.)|(?:PATIENT-.)|(?:BRIDGE-.))')


TRIPLE_KEYS = ['subject', 'predicate', 'object']


RE_MATCH_TEMPLATE_KEYS = re.compile(r'(AGENT\\-\d|PATIENT\\-\d|BRIDGE\\-\d)')
TRANS_ESCAPE_TO_RE = str.maketrans('-', '_', '\\')

RE_REMOVE_SPACE_BEFORE_FINAL_DOT = re.compile(r'\ \.$')


RE_ENTITY_SPACE_DOTCOMMA = re.compile(r'(?:(?<=AGENT-\d)|(?<=PATIENT-\d)|(?<=BRIDGE-\d))\ (?=[\.,])')
def normalize_thiagos_template(s):
    # removes single space between an entity and a dot or a comma

    return RE_ENTITY_SPACE_DOTCOMMA.sub('', s)


def make_template_from_entry(e, meta):

    if not 'entity_map' in e:
        return []

    templates = []

    for lexe in e['lexes']:

        template = normalize_thiagos_template(lexe['template'])
        template_text = PLACE_ENTITY_TAG.sub(r'{\1}', template)

        reverse_entity_map = {v:k for k, v in e['entity_map'].items()}

        delex_triples = []
        for t in e['triples']:
            delex_triples.append({'subject': reverse_entity_map[t['subject']],
                                  'predicate': t['predicate'],
                                  'object': reverse_entity_map[t['object']]})

        s = Structure.from_triples(delex_triples)

        t = Template(s, template_text, meta)
        templates.append(t)

    return templates


def get_lexicalizations(s, t):

    lex_counts = Counter()

    def replace_sop(m):

        entity = m.group(0)

        lex_counts[entity] += 1

        entity_group = '{}_{}'.format(entity.translate(TRANS_ESCAPE_TO_RE),
                        lex_counts[entity])

        return '(?P<{v}>.*?)'.format(v=entity_group)

    c_2_str = '{}$'.format(RE_MATCH_TEMPLATE_KEYS.sub(replace_sop, re.escape(t)))

    c_2 = re.compile(c_2_str)

    r = c_2.match(s).groupdict()

    r = {k.replace('_', '-'): v for k, v in r.items()}

    return r


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


def extract_value_entity(entities):

    entity_dict = {}

    for entity in entities:

        entity_placeholder, entity_value = entity.text.split('|')

        entity_dict[entity_placeholder.strip()] = entity_value.strip()

    return entity_dict


def read_thiagos_xml_entries(filepath):

    entries = []

    tree = ET.parse(filepath)
    root = tree.getroot()

    for entry_elem in root.iter('entry'):

        entry = {}
        entry['triples'] = [make_dict_from_triple(t.text) for t in entry_elem.find('modifiedtripleset').findall('mtriple')]
        entry['lexes'] = [{'text': l.findtext('text'), 'template': l.findtext('template')} for l in entry_elem.findall('lex')]
        entry['entity_map'] = extract_value_entity(entry_elem.find('entitymap').findall('entity'))

        entries.append(entry)

    return entries

def make_thiagos_template(entry):

    triples = entry['triples']
    reverse_entity_map = {v:k for k, v in entry['entity_map']}

    o0 = Slot(reverse_entity_map[triple['object']], [])
    p0 = Predicate(reverse_entity_map['predicate'], [o0])
    s0 = Slot(reverse_entity_map[triple['subject']], [p0])

    s = Structure(s0)

    for lexe in entry['lexes']:
        pass




def read_thiagos_templates():

    template_db = defaultdict(Counter)
    lexicalization_db = defaultdict(Counter)

    filepaths = glob.glob('../../webnlg/data/delexicalized/v1.4/train/**/*.xml', recursive=True)
    filepaths.extend(glob.glob('../../webnlg/data/delexicalized/v1.4/dev/**/*.xml', recursive=True))

    bixados = []

    for filepath in  filepaths:

        tree = ET.parse(filepath)
        root = tree.getroot()

        for entry in root.iter('entry'):

            category = entry.attrib['category']

            entity_map = extract_entity_value(entry.find('entitymap').findall('entity'))
            reverse_entity_map = {v:k for k, v in entity_map.items()}

            if entity_map:

                for triple in entry.find('modifiedtripleset').findall('mtriple'):

                    triple = make_dict_from_triple(triple.text)

                    if not triple['object'] in entity_map or not triple['subject'] in entity_map:
                        bixados.append(dict(eid=entry.attrib['eid'],
                                            category=entry.attrib['category'],
                                            size=entry.attrib['size']))
                        continue

                    o0 = Slot(entity_map[triple['object']], [])
                    p0 = Predicate(triple['predicate'], [o0])
                    s0 = Slot(entity_map[triple['subject']], [p0])

                    s = Structure(s0)

                    for e in entry.findall('lex'):

                        template = e.findtext('template', 'NOT-FOUND')
                        template = RE_REMOVE_SPACE_BEFORE_FINAL_DOT.sub('.', template)

                        template_text = PLACE_ENTITY_TAG.sub(r'{\1}', template)

                        try:
                            t = Template(s, template_text)
                            template_db[s][t] += 1

                            ld = get_lexicalizations(e.findtext('text'), template)

                            for k, v in ld.items():

                                if v:

                                    lexicalization_db[reverse_entity_map[k]][v] += 1
                        except:
                            pass


    return dict(template_db), dict(lexicalization_db), bixados