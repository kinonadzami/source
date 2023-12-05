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
    
    def remove_first_col(self):
        new_arr = []
        for x in self.array:
            new_arr.append(x[1:])

        self.array = new_arr
        return self
    
    @staticmethod
    def series_converter(ser:pd.Series):
        new = pd.Series()
        for index, x in ser.items():
            new = pd.concat([new, pd.Series(storage_array(x), index = [index])])
        
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
    def get_item_avg_yield(arr:storage_array, item_id, type_of_yield = 'prob'):
        try: 
            arr = np.array(arr.array).astype(int)
        except:
            return 0
        if arr.shape[1] == 0: return 0
        ret = 0
        for x in arr:
            if x[0] == item_id: 
                if len(x) < 3: ret = x[1]
                elif type_of_yield == "prob": ret += x[1]*(x[2]/100)
                elif type_of_yield == "range": ret += (x[1]+x[2])/2
        return ret
    
    @staticmethod
    def remove_extra_items(arr:storage_array, items_id:list):
        try: 
            temp = np.array(arr.array).astype(int)
        except:
            return 0
        if temp.shape[1] == 0: return 0
        ret = []
        for x in temp:
            if not x[0] in items_id: 
                ret.append(x)
        
        ret = np.array(ret).astype(str)
        arr.array = ret.tolist()
        return arr
    
    @staticmethod 
    def remove_pos_index(arr:list):
        for x in arr:
            del x[0]
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

        df['UnlockLevel'] = df['UnlockLevel'].apply(lambda x: '1' if x == '-' else x)

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
    
    @staticmethod
    def resMap_storage_import(extractor:Extractor, worksheet = 'ResourcesEnvironmentItems', range = 'A2:AH'):
        df = extractor.extract_range(worksheet, range, True)
        df = df[df['Id']!='']
        temp = df['EN']
        df = df.drop(['EN', 'EN'], axis=1)
        df['EN'] = temp.iloc[:, 0]
        df = df[['Id', 'EN', 'Requirements', 'Rewards']]

        df = df[df['Requirements']!='-']
        df = df[df['Rewards']!='-']

        df['Id'] = df['Id'].astype('int32')
        df['Requirements'] = storage_array.series_converter(df['Requirements'])
        df['EnergyCost'] = df['Requirements'].apply(lambda x:Storage_converter.get_item_avg_yield(x, energy_id))
        df['Rewards'] = storage_array.series_converter(df['Rewards'])
        df['Rewards'] = df['Rewards'].apply(lambda x: x.remove_first_col())
        df['EnergyReward'] = df['Rewards'].apply(lambda x:Storage_converter.get_item_avg_yield(x, energy_id, 'range'))
        df['ExpReward'] = df['Rewards'].apply(lambda x:Storage_converter.get_item_avg_yield(x, exp_id, 'range'))

        df['Rewards'] = df['Rewards'].apply(lambda x:Storage_converter.remove_extra_items(x, [exp_id, energy_id]))
        df['ItemId'] = df['Rewards'].apply(lambda x: x.array[0][0])
        df['ItemYield'] = df['Rewards'].apply(lambda x:Storage_converter.get_item_avg_yield(x, int(x.array[0][0]), 'range'))

        return df
    
    @staticmethod
    def animals_storage_import(extractor:Extractor, worksheet = 'Animals', range = 'A2:AZ'):
        df = extractor.extract_range(worksheet, range, True)
        df = df[df['Id']!='']
        temp = df['EN']
        df = df.drop(['EN', 'EN'], axis=1)
        df['EN'] = temp.iloc[:, 0]

        df = df[['Id', 'EN', 'LevelRestriction', 'ProductionTime', 'Requirements', 'Rewards']]

        df['Id'] = df['Id'].astype('int32')
        df = df[df['LevelRestriction']!='-']
        df = df[df['ProductionTime']!='-']
        df = df[df['Requirements']!='-']
        df = df[df['Rewards']!='-']

        df['ProductionTime'] = df['ProductionTime'].astype('int32')
        df['LevelRestriction'] = storage_array.series_converter(df['LevelRestriction'])
        df['Requirements'] = storage_array.series_converter(df['Requirements'])
        df['Rewards'] = storage_array.series_converter(df['Rewards'])

        df['Food'] = df['Requirements'].apply(lambda x: int(x.array[0][0]))
        df['FoodCount'] = df['Requirements'].apply(lambda x: int(x.array[0][1]))
        df['ProductId'] = df['Rewards'].apply(lambda x: int(x.array[0][0]))
        df['ProductYield'] = df['Rewards'].apply(lambda x:Storage_converter.get_item_avg_yield(x, int(x.array[0][0])))

        return df
    
    @staticmethod
    def seedbeds_storage_import(extractor:Extractor, worksheet = 'Seedbeds', range = 'A2:AZ'):
        df = extractor.extract_range(worksheet, range, True)
        df = df[df['Id']!='']
        temp = df['EN']
        df = df.drop(['EN', 'EN'], axis=1)
        df['EN'] = temp.iloc[:, 0]

        df = df[['Id', 'EN', 'LevelRestriction', 'RecipesIds']]

        df['Id'] = df['Id'].astype('int32')
        df = df[df['LevelRestriction']!='-']
        df = df[df['RecipesIds']!='-']

        df['LevelRestriction'] = storage_array.series_converter(df['LevelRestriction'])
        df['RecipesIds'] = storage_array.series_converter(df['RecipesIds'])

        return df
    
    @staticmethod
    def trees_storage_import(extractor:Extractor, worksheet = 'Trees', range = 'A2:AZ'):
        df = extractor.extract_range(worksheet, range, True)
        df = df[df['Id']!='']
        temp = df['EN']
        df = df.drop(['EN', 'EN'], axis=1)
        df['EN'] = temp.iloc[:, 0]

        df = df[['Id', 'EN', 'LevelRestriction', 'GrowStagesCount', 'GrowStagesTimings', 'HarvestResult', 'GrowCyclesCount']]

        df['Id'] = df['Id'].astype('int32')
        df = df[df['LevelRestriction']!='-']
        df = df[df['GrowStagesCount']!='-']
        df = df[df['GrowStagesTimings']!='-']
        df = df[df['HarvestResult']!='-']
        df = df[df['GrowCyclesCount']!='-']

        df['LevelRestriction'] = storage_array.series_converter(df['LevelRestriction'])
        df['GrowStagesTimings'] = storage_array.series_converter(df['GrowStagesTimings'])
        df['HarvestResult'] = storage_array.series_converter(df['HarvestResult'])

        df['ProductId'] = df['HarvestResult'].apply(lambda x: int(x.array[0][0]))
        df['ProductYield'] = df['HarvestResult'].apply(lambda x:Storage_converter.get_item_avg_yield(x, int(x.array[0][0])))

        return df
