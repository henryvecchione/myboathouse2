# structures.py
import datetime
from helpers import averageOfOne, averageOfAll, autoTitle

class Workout:
    """ an individual athlete's workout. Composed of an athlete's ID (int) and 
        pieces (list of Piece objects). e.g. a 6x2000m workout by athlete 
        no. 69 is a Workout with id = 69 and scores = [Piece(2000m), Piece(2000m)... x6]"""

    def __init__(self, athleteId, scores):
        self.athleteId = athleteId # int : ID of athlete doing the workout
        self.scores = scores # list of Piece objects 
        self.split = averageOfAll(scores) # datetime.time average split

    """ append a Piece object """
    def addPiece(self, piece):
        self.scores.append(piece)

    def __str__(self):
        s = f'Workout({self.athleteId}, {self.scores}, {self.split})'
        return s

    def __lt__(self,other):
        return self.split < other.split

    def __gt__(self,other):
        return self.split > other.split

    def __eq__(self,other):
        return self.split == other.split

    def __le__(self,other):
        return self.split <= other.split

    def __ge__(self,other):
        return self.split >= other.split


class Piece:
    """ a single unit of erging, e.g. a 2000m or 5:00 piece. """ 
    def __init__(self, meters, time, isDistance):
        try:
            self.meters = meters
            self.time = datetime.datetime.combine(datetime.date(2000, 2, 26), time)
            self.split = datetime.datetime.combine(datetime.date(2000, 2, 26), averageOfOne(meters, time))
             # Bool: True if the workout was a distance workout, e.g. a 2000m or 6000m piece. 
             # False if it's a timed piece, e.g. 30:00, 10:00
            self.isDistance = isDistance
        except Exception as e:
            print(str(e), ': in class Piece. Is the time a datetime.time?')
            return


    def score(self, as_string=False):
        """ returns the 'score', i.e. how the athlete performed over the prescribed
            distance or time, in a tuple with the split. e.g for a 2000m piece, 
            returns (6:20, 1:35), for a 30:00, returns (8411, 1:47)"""
        if not as_string:   
            if self.isDistance:
                return (self.time, self.split)
            else:
                return (self.meters, self.split)
        else:
            splitStr = self.split.strftime('%-M:%S.%f')[:-5]
            if self.isDistance:
                return (self.time.strftime('%-M:%S'), splitStr)
            else:
                return (str(self.meters), splitStr)

    def watts(self):
        return NotImplemented


    def __str__(self):
        if self.isDistance:
            s = f"Piece: Distance: {self.meters}, Time: {self.time}"
        else:
            s = f"Piece: Time: {self.time}, Distance: {self.meters}"
        return s


    def __lt__(self,other):
        return self.split < other.split

    def __gt__(self,other):
        return self.split > other.split

    def __eq__(self,other):
        return self.split == other.split

    def __le__(self,other):
        return self.split <= other.split

    def __ge__(self,other):
        return self.split >= other.split
