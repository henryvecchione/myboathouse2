import csv
import sys
import datetime
from helpers import autoTitle
from pprint import pprint

def csvReader(filename:str):
    """Function for reading CSV files of the standard MyBoathouse format
    Takes filename as input, creates a dictionary with keys "distances" -- 
    the lengths of the pieces -- 
    and each athlete with a list of their scores for each piece"""

    # read the csv
    csvFile = open(filename)
    reader = csv.reader(csvFile, delimiter=',', quotechar='|')
    lines = list(reader)
    csvFile.close()

    # first row of csv
    date = lines[1][1].split('/')
    test = (lines[2][1] != str(0))
    pieces = lines[3][2:]
    notes = list(note for note in lines[4][2:] if note)

    scoresDict = {}
    for row in lines[5:]:
        athleteId = row[0]
        scores = []
        scores = list(score for score in row[2:] if score) # terrible code. means add to list if not empy :)
        scoresDict[athleteId] = scores

    pprint(scoresDict)

    workoutDict = {
        'title' : autoTitle(pieces),
        'date' : datetime.datetime(int(date[2])+2000, int(date[0]), int(date[1])),
        'pieces' : list(p for p in pieces if p), # terrible code. means add to list if not empy :)
        'scores' : scoresDict,
        'notes' : notes,
        'test' : test
    }

    pprint(workoutDict)

    







if __name__ == "__main__":
    csvReader('test.csv')