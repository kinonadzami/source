import export_data
from enums import *

acceleration_range = []

class Acceleration_level:

    def __init__(self, from_sec, to_sec, price):
        self.from_sec = from_sec
        self.to_sec = to_sec
        self.price = price

    def __str__(self):
        return str(self.__dict__)

class Acceleration_range:

    def __init__(self, sheet = export_data.Sheet_type.Storage, worksheet = 'AccelerationSettings', range = 'A2:D'):
        extractor = None
        match sheet:
            case export_data.Sheet_type.Storage: extractor = export_data.storage_extractor
            case export_data.Sheet_type.Calculation: extractor = export_data.calc_extractor
        self.range = export_data.storage_extractor.extract_range(worksheet, range, True)
        self.list_acc = []

        for index, acc in self.range.iterrows():
            self.list_acc.append(Acceleration_level(int(acc['FromInSeconds']), int(acc['ToInSeconds']), int(acc['Price'])))

    def __str__(self):
        s = ''
        for x in self.list_acc:
            s += str(x) + '\n'
        return s
    
    def time_to_cost(self, time:int):
        for x in self.list_acc:
            if time > x.from_sec and (time <= x.to_sec or x.to_sec == 0): return x.price
        return 0

acc = Acceleration_range()
    