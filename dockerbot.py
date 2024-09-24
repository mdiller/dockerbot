from collections import OrderedDict
import disnake
from disnake.ext import commands
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

bot = commands.Bot(
	test_guilds=settings.get("guilds", []))

session = None

first_run=True

@bot.event
async def on_ready():
	global session
	global first_run
	print("started! (v4)")
	if first_run:
		session = aiohttp.ClientSession(loop=bot.loop)
		await refresh_containers()
		first_run = False

async def get_auth_token():
	# get auth token
	body = {
		"Username": settings["docker"]["username"],
		"Password": settings["docker"]["password"]
	}
	url = f"{settings['docker']['url']}/api/auth"
	async with session.post(url, json=body) as r:
		data = json.loads(await r.text())
		return data["jwt"]

# refresh the container info/ids from names
async def refresh_containers():
	print("refreshing containers")
	authtoken = await get_auth_token()

	headers = {
		"Authorization": f"Bearer {authtoken}"
	}
	url = f"{settings['docker']['url']}/api/endpoints/1/docker/containers/json"
	async with session.get(url, headers=headers) as r:
		print(f"status {r.status} on querying containers")
		data = json.loads(await r.text(), object_pairs_hook=OrderedDict)
		for container in containers:
			name = "/" + container["name"]
			for c in data:
				if name in c["Names"]:
					container["info"] = c
					container["id"] = c["Id"]
					print(f"loaded container {name} as {c['Id']}")
					break
			if container.get("id") is None:
				print(f"COULDN'T FIND CONTAINER: {container['name']}")
				exit(1)
		


@commands.has_any_role(settings["role"])
@commands.slash_command()
async def start(inter: disnake.CmdInter, container):
	if container not in containers:
		await inter.send("container aint a valid one")
		return

	await inter.send("Starting...")
	authtoken = await get_auth_token()

	headers = {
		"Authorization": f"Bearer {authtoken}"
	}
	container = containers[container]
	url = f"{settings['docker']['url']}/api/endpoints/1/docker/containers/{container['id']}/start"
	async with session.post(url, headers=headers) as r:
		await inter.send(f"Status code {r.status}")

		if r.status == 204:
			await inter.send("Done! Should be up now.")
		elif r.status == 304:
			await inter.send("Looks like its already running.")
		else:
			await inter.send(f"Status code {r.status}")

@commands.has_any_role(settings["role"])
@commands.slash_command()
async def stop(inter: disnake.CmdInter, container):
	if container not in containers:
		await inter.send("container aint a valid one")
		return

	await inter.send("Stopping...")
	authtoken = await get_auth_token()

	headers = {
		"Authorization": f"Bearer {authtoken}"
	}
	container = containers[container]
	url = f"{settings['docker']['url']}/api/endpoints/1/docker/containers/{container['id']}/stop"
	async with session.post(url, headers=headers) as r:

		if r.status == 204:
			await inter.send("Done! Should be down now.")
		elif r.status == 304:
			await inter.send("Looks like its already down.")
		else:
			await inter.send(f"Status code {r.status}")




if __name__ == '__main__':
	bot.run(settings.get("token"))