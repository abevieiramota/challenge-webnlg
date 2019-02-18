from sklearn.base import BaseEstimator

class OneSentenceAggregator(BaseEstimator):
    
    def aggregate(self, data):
        
        return [data]
    


class IfChainThenAggregate(BaseEstimator):
    
    def aggregate(self, data):
        
        aggregated = []
        
        previous_object = None
        current_aggregation = None
        
        for triple in data:
            
            if triple['subject'] == previous_object:
                current_aggregation.append(triple)
            else:
                current_aggregation = [triple]
                aggregated.append(current_aggregation)
                
            previous_object = triple['object']
                
        return aggregated