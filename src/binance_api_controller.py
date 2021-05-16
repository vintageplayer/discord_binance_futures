import asyncio
import json
from binance import AsyncClient, Client
from binance.exceptions import BinanceAPIException
import math

class BinanceController():
	@classmethod
	async def create(cls, api_key, api_secret, testnet=False):
		self = cls()
		self.client = await AsyncClient.create(api_key=api_key, api_secret=api_secret, testnet=testnet)
		self.futures_exchange_info = dict()
		await self.update_futures_info()
		return self

	async def update_futures_info(self):
		print('Fetching Futures Exchange Info')
		try:
			futures_exchange_info = await self.client.futures_exchange_info()
			self.process_futures_info(futures_exchange_info)
			response = 'Updated Successfully'
		except BinanceAPIException as e:
			api_error_message = str(e)
			response = f'Binance API Error: {api_error_message}'
		print(response)
		return response

	def process_futures_info(self, futures_exchange_info):
		self.futures_exchange_info = {symbol['symbol']: {'precision':self.calculate_symbol_precision(symbol['filters'])} for symbol in futures_exchange_info['symbols'] if symbol['symbol'][-4:] == 'USDT' }
		return True

	def calculate_symbol_precision(self, symbol_filters):
		step_size = 0.0
		for symbol_filter in symbol_filters:
			if symbol_filter['filterType'] == 'LOT_SIZE':
				step_size = float(symbol_filter['stepSize'])
				break
		precision = int(round(-math.log(step_size, 10), 0))
		return precision

	async def set_leverage(self, leverage):
		print(f'Updating Leverage to: {leverage}')
		succcess_count = 0
		failure_messages = []
		leverage = int(leverage)
		for symbol in self.futures_exchange_info.keys():
			try:
				response = await self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
				if response['leverage'] == leverage:
					succcess_count += 1
			except BinanceAPIException as e:
				api_error_message = str(e)
				failure_message = f'{Symbol}: {api_error_message}'
				failure_messages.append(failure_message)
		success_response = f'Updated Leverage for {succcess_count} symbols.'
		failure_response = ''
		if failure_messages:
			failure_response = '\nBinance API Error while updating following:\n' + '\n'.join(failure_messages)
		result_response = f'{success_response}{failure_response}'
		print(f'Leverage Updation Result: {result_response}')
		return result_response

	async def place_futures_on_market_price(self, symbol, amount):
		# code to place order
		print(f'Placing New Market Order for {symbol}. Amount: {amount} ')
		symbol_info = self.futures_exchange_info.get(symbol, {'precision': 0})
		precision = symbol_info['precision']
		try:
			response = await self.client.futures_symbol_ticker(symbol=symbol)
			price = float(response['price'])
			quantity = round((amount/price), precision)
			response = await self.client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity, newOrderRespType='RESULT')
			order_status = response['status']
			avg_price = response['avgPrice']
			number_of_coins = response['cumQty']
			USDT_used = response['cumQuote']
			response = f'Order Status: {order_status}. Average Price: {avg_price}. Qty: {number_of_coins}. USDT Transferred: {USDT_used}'
		except BinanceAPIException as e:
			api_error_message = str(e)
			response = api_error_message
		print(f'Order Request Response: {response}')
		return response

	async def close_connection(self):
		return await self.client.close_connection()

async def sample_controller_flow(api_key, api_secret):
	client = await BinanceController.create(api_key=api_key, api_secret=api_secret, testnet=True)
	import time
	new_leverage = 3
	symbol = 'ETHUSDT'
	amount = 1500
	start = time.time()	
	# responses = await client.set_leverage(new_leverage)
	responses = await client.place_futures_on_market_price(symbol, amount)
	end = time.time()
	print(responses)
	print(end-start)
	await client.close_connection()
	return

if __name__ == '__main__':
	with open('bot.json') as inFile:
		conf = json.load(inFile)
	api_key = conf['binance_api_key']
	api_secret = conf['binance_api_secret']
	loop = asyncio.get_event_loop()
	loop.run_until_complete(sample_controller_flow(api_key, api_secret))

