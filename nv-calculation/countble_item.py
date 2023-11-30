from item import Item, Item_type, Countble_item_source
from map_obj import Resource_obj
import json

class Countble_item(Item):

    def __init__(self, i_id: int, i_name: str, i_source: Countble_item_source):
        super().__init__(i_id, i_name)
        self.type = Item_type.Countble
        self.source = i_source
        self.recipe = Recipe(None)
        self.production_sort = i_source.value*1000000 + i_id

    def add_recipe(self, recipe):
        self.recipe = recipe
        return self
    
    def add_env_resource(self, source:Resource_obj):
        if not hasattr(self, 'sources'): self.sources = []
        self.sources.append(source)
        self.min_gathering_energy_calculate()
        return

    def min_gathering_energy_calculate(self):
        self.sources.sort(key=lambda x: x.one_item_energy_cost)
        self.gathering_energy = self.sources[0].one_item_energy_cost
        self.return_energy = self.sources[0].one_item_energy_return
        return

    def calculate_item_data(self):
        return
    
    def calculate_item_total_time(self, level = 0):
        if self.recipe.source == Countble_item_source.Default: return

        if level == 0: level = self.recipe.lvl

        time = 0

        time += self.recipe.calculate_recipe_time(level)

        time += self.recipe.calculate_req_total_time(level)

        self.total_time = time
        return time
    
    def calculate_item_total_energy(self):
        if self.source == Countble_item_source.Enviroment: return self.gathering_energy

        return self.recipe.calculate_recipe_energy_cost()



    def reset_prod_order(self):
        self.production_sort = self.recipe.recipe_depth()*1000000 + self.i_id

class Requirement:

    def __init__(self, counble_item: Countble_item, count: int):
        self.counble_item = counble_item
        self.count = count

    def __str__(self):
        return str(self.__dict__)
    
class Recipe:

    def __init__(self, item: Countble_item, requirements = [], time = 0, r_yield = 1, req_lvl = 1):
        if item == None: 
            self.source = Countble_item_source.Default
            return
        self.time = time
        self.r_yeild = r_yield
        self.source = item.source
        self.lvl = req_lvl
        match self.source:
            case Countble_item_source.Production:
                if len(requirements) == 0: raise Exception("Requirements empty, expect list<Requirement> " + self.item.name)
                if not type(requirements[0]) is Requirement: raise Exception("Wrong requirements type, expect list<Requirement> " + self.item.name)

                self.recipe_req = requirements
                
                if self.prod_rec_validator(item.id): raise Exception("Circular dependency in recipe " + self.item.name)
            case Countble_item_source.Enviroment:
                self.environment_sources = requirements
                #yield and energy calc
            case Countble_item_source.Animals:
                self.animals = requirements
                #yield calc
            case Countble_item_source.Seedbeds:
                self.seedbeds = requirements
                #yield calc on level
            case Countble_item_source.Trees:
                self.trees = requirements
                #yield and calc
            case Countble_item_source.Generation:
                self.generating_obj = requirements
                #yield calc
        
        item.addRecipe(self)
        self.item = item

    def __str__(self):
        return str(self.__dict__)

    def prod_rec_validator(self, id_to_validate):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return False
        if self.source == Countble_item_source.Production:
            for req in self.recipe_req:
                if req.counble_item.id == id_to_validate: return True
                if req.counble_item.recipe.prod_rec_validator(id_to_validate): return True
            return False
        if self.source == Countble_item_source.Animals:
            for req in self.recipe_req:
                if req.animal.food.id == id_to_validate: return True
                if req.animal.food.recipe.prod_rec_validator(id_to_validate): return True
            return False
        return False
    
    def recipe_depth(self):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return 1
        max_depth = 0
        for req in self.recipe_req:
            depth = req.recipe.recipe_deep()
            if max_depth < depth: max_deep = depth
        return max_depth + 1
    
    def calculate_req_total_time(self, level):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return 0

        time = 0
        
        if self.source == Countble_item_source.Production:
            for req in self.recipe_req:
                time += req.counble_item.calculate_item_total_time(level) * req.count
            return time
        if self.source == Countble_item_source.Animals:
            for req in self.recipe_req:
                time += req.animal.food.calculate_item_total_time(level) * req.count
            return time

        return time
    
    def calculate_recipe_time(self, level):
        match self.source:
            case Countble_item_source.Default:
                return 0
            
            case Countble_item_source.Enviroment:
                return 0
            
            case Countble_item_source.Seedbeds:
                return int(float(self.time)/float(self.r_yeild*self.seedbeds[level]))
            
            case Countble_item_source.Trees:
                time = self.trees[level].tree.grow_time + (self.trees[level].tree.gather_time * self.trees[level].tree.gather_cycles)
                t_yield = self.trees[level].tree.r_yield * self.trees[level].tree.gather_cycles * self.trees[level].count
                return int(float(time)/float(t_yield))      
                 
            case Countble_item_source.Generation:
                avg_yield = 0
                for gen in self.generating_obj:
                    avg_yield += float(gen.r_yeild)/float(gen.time)
                return int(1/avg_yield)             
               
            case Countble_item_source.Animals:
                return int(float(self.time)/float(self.r_yeild*self.animals[level].count))
            
            case Countble_item_source.Production:
                return int(float(self.time)/float(self.r_yeild))
    
    def calculate_recipe_energy_cost(self):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return 0
        energy = 0

        if self.source == Countble_item_source.Production:
            for req in self.recipe_req:
                energy += req.counble_item.calculate_item_total_energy() * req.count
            return energy
        if self.source == Countble_item_source.Animals:
            for req in self.recipe_req:
                energy += req.animal.food.calculate_item_total_energy() * req.count
            return energy
        
        return energy



    
#
#test = Countble_item(1, "Test", Countble_item_source.Production)
#test2 = Countble_item(2, "Test2", Countble_item_source.Enviroment)
#req = [Requirement(test2, 2)]
#print(len(req))
#
#
#rec = Recipe(test, req, 1, 1)
#
#print(test)
#print(test.recipe)
#print(test.recipe.recipe_req[0])
#print(test.recipe.recipe_req[0].counble_item)
#print(test.recipe.recipe_req[0].counble_item.recipe)
#
#print("___________________________")
#
#test2.name = "Test3"
#
#print(test)
#print(test.recipe)
#print(test.recipe.recipe_req[0])
#print(test.recipe.recipe_req[0].counble_item)
#print(test.recipe.recipe_req[0].counble_item.recipe)
#            
        
            