import discord
import os
import json
from binance_api_controller import BinanceController
import asyncio 

client = discord.Client()

binance_controller = None
CONF_FILE = 'bot.json'

conf = None
with open(CONF_FILE) as inFile:
	conf = json.load(inFile)

BOT_HELP_MESSAGE = """
Automate market orders on futures using Binance API.
1. Set the leverage to a number: **!leverage n** (for eg: **!leverage 10**)
2. Place a market order for a future pair, for one the following specific amounts:
	a. $500 - **i <symbol>** eg: **i eth**
	b. $1000 - **m <symbol>** eg: **m eth**
	c. $1500 - **h <symbol>** eg: **h eth**
3. Refresh Symbols and their Lot Sizes: **!refresh**
"""

async def handle_bot_command(message):
	parts = message.split(' ')
	if len(parts) > 2:
		return BOT_HELP_MESSAGE

	response = None
	command = parts[0].lower()
	if command =='!refresh':
		response = await binance_controller.update_futures_info()
		return response
	if command == '!leverage' and len(parts)==2:
		new_leverage = int(parts[1])
		response = await binance_controller.set_leverage(new_leverage)
		return response

	amount_map = {
		'i': 500,
		'm': 1000,
		'h': 1500
	}

	amount = amount_map.get(command, None)
	if amount and len(parts) == 2:
		coin_symbol = f'{parts[1].upper()}USDT'
		response = await binance_controller.place_futures_on_market_price(coin_symbol, amount)
		return response
	
	return BOT_HELP_MESSAGE

async def create_binance_client():
	global binance_controller
	binance_controller = await BinanceController.create(
		api_key=conf['binance_api_key'],
		api_secret=conf['binance_api_secret'],
		testnet=conf['testnet']
	)
	return

@client.event
async def on_ready():
	print(f'We have looged in as {client.user}')
	await create_binance_client()

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	reponse = await handle_bot_command(message.content)
	await message.channel.send(reponse)

if __name__ == '__main__':
	client.run(conf['discord_token'])