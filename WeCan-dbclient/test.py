import routine
import pandas as pd

def check_results(file_1, file_2):
    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)

    if df1.__array__ == df2.__array__:
        print("Check: OK")
    else:
        print("Check: Fault")

def test_users_update():

    print("Test users")

    try:
        print("Unit test 1")
        routine.users_update("users_test_1.csv", "journal_test1")
        print("OK")
        check_results("users_test_1.csv", ".\\results\\users_test_1.csv")

        print("Unit test 2")
        routine.users_update("users_test_2.csv", "journal_test2")
        print("OK")
        check_results("users_test_2.csv", ".\\results\\users_test_2.csv")

        print("Unit test 3")
        routine.users_update("users_test_3.csv", "journal_test3")
        print("OK")
        check_results("users_test_3.csv", ".\\results\\users_test_3.csv")

        print("Unit test 4")
        routine.users_update("users_test_4.csv", "journal_test4")
        print("OK")
        check_results("users_test_4.csv", ".\\results\\users_test_4.csv")

        print("Load test 1")
        routine.users_update("users_test_5.csv", "journal_test5")
        print("OK")

        print("Load test 2")
        routine.users_update("users_test_6.csv", "journal_test6")
        print("OK")
    
    except enumerate:
        print(enumerate.__str__)

def load_test_update():

    print("Test sessions")

    try:
        print("Load test 1")
        routine.users_update("sessions_load_test1.csv", "journal_test5")
        routine.sessions_update("sessions_load_test1.csv", "journal_test5")
        print("OK")

        print("Load test 2")
        routine.users_update("sessions_load_test1.csv", "journal_test6")
        routine.sessions_update("sessions_load_test1.csv", "journal_test6")
        print("OK")
        
        print("Load test 3")
        routine.users_update("sessions_load_test1.csv", "journal_test7")
        routine.sessions_update("sessions_load_test1.csv", "journal_test7")
        print("OK")
    
    except enumerate:
        print(enumerate.__str__)




        