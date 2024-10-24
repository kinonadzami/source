import mongo_client
import pandas as pd
import datetime

mongo_client.startup_db_client()

#users upd
try:
    users = pd.read_csv("users.csv").set_index("user_id")
    print(users)
    max_date = users.max()["first_datetime"]

except FileNotFoundError: 
    users = pd.DataFrame()
    max_date = datetime.datetime(1970,1,1,0,0,0,0)

pipeline = [
    {
        '$match': {
            'date': {
                '$gt': max_date
            }
        }
    }, {
        '$unset': [
            '_id', 'op_params', 'error', 'ip', 'cli_version', 'inst_id'
        ]
    }, {
        '$group': {
            '_id': '$user_id', 
            'first_datetime': {
                '$max': '$date'
            }
        }
    }
]

cc = mongo_client.app.database["journal"].aggregate(pipeline)

users_new = pd.DataFrame(list(cc))
users_new = users_new.rename(columns={"_id":"user_id"}).set_index("user_id")

if users.empty:
    users = users_new.copy()
else:
    users_temp = pd.merge(users_new, users, how = 'left', indicator=True, left_index=True, right_index=True).query('_merge=="left_only"').drop(['_merge', 'first_datetime_y'], axis=1).rename(columns={"first_datetime_x":"first_datetime"})
    users = pd.concat([users, users_temp])

users.to_csv("users.csv")

mongo_client.shutdown_db_client()
