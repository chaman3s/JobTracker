import datetime
import os
import json
class handleFile:
    def __init__(self):
        self.pastfile = os.path.join(os.getcwd(), "pastfile.json")
    def load_json(self):
        print("ok22")
        """Load past applications from pastfile.json or return an empty dictionary."""
        if not os.path.exists(self.pastfile):
            return {}
        print("ok23")
        with open(self.pastfile, "r") as file:
            return json.load(file)
    def save_json(self, dt,company=None):
        if company is None:  
            keys = dt.keys()
            company=list(keys)[0]
            data= self.load_json()
            data[company] = dt[company]
        with open(self.pastfile, "w") as file:
            json.dump(data, file, indent=4)
            print("Success fully upated")
        
        