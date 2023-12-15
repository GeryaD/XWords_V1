from typing import Dict
import json

from enum import Enum


class FieldType(Enum):
    LOW = "low"
    MEDIUM = "medium"
    LARGE = "large"

class FieldSetting:
    def __init__(self):
        self.letterScore = {}
        self.letterCount = {}
class Dictionary:
    def __init__(self, pathFileJson: str):
        with open(pathFileJson, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.fieldTypes = {}
        self.words = data["words"]
        for fieldType in FieldType:
            if fieldType.value in data:
                fieldSettings = FieldSetting()
                for key, value in data[fieldType.value].items():
                    fieldSettings.letterCount[key] = value[0]
                    fieldSettings.letterScore[key] = value[1]
                self.fieldTypes[fieldType] = fieldSettings
    def checkWord(self, word: str):
        if word in self.words:
            return True
        else:
            return False
    def getBag(self,fieltType : FieldType):
        return (self.fieldTypes[fieltType].letterCount.copy(), self.fieldTypes[fieltType].letterScore.copy(), )


# dict = Dictionary("dict_ru_v3.json")
# print(dict.getBag(FieldType.MEDIUM))