import logging
from sklearn.base import BaseEstimator


class FallBackPipelineSentenceGenerator(BaseEstimator):

    def __init__(self, models):

        self.models = models 
        self.logger = logging.getLogger(self.__class__.__name__)

    
    def fit(self, template_model):

        for model in self.models:

            model.fit(template_model)


    def generate(self, data):

        for model in self.models:

            generated_sentence = model.generate(data)

            if generated_sentence:
                return generated_sentence
        
            self.logger.debug(f"Fallback from [{model}] for data [{data}]")

        return None


class JustJoinTripleSentenceGenerator(BaseEstimator):

    def __init__(self, sentence_template="{subject} {predicate} {object}"):

        self.sentence_template = sentence_template


    def fit(self, *args, **kwargs):

        pass


    def generate(self, data):

        return self.sentence_template.format(**data)


class MostFrequentTemplateSentenceGenerator(BaseEstimator):

    def __init__(self):

        self.template_db = {}
        self.logger = logging.getLogger(self.__class__.__name__)


    def fit(self, template_model):

        for k, templates in template_model.template_db.items():

            self.template_db[k] = max(templates.items(), key=lambda x: len(x[1]))[0]

        self.logger.debug(f"Initialized with template_model [{template_model}]")


    def generate(self, data):

        predicate = data['predicate']

        if predicate not in self.template_db:

            self.logger.debug(f"Not found predicate [{predicate}]")

            return None 

        template = self.template_db[predicate]

        self.logger.debug(f"Template found for predicate [{predicate}]\nTemplate: {template}")

        return template.fill(data)

    def predicates(self):

        return self.template_db.keys()


class NearestPredicateTemplateSentenceGenerator(BaseEstimator):

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


    def fit(self, template_model):

        self.template_model = template_model


    def get_nearest_predicate(self, predicate):
    
        similarities = []
    
        for known_predicate in self.template_model.template_db.keys():
            
            sim = self.similarity_metric(known_predicate, predicate)
            
            similarities.append((known_predicate, sim))
        
        return max(similarities, key=lambda v: v[1])        


    def generate(self, data):

        predicate = data['predicate']

        nearest_predicate, sim = self.get_nearest_predicate(predicate)

        self.logger.debug(f"Found nearest predicate [{nearest_predicate}], with similarity [{sim}], for predicate [{predicate}]")

        if sim > self.threshold:

            data['predicate'] = nearest_predicate

            return self.sentence_generator.generate(data)
        
        else:
            self.logger.debug("Not found nearest predicate.")

            return None



