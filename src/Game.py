from Player import Player
from enum import Enum
from fastapi.websockets import WebSocket
from Dictionary import FieldType, Dictionary
import asyncio
from typing import List, Dict
import random

class dataCell():
    letter:str
    modification: str

class dataLetter():
    name:str
    x:int
    y:int

class dataField_type(Enum):
    SMALL:int = 9
    MEDIUM:int = 15
    LARGE:int = 21

class Game():
    dead = False
    room_number: str
    num_of_players: int
    field_type: FieldType
    dict_type:  int
    players: list[Player] = []
    curent_player: Player
    multiplier_field: list[str] = [['r', '', '', '', 'b', '', '', '', 'r',],
                                   ['', 'o', '', '', '', '', '', 'o', '',],
                                   ['', '', 'g', '', '', '', 'g', '', '',],
                                   ['', '', '', 'g', '', 'g', '', '', '',],
                                   ['b', '', '', '', '', '', '', '', 'b',],
                                   ['', '', '', 'g', '', 'g', '', '', '',],
                                   ['', '', 'g', '', '', '', 'g', '', '',],
                                   ['', 'o', '', '', '', '', '', 'o', '',],
                                   ['r', '', '', '', 'b', '', '', '', 'r',],]
    old_field: list[dataCell] = [['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],]
    new_field: list[dataCell] = [['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],
                                 ['','','','','','','','','',],]
    passes: int = 0
    passes_limit: int
    moves: int = 0
    rounds: int = 0
    letter_count: dict
    letter_score: dict

    def __init__(self, room_number: str, num_of_players: int, bag: tuple) -> None:
        self.letter_count = bag[0]
        self.letter_score = bag[1]
        self.num_of_players = num_of_players
        self.room_number = room_number
        self.passes_limit = num_of_players*2

    def get_letter(self, num: int):
        letters_list = random.choices(list(self.letter_count.keys()), k=num)
        for letter in letters_list:
            self.letter_count[letter] -= 1
        return letters_list

    async def say_all_Players(self, message:Dict):
        for player in self.players:
            await player.connection.send_json(message)

    async def add_Player(self, name: str, connection: WebSocket):
        self.players.append(Player(name=name, connection=connection, letters_limit=7))
        await self.say_all_Players({'action': 'players_in_room', 'names': [player.name for player in self.players]})
        for player in self.players:
            if player.name == name:
                await player.connection.send_json({'action': 'get_field_mask', 'size':(9,9), 'field_mask':self.multiplier_field, 'transcription':{'r':{'RGB':(237,28,36), 'HEX':'#ed1c24'},
                                                                                                                                    'g':{'RGB':(37,177,76), 'HEX':'#22b14c'},
                                                                                                                                    'b':{'RGB':(0,162,232), 'HEX':'#00a2e8'},
                                                                                                                                    'o':{'RGB':(255,127,29), 'HEX':'#ff7f27'},
                                                                                                                                    '':{'RGB':(255,241,184), 'HEX':'#fff1b8'},}})
                await player.add_letters(self.get_letter(player.letters_limit))
                
    async def waiting(self):
        start_time = asyncio.get_event_loop().time()
        while len(self.players) < self.num_of_players:
            print(asyncio.get_event_loop().time() - start_time)
            if (asyncio.get_event_loop().time() - start_time) > 300:
                self.dead = True
                break
            await asyncio.sleep(2)
        await self.run()
    
    async def run(self):
        if len(self.players) < self.num_of_players: raise Exception('The users never got together in 5 minutes')
        curent_id = 0
        self.curent_player = self.players[curent_id]
        started = True
        while started:
            if self.passes == self.passes_limit: 
                self.dead = True
                started = False
                self.say_all_Players({'action': 'end_the_game'})
                break
            self.curent_player = self.players[curent_id]
            data = await self.curent_player.connection.receive_json()
            if data['action'] == 'pass': 
                curent_id +=1 
                if (curent_id >= self.num_of_players): curent_id = 0
                await self.curent_player.connection.send_json({'action': 'pass_move', 'new_curent_player':self.players[curent_id].name})
                continue
            elif data['action'] == 'replace_letters':
                replaceable: list[str] = data['letters']
                for leter in replaceable:
                    self.curent_player.letters_on_hand.remove(leter)
                    self.letter_count[leter] += 1
                new_letters = random.choices(list(self.letter_count.keys), k=len(replaceable))
                for leter in new_letters:
                    self.letter_count[leter] -=1
                _id = curent_id
                self.curent_player.letters_on_hand += new_letters
                curent_id +=1 
                if (curent_id >= self.num_of_players): curent_id = 0
                await self.curent_player.connection.send_json({'action': 'replace_letters', 'letters_on_hand':self.players[_id].letters_on_hand,'new_curent_player':self.players[curent_id].name})
                continue
            elif data['action'] == 'make_move': pass
            # Доделать эндпоинт "Сделать ход", если забуду все придуманные 
            # алгоритмы после того как проснусь, то зайти в переписку к Димасу
            # Реализовать проверку подключения игроков
            # Реализовать логирование