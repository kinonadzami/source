from item import Item
from enums import *
import global_p
from resource_obj import *
import json
from export_data import *
from storage_serilizer import *

class Countble_item(Item):

    def __init__(self, i_id: int, i_name: str, i_source: Countble_item_source):
        super().__init__(i_id, i_name)
        self.type = Item_type.Countble
        self.source = i_source
        self.recipe = Recipe(None)
        self.production_sort = i_source.value*1000000 + i_id

    def add_recipe(self, recipe):
        self.recipe = recipe
        if recipe.source == Countble_item_source.Animals:
            self.source = Countble_item_source.Animals
        elif recipe.source == Countble_item_source.Generation:
            self.source = Countble_item_source.Generation
        elif recipe.source == Countble_item_source.Trees:
            self.source = Countble_item_source.Trees
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
        self.gathering_exp = self.sources[0].one_item_exp
        return

    def calculate_item_data(self):
        if self.recipe.source == Countble_item_source.Default: return
        self.calculate_item_total_time(self.recipe.lvl)
        self.calculate_item_total_energy()
        self.calculate_item_total_energy_return()
        self.calculate_item_total_exp()

        if (self.total_time/60 + self.total_energy_cost*0.5)/6 <= 1:
            self.cost_hard = 1
        else:
            self.cost_hard = (self.total_time/60 + self.total_energy_cost*0.5)/6
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
        if self.recipe.source == Countble_item_source.Default: return
        if self.source == Countble_item_source.Enviroment: 
            self.total_energy_cost = self.gathering_energy
            return self.gathering_energy

        self.total_energy_cost = self.recipe.calculate_recipe_energy_cost()
        return self.total_energy_cost
    
    def calculate_item_total_energy_return(self):
        if self.recipe.source == Countble_item_source.Default: return
        if self.source == Countble_item_source.Enviroment: 
            self.total_energy_return = self.return_energy
            return self.return_energy

        self.total_energy_return = self.recipe.calculate_recipe_energy_return()
        return self.total_energy_return
    
    def calculate_item_total_exp(self):
        if self.recipe.source == Countble_item_source.Default: return
        if self.source == Countble_item_source.Enviroment: 
            self.total_exp = self.gathering_exp
            return self.gathering_exp
        
        self.total_exp = self.recipe.calculate_recipe_exp()
        return self.total_exp

    def reset_prod_order(self):
        if self.recipe.source == Countble_item_source.Default: return
        self.production_sort = self.recipe.recipe_depth()*1000000 + self.i_id


class Requirement:

    def __init__(self, counble_item: Countble_item, count: int):
        self.counble_item = counble_item
        self.count = count

    def __str__(self):
        return str(self.__dict__)
    
class Recipe:

    def __init__(self, item:Countble_item, requirements = [], time = 0, r_yield = 1, req_lvl = 1, rarity = Recipe_rarity.Common):
        if item == None: 
            self.source = Countble_item_source.Default
            return
        self.time = time
        self.acceleration_cost = global_p.acc.time_to_cost(self.time)
        self.r_yeild = r_yield
        self.source = item.source
        self.lvl = req_lvl
        self.rarity = rarity
        match self.source:
            case Countble_item_source.Production:
                if len(requirements) == 0: raise Exception("Requirements empty, expect list<Requirement> " + self.item.name)
                if not type(requirements[0]) is Requirement: raise Exception("Wrong requirements type, expect list<Requirement> " + self.item.name)

                self.recipe_req = requirements
                
                if self.prod_rec_validator(item.id): raise Exception("Circular dependency in recipe " + self.item.name)
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
        
        item.add_recipe(self)
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
                return int(float(self.time)/float(self.r_yeild*self.seedbeds[level-1]))
            
            case Countble_item_source.Trees:
                time = self.trees[level-1].tree.grow_time + (self.trees[level-1].tree.gather_time * self.trees[level-1].tree.gather_cycles)
                t_yield = self.trees[level-1].tree.r_yield * self.trees[level-1].tree.gather_cycles * self.trees[level-1].count
                return int(float(time)/float(t_yield))      
                 
            case Countble_item_source.Generation:
                avg_yield = 0
                for gen in self.generating_obj:
                    avg_yield += float(gen.r_yeild)/float(gen.time)
                return int(1/avg_yield)             
               
            case Countble_item_source.Animals:
                return int(float(self.time)/float(self.r_yeild*self.animals[level-1].count))
            
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
    
    def calculate_recipe_energy_return(self):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return 0
        energy = 0

        if self.source == Countble_item_source.Production:
            for req in self.recipe_req:
                energy += req.counble_item.calculate_item_total_energy_return() * req.count
            return energy
        if self.source == Countble_item_source.Animals:
            for req in self.recipe_req:
                energy += req.animal.food.calculate_item_total_energy_return() * req.count
            return energy
        
        return energy
    
    def calculate_recipe_exp(self):
        if not self.source in [Countble_item_source.Production, Countble_item_source.Animals]: return 0
        energy = 0

        if self.source == Countble_item_source.Production:
            for req in self.recipe_req:
                energy += req.counble_item.calculate_item_total_exp() * req.count
            return energy
        if self.source == Countble_item_source.Animals:
            for req in self.recipe_req:
                energy += req.animal.food.calculate_item_total_exp() * req.count
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
        
            