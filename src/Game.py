from Player import Player
from enum import Enum
from fastapi.websockets import WebSocket
import websockets.exceptions
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

    async def say_all_Players(self, message):
        for i in range(len(self.players)):
            ## await asyncio.sleep(0.5)
            if not self.players[i].disconnected:
                try:
                    if self.players[i].connection.client_state == websockets.protocol.OPEN:
                        await self.players[i].connection.send_json(message)
                except websockets.exceptions.ConnectionClosed as e:
                    self.players[i].disconnected = True
                    self.players[i].connection.close()
                    print(f"Connection closed with code {e.code}, reason: {e.reason}")
                except websockets.exceptions.ProtocolError as t:
                    self.players[i].disconnected = True
                    self.players[i].connection.close()
                    print(f"Ошибка сети {t}")
                except websockets.exceptions.InvalidHandshake as q:
                    self.players[i].disconnected = True
                    self.players[i].connection.close()
                    print(f"Ошибка сети {q}")
                except websockets.exceptions.WebSocketException as p:
                    self.players[i].disconnected = True
                    self.players[i].connection.close()
                    print(f"Ошибка ебать {p}")
                

    def give_to_player_start_letters(self, player: Player):
        player.set_letters_on_hand(random.choices(list(self.letter_count.keys()), k=7))
        for leter in player.letters_on_hand:
            self.letter_count[leter] -= 1

    async def add_Player(self, name: str, connection: WebSocket):
        self.players.append(Player(name=name, connection=connection, letters_limit=7))
        await asyncio.sleep(1)
        for player in self.players:
            print(player.name, player.letters_on_hand)
            if player.name == name and len(player.letters_on_hand) == 0:
                self.give_to_player_start_letters(player=player)
                await player.connection.send_json({'action': 'init_game', 'size':(9,9), 'field_mask':self.multiplier_field, 'transcription':{'r':{'RGB':(237,28,36), 'HEX':'#ed1c24'},
                                                                                                                                    'g':{'RGB':(37,177,76), 'HEX':'#22b14c'},
                                                                                                                                    'b':{'RGB':(0,162,232), 'HEX':'#00a2e8'},
                                                                                                                                    'o':{'RGB':(255,127,29), 'HEX':'#ff7f27'},
                                                                                                                                    '':{'RGB':(255,241,184), 'HEX':'#fff1b8'},}, 'leters_score':self.letter_score, 'letters_on_hand':player.letters_on_hand},)
        for player in self.players:
            await player.connection.send_json({'action': 'players_in_room', 'names': [player.name for player in self.players]})
        
    async def waiting(self):
        start_time = asyncio.get_event_loop().time()
        while len(self.players) < self.num_of_players:
            if (asyncio.get_event_loop().time() - start_time) > 300:
                self.dead = True
                break
            await asyncio.sleep(3) 
        await self.run()
    
    async def run(self):
        ## await asyncio.sleep(1)    
        if len(self.players) < self.num_of_players: raise Exception('The users never got together in 5 minutes')
        curent_id = 0
        self.curent_player = self.players[curent_id]
        started = True
        # for player in self.players:
        #     await player.connection.accept()
        while started:
            print(self.players)
            if self.passes == self.passes_limit: 
                self.dead = True
                started = False
                await asyncio.sleep(0.3) 
                for player in self.players:
                    await player.connection.send_json({'action': 'end_the_game'})
                break
            await asyncio.sleep(0.4)
            for player in self.players:
                await player.connection.send_json({'action': 'start_game', 'curent_player':f'{self.players[curent_id].name}'})
            
            try:
                # if self.players[curent_id].connection.client_state == websockets.protocol.OPEN:
                    data = await self.players[curent_id].connection.receive_json()
            except websockets.exceptions.ConnectionClosed as e:
                self.players[curent_id].disconnected = True
                await asyncio.sleep(0.3)
                for player in self.players:
                    await player.connection.send_json({'action': 'end_the_game', 'message': f'Игрок {self.players[curent_id].name} покинул игру!', 'scors': {player.name: player.score for player in self.players}})
                print(f"Connection closed with code {e.code}, reason: {e.reason}")
                break
            if data['action'] == 'pass':
                curent_id +=1 
                if (curent_id >= self.num_of_players): curent_id = 0
                await asyncio.sleep(0.3)
                await self.players[curent_id].connection.send_json({'action': 'pass_move', 'new_curent_player':self.players[curent_id].name})
                continue
            elif data['action'] == 'replace_letters':
                replaceable: list[str] = data['letters']
                for leter in replaceable:
                    self.players[curent_id].letters_on_hand.remove(leter)
                    self.letter_count[leter] += 1
                new_letters = random.choices(list(self.letter_count), k=len(replaceable))
                for leter in new_letters:
                    self.letter_count[leter] -=1
                _id = curent_id
                self.players[curent_id].letters_on_hand += new_letters
                curent_id +=1 
                if (curent_id >= self.num_of_players): curent_id = 0
                await asyncio.sleep(0.3)
                await self.players[curent_id].connection.send_json({'action': 'replace_letters', 'letters_on_hand':self.players[_id].letters_on_hand,'new_curent_player':self.players[curent_id].name})
                continue
            elif data['action'] == 'make_move': 
                if data['finaly' == True]:
                    await asyncio.sleep(0.3)
                    await self.players[curent_id].connection.send_json({'action':'get_letters', 'letters_on_hand':self.players[curent_id].letters_on_hand})
                    curent_id +=1 
                    if (curent_id >= self.num_of_players): curent_id = 0
                    await asyncio.sleep(0.3)
                    for player in self.players:
                        await player.connection.send_json({'action': 'player_moved', 'scores':{player.name:player.score for player in self.players}, 'field':[['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],],
'new_curent_player': self.players[curent_id]})
                    continue
                else:
                    await asyncio.sleep(0.3)
                    await self.players[curent_id].connection.send_json(random.choice([{'action':'calculated_points', 'words_scores':{'камар': 20, 'рог':7}}, {'action':'no_such_word', 'field':[['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],
['','','','','','','','','',],], 'letters_on_hand': self.players[curent_id].letters_on_hand}]))
            # Доделать эндпоинт "Сделать ход", если забуду все придуманные 
            # алгоритмы после того как проснусь, то зайти в переписку к Димасу
            # Реализовать логирование
            # cd .\XWords_V1\src\ 
            # uvicorn api:app --reload