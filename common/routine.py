import pymongo
import json, os, sys
import logging, json

fileFolderPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(fileFolderPath))
os.chdir(fileFolderPath)


def open_db_connection(environment, db_name=None):
    try:

        db_config_file = open("../config/db_config.json")
        db_config_dict = json.load(db_config_file)
        available_environments = db_config_dict.keys()
        # setting up the MongoClient based on the environment
        if environment in available_environments:
            ATLAS_CONNECTION_STRING = (
                "mongodb+srv://"
                + db_config_dict[environment]["MONGO_USER"]
                + ":"
                + db_config_dict[environment]["MONGO_PASS"]
                + "@"
                + db_config_dict[environment]["HOSTNAME"]
                + "/"
                + db_config_dict[environment]["MONGO_DB"]
                + "?retryWrites=true&w=majority"
            )
            mongo_client = pymongo.MongoClient(ATLAS_CONNECTION_STRING)
        opened_db = mongo_client[db_config_dict[environment]["MONGO_DB"]]
        opened_client = mongo_client
        # print("Connected to database")
        return opened_db, opened_client
    except Exception as e:
        raise Exception(
            "Could not connect to database"
        )  # adding logging module to log to a file
        return null


def get_api_key_data(keyProvider, targetdb):

    result = targetdb["apiKeyStore"].find_one(
        {"keyProvider": keyProvider, "active": True}
    )

    if result != None or result != 0:
        return result
    else:
        return ""
