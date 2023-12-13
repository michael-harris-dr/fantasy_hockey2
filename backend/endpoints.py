from fastapi import FastAPI, Security
import json
from fastapi.middleware.cors import CORSMiddleware
from fan import *
from typing import Union
import os
from security import *

app = FastAPI()

origins = ["*"]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/health")
def health():
	return {"status" : "up and running"}

@app.get("/validatePlayer", dependencies=[Security(validate_api_key)])
def get_player(Player: str):
	found = valid_player(Player)
	return json.dumps(found)

@app.get("/players", dependencies=[Security(validate_api_key)])
def get_players(Players: Union[str, None] = None):
	playerStats = get_player_stats(json.loads(Players))
	
	return json.dumps(playerStats)
