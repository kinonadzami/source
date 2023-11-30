import pandas as pd
import json
from enum import Enum

class Item_type(Enum):
    Countble = 1
    Map_obj = 2

    def __str__(self):
        return str(self.name)

class Countble_item_source(Enum):
    Default = 0
    Enviroment = 1
    Seedbeds = 2
    Trees = 3
    Generation = 4
    Animals = 5
    Production = 6

    def __str__(self):
        return str(self.name)

class Map_obj_type(Enum):
    Resource = 1
    Building = 2
    Decoration = 3
    Generator = 4
    Animal = 5
    Seedbed = 6
    Tree = 7

    def __str__(self):
        return str(self.name)


class Item:

    def __init__(self, i_id: int, i_name: str):
        self.id = i_id
        self.name = i_name

    def __str__(self):
        return str(self.__dict__)


            
