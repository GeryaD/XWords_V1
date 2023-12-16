from fastapi import WebSocket

class Player():
    connection: WebSocket
    player_id: str
    name: str = ''
    score: int
    letters_on_hand: list[str] = []
    letters_limit: int
    disconnected: bool = False

    def __init__(self, name:str, connection: WebSocket, letters_limit: int) -> None:
        self.name = name
        self.connection = connection
        self.letters_limit = letters_limit

    def add_score(self, score:int):
        if score>0:
            self.score += score
        else: Exception('Начисляемые очки меньше нуля')

    def chenge_letter(self, old_latter: str, new_latter:str):
        if old_latter in self.letters_on_hand:
            self.letters_on_hand.remove(old_latter)
            self.letters_on_hand.append(new_latter)
        else: raise Exception('Буква, которую выхотите поменять не существует у игрока на руках!')

    def set_letters_on_hand(self, letters:list[str]):
        self.letters_on_hand = letters
