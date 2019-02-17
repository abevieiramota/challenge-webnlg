from sklearn.base import BaseEstimator, RegressorMixin

class TemplateBasedTextGenerator(BaseEstimator, RegressorMixin):

    def __init__(self, 
                 content_selection_model, 
                 sentence_generation_model, 
                 lexicalization_model,
                 discourse_structuring_model,
                 sentence_aggregation_model):

        self.content_selection_model = content_selection_model
        self.sentence_generation_model = sentence_generation_model
        self.lexicalization_model = lexicalization_model
        self.discourse_structuring_model = discourse_structuring_model
        self.sentence_aggregation_model = sentence_aggregation_model


    def predict(self, X):

        return [self.predict_entry(x) for x in X]

    def predict_entry(self, x):

        selected_content = self.content_selection_model.select(x)
        structured = self.discourse_structuring_model.structure(selected_content)
        aggregated = self.sentence_aggregation_model.aggregate(structured)
        
        lexicalized = [self.lexicalization_model.lexicalize(t) for t in aggregated]
        sentences = [self.sentence_generation_model.generate(t) for t in lexicalized]
        

        return ' '.join(sentences)



class IfAfterNthProcessPipelineTextGenerator:

    def __init__(self, content_selection, sentence_generator, sentence_aggregator, discourse_structurer, lexicalizer, processor=lambda x: x, nth=-1):

        self.content_selection = content_selection
        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator
        self.processor = processor
        self.nth = nth
        self.discourse_structurer = discourse_structurer
        self.lexicalizer = lexicalizer


    def generate(self, data):

        generated_texts = []

        for entry in data:

            selected_entry = self.content_selection.select(entry)

            sorted_data = self.discourse_structurer.sort(selected_entry)

            sentences = []
            for i, d in enumerate(sorted_data):

                if i > self.nth:

                    d = self.processor(d)
                
                sentence = self.sentence_generator.generate(self.lexicalizer.lexicalize(d))

                sentences.append(sentence)

            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts
