from collections import namedtuple
import re

Slot = namedtuple('Slot', ['value', 'predicates'])
Predicate = namedtuple('Predicate', ['value', 'objects'])


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


def route_predicates(s):

    predicates = list(s.predicates)

    for p in predicates:

        yield p.value

        for o in p.objects:

            predicates.extend(o.predicates)


def route_match(s1, s2):

    yield s1.value, s2.value

    predicates = list(zip(s1.predicates, s2.predicates))

    for p1, p2 in predicates:

        for o1, o2 in zip(p1.objects, p2.objects):

            yield o1.value, o2.value

            predicates.extend(zip(o1.predicates, o2.predicates))


class Structure:

    def __init__(self, head):

        self.head = head
        self._predicates = tuple(route_predicates(self.head))

    def __hash__(self):

        return hash(self._predicates)

    def __eq__(self, other):

        return isinstance(self, type(other)) and \
               self._predicates == other._predicates

    def __repr__(self):

        return '\n'.join(route_str(self.head))

    def __len__(self):

        return len(self._predicates)


STRING_TEMPLATE_SLOTS = re.compile(r'\{(.*?)\}')


def validate_template_text(structure, template_text):

    template_slots = STRING_TEMPLATE_SLOTS.findall(template_text)

    if len(template_slots) > len(set(template_slots)):
        raise ValueError('template_text must have unique slots')

    structure_slots = list(route_slots(structure.head))

    if len(structure_slots) > len(set(structure_slots)):
        raise ValueError('structure must have unique slots')

    if not template_slots == structure_slots:
        raise ValueError('structure and template_text must match slots')


class Template:

    def __init__(self, structure, template_text):

        validate_template_text(structure, template_text)

        self.structure = structure
        self.template_text = template_text

    def fill(self, data, lexicalize):

        positioned_data = self.position_data(data)

        positioned_data = {k: lexicalize(v) for k,v in positioned_data.items()}

        return self.template_text.format(**positioned_data)

    def position_data(self, data):

        if self.structure != data:
            raise ValueError('data must have the same structure as '
                             'the template\'s'
                             )

        return dict(route_match(self.structure.head, data.head))

    def __hash__(self):

        return hash(self.structure, self.template_text)

    def __eq__(self, other):

        return isinstance(self, type(other)) and \
               self.structure == other.structure and \
               self.template_text == other.template_text


class StructureData:

    def __init__(self, template_db):
        self.template_db = template_db

    def structure(self, triples):

        structured_data = []

        for triple in triples:

            o0 = Slot(triple['object'], [])
            p0 = Predicate(triple['predicate'], [o0])
            s0 = Slot(triple['subject'], [p0])

            s = Structure(s0)

            ts = self.template_db[s]

            structured_data.append((s, ts))

        return structured_data


class JustJoinTemplate:

    def fill(self, data, lexicalize):

        if len(data) != 1:
            raise ValueError('this template only accepts data w/ 1 triple')

        s = lexicalize(data.head.value)
        p = data.head.predicates[0].value
        o = lexicalize(data.head.predicates[0].objects[0].value)

        return f'{s} {p} {o}.'

    def __repr__(self):
        return 'template {s} {p} {o}.'


class SelectTemplate:

    def select_template(self, structured_data):

        selected_templates = [(s, ts[0]) for s, ts in structured_data]

        return selected_templates


class MakeText:

    def __init__(self, lexicalize=None):

        if lexicalize is None:
            lexicalize = lambda x: x
        self.lexicalize = lexicalize

    def make_text(self, lexicalized_templates):

        texts = [t.fill(s, self.lexicalize) for s, t in lexicalized_templates]

        return ' '.join(texts)
