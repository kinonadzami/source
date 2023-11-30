import export_data

acceleration_range = []

class Acceleration_level:

    def __init__(self, from_sec, to_sec, price):
        self.from_sec = from_sec
        self.to_sec = to_sec
        self.price = price

    def __str__(self):
        return str(self.__dict__)

class Acceleration_range:

    def __init__(self):
        self.range = export_data.storage_extractor.extract_range('AccelerationSettings', 'A2:D', True)
        self.list_acc = []

        for index, acc in self.range.iterrows():
            self.list_acc.append(Acceleration_level(int(acc['FromInSeconds']), int(acc['ToInSeconds']), int(acc['Price'])))

    def __str__(self):
        s = ''
        for x in self.list_acc:
            s += str(x) + '\n'
        return s

acc = Acceleration_range()
    