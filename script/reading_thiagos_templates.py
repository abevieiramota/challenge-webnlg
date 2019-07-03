import xml.etree.ElementTree as ET
import re
from template_based import Structure, Template
from collections import defaultdict, Counter


PLACE_ENTITY_TAG = re.compile('((?:AGENT-.)|(?:PATIENT-.)|(?:BRIDGE-.))')

RE_MATCH_TEMPLATE_KEYS = re.compile(r'(AGENT\\-\d|PATIENT\\-\d|BRIDGE\\-\d)')
TRANS_ESCAPE_TO_RE = str.maketrans('-', '_', '\\')

RE_ENTITY_SPACE_DOTCOMMA = re.compile(r'(?:(?<=AGENT-\d)|(?<=PATIENT-\d)|'
                                      r'(?<=BRIDGE-\d))\ (?=[\.,])')


def normalize_thiagos_template(s):
    # removes single space between an entity and a dot or a comma

    return RE_ENTITY_SPACE_DOTCOMMA.sub('', s)


def make_template(triples, s, template_text, r_entity_map, metadata):

    # substitui, por exemplo, AGENT-1 por {AGENT-1}, criando templates Python
    template_text = PLACE_ENTITY_TAG.sub(r'{\1}', template_text)

    delex_triples = []
    for t in triples:
        delex_triples.append({'subject': r_entity_map[t['subject']],
                              'predicate': t['predicate'],
                              'object': r_entity_map[t['object']]})

    s = Structure.from_triples(delex_triples)

    t = Template(s, template_text, metadata)

    return t


def get_lexicalizations(s, t, entity_map):

    # permite capturar entidades que aparecem mais de uma vez no template
    # ex:
    #   AGENT-1 comeu PATIENT-1 e AGENT-1 vai trabalhar.
    #   João comeu carne e ele vai trabalhar.
    # como uso um regex com grupos nomeados de acordo com o label da entidade
    #    e só posso ter um grupo por label, é preciso criar labels diferentes
    #    para AGENT-1
    # para tanto, adiciono um contado à frente do label, ficando:
    # (?P<AGENT_1_1>.*?) comeu (?P<PATIENT_1_1>.*?) e (?P<AGENT_1_2>.*?)
    # vai trabalhar.

    # contador, por label, de quantos grupos regex já foram utilizados
    lex_counts = Counter()

    def replace_sop(m):

        entity = m.group(0)
        lex_counts[entity] += 1

        # cria o nome do grupo a partir do label
        # como a string está escapada, os labels são recebidos como, ex:
        #    AGENT\\-1
        # devendo ser transformado, para ser utilizado como grupo em:
        #    AGENT_1_1
        # o que ocorre em dois passos:
        #    .translate(TRANS_ESCAPE_TO_RE) - remove \ e troca - por _
        #    '{}_{}'.format(_, lex_counts[entity]) - add o contador de entidade
        entity_group = '{}_{}'.format(entity.translate(TRANS_ESCAPE_TO_RE),
                                      lex_counts[entity])

        # retorna então o regex do grupo que irá capturar
        #    os caracteres da entidade
        return '(?P<{v}>.*?)'.format(v=entity_group)

    # substitui os labels de entidades por regex para capturar suas substrings
    #    adiciona ^ e $ para delimitar o início e fim da string
    t_re = '^{}$'.format(RE_MATCH_TEMPLATE_KEYS.sub(replace_sop,
                                                    re.escape(t)))

    m = re.match(t_re, s)

    lexicals = defaultdict(list)

    if m:
        for g_name, v in m.groupdict().items():

            entity_label = g_name[:-2].replace('_', '-')
            lex_key = entity_map[entity_label]

            lexicals[lex_key].append(v.lower())

    return dict(lexicals)


def extract_triples(entry_elem):

    triples = []

    modifiedtripleset_elem = entry_elem.find('modifiedtripleset')

    for t in modifiedtripleset_elem.findall('mtriple'):

        triple_dict = {}

        for triple_key, part in zip(['subject', 'predicate', 'object'],
                                    t.text.split('|')):

            stripped_part = part.strip()

            triple_dict[triple_key] = stripped_part

        triples.append(triple_dict)

    return triples


def extract_entity_map(entry_elem):

    entity_dict = {}

    for ent_elem in entry_elem.find('entitymap').findall('entity'):

        ent_placeholder, ent_value = ent_elem.text.split('|')

        entity_dict[ent_placeholder.strip()] = ent_value.strip()

    return entity_dict


def extract_lexes(entry_elem):

    lexes = []

    for lex_elem in entry_elem.findall('lex'):

        lex = {'text': lex_elem.findtext('text'),
               'template': normalize_thiagos_template(lex_elem
                                                      .findtext('template',
                                                                '')),
               'comment': lex_elem.attrib['comment']
               }

        lexes.append(lex)

    return lexes


def read_thiagos_xml_entries(filepath):

    entries = []

    tree = ET.parse(filepath)
    root = tree.getroot()

    for entry_elem in root.iter('entry'):

        entry = {}
        entry['triples'] = extract_triples(entry_elem)
        entry['lexes'] = extract_lexes(entry_elem)
        entry['entity_map'] = extract_entity_map(entry_elem)
        # reversed entity map
        entry['r_entity_map'] = {v: k for k, v in entry['entity_map'].items()}

        entries.append(entry)

    return entries
