import logging


fbp_logger = logging.getLogger("FallBackPipelineSentenceGenerator")
class FallBackPipelineSentenceGenerator:

    def __init__(self, models):

        self.models = models 

    def generate(self, data):

        for model in self.models:

            generated_sentence = model.generate(data)

            if generated_sentence:
                return generated_sentence
        
            fbp_logger.debug("Fallback from [%s] for data [%s]", model, data)

        return None


class JustJoinTripleSentenceGenerator:

    def __init__(self, sentence_template="{m_subject} {m_predicate} {m_object}", preprocessor=lambda x: x):

        self.sentence_template = sentence_template
        self.preprocessor = preprocessor

    def generate(self, data):

        preprocessed_data = {k: self.preprocessor(v) for k, v in data.items()}

        return self.sentence_template.format(**preprocessed_data)


mft_logger = logging.getLogger("MostFrequentTemplateSentenceGenerator")
class MostFrequentTemplateSentenceGenerator:

    def __init__(self, template_model, preprocessor=lambda x: x):

        self.template_db = {}
        self.preprocessor = preprocessor

        for k, templates in template_model.template_db.items():

            self.template_db[k] = max(templates.items(), key=lambda x: len(x[1]))[0]

        mft_logger.debug("Initialized with template_model [%s] preprocessor [%s]",
                         template_model, self.preprocessor)


    def generate(self, data):

        m_predicate = data['m_predicate']

        preprocessed_data = {k: self.preprocessor(v) for k, v in data.items()}

        if m_predicate not in self.template_db:

            mft_logger.debug("Not found predicate [%s]", m_predicate)

            return None 

        template = self.template_db[m_predicate]

        mft_logger.debug("Template found for m_predicate [%s]\nTemplate: %s", m_predicate, template)

        return template.fill(preprocessed_data)

    def predicates(self):

        return self.template_db.keys()


npt_logger = logging.getLogger("NearestPredicateTemplateSentenceGenerator")
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

        for predicate in predicates:

            nearest, sim = self.get_nearest_predicate(predicate)

            npt_logger.debug("Found nearest predicate [%s] from [%s] with similarity [%f]",
                             nearest, predicate, sim)

            self.nearest_predicate[predicate] = (nearest, sim)

        npt_logger.debug("Initialized with similarity metric [%s] and threshold [%f]", 
                         self.similarity_metric, self.threshold)


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

        npt_logger.debug("Found nearest predicate [%s], with similarity [%f], for predicate [%s]",
                         nearest_predicate, sim, predicate)

        if sim > self.threshold:

            preprocessed_data['m_predicate'] = nearest_predicate

            return self.template_sentence_generator.generate(preprocessed_data)
        
        else:
            npt_logger.debug("Not found nearest predicate.")
            return None



