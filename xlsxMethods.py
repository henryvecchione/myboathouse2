import xlsxwriter
import openpyxl
import pandas as pd
import database as db
from helpers import autoTitle
from pprint import pprint


def xlsxRead(filename):

    xlsx = pd.read_excel(filename)
    data = pd.DataFrame(xlsx)
    data = data.T

    # parse the date and pieces
    date = data[0]['MyBoathouse']
    pieces = list(data.index)[2:]
    for i in range(len(pieces)):
        if '.' in pieces[i]:
            pieces[i] = pieces[i].split('.')[0]
    notes = list(note for note in data[0][2:] if note) # all non-empty notes

    # parse the scores
    scoresDict = {}
    for i in data.keys():
        if i < 2:
            continue
        # this isn't obvious but necessitated by structure of sheet
        col = data[i]
        first = col['MyBoathouse']
        last = col['Piece:']
        athleteId = db.queryAthleteByName(first, last)['_id']
        scores = []
        for piece in pieces:
            scores.append(str(col[piece]))
        scoresDict[athleteId] = scores
    workoutDict = {
        'title' : ', '.join(pieces),
        'date' : date,
        'pieces' : pieces,
        'scores' : scoresDict,
        'notes' : notes
    }

    return workoutDict

def xlsxWrite():
    return NotImplemented

if __name__ == "__main__":
    pprint((xlsxRead('test.xlsx')))
