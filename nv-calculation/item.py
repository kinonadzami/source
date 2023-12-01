from enums import *

class Item:

    def __init__(self, i_id: int, i_name: str):
        self.id = i_id
        self.name = i_name

    def __str__(self):
        return str(self.__dict__)


            
