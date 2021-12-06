from pymongo import MongoClient
import pymongo
import datetime
from pprint import pprint
import os 
import bcrypt
import pickle
import random


if 'database_url' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    CONNECTION_STRING = os.environ.get('database_url')
else:
    CONNECTION_STRING = os.environ['database_url']
    
DBNAME = 'irgo'
ATHLETE_COLLECTION = 'athletes'
WORKOUT_COLLECTION = 'workouts'
CREDENTIALS_COLLECTION = 'credentials'
TEAMS_COLLECTION = 'teams'

# ------------------------------------------------------------------- #
# General Database methods

def getDatabase():
    client = pymongo.MongoClient(CONNECTION_STRING)
    return client[DBNAME]

def getCollection(collection):
    try:
        dbname = getDatabase()
        return dbname[collection]
    except Exception as e:
        print(str(e))
        return None
# ------------------------------------------------------------------- #
# general athlete collection methods 

def addAthlete(athleteDict):
    # print(f'addAthlete called with {athleteDict}')
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.insert_one(athleteDict)
        return result.inserted_id
    except Exception as e:
        print(str(e))
        return None

def editAthlete(athleteId, field, newVal):
    # print(f'editAthlete called with {athleteId}, {field}, {newVal}')
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.update_one({'_id' : athleteId}, {'$set' : {field : newVal}})
        return result.modified_count
    except Exception as e:
        print(str(e))
        return None

def queryAthlete(athleteId):
    # print(f'queryAthlete called with {athleteId}')
    try:
        athleteId = int(athleteId)
        collection_name = getCollection(ATHLETE_COLLECTION)
        return collection_name.find_one({'_id' : athleteId})
    except Exception as e:
        print(str(e))
        return None

def queryAthleteByName(first, last):
    # print(f'queryAthleteByName called with {first} {last}')
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        return collection_name.find_one({'first' : first, 'last' : last})
    except Exception as e:
        print(str(e))
        return None

def getAllAthletes(teamId, sort_by='name', active_only=False):
    print(f'getAllAthletes called with {teamId}')    
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        if active_only:
            return collection_name.find({'active': True, 'teamId' : teamId}, sort=[(sort_by, pymongo.ASCENDING)])
        else:
            return collection_name.find({'teamId' : teamId}, sort=[(sort_by, pymongo.ASCENDING)])
    except Exception as e:
        print(str(e))
        return None

def addWorkoutToAthlete(athleteId, newWorkout, workoutId):
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.update({'_id' : int(athleteId)}, {'$set' : {f'workouts.{workoutId}' : newWorkout}})
        return result
    except Exception as e:
        print(str(e))
        return None

def removeWorkoutFromAthlete(athleteId, workoutId):
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.update({'_id' : athleteId}, {'$unset' : {f'workouts.{workoutId}' : ''}})
        return result
    except Exception as e:
        print(str(e))
        return None
# ------------------------------------------------------------------- #
# general workout collection methods 

def addWorkout(workoutDict, teamId):
    # print(f'addworkout called with {workoutDict}, {teamId}')
    try:
        print(workoutDict)
        collection_name = getCollection(WORKOUT_COLLECTION)
        workoutDict['teamId'] = teamId
        result = collection_name.insert_one(workoutDict)
        return result.inserted_id
    except Exception as e:
        print(str(e))
        return None

def editWorkout(workoutId, field, newVal):
    # print(f'editWorkout called with {workoutId}, {field}, {newVal}')
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        result = collection_name.update_one({'_id' : workoutId}, {'$set' : {field : newVal}})
        return result.modified_count
    except Exception as e:
        print(str(e))
        return None

def queryWorkout(workoutId):
    # print(f'queryWorkout called with {workoutId}')
    try:
        workoutId = int(workoutId)
        collection_name = getCollection(WORKOUT_COLLECTION)
        res = collection_name.find_one({'_id' : workoutId})
        temp = pickle.loads(res['scores'])
        res['scores'] = temp
        return res
    except Exception as e:
        print(str(e))
        return None

def deleteWorkout(workoutId):
    # print(f'deleteWorkout called with {workoutId}')
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        result = collection_name.delete_one({'_id' : workoutId})
        return result.deleted_count
    except Exception as e:
        print(str(e))
        return None

def getAllWorkouts(teamId, sort_by='date'):
    # print(f'getAllWorkouts called with {teamId}')
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        return collection_name.find({'teamId' : teamId}, sort=[(sort_by, pymongo.DESCENDING)])
    except Exception as e:
        print(str(e))
        return None

# ------------------------------------------------------------------ # 
# general team db methods
def queryTeam(teamId):
    # print(f'queryTeam called with {teamId}')
    try:
        teamId = int(teamId)
        collection_name = getCollection(TEAMS_COLLECTION)
        res = collection_name.find_one({'_id' : teamId})
        return res
    except Exception as e:
        print(str(e))
        return None

def addTeam(name):
    # print(f'addTeam called with {name}')
    try:
        teamId = random.randint(10, 999999)
        # ensure no id collision
        while queryTeam(teamId):
            teamId = random.randint(10, 999999) 

        collection_name = getCollection(TEAMS_COLLECTION)
        res = collection_name.insert_one({'_id' : teamId, 'name' : name})
        return res.inserted_id
    except Exception as e:
        print(str(e))
        return None

# ------------------------------------------------------------------- #
# takes a workout ID, gets all participating athletes, and adds that 
# workout to each athlete's 'workouts' array
def attributeWorkout(workoutId):
    try:
        athletes_collection = getCollection(ATHLETE_COLLECTION)
        workout_collection = getCollection(WORKOUT_COLLECTION)

        workout = workout_collection.find_one({'_id' : workoutId})
        # athletes who completeted the workout
        participating = [int(k) for k in workout['scores'].keys()]
        result = athletes_collection.update_many({'_id' : {'$in' : participating}}, {'$addToSet' : {'workouts' : workoutId}})
        return result.modified_count

    except Exception as e:
        print(str(e))
        return None


# ------------------------------------------------------------------- #
# gets athleteId's scores on workoutId
# return a list [(distance, time)] 
def getScoreByAthlete(athleteId, workoutId):
    try:
        workout_collection = getCollection(WORKOUT_COLLECTION)
        result = workout_collection.find_one({'_id' : workoutId })
        if not result:
            print('No workout with id ' + str(workoutId))
            return None
        try:
            return zip(result['pieces'] , result['scores'][str(athleteId)])
        except KeyError as _:
            print('Athlete with id ' + str(athleteId) + ' did not complete this workout')
            return None

    except Exception as e:
        print(str(e))
        return None

# ------------------------------------------------------------------- #
# add an athlete to the credentials database
def addCredentials(athleteId, email, pwHash, salt):
    # print(f'addCredentials called with {athleteId}, {email}')
    try:
        collection_name = getCollection(CREDENTIALS_COLLECTION)
        newCreds = {
            "_id" : athleteId,
            "email" : email,
            "pwHash" : pwHash,
            "salt" : salt
            }
        result = collection_name.insert_one(newCreds)
        return result.inserted_id
    except Exception as e:
        print(str(e))
        return None


def getCredentials(email):
    # print(f'getCredentials called with {email}')
    try:
        collection_name = getCollection(CREDENTIALS_COLLECTION)
        result = collection_name.find_one({'email' : email})
        return result
    except Exception as e:
        print(str(e))
        return None



# ------------------------------------------------------------------- #
# Test code

if __name__ == "__main__":
    # athlete1 = {
    #     "_id" : 69,
    #     "first" : "Henry",
    #     "last" : "Vecchione",
    #     "permissions" : ["admin"],
    #     "prs" : {
    #         "2000m" : "6:24",
    #         "6000m" : "20:32"
    #     },
    #     "workouts" : [],
    #     "side" : ["port"],
    #     "class" : 2022,
    #     "active" : True,
    #     "awards" : {
    #         "earc" : [],
    #         "ira" : [],
    #         "shirts" : ['g','de','n','da','t','p']
    #     },
    #     "teamId" : 1
    # }
    # athlete2 = {
    #     "_id" : 1,
    #     "first" : "Cal",
    #     "last" : "Gorvy",
    #     "permissions" : [],
    #     "prs" : {
    #         "2000m" : "5:59",
    #         "6000m" : "17:24"
    #     },
    #     "workouts" : [],
    #     "side" : ["starboard"],
    #     "class" : 2025,
    #     "active" : True,
    #     "awards" : {
    #         "earc" : ['4V'],
    #         "ira" : ['1V'],
    #         "shirts" : ['g','de','n','h','y','t','p']
    #     },
    #     "teamId" : 1
    # }
    # athlete3 = {
    #     "_id" : 2,
    #     "first" : "Peter",
    #     "last" : "Skinner",
    #     "permissions" : [],
    #     "prs" : {
    #         "2000m" : "5:59",
    #         "6000m" : "17:24"
    #     },
    #     "workouts" : [],
    #     "side" : ["port"],
    #     "class" : 2023,
    #     "active" : True,
    #     "awards" : {
    #         "earc" : ['4V'],
    #         "ira" : ['1V'],
    #         "shirts" : ['g','de','n','h','y','t','p']
    #     },
    #     "teamId" : 1
    # }
    # athlete4 = {
    #     "_id" : 3,
    #     "first" : "Will",
    #     "last" : "Olson",
    #     "permissions" : [],
    #     "prs" : {
    #         "2000m" : "5:59",
    #         "6000m" : "17:24"
    #     },
    #     "workouts" : [],
    #     "side" : ["port"],
    #     "class" : 2023,
    #     "active" : True,
    #     "awards" : {
    #         "earc" : ['4V'],
    #         "ira" : ['1V'],
    #         "shirts" : ['g','de','n','h','y','t','p']
    #     },
    #     "teamId" : 1
    # }
    # workout1 = {
    #     '_id' : 1,
    #     'title' : '2x4000m, 3000m',
    #     'date' : datetime.datetime(2021, 11, 8),
    #     'pieces' : ['4000m', '4000m', '3000m'],
    #     'scores' : {
    #         '69' : ['15:12', '15:25' , '12:00'],
    #         '1' : ['13:14', '14:20', '13:15']
    #     },
    #     'notes' : 'open rate',
    #     'test' : False
    # }
    # workout2 = {
    #     '_id' : 2,
    #     'title' : '6x2000m',
    #     'date' : datetime.datetime(2021, 10, 31),
    #     'pieces' : ['2000m','2000m','2000m','2000m','2000m','2000m'],
    #     'scores' : {
    #         '69' : ['15:12', '15:25' , '12:00','15:12', '15:25' , '12:00'],
    #         '1' : ['13:14', '14:20', '13:15','13:14', '14:20', '13:15']
    #     },
    #     'notes' : 'wowwwee',
    #     'test' : False
    # }

    # pwPlain = b"sugmaLigma"
    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(pwPlain, salt)
    # addCredentials(69,"hjv@princeton.edu", hashed, salt)

    # pwPlain = b'admin'
    # salt = bcrypt.gensalt()
    # hashed = bcrypt.hashpw(pwPlain, salt)
    # addCredentials(420, 'a@x.com', hashed, salt)


    # creds = getCredentials('hjv@princeton.edu')
    # print(creds)
    # print(bcrypt.checkpw(b'sugmaLigma', creds['pwHash']))

    # for a in getAllAthletes(1, sort_by='class'):
    #     pprint(a)
    # for w in getAllWorkouts(1):
    #     pprint(w)

    # # for z in getScoreByAthlete(69,2):
    # #     pprint(z)

    # print(editAthlete(69, 'first', 'wiener'))

    # print(editWorkout(75, 'title', "10k, 10x(30' on, 1:30 off)"))
    print(getAllAthletes(1887))
    for athlete in getAllAthletes(1887):
        print(removeWorkoutFromAthlete(athlete['id'], 92))