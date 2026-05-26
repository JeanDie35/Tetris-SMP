import json
import os

class Config:

    def __init__(self):
        self.file_name = "../config.json"
        self.data = self.get_data()

    def save_file(self):
        with open(self.file_name, "w") as file:
            file.write(json.dumps(self.data, indent=4))
            file.close()

    def get_data(self):
        with open(self.file_name) as file:
            return json.load(file)
