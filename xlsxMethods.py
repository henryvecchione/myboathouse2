import xlsxwriter
import openpyxl
import pandas as pd
import database as db
from helpers import autoTitle
from pprint import pprint


def xlsxRead(filename):
    """ Reads a .xlsx file of the format generated by the method below 
        Creates a workout dictionary of the document format to be 
        uploaded to Mongo
    """

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
        first = col['MyBoathouse'].capitalize()
        last = col['Piece:'].capitalize()
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



# --------------------------------------------------------------------------------------#
def xlsxWrite():
    """ Creates a blank .xlsx file of the format compatible to be read
        by the method above. Sheet1 is the blank sheet, Sheet2 is the 
        roster pulled from the database
    """
    # create the workbook
    workbook = xlsxwriter.Workbook('blank.xlsx')
    worksheet = workbook.add_worksheet() # sheet for scores
    worksheet1 = workbook.add_worksheet() # roster sheet
    bold = workbook.add_format({'bold' : True})

    # score sheet header info
    header = ['MyBoathouse', 'Piece:', '(XXXXm | mm:ss)', '(XXXXm | mm:ss)', '(XXXXm | mm:ss)']
    notes = ['YYYY-MM-DD', 'Notes:']
    firstLast = ['First', 'Last']
    example = ['(mm:ss | YYYYm)','(mm:ss | YYYYm)','(mm:ss | YYYYm)']
    worksheet.write_row('A1', header, bold)
    worksheet.write_row('A2', notes, bold)
    worksheet.write_row('A3', firstLast, bold)
    worksheet.write_row('C4', example)

    # write the vlookup formula that fills names from the roser
    for i in range(4, 50):
        cell = 'A' + str(i)
        formula = '=IF(B{}<>"",VLOOKUP(B{},Sheet2!A:B,2,FALSE), "")'.format(str(i),str(i))
        worksheet.write_formula(cell, formula)

    # write in the athletes
    ind = 1
    athletes = db.getAllAthletes(active_only=True)
    for a in athletes:
        nameRow = [a['last'], a['first']]
        cell = 'A' + str(ind)
        worksheet1.write_row(cell, nameRow)
        ind +=1

    workbook.close()

    return

# --------------------------------------------------------------------------------------#

# test code
if __name__ == "__main__":
    pprint((xlsxRead('test2.xlsx')))
    xlsxWrite()