import logging
from itertools import islice


class SelectAllContentSelector():

    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)
        

    def select(self, data):

        return data


class SelectFirstNContentSelection():

    def __init__(self, n=1, sort_function=lambda x: x):

        self.n = n
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sort_function = sort_function

    
    def select(self, data):

        data_sorted = self.sort_function(data)

        return list(islice(data_sorted, 0, self.n))

        