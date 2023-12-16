from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.websockets import WebSocket
from typing import List, Dict
from Game import Game
from Dictionary import Dictionary, FieldType
import asyncio
import random
from pydantic import BaseModel
import uvicorn
import time

app = FastAPI()
games: Dict[str, Game] = {}
ru_dict: Dictionary = Dictionary('dict_ru_v3.json')
ru_bag = ru_dict.getBag(FieldType.MEDIUM)

# class dataCreateRoom(BaseModel):
#     num_of_players: int
#     field_type: str
#     dict_type: str

def create_room_number():
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ]
    p = 0
    while p < 500:
        key = ''.join(random.choices(alphabet, k=5))
        if key not in games: return key

def check_room_number(room_number:str):
    for game in games:
        if room_number in game:
            print(True)
            return True
    print(False)
    return False

def del_deaded_games():
    for key in list(games.keys()):
        if games[key]['game'] != None :
            if games[key]['game'].dead == True:
                del games[key]
        elif games[key]['empty_time']-time.time() > 150: del games[key]

@app.get('/api/v1/init_sett_room')
async def init_sett_room():
    return {'dictionary':{'ru':['9x9']}, 'players_limits': ['2', '3', '4']}

@app.post("/api/v1/create_room")
async def create_room(request: Request, back_task:BackgroundTasks, num_of_players: int = Form(''), field_type: str = Form(''), dict_type: str = Form('')):
    del_deaded_games()
    if num_of_players < 2 or num_of_players > 4:
        return {'code': 400, 'message': 'Room not created, num_of_player < 2 or > 4'}
    key = create_room_number()
    games[key] = {'game': None, 'num_of_players':num_of_players, 'empty_time':time.time()}
    return {'code': 201, 'number':key, 'message': 'Room created, all good!'}

@app.get('/api/v1/check/{name}/{number}')
async def check(request: Request, name:str, number:str):
    ch=check_room_number(number)
    if ch == True:
        if len(games[number]['game'].players) == 0: return {'code': 200, 'message': f'Yes, that name ({name}) is not in this room ({number}).'}
        for player in games[number]['game'].players:
            if name in player.name:
                return {'code': 400, 'message': f'This name ({name}) is already occupied in the room ({number})'}
            else: return {'code': 200, 'message': f'Yes, that name ({name}) is not in this room ({number}).'}
    else: return {'code': 400, 'message': f'There is no such room ({number})'}



@app.websocket("/ws/v1/{name}/{number}")
async def websocket_endpoint(websocket: WebSocket, name:str, number:str):
    if games[number]['game'] == None:
        games[number]['game'] = Game(room_number=number, num_of_players=games[number]['num_of_players'], bag=ru_bag)
        await asyncio.sleep(0.5)
        await websocket.accept()
        await games[number]['game'].add_Player(name=name, connection=websocket)
        await games[number]['game'].waiting()
    await asyncio.sleep(0.5)
    await websocket.accept()
    await games[number]['game'].add_Player(name=name, connection=websocket)

    # except Exception as e:
    #     print(f"WebSocket connection error: {e}")
    #     await websocket.close()
    #     del games[number]
