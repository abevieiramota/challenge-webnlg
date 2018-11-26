import logging
from sklearn.base import BaseEstimator

class JustJoinSentencesSentenceAggregator(BaseEstimator):

    def __init__(self, sep=' '):

        self.sep = sep
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug(f"Initialized with sep [{self.sep}]")
        

    def aggregate(self, sentences):

        return self.sep.join(sentences)