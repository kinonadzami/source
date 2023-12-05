from countble_item import *
from resource_obj import *

class storage_data:

    def __init__(self, extractor = storage_extractor):
        self.extractor = extractor

        self.ci_df = storage_data.import_items_list_from_storage(self.extractor)
        self.rec_df = storage_data.import_recipes_list_from_storage(self.ci_df, self.extractor)
        self.resMap_df = storage_data.import_resMap_list_from_storage(self.ci_df, self.extractor)

    @staticmethod
    def import_items_list_from_storage(extractor = storage_extractor):
        df = pd.DataFrame()
        
        res = Storage_converter.resource_storage_import(extractor)
        mat = Storage_converter.materials_storage_import(extractor)
        crops = Storage_converter.crops_storage_import(extractor)
        products = Storage_converter.products_storage_import(extractor)

        for ind in res.index:
            t = Countble_item(int(res['Id'][ind]), res['EN'][ind], res['type'][ind])
            df = pd.concat([df, pd.DataFrame([t], index=[int(res['Id'][ind])], columns=['item'])])

        for ind in mat.index:
            t = Countble_item(int(mat['Id'][ind]), mat['EN'][ind], mat['type'][ind])
            df = pd.concat([df, pd.DataFrame([t], index=[int(mat['Id'][ind])], columns=['item'])])

        for ind in crops.index:
            t = Countble_item(int(crops['Id'][ind]), crops['EN'][ind], crops['type'][ind])
            df = pd.concat([df, pd.DataFrame([t], index=[int(crops['Id'][ind])], columns=['item'])])

        for ind in products.index:
            t = Countble_item(int(products['Id'][ind]), products['EN'][ind], products['type'][ind])
            df = pd.concat([df, pd.DataFrame([t], index=[int(products['Id'][ind])], columns=['item'])])

        return df
    
    @staticmethod
    def import_recipes_list_from_storage(ci_df, extractor = storage_extractor):
        df = pd.DataFrame()

        prod_recipes = Storage_converter.production_recipe_storage_import(extractor)

        for ind in prod_recipes.index:
            itemId = int(prod_recipes['ProductId'][ind])
            if itemId in ci_df.index: 
                reqs = []
                for x in prod_recipes['Ingredients'][ind].array:
                    reqId = int(x[0])
                    if reqId in ci_df.index: 
                        reqs.append(Requirement(ci_df['item'][reqId], int(x[1])))

                if len(reqs) > 0:
                    ci_df['item'][itemId].source = Countble_item_source.Production
                    t = Recipe(ci_df['item'][itemId], reqs, prod_recipes['ProductionTime'][ind], prod_recipes['ProductYield'][ind], int(prod_recipes['UnlockLevel'][ind]), Recipe_rarity(int(prod_recipes['ExpReward'][ind])))
                    df = pd.concat([df, pd.DataFrame([t], index=[itemId], columns=['recipe'])])

        return df
    
    @staticmethod
    def import_resMap_list_from_storage(ci_df, extractor = storage_extractor):
        df = pd.DataFrame()

        prod_sources = Storage_converter.resMap_storage_import(extractor)

        for ind in prod_sources.index:
            itemId = int(prod_sources['ItemId'][ind])
            if itemId in ci_df.index: 
                ci_df['item'][itemId].source = Countble_item_source.Enviroment
                t = Resource_obj(prod_sources['Id'][ind], prod_sources['EN'][ind], int(prod_sources['EnergyCost'][ind]), int(prod_sources['EnergyReward'][ind]), ci_df['item'][itemId], int(prod_sources['ItemYield'][ind]), int(prod_sources['ExpReward'][ind]))
                df = pd.concat([df, pd.DataFrame([t], index=[itemId], columns=['obj'])])

        return df
        
    
    
st = storage_data()
    

print(st.ci_df.head())
print(st.rec_df.head())
print(st.resMap_df.head())