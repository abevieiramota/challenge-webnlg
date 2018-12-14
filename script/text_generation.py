class PipelineTextGenerator:

    def __init__(self, content_selection, sentence_generator, sentence_aggregator, discourse_structurer, lexicalizer):

        self.content_selection = content_selection
        self.sentence_generator = sentence_generator
        self.sentence_aggregator = sentence_aggregator
        self.discourse_structurer = discourse_structurer
        self.lexicalizer = lexicalizer


    def generate(self, data):

        generated_texts = []

        # rename entry/data -> confusion between entry data and the whole dataset
        for entry in data:

            selected_entry = self.content_selection.select(entry)
            sorted_data = self.discourse_structurer.sort(selected_entry)
            sentences = [self.sentence_generator.generate(self.lexicalizer.lexicalize(d)) for d in sorted_data]
            text = self.sentence_aggregator.aggregate(sentences)

            generated_texts.append(text)

        return generated_texts


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
