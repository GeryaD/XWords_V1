from src.Dictionary import Dictionary, FieldType

_dict = Dictionary("dict_ru_v3.json")
dictionary = _dict.words

class Letter:
    macke_word: bool = False
    def __init__(self, name: str, x: int, y: int, macke_word: bool = False) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.macke_word: bool = macke_word

    def clear(self):
        self.name = ' '
        self.macke_word = False

    def set(self, name: str, x: int, y: int, macke_word: bool = False) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.macke_word: bool = macke_word

    def get(self):
        return {'name': self.name, 'x':self.x, 'y':self.y, 'macke_word':self.macke_word}
    
    def __str__(self) -> str:
        return f"'name': {self.name}, 'x':{self.x}, 'y':{self.y}, 'macke_word':{self.macke_word}"
    

curent_field = [[Letter(' ', j, i)for j in range(9)]for i in range(9)]
        

for row in curent_field:
    for element in row:
        print(f"{element}", end=" ")
    print()
