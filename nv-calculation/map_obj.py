from item import Item

class Map_obj(Item):

    def __init__(self, i_id: int, i_name: str):
        super().__init__(i_id, i_name)
        self.type = Item_type.Map_obj

