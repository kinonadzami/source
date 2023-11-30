import gspread
from oauth2client.service_account import ServiceAccountCredentials

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('nv-calculation/analytics-376509-f0f9a5430e99.json', scope)

# authorize the clientsheet 
client = gspread.authorize(creds)