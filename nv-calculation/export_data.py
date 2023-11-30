from connection import client, gspread
import pandas as pd

sheet = client.open('Copy of NV - Calculation')

sheet_instance = sheet.worksheet('Dictionary')

records_data = sheet_instance.get_all_records()
records_df = pd.DataFrame.from_dict(records_data)

print(records_df.head())
