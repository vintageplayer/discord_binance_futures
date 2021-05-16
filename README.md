1. Update your discord bot key and binance api key & secret in src/bot.json
2. Update testnet value as per your preference
3. Build the docker image (ensure you are in the same directory as Dockerfile): `docker build . -t 'discord_binance_bot:latest'`
4. Run the bot container `docker run -d --name discord_bot discord_binance_bot`
5. Verify the container is in running state: `docker ps -a` (Status should Up and not Exited for the container with name discord_bot)