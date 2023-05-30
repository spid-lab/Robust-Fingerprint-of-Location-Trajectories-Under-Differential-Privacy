from imports import *
from configuration import *

class Detection:

    @staticmethod
    def similarity_detection(leak_trajectory, candidates):
        scores = np.zeros((len(candidates),))
        length = len(leak_trajectory)
        for i, (leak_lat, leak_lng, _) in enumerate(leak_trajectory):
            suspects = []
            for j, (cand_trajectory, _) in enumerate(candidates):

                cand_lat, cand_lng, _ = cand_trajectory[i]
                suspects.append((leak_lat - cand_lat)**2 + (leak_lng - cand_lng)**2)
            min_value = min(suspects)

            suspects = list(filter(lambda x: suspects[x] == min_value, range(len(suspects))))
            for suspect in suspects:
                scores[suspect] += 1/length
                
        return np.argmax(scores), scores