import numpy as np

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
    
        