import mongo_client
import pandas as pd
import datetime

mongo_client.startup_db_client()

#users upd
try:
    users = pd.read_csv("users.csv").set_index("user_id")
    max_date = users.max()["first_datetime"]

except FileNotFoundError: 
    users = pd.DataFrame()
    max_date = datetime.datetime(1970,1,1,0,0,0,0)

pipeline_users = [
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

cc = mongo_client.app.database["journal"].aggregate(pipeline_users)

users_new = pd.DataFrame(list(cc))
if not users_new.empty:
    users_new = users_new.rename(columns={"_id":"user_id"}).set_index("user_id")

    if users.empty:
        users = users_new.copy()
    else:
        users_temp = pd.merge(users_new, users, how = 'left', indicator=True, left_index=True, right_index=True).query('_merge=="left_only"').drop(['_merge', 'first_datetime_y'], axis=1).rename(columns={"first_datetime_x":"first_datetime"})
        users = pd.concat([users, users_temp])

    users.to_csv("users.csv")

#sessions upd
try:
    sessions = pd.read_csv("sessions.csv").set_index("_id")
    max_date = sessions.max()["date"]
    max_date = max_date - datetime.timedelta(days=2)

except FileNotFoundError: 
    sessions = pd.DataFrame()
    max_date = datetime.datetime(1970,1,1,0,0,0,0)

pipeline_sessions = [
    {
        '$match': {
            'date': {
                '$gt': max_date
            }
        }
    }, {
        '$unset': [
            'op_name', 'op_params', 'error', 'ip', 'ip_cc', 'cli_version', 'inst_id', 'task'
        ]
    }, {
        '$setWindowFields': {
            'partitionBy': '$user_id', 
            'sortBy': {
                'date': 1
            }, 
            'output': {
                'previous_datetime': {
                    '$shift': {
                        'output': '$date', 
                        'by': -1, 
                        'default': datetime.datetime(1970,1,1,0,0,0,0)
                    }
                }, 
                'next_datetime': {
                    '$shift': {
                        'output': '$date', 
                        'by': 1, 
                        'default': -1
                    }
                }
            }
        }
    }, {
        '$addFields': {
            'new_session': {
                '$cond': {
                    'if': {
                        '$or': [
                            {
                                '$gt': [
                                    {
                                        '$divide': [
                                            {
                                                '$subtract': [
                                                    '$date', '$previous_datetime'
                                                ]
                                            }, 60000
                                        ]
                                    }, 10
                                ]
                            }, {
                                '$eq': [
                                    '$next_datetime', -1
                                ]
                            }
                        ]
                    }, 
                    'then': 1, 
                    'else': 0
                }
            }
        }
    }, {
        '$match': {
            'new_session': 1
        }
    }, {
        '$setWindowFields': {
            'partitionBy': '$user_id', 
            'sortBy': {
                'date': 1
            }, 
            'output': {
                'session_end_datetime': {
                    '$shift': {
                        'output': '$previous_datetime', 
                        'by': 1, 
                        'default': -1
                    }
                }
            }
        }
    }, {
        '$match': {
            'session_end_datetime': {
                '$ne': -1
            }
        }
    }, {
        '$unset': [
            'next_datetime', 'new_session'
        ]
    }
]

cc = mongo_client.app.database["journal"].aggregate(pipeline_sessions)

sessions_new = pd.DataFrame(list(cc))
if not sessions_new.empty:
    sessions_new = sessions_new.set_index("_id")


    if sessions.empty:
        sessions = sessions_new.copy()
    else:
        sessions = sessions.drop(columns='session_num')

        sessions_temp = pd.merge(sessions_new, sessions, how = 'inner', indicator=True, left_index=True, right_index=True)

        sessions = sessions.drop(index=sessions_temp.index)

        sessions = pd.concat([sessions, sessions_new])


    tt = sessions.groupby('user_id').expanding().count().reset_index().set_index('_id')
    
    sessions['session_num'] = tt['date']
    
    sessions = sessions.drop(sessions[(sessions.session_num > 1) & (sessions.previous_datetime == datetime.datetime(1970,1,1,0,0,0,0))].index)
    
    sessions.to_csv("sessions.csv")





mongo_client.shutdown_db_client()