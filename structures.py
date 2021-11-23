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


class Piece:
    """ a single unit of erging, e.g. a 2000m or 5:00 piece. """ 
    def __init__(self, meters, time):
        try:
            self.meters = meters
            self.time = time
            self.split = averageOfOne(meters, time)
        except Exception as e:
            print(str(e), ': in Piece. Is the time a datetime.time?')


    def __str__(self):
        s = f"Piece({self.meters}m , {self.time}, {self.split})"
        return s