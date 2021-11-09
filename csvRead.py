import csv
import sys

def csvReader(filename:str):
    """Function for reading CSV files of the standard MyBoathouse format
    Takes filename as input, creates a dictionary with keys "distances" -- 
    the lengths of the pieces -- 
    and each athlete with a list of their scores for each piece"""
    out = {}

    # read the csv
    csvFile = open(filename)
    reader = csv.DictReader(csvFile, delimiter=',', quotechar='|')
    lines = list(reader)
    csvFile.close()

    # first row of csv
    header = lines[0]
    notesLine = lines[1]
    pieces = [] # the keys from the first row, eg. 'Piece 1', 'Piece 2' etc. Allows any number of pieces
    distances = []  # the distance or time of the piece
    notes = [] # notes per piece
    for key in header:
        if 'Piece ' in key:
            pieces.append(key)
            distances.append(header[key])
            notes.append(notesLine[key])
    

    # from the rest of the lines, make a dict of format {athlete : [p1score, p2score, ...]}
    scoresByAthlete = {}
    for i in range(2, len(lines)):
        row = lines[i]
        athlete = row['MyBoathouse']
        scores = []
        for key in pieces:
            scores.append(row[key])

        scoresByAthlete[athlete] = scores


    out['distances'] = distances
    out['notes'] = notes
    out['scores_by_athlete'] = scoresByAthlete

    print(out)







if __name__ == "__main__":
    csvReader('test.csv')