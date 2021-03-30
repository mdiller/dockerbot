from discord.ext import commands
import random
import json
import asyncio
import os
import aiohttp

# https://discord.com/oauth2/authorize?permissions=2048&scope=bot&client_id=826295488743211009

with open("settings.json", "r") as f:
	settings = json.loads(f.read())

with open("containers.json", "r") as f:
	containers = json.loads(f.read())

bot = commands.Bot(command_prefix=settings["prefix"])

session = None


@bot.event
async def on_ready():
	global session
	session = aiohttp.ClientSession(loop=bot.loop)
	print("started! (v3)")
	
@commands.has_any_role(803116138212884510)
@bot.command()
async def start(ctx, container):
	if container not in containers:
		await ctx.send("container aint a valid one")
		return

	await ctx.send("Starting...")

	headers = {
		"Authorization": f"Bearer {settings['dockertoken']}"
	}
	container = containers[container]
	url = f"{settings['dockerurl']}/api/endpoints/1/docker/containers/{container['id']}/start"
	async with session.post(url, headers=headers) as r:
		await ctx.send(f"Status code {r.status}")

		if r.status == 204:
			await ctx.send("Done! Should be up now.")
		elif r.status == 304:
			await ctx.send("Looks like its already running.")
		else:
			await ctx.send(f"Status code {r.status}")

@commands.has_any_role(803116138212884510)
@bot.command()
async def stop(ctx, container):
	if container not in containers:
		await ctx.send("container aint a valid one")
		return

	await ctx.send("Stopping...")

	headers = {
		"Authorization": f"Bearer {settings['dockertoken']}"
	}
	container = containers[container]
	url = f"{settings['dockerurl']}/api/endpoints/1/docker/containers/{container['id']}/stop"
	async with session.post(url, headers=headers) as r:

		if r.status == 204:
			await ctx.send("Done! Should be down now.")
		elif r.status == 304:
			await ctx.send("Looks like its already down.")
		else:
			await ctx.send(f"Status code {r.status}")




if __name__ == '__main__':
	bot.run(settings.get("token"))