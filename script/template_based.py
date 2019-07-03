from collections import namedtuple
import re

MSG_ERROR_ROUTE_MATCH = 'structures must be isomorphic'
MSG_ERROR_FROM_TRIPLES = 'triples must contain only one root'
MSG_ERROR_VALIDATE_TEMPLATE_TEXT = ('structure and template_text must match'
                                    ' slots')

Slot = namedtuple('Slot', ['value', 'predicates'])
Predicate = namedtuple('Predicate', ['value', 'objects'])


def p_slot(s, level=1):

    ident = '\t'*level

    if len(s.predicates) == 0:
        return '{}'.format(s.value)
    else:
        preds_strs = []
        for p in s.predicates:

            pred_str = '\n{}{}'.format(ident, p_pred(p, level+1))
            preds_strs.append(pred_str)

        pred_str = '\n' + ','.join(preds_strs)

        return '[{}, {}]'.format(s.value, pred_str)


def p_pred(p, level):

    ident = '\t'*level

    objs_strs = []
    if len(p.objects) == 1 and len(p.objects[0].predicates) == 0:
        objs_str = '{}'.format(p.objects[0].value)
    else:
        for o in p.objects:

            objs_str = '\n{}{}'.format(ident, p_slot(o, level+1))
            objs_strs.append(objs_str)

        objs_str = ','.join(objs_strs)

    return '<{}, [{}]>'.format(p.value, objs_str)


def route_str(s):

    predicates = list(s.predicates)

    for p in predicates:

        for o in p.objects:

            yield f'<{s.value}, {p.value}, {o.value}>'

            for t in route_str(o):

                yield t


def route_slots(s):

    predicates = list(s.predicates)

    yield s.value

    for p in predicates:

        for o in p.objects:

            yield o.value

            predicates.extend(o.predicates)


# TODO: find a better way to index a structure
def route_predicates(s):

    predicates = [p for p in s.predicates]

    for p in predicates:

        yield p.value

        for o in p.objects:

            predicates.extend(o.predicates)


def route_match(s1, s2):
    # matches two structures returning pairs mapping of
    #    s1.slots.value into s2.slots.value
    # if they have the same structure

    if s1 is None or s2 is None or len(s1.predicates) != len(s2.predicates):
        raise ValueError(MSG_ERROR_ROUTE_MATCH)

    yield s1.value, s2.value

    predicates = list(zip(s1.predicates, s2.predicates))

    for p1, p2 in predicates:

        if p1.value != p2.value:
            raise ValueError(MSG_ERROR_ROUTE_MATCH)

        if len(p1.objects) != len(p2.objects):
            raise ValueError(MSG_ERROR_ROUTE_MATCH)

        for o1, o2 in zip(p1.objects, p2.objects):

            yield o1.value, o2.value

            if len(o1.predicates) != len(o2.predicates):
                raise ValueError(MSG_ERROR_ROUTE_MATCH)

            predicates.extend(zip(o1.predicates, o2.predicates))


class Structure:

    def __init__(self, head):

        self.head = head
        self._predicates = tuple(route_predicates(self.head))

    def position_data(self, data):

        return dict(route_match(self.head, data.head))

    def __hash__(self):

        return hash(self._predicates)

    def __eq__(self, other):

        if isinstance(self, type(other)):
            try:
                self.position_data(other)
                return True
            except ValueError:
                return False
        else:
            return False

    def __repr__(self):

        return p_slot(self.head)

    def __len__(self):

        return len(self._predicates)

    @staticmethod
    def from_triples(triples):

        slots = {}
        predicates = {}
        subs = set()
        objs = set()

        for t in triples:

            subs.add(t['subject'])
            objs.add(t['object'])

            if t['subject'] in slots:
                s = slots[t['subject']]
            else:
                s = Slot(t['subject'], [])
                slots[t['subject']] = s

            if t['object'] in slots:
                o = slots[t['object']]
            else:
                o = Slot(t['object'], [])
                slots[t['object']] = o

            if (t['subject'], t['predicate']) in predicates:
                p = predicates[(t['subject'], t['predicate'])]

                p.objects.append(o)

            else:
                p = Predicate(t['predicate'], [o])
                s.predicates.append(p)

                predicates[(t['subject'], t['predicate'])] = p

        # gets the slot that isn't object
        subs_not_objs = subs - objs

        if len(subs_not_objs) != 1:
            raise ValueError(MSG_ERROR_FROM_TRIPLES)

        head = slots[list(subs_not_objs)[0]]

        return Structure(head)


STRING_TEMPLATE_SLOTS = re.compile(r'\{(.*?)\}')


class Template:

    def __init__(self, structure, template_text, meta):

        Template.validate_template_text(structure, template_text)

        self.structure = structure
        self.template_text = template_text
        self.meta = meta

    def fill(self, data, lexicalization_f):

        positioned_data = self.structure.position_data(data)

        positioned_data = {k: lexicalization_f(v) for k, v in
                           positioned_data.items()}

        return self.template_text.format(**positioned_data)

    def __hash__(self):

        return hash((self.structure, self.template_text))

    def __eq__(self, other):

        return isinstance(self, type(other)) and \
               self.structure == other.structure and \
               self.template_text == other.template_text

    def __repr__(self):

        return 'Structure: {}\nText: {}'.format(self.structure,
                                              self.template_text)

    @staticmethod
    def validate_template_text(structure, template_text):

        template_slots = set(STRING_TEMPLATE_SLOTS.findall(template_text))

        structure_slots = set(route_slots(structure.head))

        if not template_slots == structure_slots:
            raise ValueError(MSG_ERROR_VALIDATE_TEMPLATE_TEXT)


class StructureData:

    def __init__(self, template_db):
        self.template_db = template_db

    def structure(self, triples):

        triples_struc = Structure.from_triples(triples)

        if triples_struc in self.template_db:

            return [(triples_struc, self.template_db[triples_struc])]

        else:
            structured_data = []

            for triple in triples:

                s = Structure.from_triples([triple])

                structured_data.append((s, self.template_db[s]))

            return structured_data


class JustJoinTemplate:

    def fill(self, data, lexicalization_f):

        if len(data) != 1:
            raise ValueError('this template only accepts data w/ 1 triple')

        s = lexicalization_f(data.head.value)
        p = lexicalization_f(data.head.predicates[0].value)
        o = lexicalization_f(data.head.predicates[0].objects[0].value)

        return f'{s} {p} {o}.'

    def __repr__(self):
        return 'template {s} {p} {o}.'


class SelectTemplate:

    def select_template(self, structured_data):

        return [(s, ts.most_common(1)[0][0]) for s, ts in structured_data]


class MakeText:

    def __init__(self, lexicalization_f=None):
        self.lexicalization_f = lexicalization_f

    def make_text(self, lexicalized_templates):

        texts = [t.fill(s, self.lexicalization_f)
                 for s, t in lexicalized_templates]

        return ' '.join(texts)
