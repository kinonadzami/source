import numpy as np
import pandas as pd
from export_data import Extractor, storage_extractor
from global_p import exp_id, energy_id
from enums import Countble_item_source

class storage_array:

    def __init__(self, string):
        self.array = Storage_converter.array_from_storage_format(string)

    def __str__(self):
        return Storage_converter.storage_format_from_array(self.array)
    
    @staticmethod
    def series_converter(ser:pd.Series):
        new = pd.Series()
        for index, x in ser.items():
            new = pd.concat([new, pd.Series(storage_array(x), index = [index])])
        
        print(new)
        return new

class Storage_converter:

    @staticmethod
    def array_from_storage_format(array_string:str):
        array_string = array_string.strip()
        list_of_rows = array_string.split('\n')
        arr = []
        for row in list_of_rows:
            arr.append(row.split(','))
        return arr
    
    @staticmethod
    def storage_format_from_array(array:list([list])):
        list_of_rows = []
        for row in array:
            list_of_rows.append(','.join(row))
        array_string = '\n'.join(list_of_rows)
        return array_string
    
    @staticmethod
    def get_item_avg_yield(arr:storage_array, item_id):
        arr = np.array(arr.array).astype(int)
        ret = 0
        for x in arr:
            if x[0] == item_id: 
                if len(x) < 3: ret = x[1]
                else: ret += x[1]*(x[2]/100)
        return ret
    
    @staticmethod
    def remove_extra_items(arr:storage_array, items_id:list):
        temp = np.array(arr.array).astype(int)
        ret = []
        for x in temp:
            if not x[0] in items_id: 
                ret.append(x)
        
        ret = np.array(ret).astype(str)
        arr.array = ret.tolist()
        return arr
    
    @staticmethod
    def production_recipe_storage_import(extractor:Extractor, worksheet = 'ProductionReceipts', range = 'J2:N'):
        df = extractor.extract_range(worksheet, range, True)
        df['ProductionResult'] = storage_array.series_converter(df['ProductionResult'])
        df['ProductionTime'] = df['ProductionTime'].astype('int32')
        df['Ingredients'] = storage_array.series_converter(df['Ingredients'])
        
        df['ExpReward'] = df['ProductionResult'].apply(lambda x:Storage_converter.get_item_avg_yield(x, exp_id))

        df['ProductionResult'] = df['ProductionResult'].apply(lambda x:Storage_converter.remove_extra_items(x, [exp_id, energy_id]))
        df['ProductId'] = df['ProductionResult'].apply(lambda x: x.array[0][0])
        df['ProductYield'] = df['ProductionResult'].apply(lambda x: Storage_converter.get_item_avg_yield(x, int(x.array[0][0])))

        return df
    
    @staticmethod
    def resource_storage_import(extractor:Extractor, worksheet = 'ResourcesItems', range = 'A2:B'):
        df = extractor.extract_range(worksheet, range, True)
        df['Id'] = df['Id'].astype('int32')
        df['type'] = Countble_item_source.Enviroment

        return df
    
    @staticmethod
    def materials_storage_import(extractor:Extractor, worksheet = 'MaterialsItems', range = 'A2:B'):
        df = extractor.extract_range(worksheet, range, True)
        df['Id'] = df['Id'].astype('int32')
        df['type'] = Countble_item_source.Production

        return df
    
    @staticmethod
    def crops_storage_import(extractor:Extractor, worksheet = 'CropsItems', range = 'A2:B'):
        df = extractor.extract_range(worksheet, range, True)
        df['Id'] = df['Id'].astype('int32')
        df['type'] = Countble_item_source.Seedbeds

        return df
    
    @staticmethod
    def products_storage_import(extractor:Extractor, worksheet = 'ProductsItems', range = 'A2:B'):
        df = extractor.extract_range(worksheet, range, True)
        df['Id'] = df['Id'].astype('int32')
        df['type'] = Countble_item_source.Production

        return df

df = Storage_converter.products_storage_import(storage_extractor)

print(df.head())