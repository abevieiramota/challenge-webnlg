import logging


class FallBackPipelineSentenceGenerator:

    def __init__(self, models):

        self.models = models 
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate(self, data):

        for model in self.models:

            generated_sentence = model.generate(data)

            if generated_sentence:
                return generated_sentence
        
            self.logger.debug(f"Fallback from [{model}] for data [{data}]")

        return None


class JustJoinTripleSentenceGenerator:

    def __init__(self, sentence_template="{m_subject} {m_predicate} {m_object}", preprocessor=lambda x: x):

        self.sentence_template = sentence_template
        self.preprocessor = preprocessor

    def generate(self, data):

        preprocessed_data = {k: self.preprocessor(v) for k, v in data.items()}

        return self.sentence_template.format(**preprocessed_data)


class MostFrequentTemplateSentenceGenerator:

    def __init__(self, template_model, preprocessor=lambda x: x):

        self.template_db = {}
        self.preprocessor = preprocessor
        self.logger = logging.getLogger(self.__class__.__name__)

        for k, templates in template_model.template_db.items():

            self.template_db[k] = max(templates.items(), key=lambda x: len(x[1]))[0]

        self.logger.debug(f"Initialized with template_model [{template_model}] preprocessor [{self.preprocessor}]")


    def generate(self, data):

        m_predicate = data['m_predicate']

        preprocessed_data = {k: self.preprocessor(v) for k, v in data.items()}

        if m_predicate not in self.template_db:

            self.logger.debug(f"Not found predicate [{m_predicate}]")

            return None 

        template = self.template_db[m_predicate]

        self.logger.debug(f"Template found for m_predicate [{m_predicate}]\nTemplate: {template}")

        return template.fill(preprocessed_data)

    def predicates(self):

        return self.template_db.keys()


class NearestPredicateTemplateSentenceGenerator:

    def __init__(self, template_sentence_generator, similarity_metric=None, 
                       predicates=None, preprocessor=lambda x: x, 
                       threshold=None):

        if not similarity_metric:
            raise ValueError("similarity_metric mustn't be None")
        if not predicates:
            raise ValueError("predicates mustn't be None")
        if not threshold:
            raise ValueError("threshold mustn't be None")

        self.template_sentence_generator = template_sentence_generator
        self.preprocessor = preprocessor
        self.similarity_metric = similarity_metric
        self.known_predicates = self.template_sentence_generator.predicates()
        self.threshold = threshold

        self.nearest_predicate = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        for predicate in predicates:

            nearest, sim = self.get_nearest_predicate(predicate)

            self.logger.debug(f"Found nearest predicate [{nearest}] from [{predicate}] with similarity [{sim}]")

            self.nearest_predicate[predicate] = (nearest, sim)

        self.logger.debug(f"Initialized with similarity metric [{self.similarity_metric}] and threshold [{self.threshold}]")


    def get_nearest_predicate(self, predicate):
    
        similarities = []
    
        for known_predicate in self.known_predicates:
            
            sim = self.similarity_metric(known_predicate, predicate)
            
            similarities.append((known_predicate, sim))
        
        return max(similarities, key=lambda v: v[1])        


    def generate(self, data):

        predicate = data['m_predicate']
        preprocessed_data = {k: self.preprocessor(v) for k, v in data.items()}

        nearest_predicate, sim = self.nearest_predicate[predicate]

        self.logger.debug(f"Found nearest predicate [{nearest_predicate}], with similarity [{sim}], for predicate [{predicate}]")

        if sim > self.threshold:

            preprocessed_data['m_predicate'] = nearest_predicate

            return self.template_sentence_generator.generate(preprocessed_data)
        
        else:
            self.logger.debug("Not found nearest predicate.")
            return None



