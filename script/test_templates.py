from reading_thiagos_templates import (
        get_lexicalizations,
        RE_MATCH_TEMPLATE_KEYS,
        normalize_thiagos_template,
        read_thiagos_xml_entries,
        make_template
)

from template_based import (
        Slot,
        Structure,
        Predicate
)

import pytest


class TestNormalizeThiagosTemplates:

    def test_0(self):

        i = 'AGENT-1 or PATIENT-4 , a dish made of PATIENT-2 , is from the PATIENT-3 region of PATIENT-1 .'
        result = normalize_thiagos_template(i)
        expected = 'AGENT-1 or PATIENT-4, a dish made of PATIENT-2, is from the PATIENT-3 region of PATIENT-1.'

        assert result == expected

    def test_1(self):

        i = 'AGENT-1 or PATIENT-1 are wrong'
        result = normalize_thiagos_template(i)
        expected = i

        assert result == expected

class TestGetLexicalization:

    def test_0(self):

        result = RE_MATCH_TEMPLATE_KEYS.findall('AGENT\\-1')
        expected = ['AGENT\\-1']

        assert result == expected

    def test_1(self):

        s = 'Albertson Vandelberg went to the park'
        t = 'AGENT-1 went to PATIENT-1'
        entity_map = {'AGENT-1': 'Albertson_Vandelberg',
                      'PATIENT-1': 'park'}

        result = get_lexicalizations(s, t, entity_map)
        expected = {'Albertson_Vandelberg': ['Albertson Vandelberg'],
                    'park': ['the park']}

        assert result == expected

    def test_train_food_5triples_id1(self):
        # note that PATIENT-4 is Ajo Blanco, rather than ajo blanco

        s = 'Ajoblanco or ajo blanco, a dish made of bread, almonds, garlic, water, olive oil, is from the Andalusia region of Spain.'
        t = 'AGENT-1 or PATIENT-4, a dish made of PATIENT-2, is from the PATIENT-3 region of PATIENT-1.'
        entity_map = {'AGENT-1': 'ajoblanco',
                    'PATIENT-4': 'ajoblanco',
                    'PATIENT-2': 'bread, almonds, garlic, water, olive oil',
                    'PATIENT-3': 'andalusia',
                    'PATIENT-1': 'spain'}

        result = get_lexicalizations(s, t, entity_map)
        expected = {'ajoblanco': ['Ajoblanco', 'ajo blanco'],
                    'bread, almonds, garlic, water, olive oil': ['bread, almonds, garlic, water, olive oil'],
                    'andalusia': ['Andalusia'],
                    'spain': ['Spain']}

        assert result == expected

    def test_3(self):

        s = 'Alan Bean was born on the 15th of March 1932 and his Alma Mater is UT Austin, B.S. 1955.'
        t = 'AGENT-1 was born on PATIENT-1 and AGENT-1 Alma Mater is PATIENT-2.'
        entity_map = {'AGENT-1': 'alan_bean',
                    'PATIENT-1': '15/03/32',
                    'PATIENT-2': 'ut55'}

        result = get_lexicalizations(s, t, entity_map)
        expected = {'alan_bean': ['Alan Bean', 'his'],
                    '15/03/32': ['the 15th of March 1932'],
                    'ut55': ['UT Austin, B.S. 1955']}

        assert result == expected

class TestReadThiagoXML:

    def test_0(self):

        entries = read_thiagos_xml_entries('monument_test.xml')
        expected = [{'triples': [{'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'country', 'object': '"United States"'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'location', 'object': 'Seminary_Ridge'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'location', 'object': 'Adams_County,_Pennsylvania'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'state', 'object': '"Pennsylvania"'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'established', 'object': '2000'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'category', 'object': 'Contributing_property'},
                                 {'subject': '11th_Mississippi_Infantry_Monument', 'predicate': 'municipality', 'object': 'Gettysburg,_Pennsylvania'}
                                 ],
                     'lexes': [{'comment': 'good', 'text': 'The 11th Mississippi Infantry Monument is located at Seminary Ridge in Adams County in the municipality of Gettysburg @ Pennsylvania (United States). It was established in the year 2000 and is categorised as a contributing property.', 'template': 'AGENT-1 is located at PATIENT-2 in PATIENT-3 the municipality of PATIENT-7 @ PATIENT-4 ( PATIENT-1 ) . AGENT-1 was established in PATIENT-5 and is categorised as PATIENT-6.'},
                               {'comment': 'good', 'text': 'The 11th Mississippi Infantry Monument (completed in 2000) is a contributing property found at Seminary Ridge, Adams County, in the municipality of Gettysburg in the American state of Pennsylvania.', 'template': 'AGENT-1 (completed in PATIENT-5) is PATIENT-6 found at PATIENT-2, PATIENT-3, in the municipality of PATIENT-7 in the PATIENT-1 state of PATIENT-4.'},
                               {'comment': 'good', 'text': 'Seminary Ridge in Gettysburg is located in Adams County, Pennsylvania and is the location of the 11th Mississippi Infantry monument which was established in 2000 and categorised as a contributing property within the United States.', 'template': 'PATIENT-2 in PATIENT-7 is located in PATIENT-3, PATIENT-4 and is the location of AGENT-1 which was established in PATIENT-5 and categorised as PATIENT-6 within PATIENT-1.'}],
                     'entity_map': {'AGENT-1': '11th_Mississippi_Infantry_Monument',
                                    'PATIENT-5': '2000',
                                    'PATIENT-4': '"Pennsylvania"',
                                    'PATIENT-7': 'Gettysburg,_Pennsylvania',
                                    'PATIENT-6': 'Contributing_property',
                                    'PATIENT-1': '"United States"',
                                    'PATIENT-3': 'Adams_County,_Pennsylvania',
                                    'PATIENT-2': 'Seminary_Ridge'}}]

        assert len(entries) == len(expected)
        assert entries[0]['triples'] == expected[0]['triples']
        assert entries[0]['lexes'] == expected[0]['lexes']
        assert entries[0]['entity_map'] == expected[0]['entity_map']

class TestEverything:

    def test_0(self):

        entries = read_thiagos_xml_entries('sport_test.xml')

        entry = entries[0]

        lexicalizations = []

        for lexe in entry['lexes']:

            normalized_template = normalize_thiagos_template(lexe['template'])

            lexicalization = get_lexicalizations(lexe['text'],
                                                 normalized_template,
                                                 entry['entity_map'])

            lexicalizations.append(lexicalization)

        expected = [{'Alan_Bean': ['Alan Bean'],
                     '"1932-03-15"': ['March 15, 1932'],
                     '"UT Austin, B.S. 1955"': ['a Bachelor of Science degree at the University of Texas at Austin in 1955']
                     },
                    {'Alan_Bean': ['Alan Bean', 'his'],
                     '"1932-03-15"': ['March 15, 1932'],
                     '"UT Austin, B.S. 1955"': ['UT Austin BS, in 1955']
                     }]

        assert len(lexicalizations) == len(expected)
        assert lexicalizations == expected

class TestMakeTemplatesFromEntry:

    def test_0(self):

        entries = read_thiagos_xml_entries('sport_test.xml')

        entry = entries[0]

        lexe = entry['lexes'][0]

        ts = make_template(entry['triples'], lexe['text'], lexe['template'],
                           entry['r_entity_map'],
                           {'filepath': 'sport_test.xml'})


class TestMakeStructureFromTriples:

    def test_0(self):

        triples = [{'subject': 'A', 'predicate': 'X1', 'object': 'B'},
                   {'subject': 'A', 'predicate': 'X1', 'object': 'C'},
                   {'subject': 'A', 'predicate': 'X2', 'object': 'D'}]

        def make_expected():

            sB = Slot('B', [])
            sC = Slot('C', [])
            sD = Slot('D', [])

            px1 = Predicate('X1', [sB, sC])
            px2 = Predicate('X2', [sD])

            sA = Slot('A', [px1, px2])

            return Structure(sA)

        result = Structure.from_triples(triples)
        expected = make_expected()

        assert result == expected

    def test_1(self):

        triples = [{'subject': 'A', 'predicate': 'X1', 'object': 'B'},
                   {'subject': 'A', 'predicate': 'X1', 'object': 'C'}]

        def make_expected():

            sB = Slot('B', [])
            sC = Slot('C', [])

            px1 = Predicate('X1', [sB, sC])

            sA = Slot('A', [px1])

            return Structure(sA)

        result = Structure.from_triples(triples)
        expected = make_expected()

        assert result == expected
