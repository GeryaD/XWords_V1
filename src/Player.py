from fastapi import WebSocket

class Player():
    connection: WebSocket
    player_id: str
    name: str = ''
    score: int
    letters_on_hand: list[str]
    letters_limit: int

    def __init__(self, name:str, connection: WebSocket, letters_limit: int) -> None:
        self.name = name.upper()
        self.connection = connection
        self.letters_limit = letters_limit

    async def add_score(self, score:int):
        if score>0:
            self.score += score
        else: Exception('Начисляемые очки меньше нуля')

    async def add_letters(self, letters: list[str]):
        if len(self.letters_on_hand + letters) <= self.letters_limit:
            self.letters_on_hand += letters
            self.connection.send_json({'action':'add_letters', 'message': f'The letters were issued: {letters}', 'letters':letters})
        else: raise Exception("Сумма добавляемых букв превышает лимит!")

    async def chenge_letter(self, old_latter: str, new_latter:str):
        if old_latter in self.letters_on_hand:
            self.letters_on_hand.remove(old_latter)
            self.letters_on_hand.append(new_latter)
        else: raise Exception('Буква, которую выхотите поменять не существует у игрока на руках!')

    async def set_connection(self, connection):
        self.connection = connection

    async def ws_get_letter(self,):
        self.connection.send_json({'action':'get_letters', 'letters':self.letters_on_hand})