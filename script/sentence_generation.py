import logging

class JustJoinTripleSentenceGenerator():

    def generate(self, triples):

        sentences = [] 
        for triple in triples:

            sentence = '{subject} {predicate} {object}'.format(**triple)

            sentences.append(sentence)
        
        return ' '.join(sentences)

class MostFrequentTemplateSentenceGenerator():

    def __init__(self):

        self.template_db = None
        self.logger = logging.getLogger(self.__class__.__name__)


    def fit(self, template_db):

        self.template_db = {}
        for predicate, templates_counter in template_db.items():

            self.template_db[predicate] = templates_counter.most_common(1)[0][0]

        return self


    def generate(self, triples):

        sentences = [] 

        for triple in triples:
        
            if triple['predicate'] in self.template_db:
            
                template = self.template_db[triple['predicate']]

                self.logger.debug(f"Template found for predicate [{triple['predicate']}]\nTemplate: {template}")

                sentence = template.fill(triple)
                sentences.append(sentence)

        return ' '.join(sentences)


    def predicates(self):

        return self.template_db.keys()


class NearestPredicateTemplateSentenceGenerator():

    def __init__(self, sentence_generator, similarity_metric=None, 
                       threshold=None):

        if not similarity_metric:
            raise ValueError("similarity_metric mustn't be None")
        if not threshold:
            raise ValueError("threshold mustn't be None")

        self.sentence_generator = sentence_generator
        self.similarity_metric = similarity_metric
        self.threshold = threshold

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Initialized with similarity metric [{self.similarity_metric}] and threshold [{self.threshold}]")


    def fit(self, template_db):

        self.template_db = template_db


    def get_nearest_predicate(self, predicate):
    
        similarities = []
    
        for known_predicate in self.template_db.keys():
            
            sim = self.similarity_metric(known_predicate, predicate)
            
            similarities.append((known_predicate, sim))
        
        return max(similarities, key=lambda v: v[1])        


    def generate(self, triple):
        
        predicate = triple['predicate']

        nearest_predicate, sim = self.get_nearest_predicate(predicate)

        self.logger.debug(f"Found nearest predicate [{nearest_predicate}], with similarity [{sim}], for predicate [{predicate}]")

        if sim > self.threshold:

            triple['predicate'] = nearest_predicate

            return self.sentence_generator.generate(triple)
        
        else:
            self.logger.debug("Not found nearest predicate.")

            return None


class FallBackPipelineSentenceGenerator():

    def __init__(self, models):

        self.models = models 
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate(self, triples):

        sentences = []

        for triple in triples:

            for model in self.models:
                
                generated_sentence = model.generate(triple)

                if generated_sentence:
                    sentences.append(generated_sentence)
                    continue
                self.logger.debug(f"Fallback from [{model}] for data [{triple}]")

        return ' '.join(sentences)
