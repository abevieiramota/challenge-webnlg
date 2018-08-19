import logging

jjs_logger = logging.getLogger("JustJoinSentencesSentenceAggregator")
class JustJoinSentencesSentenceAggregator:

    def __init__(self, sep=' '):

        self.sep = sep

        jjs_logger.debug("Initialized with sep [%s]",
                         self.sep)
        

    def aggregate(self, sentences):

        return self.sep.join(sentences)