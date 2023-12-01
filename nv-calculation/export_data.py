from connection import client, gspread
import pandas as pd
from enums import *
from enum import Enum


calc_sheet_name = 'Copy of NV - Calculation'
storage_sheet_name = 'Copy of Nile Valley - Game Config [Development]-Main'

class Extractor:

    def __init__(self, sheet:str):
        self.sheet = client.open(sheet)

    def extract_range(self, worksheet:str, range:str, with_header = False):
        worksheet = self.sheet.worksheet(worksheet)
        range = worksheet.get(range)
        df = pd.DataFrame.from_dict(range)
        if with_header:
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header
        return df

calc_extractor = Extractor(calc_sheet_name)
storage_extractor = Extractor(storage_sheet_name)
