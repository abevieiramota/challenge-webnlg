class PipelineTextGenerator:

    def __init__(self, sentence_generator, sentence_aggregator, discourse_structurer, lexicalizer):

        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator
        self.discourse_structurer = discourse_structurer
        self.lexicalizer = lexicalizer

    def generate(self, data):

        generated_texts = []

        for entry in data:
            sorted_data = self.discourse_structurer.sort(entry)
            sentences = [self.sentence_generator.generate(self.lexicalizer.lexicalize(d)) for d in sorted_data]
            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts


class IfAfterNthProcessPipelineTextGenerator:

    def __init__(self, sentence_generator, sentence_aggregator, discourse_structurer, lexicalizer, processor=lambda x: x, nth=-1):

        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator
        self.processor = processor
        self.nth = nth
        self.discourse_structurer = discourse_structurer
        self.lexicalizer = lexicalizer

    def generate(self, data):

        generated_texts = []

        for entry in data:

            sorted_data = self.discourse_structurer.sort(entry)

            sentences = []
            for i, d in enumerate(sorted_data):

                if i > self.nth:

                    d = self.processor(d)
                
                sentence = self.sentence_generator.generate(self.lexicalizer.lexicalize(d))

                sentences.append(sentence)

            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts
