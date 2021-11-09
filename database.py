from pymongo import MongoClient
import pymongo
import secret
import datetime
from pprint import pprint

CONNECTION_STRING = secret.database_url
DBNAME = 'irgo'
ATHLETE_COLLECTION = 'athletes'
WORKOUT_COLLECTION = 'workouts'

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
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.insert_one(athleteDict)
        return result.inserted_id
    except Exception as e:
        print(str(e))
        return None

def editAthlete(athleteId, field, newVal):
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        result = collection_name.update_one({'_id' : athleteId}, {'$set' : {field : newVal}})
        return result.modified_count
    except Exception as e:
        print(str(e))
        return None

def queryAthlete(athleteId):
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        return collection_name.find_one({'_id' : athleteId})
    except Exception as e:
        print(str(e))
        return None

def getAllAthletes(sort_by='name'):
    try:
        collection_name = getCollection(ATHLETE_COLLECTION)
        return collection_name.find({}, sort=[(sort_by, pymongo.ASCENDING)])
    except Exception as e:
        print(str(e))
        return None

# ------------------------------------------------------------------- #
# general workout collection methods 

def addWorkout(workoutDict):
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        result = collection_name.insert_one(workoutDict)
        return result.inserted_id
    except Exception as e:
        print(str(e))
        return None

def editWorkout(workoutId, field, newVal):
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        result = collection_name.update_one({'_id' : workoutId}, {'$set' : {field : newVal}})
        return result.modified_count
    except Exception as e:
        print(str(e))
        return None

def queryWorkout(workoutId):
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        return collection_name.find_one({'_id' : workoutId})
    except Exception as e:
        print(str(e))
        return None

def getAllWorkouts(sort_by='date'):
    try:
        collection_name = getCollection(WORKOUT_COLLECTION)
        return collection_name.find({}, sort=[(sort_by, pymongo.DESCENDING)])
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
# Test code

if __name__ == "__main__":
    athlete1 = {
        "_id" : 69,
        "name" : "Henry Vecchione",
        "permissions" : ["admin"],
        "prs" : {
            "2000m" : "6:24",
            "6000m" : "20:32"
        },
        "workouts" : [],
        "side" : ["port"],
        "class" : 2022,
        "active" : True,
        "awards" : {
            "earc" : [],
            "ira" : [],
            "shirts" : ['g','de','n','da','t','p']
        }
    }
    athlete2 = {
        "_id" : 1,
        "name" : "Cal Gorvy",
        "permissions" : [],
        "prs" : {
            "2000m" : "5:59",
            "6000m" : "17:24"
        },
        "workouts" : [],
        "side" : ["starboard"],
        "class" : 2025,
        "active" : True,
        "awards" : {
            "earc" : ['4V'],
            "ira" : ['1V'],
            "shirts" : ['g','de','n','h','y','t','p']
        }
    }
    workout1 = {
        '_id' : 1,
        'title' : '2x4000m, 3000m',
        'date' : datetime.datetime(2021, 11, 8),
        'pieces' : ['4000m', '4000m', '3000m'],
        'scores' : {
            '69' : ['15:12', '15:25' , '12:00'],
            '1' : ['13:14', '14:20', '13:15']
        },
        'notes' : 'open rate',
        'test' : False
    }
    workout2 = {
        '_id' : 2,
        'title' : '6x2000m',
        'date' : datetime.datetime(2021, 10, 31),
        'pieces' : ['2000m','2000m','2000m','2000m','2000m','2000m'],
        'scores' : {
            '69' : ['15:12', '15:25' , '12:00','15:12', '15:25' , '12:00'],
            '1' : ['13:14', '14:20', '13:15','13:14', '14:20', '13:15']
        },
        'notes' : 'wowwwee',
        'test' : False
    }

    for a in getAllAthletes(sort_by='class'):
        pprint(a)
    for w in getAllWorkouts():
        pprint(w)

    for z in getScoreByAthlete(69,2):
        pprint(z)