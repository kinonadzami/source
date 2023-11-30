from item import Item, Map_obj_type, Item_type

class Map_obj(Item):

    def __init__(self, i_id: int, i_name: str):
        super().__init__(i_id, i_name)
        self.type = Item_type.Map_obj

class Resource_obj(Map_obj):

    def __init__(self, i_id: int, i_name: str, energy_cost:int, energy_return:int, resource:int, count:int, exp:int):
        super().__init__(i_id, i_name)
        self.type = Item_type.Map_obj
        self.obj_type = Map_obj_type.Resource
        self.energy_cost = energy_cost
        self.energy_return = energy_return
        self.resource = resource
        self.count = count
        self.exp = exp
        self.one_item_energy_cost = float(energy_cost)/float(count)
        self.one_item_energy_return = float(energy_return)/float(count)
        self.one_item_exp = float(exp)/float(count)
        self.resource.add_env_resource(self)