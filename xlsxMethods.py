import xlsxwriter
import openpyxl
import pandas as pd
import database as db
from helpers import autoTitle
from pprint import pprint
from io import StringIO, BytesIO
from structures import Workout, Piece
import datetime
from bson.binary import Binary
import pickle
import random


def xlsxRead(filename, teamId):
    """ Reads a .xlsx file of the format generated by the method below 
        Creates a workout dictionary of the document format to be 
        uploaded to Mongo
    """

    xlsx = pd.read_excel(filename)
    data = pd.DataFrame(xlsx)
    data = data.T

    # parse the date and pieces
    date = data[0]['irgo']
    if 'Y' in date or 'M' in date or 'D' in date:
        date = datetime.datetime.now()
    pieces = list(data.index)[2:] 

    notes = list(note for note in data[0][2:] if note) # all non-empty notes

    # parse the scores
    workoutList = []
    for i in data.keys():
        if i < 2:
            continue
        # this isn't obvious but necessitated by structure of sheet
        col = data[i]
        # first and last name of athlete
        try:
            first = col['irgo'].capitalize()
            last = col['Piece:'].capitalize()
        except Exception as _:
            continue

        athleteId = str(db.queryAthleteByName(first, last)['_id'])

        scores = []

        for piece in pieces:
            try:
                # if the piece is an int, e.g. 2000, make a distance piece
                if isinstance(piece, int):
                    t = str(col[piece]).split(':')
                    if t[0] == '00':
                        print(t)
                        t_sec, t_tenth = t[2].split('.') 
                        time = datetime.time(minute=int(t[1]), second=int(t_sec), microsecond=int(t_tenth))
                        print(time, '1, 1')
                    else:
                        t_tenth = (t[2].split('.'))[1]
                        time = datetime.time(minute=int(t[0]), second=int(t[1]), microsecond=int(t_tenth))
                        print(time, '1, 2')
                    p = Piece(piece, time, True)
                    scores.append(p)
                # else if its a datetime, make a time piece
                elif isinstance(piece, datetime.time):
                    meters = int(col[piece])
                    time = datetime.time(minute=piece.hour, second=piece.minute)
                    p = Piece(meters, time, False)
                    scores.append(p)
                # read_excel, if there are duplicate col headers, appends a .X, e.g 2000, 2000.1, 2000.2... 
                # trim this off, make it an int
                elif '.' in piece:
                    meters = int(piece.split('.')[0])
                    t = str(col[piece]).split(':')
                    if t[0] == '00':
                        t_sec, t_tenth = t[2].split('.') 
                        time = datetime.time(minute=int(t[1]), second=int(t_sec), microsecond=int(t_tenth))
                        print(time, '2, 1')
                    else:
                        t_tenth = (t[2].split('.'))[1]
                        time = datetime.time(minute=int(t[0]), second=int(t[1]), microsecond=int(t_tenth))
                        print(time, '2, 2')
                    p = Piece(meters, time, True)
                    scores.append(p)
                else:
                    print("Distance/time mismatch")
                    return None
            except TypeError as e:
                print(str(e))
                print("Distance/Time mismatch")
                return None
                
        workout = Workout(athleteId, scores)
        workoutList.append(workout)
        
    try:
        nextId = int(db.getAllWorkouts(teamId, sort_by='_id')[0]['_id']) + 1 # increment _id
    except IndexError:
        nextId = random.randint(1, 1000)

    workoutListBytes = pickle.dumps(workoutList)


    workoutDict = {
        '_id' : nextId,
        'title' : ', '.join(str(p) for p in pieces),
        'date' : date,
        'pieces' : [str(p) for p in pieces],
        'scores' : Binary(workoutListBytes),
        'notes' : notes
    }

    return workoutDict



# --------------------------------------------------------------------------------------#
def xlsxBlank(teamId):
    """ Creates a blank .xlsx file of the format compatible to be read
        by the method above. Sheet1 is the blank sheet, Sheet2 is the 
        roster pulled from the database
    """

    output = BytesIO()

    # create the workbook
    workbook = xlsxwriter.Workbook(output, {'in_memory' : True})
    worksheet = workbook.add_worksheet('scores') # sheet for scores
    worksheet1 = workbook.add_worksheet('roster') # roster sheet
    bold = workbook.add_format({'bold' : True})

    # score sheet header info
    header = ['irgo', 'Piece:', '(XXXX | mm:ss)', '(XXXX | mm:ss)', '(XXXX | mm:ss)']
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    notes = [date, 'Notes:']
    firstLast = ['First', 'Last']
    example = ['(mm:ss | YYYY)','(mm:ss | YYYY)','(mm:ss | YYYY)']
    worksheet.write_row('A1', header, bold)
    worksheet.write_row('A2', notes, bold)
    worksheet.write_row('A3', firstLast, bold)
    worksheet.write_row('C4', example)

    # write the vlookup formula that fills names from the roser
    for i in range(4, 50):
        cell = 'A' + str(i)
        formula = '=IF(B{}<>"",VLOOKUP(B{},roster!A:B,2,FALSE), "")'.format(str(i),str(i))
        worksheet.write_formula(cell, formula)

    # write in the athletes
    try:
        athletes = db.getAllAthletes(teamId)
        for ind, a in enumerate(athletes):
            nameRow = [a['last'], a['first']]
            cell = 'A' + str(ind + 1) # enumerate is 0-index but excel is 1-index
            worksheet1.write_row(cell, nameRow)
        workbook.close()
    except Exception as e:
        print(str(e))
        workbook.close()

    output.seek(0)
    return output

# --------------------------------------------------------------------------------------#

# test code
if __name__ == "__main__":
    pprint((xlsxRead( 'test5.xlsx', 1887)))
    xlsxBlank(1887)