class PipelineTextGenerator:

    def __init__(self, sentence_generator, sentence_aggregator):

        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator

    def generate(self, data):

        generated_texts = []

        for entry in data:
            sentences = [self.sentence_generator.generate(d) for d in entry]
            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts

class IfAfterNthProcessPipelineTextGenerator:

    def __init__(self, sentence_generator, sentence_aggregator, processor=lambda x: x, nth=-1):

        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator
        self.processor = processor
        self.nth = nth

    def generate(self, data):

        generated_texts = []

        for entry in data:

            sentences = []
            for i, d in enumerate(entry):

                if i > self.nth:

                    d = self.processor(d)
                
                sentence = self.sentence_generator.generate(d)

                sentences.append(sentence)

            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts
