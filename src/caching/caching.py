import os
from pathlib import Path
import os.path, json
class APICaching:

    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    BASE_DIR = Path(__file__).resolve().parent

    def __init__(self):
        
        if not os.path.exists(os.path.join(self.ROOT_DIR,'__cache__')):
            os.mkdir(os.path.join(self.ROOT_DIR,'__cache__'))

    def add(self, key, data):
        new_file = open(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'), 'wb')   
        new_file.write(data) 

    def set():
        pass

    def get(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache')):
            file = open(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'), "rb")
            data = file.read()
            file.close()
            return data
    

    def delete(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache')):
            os.remove(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'))
            return True
        return False

    def expire(self, key, time_hour):
        if not os.path.exists(os.path.join(self.BASE_DIR,'expireTable.json')):
            json_decoded = {}
        else:
            with open(os.path.join(self.BASE_DIR,'expireTable.json')) as json_file:
                json_decoded = json.load(json_file)

        json_decoded[key] = time_hour

        with open(os.path.join(self.BASE_DIR,'expireTable.json'), 'w') as json_file:
            json.dump(json_decoded, json_file)
    
