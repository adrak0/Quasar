import asyncio
import binascii
import io
import json
import os
import platform
import random
import re
import time
import difflib
import urllib
import what3words as w3w
from asyncio import TimeoutError, sleep
from datetime import datetime
from itertools import cycle
from platform import python_version
from random import choice, randint
from time import time
from typing import List, Optional, Union, Dict 
from urllib.parse import quote_plus
from discord.utils import get
from dateutil import parser
from dotenv import load_dotenv

import aiohttp
import discord
import humanize
import PIL.ImageOps
import pyfiglet
import qrcode
import requests
import requests_cache
import numpy as np
import math as math
import base64
from io import BytesIO 
from math import * 
from aiohttp import request
from async_timeout import timeout
from discord import Embed ,Member
from discord.ext import commands, tasks
from discord.ext.commands import (BadArgument, Bot, BucketType,
                                  clean_content, command, cooldown)
from discord.utils import get
from PIL import Image, ImageFilter
from requests import Request, Session
load_dotenv()
intents = discord.Intents.default()
bot =  discord.Bot(intents = intents    
, command_prefix = "=")

@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(name="/help"),status=discord.Status.idle) 
  print("Bot is ready!")


@bot.slash_command(name="chgsts",description="🦎 Changes status of the bot remotely.")
async def change_presence(ctx, text):
    if ctx.author.id == 514119980518735903:
        await bot.change_presence(activity=discord.Game(name=text),status=discord.Status.idle) 
        await ctx.respond("Presence changed.", ephemeral  = True)
    else:
      em = discord.Embed(title="Only the owner of this bot can run this command.")
      await ctx.respond(embed=em, ephemeral  = True)

@bot.slash_command(name="help",description="📰 Help menu.")
async def help(ctx):
    em = discord.Embed(description="Thank you for using this command as a slash command.\nㅤ\nGo ahead and hit `/` to discover my all commands!")
    await ctx.respond(embed = em,ephemeral  = True)

@bot.slash_command(name="privacy",description="🔏 Info about privacy policy.")
async def privacy(ctx):
  em = discord.Embed(title="🔏 Privacy Policy", description = "We don't collect/store any user or guild data.")
  await ctx.respond(embed = em, ephemeral  = True)

@bot.slash_command(name="avatar",description="📷 Fetches User Avatar.")
async def avatar(ctx, user: discord.Member = None):
  if user == None:
    author = ctx.author
    pfp = author.avatar.url
    embed = discord.Embed(title="Your avatar")
    embed.set_image(url=pfp)
    await ctx.respond(embed=embed)
  else:
    userAvatarUrl = user.avatar.url    
    embed = discord.Embed(title=f"{user}'s avatar")
    embed.set_image(url=userAvatarUrl)
    await ctx.respond(embed=embed)

@bot.slash_command(name="flip",description="💸 Flips a coin randomly.")
async def flip(ctx):
  coin_flip = ["*Heads*","*Tails*"]
  em = discord.Embed(title="Flipping a coin... <a:flipcoin:915827162311966740>")
  message = await ctx.respond(embed = em)
  await asyncio.sleep(3)
  embed = discord.Embed(title=f"{random.choice(coin_flip)}")
  await message.edit(embed = embed)

@bot.slash_command(name="invite",description="➕ Invite link for the bot.")
async def invite(ctx):
  await ctx.respond("[Add Quasars to your server!](https://discord.com/oauth2/authorize?client_id=821742438603292672&permissions=2150722624&scope=bot+applications.commands)",ephemeral  = True)

@bot.slash_command(name="github",description="👩‍💻 GitHub link for the bot.")
async def github(ctx):
  await ctx.respond("[Here's the link!](https://github.com/anniwth/quasars)",ephemeral  = True)

@bot.slash_command(name="echo",description="🗣️ Repeats a message provided by a user.")
async def echo(ctx, text):
  await ctx.channel.send(text)
  await ctx.respond('Posted your message.',ephemeral  = True)

backend_url =  os.getenv('backendurl')

def get_images_from_backend(prompt):
    r = requests.post(backend_url, json={"prompt": prompt})
    if r.status_code == 200:
        json = r.json()
        images = json["images"]
        images = [base64.b64decode(img) for img in images]

        for i in range(len(images)):
            image = images[i]
            with open(f"image_{i}.jpg", "wb") as f:
               f.write(image)
        return True

    else:
        print("Error:", r.status_code)
        return False

@bot.slash_command(name="dallemini",description="📸Generates text to image using Dalle Mini.")
async def dallemini(ctx, prompt):
  await ctx.defer()
  await ctx.respond("Please wait... ⏳", ephemeral  = True)
  if get_images_from_backend(prompt):
      file = discord.File("image_0.jpg", filename="image_0.jpg")
      file1 = discord.File("image_1.jpg", filename="image_1.jpg")
      file2 = discord.File("image_2.jpg", filename="image_2.jpg")
      file3 = discord.File("image_3.jpg", filename="image_3.jpg")
      file4 = discord.File("image_4.jpg", filename="image_4.jpg")
      file5 = discord.File("image_5.jpg", filename="image_5.jpg")
      file6 = discord.File("image_6.jpg", filename="image_6.jpg")
      file7 = discord.File("image_7.jpg", filename="image_7.jpg")
      file8 = discord.File("image_8.jpg", filename="image_8.jpg")
      await ctx.channel.send(f"Successfully uploaded images for `{prompt}`, requested by {ctx.author}.\nCreated using [Dalle-Mini](https://github.com/borisdayma/dalle-mini).",files=[file,file1,file2,file3,file4,file5,file6,file7,file8])
      os.remove("image_0.jpg")
      os.remove("image_1.jpg")
      os.remove("image_2.jpg")
      os.remove("image_3.jpg")
      os.remove("image_4.jpg")
      os.remove("image_5.jpg")
      os.remove("image_6.jpg")
      os.remove("image_7.jpg")
      os.remove("image_8.jpg")
  else:
      await ctx.respond("Something went wrong, try using the command again.", ephemeral  = True)

@bot.slash_command(name="inspire",description="🐜 Sends inspirational quotes.")
async def inspire(ctx):
    async with aiohttp.ClientSession() as cs:
      async with cs.get("https://zenquotes.io/api/random") as r:
        fact = await r.json() 
        quote = fact[0]['q'] + " \n - " + fact[0]['a']
        await ctx.respond(f"```{quote}```")
  
@bot.slash_command(name="ascii",description="🧬 Convert texts into isometric font.")
async def ascii(ctx, text):
  try:
    ascii = pyfiglet.figlet_format(text)
    await ctx.respond(f"```{ascii}```")
  except Exception as e:
    await ctx.respond(f'Error:\n{e}', ephemeral  = True)
    

@bot.slash_command(name="ship",description="⚓ Ships between two users.")
async def ship(ctx,  user1 : discord.Member, user2 : discord.Member):
    shipnumber = random.randint(0,100)

    if shipnumber <= 33:
        shipColor = 0xE80303
    elif 33 < shipnumber < 66:
        shipColor = 0xff6600
    else:
        shipColor = 0x3be801

    emb = (discord.Embed(color=shipColor, 
                          title="Love test for:", 
                          description="**{0}** and **{1}** {2}".format(user1.name, user2.name, random.choice([
                                                                                                    ":sparkling_heart:", 
                                                                                                    ":heart_decoration:", 
                                                                                                    ":heart_exclamation:", 
                                                                                                    ":heartbeat:", 
                                                                                                    ":heartpulse:", 
                                                                                                    ":hearts:", 
                                                                                                    ":blue_heart:", 
                                                                                                    ":green_heart:", 
                                                                                                    ":purple_heart:", 
                                                                                                    ":revolving_hearts:", 
                                                                                                    ":yellow_heart:", 
                                                                                                    ":two_hearts:"]))))
    emb.add_field(name="Results:", value=f"{shipnumber}%", inline=True)
    emb.set_author(name="Ship", icon_url="https://www.freeiconspng.com/thumbs/heart-icon/valentine-heart-icon-6.png")
    await ctx.respond(embed=emb)
  
@bot.slash_command(name="morse",description="🧮 Converts the text into morse code.")
async def morse(ctx,text):
   async with aiohttp.ClientSession() as cs:
      async with cs.get( f"http://www.morsecode-api.de/encode?string={text}") as r:
          qrObj = await r.json() 
          await ctx.respond(f'```yaml\n{qrObj["morsecode"]}```')

@bot.slash_command(name="what3words",description="🗺 Converts the 3 words to coordinates.")
async def what3words(ctx, word1 :str, word2:str, word3:str):
  try:
    wht3api = os.environ['what3api']
    geocoder = w3w.Geocoder(wht3api)
    res = geocoder.convert_to_coordinates(f'{word1}.{word2}.{word3}')
    embed = discord.Embed(title="what3words",description="This function converts a 3 word address to a position, expressed as coordinates of latitude and longitude.")
    embed.add_field(name="Co-Ordinates",value=f"{res['coordinates']['lat'], res['coordinates']['lng']}")
    embed.add_field(name="Nearest Place",value=f"{res['nearestPlace']}")
    embed.set_image(url=f"https://mapapi.what3words.com/map/minimap?lat={res['coordinates']['lat']}&lng={res['coordinates']['lng']}&zoom=15&width=600&height=600")
    buttons = [
      create_button(style=ButtonStyle.URL, label="PlayStore", url = "https://play.google.com/store/apps/details?id=com.what3words.android"),
      create_button(style=ButtonStyle.URL, label="Website", url = f"{res['map']}")]
    action_row = create_actionrow(*buttons)
    await ctx.respond(embed=embed ,components=[action_row])
  except KeyError:
    await ctx.respond("Those combinations of words don't have any coordinates on our map.",ephemeral =True)
  
@bot.slash_command(name="what2coordinates",description="🗺 Converts coordinates to 3 words.")
async def what3words(ctx, latitude :int, longitude:int):
  try:
    wht3api = os.environ['what3api']
    geocoder = w3w.Geocoder(wht3api)
    res = geocoder.convert_to_3wa(w3w.Coordinates(f'{latitude}',f'{longitude}'))
    embed = discord.Embed(title="what3words",description="This function converts coordinates (expressed as latitude and longitude) to a 3 word address.\nLatitude must be always >=-90 and <= 90.")
    embed.add_field(name="Nearest Place",value=f"{res['nearestPlace']}")
    embed.add_field(name="3 Words",value=f"{res['words']}")
    embed.set_image(url=f"https://mapapi.what3words.com/map/minimap?lat={res['coordinates']['lat']}&lng={res['coordinates']['lng']}&zoom=15&width=600&height=600")
    buttons = [
      create_button(style=ButtonStyle.URL, label="PlayStore", url = "https://play.google.com/store/apps/details?id=com.what3words.android"),
      create_button(style=ButtonStyle.URL, label="Website", url = f"{res['map']}")]
    action_row = create_actionrow(*buttons)
    await ctx.respond(embed=embed ,components=[action_row])
  except KeyError:
    await ctx.respond('Bad coordinates, latitude must be >=-90 and <= 90.',ephemeral =True)

@bot.slash_command(name="weather",description="☁️ Forecast for a specific location.")
@commands.cooldown(1, 5, BucketType.user)
async def weather(ctx,location):
    try:
      wapi = os.environ['weatherapi']
      async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={wapi}&units=metric") as r:
          data = await r.json() 
          embed = discord.Embed(title=f"Forecast for {data['name']} ", description = f"** {data['weather'][0]['description']}**",
                color = discord.Color.purple()
              )

          embed.add_field(name="Temperatue", value=f"{data['main']['temp']} °C", inline=True)
          embed.add_field(name="Feels like", value=f"{data['main']['feels_like']} °C", inline=True)
          embed.add_field(name="Humidity", value=f"{data['main']['humidity']} %", inline=False)
          embed.add_field(name="Pressure", value=f"{data['main']['pressure']} Pa", inline=False)
          embed.add_field(name="Sunrise", value=f"<t:{data['sys']['sunrise']}:R>", inline=True)
          embed.add_field(name="Sunset", value=f"<t:{data['sys']['sunset']}:R>", inline=True)
          await ctx.respond(embed=embed)
    except KeyError:
      await ctx.respond("`That location doesn't exist in our database.`",ephemeral =True)
    except commands.errors.CommandOnCooldown:
      await ctx.respond("You are on cooldown.",ephemeral =True)


@bot.slash_command(name="morsetable",description="📊 Look-up for the morse code table.")
async def morsetable(ctx, num_per_row = None):
  morse_code = { 
			"a" : ".-",
			"b" : "-...",
			"c" : "-.-.",
			"d" : "-..",
			"e" : ".",
			"f" : "..-.",
			"g" : "--.",
			"h" : "....",
			"i" : "..",
			"j" : ".---",
			"k" : "-.-",
			"l" : ".-..",
			"m" : "--",
			"n" : "-.",
			"o" : "---",
			"p" : ".--.",
			"q" : "--.-",
			"r" : ".-.",
			"s" : "...",
			"t" : "-",
			"u" : "..-",
			"v" : "...-",
			"w" : ".--",
			"x" : "-..-",
			"y" : "-.--",
			"z" : "--..",
			"1" : ".----",
			"2" : "..---",
			"3" : "...--",
			"4" : "....-",
			"5" : ".....",
			"6" : "-....",
			"7" : "--...",
			"8" : "---..",
			"9" : "----.",
			"0" : "-----"
			}
  try:
    num_per_row = int(num_per_row)
  except Exception:
    num_per_row = 5

  msg = "__**Morse Code Lookup Table:**__\n```\n"
  max_length = 0
  current_row = 0
  row_list = [[]]
  cur_list = []
  sorted_list = sorted(morse_code)
  for key in sorted_list:
    entry = "{} : {}".format(key.upper(), morse_code[key])
    if len(entry) > max_length:
      max_length = len(entry)
    row_list[len(row_list)-1].append(entry)
    if len(row_list[len(row_list)-1]) >= num_per_row:
      row_list.append([])
      current_row += 1

  for row in row_list:
    for entry in row:
      entry = entry.ljust(max_length)
      msg += entry + "  "
    msg += "\n"

  msg += "```"
  await ctx.respond(msg)
   
@bot.slash_command(name="servers",description="📃 Name list of all the servers the bot is in."
)
async def servers(ctx):
  if ctx.author.id == 514119980518735903:
    list1 = []
    for guild in bot.guilds:
      list1.append(guild.name)
    f = open("servers.txt", "w")
    f.write("\n".join(sorted(list1)))
    f.close()
    await ctx.author.send(file=discord.File("servers.txt"))
    await ctx.respond("The file has been sent to your DMs.",ephemeral  = True)
    os.remove(f.name)
  else:
    em = discord.Embed(title="Only the owner of this bot can run this command.")
    await ctx.respond(embed=em, ephemeral  = True)

@bot.slash_command(name="unmorse",description="🧮 Converts a morse code into text.")
async def unmorse(ctx, content):
  morse_code = { 
    "a" : ".-",
    "b" : "-...",
    "c" : "-.-.",
    "d" : "-..",
    "e" : ".",
    "f" : "..-.",
    "g" : "--.",
    "h" : "....",
    "i" : "..",
    "j" : ".---",
    "k" : "-.-",
    "l" : ".-..",
    "m" : "--",
    "n" : "-.",
    "o" : "---",
    "p" : ".--.",
    "q" : "--.-",
    "r" : ".-.",
    "s" : "...",
    "t" : "-",
    "u" : "..-",
    "v" : "...-",
    "w" : ".--",
    "x" : "-..-",
    "y" : "-.--",
    "z" : "--..",
    "1" : ".----",
    "2" : "..---",
    "3" : "...--",
    "4" : "....-",
    "5" : ".....",
    "6" : "-....",
    "7" : "--...",
    "8" : "---..",
    "9" : "----.",
    "0" : "-----"
    }
  
  if content == None:
    await ctx.respond("Usage `{}unmorse [content]`".format(ctx.prefix))
    return

  content = "".join([x for x in content if x in " .-"])
  word_list = content.split("    ")
  ascii_list = []
  for word in word_list:
    letter_list = word.split()
    letter_ascii = []
    for letter in letter_list:
      for key in morse_code:
        if morse_code[key] == letter:
          letter_ascii.append(key.upper())
    if len(letter_ascii):
      ascii_list.append("".join(letter_ascii))
    
  if not len(ascii_list):
    await ctx.respond("There were no valid morse chars in the passed content.")
    return
  msg = " ".join(ascii_list)
  msg = "```\n" + msg + "```"
  await ctx.respond(msg)

@bot.slash_command(name="texttohex",description="🧮 Convert texts into hexadecimal.")
async def texttohex(ctx, text):
    try:
        hexoutput =  discord.utils.escape_markdown((" ".join("{:02x}".format(ord(c)) for c in text)))
    except Exception as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.",ephemeral =True)
    if len(hexoutput) <= 479:
        await ctx.respond(f"```fix\n{hexoutput}```")
    else:
        try:
            await ctx.author.send(f"```fix\n{hexoutput}```")
            await ctx.respond(f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",ephemeral =True)
        except Exception:
            await ctx.respond(f"There was a problem, and I could not send the output. It may be too large or malformed",ephemeral =True)

@bot.slash_command(name="apod",description="🌌 Astronomy Picture of the Day.")
async def apod(ctx):
  nasaapi = os.environ['nasa_api']
  async with aiohttp.ClientSession() as cs:
    async with cs.get(f'https://api.nasa.gov/planetary/apod?api_key={nasaapi}') as r:
        qrObj = await r.json()
        try:
          embed = discord.Embed(title=f"🔭APOD of {qrObj['date']}",
                color = discord.Color.purple()
              )
          embed.add_field(name=qrObj['title'], value=f"{qrObj['explanation'][:900]}...\n[Learn more](https://apod.nasa.gov/apod/astropix.html)")
          embed.set_image(url=qrObj['hdurl'])
          embed.set_footer(text=f"The API refreshes once every 24 hours.")
          await ctx.respond(embed=embed)
        except KeyError:
          embed = discord.Embed(title=f"🔭APOD of {qrObj['date']}",
                color = discord.Color.purple()
              )
          embed.add_field(name=qrObj['title'], value=f"{qrObj['explanation'][:900]}...\n[Learn more](https://apod.nasa.gov/apod/astropix.html)")
          embed.add_field(name="Discord doesn't support video URLs.", value = "[Click here to view all.](https://apod.nasa.gov/apod/astropix.html)",inline =False)
          embed.set_footer(text=f"The API refreshes once every 24 hours.")
          await ctx.respond(embed=embed)

@bot.slash_command(name="sma",description="👩‍🔬 Calculate Semi-Major Axis.")
async def sma(ctx, aphelion : int, perihelion :int):
  if aphelion > perihelion:
    embed = discord.Embed(title="🛰️ Semi-Major Axis.", description = "Semi-Major Axis is just the average orbit height, is defined as one-half the sum of the perihelion and the aphelion.")
    calc = (aphelion + perihelion)/2
    e = math.sqrt(aphelion**2 - perihelion**2)/aphelion
    embed.add_field(name = "Results", value = f"{int(calc)} m")
    embed.add_field(name = "Elliptical Eccentricity", value = f"{e}",inline=False)
    embed.set_image(url="https://i.stack.imgur.com/R3DI2.jpg")
    await ctx.respond(embed = embed)
  elif perihelion >= aphelion:
    embed = discord.Embed(title="🛰️ Semi-Major Axis.", description = "Semi-Major Axis is just the average orbit height, is defined as one-half the sum of the perihelion and the aphelion.")
    calc = (aphelion + perihelion)/2
    e = math.sqrt(perihelion**2 - aphelion**2)/perihelion
    embed.add_field(name = "Results", value = f"{int(calc)} m")
    embed.add_field(name = "Elliptical Eccentricity", value = f"{e}",inline=False)
    embed.set_image(url="https://i.stack.imgur.com/R3DI2.jpg")
    await ctx.respond(embed = embed)


@bot.slash_command(name="deltav",description="👨‍🔬 Calculate DeltaV.")
async def deltav(ctx, engineimpulse : int, wetmass :int,drymass :int):
  embed = discord.Embed(title="🚀 DeltaV (Ideal Rocket Equation)", description = "DeltaV is the maximum change of velocity of the vehicle (with no external forces acting), is a measure of the impulse per unit of spacecraft mass that is needed to perform a maneuver such as launching from or landing on a planet or moon, or an in-space orbital maneuver. \nㅤ\nEquation: [ΔV == Isp * 9.82 * log(WetMass/DryMass)](https://en.wikipedia.org/wiki/Tsiolkovsky_rocket_equation)")
  dv = engineimpulse*9.806*(np.log(wetmass/drymass))
  embed.add_field(name = "Results", value = f"{int(dv)} m/s")
  embed.set_image(url="https://c.tenor.com/YKLoTukF75UAAAAC/spacex-falcon9.gif")
  await ctx.respond(embed = embed)

@bot.slash_command(name="iss",description="🛰️ Coordinates for International Space Station.")
async def iss(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get(f'http://api.open-notify.org/iss-now.json') as r:
          qrObj = await r.json() 
          embed = discord.Embed(title="🛰Current position for ISS", description ='Coordinates for International Space Station.',
                color = discord.Color.purple()
              )
          embed.add_field(name='Latitude', value=(qrObj['iss_position'])['latitude'])
          embed.add_field(name='Longitude', value=(qrObj['iss_position'])['longitude'])
          embed.add_field(name='TimeStamp', value=f"<t:{qrObj['timestamp']}:R>")
          embed.add_field(name='Live Tracker', value="http://www.isstracker.com/")
          embed.set_image(url="https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/spacestation_images/international2520space2520station_image_20190220215716.jpeg")
          await ctx.respond(embed=embed)


@bot.slash_command(name="nextlaunch",description="🚀 Detailed info about the next rocket launch.")
async def nextlaunch(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get(f'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json') as r:
        try:
          qrObj = await r.json()
          embed = discord.Embed(title = f"🚀 {qrObj['results'][0]['name']}", description = f"{qrObj['results'][0]['mission']['description']}")
          embed.add_field(name = "Start Window", value =f"<t:{parser.parse(qrObj['results'][0]['window_start']).strftime('%s')}:R>", inline=True)
          embed.add_field(name="End Window", value=f"<t:{parser.parse(qrObj['results'][0]['window_end']).strftime('%s')}:R>", inline=True)
          embed.add_field(name="Orbit", value = f"{qrObj['results'][0]['mission']['orbit']['name']}", inline=True)
          embed.add_field(name="Agency", value = f"{qrObj['results'][0]['launch_service_provider']['name']}", inline=True)
          embed.add_field(name=f"Location", value = f"{qrObj['results'][0]['pad']['location']['name']}", inline=True)
          embed.add_field(name=f"Co-ordinates", value = f"[Google Maps]({qrObj['results'][0]['pad']['map_url']})", inline=True) 
          embed.set_image(url=f"{qrObj['results'][0]['image']}")
          await ctx.respond(embed=embed)
        except TypeError:
          qrObj = await r.json()
          embed = discord.Embed(title = f"🚀 {qrObj['results'][0]['name']}", description = "No description was provided.")
          embed.add_field(name = "Start Window", value =f"<t:{parser.parse(qrObj['results'][0]['window_start']).strftime('%s')}:R>", inline=True)
          embed.add_field(name="End Window", value=f"<t:{parser.parse(qrObj['results'][0]['window_end']).strftime('%s')}:R>", inline=True)
          embed.add_field(name="Orbit", value = "No orbit was provided.", inline=True)
          embed.add_field(name="Agency", value = f"{qrObj['results'][0]['launch_service_provider']['name']}", inline=True)
          embed.add_field(name=f"Location", value = f"{qrObj['results'][0]['pad']['location']['name']}", inline=True)
          embed.add_field(name=f"Co-ordinates", value = f"[Google Maps]({qrObj['results'][0]['pad']['map_url']})", inline=True) 
          embed.set_image(url=f"{qrObj['results'][0]['image']}")
          await ctx.respond(embed=embed)


@bot.slash_command(name="launches",description="☄️ Info about upcoming rocket launches.")
async def launches(ctx):
  embed = discord.Embed(title="🚀 Upcoming launches")
  async with aiohttp.ClientSession() as cs:
      async with cs.get(f'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json') as r:
          qrObj = await r.json() 
  for i in range(len(qrObj["results"])):
    if not i > 9:
      embed.add_field(name = f"{qrObj['results'][i]['name']}",value = f"Launch window: <t:{parser.parse(qrObj['results'][i]['window_start']).strftime('%s')}:R>", inline=False)
  await ctx.respond(embed=embed)


@bot.slash_command(name="rover",description="🪐 Images taken by curiosity rover on Mars.")
async def rover(ctx):
    nasaapi = os.environ['nasa_api']
    async with aiohttp.ClientSession() as cs:
      async with cs.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={nasaapi}") as r:
          qrObj = await r.json() 
          em = discord.Embed( title = "📸Image taken by Curiosity Rover on Mars.", color = ctx.author.color)
          em.set_image(url= random.choice(qrObj['photos'])['img_src'])
          await ctx.respond(embed = em)


@bot.slash_command(name="astronauts",description="👩‍🚀 People outside our atmosphere.")
async def astronauts(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('http://api.open-notify.org/astros.json') as r:
      qrObj = await r.json()
      strnamecraft = "" 
      for i in qrObj['people']:
        strnamecraft += i['name'] + " : " + i['craft'] + "\n"
      em = discord.Embed( title = "👩‍🚀Astronauts currently in space.", description = "People who are currently outside our atmosphere.", color = ctx.author.color)
      em.add_field(name="Names and Crafts.",value=f"""
```yaml
{strnamecraft}
```
""",inline=True)
      await ctx.respond(embed = em)
  

@bot.slash_command(name="hextotext",description="🧮 Converts hexadecimal to a text.")
async def hextotext(ctx, text):
    try:
        cleanS = discord.utils.escape_markdown(bytearray.fromhex(text).decode())
    except Exception as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.",ephemeral =True)
    if len(cleanS) <= 479:
        await ctx.respond(f"```{cleanS}```")
    else:
        try:
            await ctx.author.send(f"```{cleanS}```")
            await ctx.respond(f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:")
        except Exception:
            await ctx.respond(f"There was a problem, and I could not send the output. It may be too large or malformed",ephemeral =True)

@bot.slash_command(name="texttobinary",description="🧮 Converts text into binary numbers.")
async def texttobinary(ctx, text):
    try:
        cleanS = discord.utils.escape_markdown(' '.join(format(ord(x), 'b') for x in text))
    except Exception as e:
        return await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.",ephemeral =True)
    if len(cleanS) <= 479:
        await ctx.respond(f"```fix\n{cleanS}```")
    else:
        try:
            await ctx.author.send(f"```fix\n{cleanS}```")
            await ctx.respond(f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",ephemeral =True)
        except Exception:
            await ctx.respond(f"There was a problem, and I could not send the output. It may be too large or malformed",ephemeral =True)

@bot.slash_command(name="binarytotext",description="🧮 Converts binary numbers into a text.")
async def binarytotext(ctx, text):
  try:
    cleanS = discord.utils.escape_markdown(''.join([chr(int(text, 2)) for text in text.split()]))
  except Exception as e:
    await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data",ephemeral =True)
  if len(cleanS) <= 479:
    await ctx.respond(f"```{cleanS}```")
  else:
    try:
      await ctx.author.send(f"```{cleanS}```")
      await ctx.respond(f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",ephemeral =True)
    except Exception:
      await ctx.respond(f" There was a problem, and I could not send the output. It may be too large or malformed",ephemeral =True)

@bot.slash_command(name="reverse",description="◀️ Reverses the text form.")
async def reverse(ctx, text):
  if text == None:
    await ctx.respond("Provid a text with the command.")
  else:
    t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
    await ctx.respond(f"🔁 {t_rev}")

@bot.slash_command(name="mock",description="😵‍💫 Makes texts look weird.")
async def drunkify(ctx, text):
    lst = [str.upper, str.lower]
    newText = discord.utils.escape_markdown(''.join(random.choice(lst)(c) for c in text))
    if len(newText) <= 380:
        await ctx.respond(newText)
    else:
        try:
            await ctx.author.send(newText)
            await ctx.respond(f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",ephemeral =True)
        except Exception:
            await ctx.respond(f"There was a problem, and I could not send the output. It may be too large or malformed",ephemeral =True)

@bot.slash_command(name="qrcode",description="🐉 Generates a QR for a specific text.")
@commands.cooldown(1, 6, BucketType.user)
async def qr(ctx, text):
      img=qrcode.make(text)
      img.save("databases/qrcodes/QR.png")
      embed = discord.Embed()
      file = discord.File("databases/qrcodes/QR.png", filename="QR.png")
      embed.set_image(url="attachment://QR.png")
      embed.set_footer(text=f"Requested by {ctx.author}")
      await ctx.channel.send(file=file,embed=embed)
      await ctx.respond("Posted your qrcode.",ephemeral = True)
      os.remove("databases/qrcodes/QR.png")

@bot.slash_command(name="gray",description="🖼️ Converts an user avatar into grayscale.")
@commands.cooldown(1, 6, BucketType.user)
async def grayscale(ctx,user: discord.Member):
  try:
    userAvatarUrl = user.avatar.url   
    response = requests.get(userAvatarUrl)     
    img = Image.open(BytesIO(response.content)).convert('L')
    img.save('databases/Gray.png')
    embed = discord.Embed(title=f"{user.display_name}'s avatar has been converted to grayscale.")
    file = discord.File("databases/Gray.png", filename="Gray.png")
    embed.set_image(url="attachment://Gray.png")
    await ctx.respond(file=file,embed=embed)
    os.remove("databases/Gray.png")
  except AttributeError:
    await ctx.respond("You can use this command on servers only.", ephemeral  = True)

@bot.slash_command(name="blur",description="🖼️ Blurs an user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def blur(ctx,user: discord.Member):
  try:
    userAvatarUrl = user.avatar.url   
    response = requests.get(userAvatarUrl)    
    OriImage = Image.open(BytesIO(response.content))
    gaussImage = OriImage.filter(ImageFilter.GaussianBlur(7))
    gaussImage.save('databases/blur.png')
    embed = discord.Embed(title=f"{user.display_name}'s avatar has been blurred.")
    file = discord.File("databases/blur.png", filename="blur.png")
    embed.set_image(url="attachment://blur.png")
    await ctx.respond(file=file,embed=embed)
    os.remove("databases/blur.png")
  except AttributeError:
    await ctx.respond("You can use this command on servers only.", ephemeral  = True)

@bot.slash_command(name="invert",description="🖼️ Inverts the colors for an user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def invert(ctx,user: discord.Member):
  try:
    userAvatarUrl = user.avatar.url   
    response = requests.get(userAvatarUrl)
    im = Image.open(BytesIO(response.content))
    im_invert = PIL.ImageOps.invert(im.convert('RGB'))
    im_invert.save('databases/invert.png', quality=100)
    embed = discord.Embed(title=f"{user.display_name}'s avatar has been inverted.")
    file = discord.File("databases/invert.png", filename="invert.png")
    embed.set_image(url="attachment://invert.png")
    await ctx.respond(file=file,embed=embed)
    os.remove("databases/invert.png") 
  except AttributeError:
    await ctx.respond("You can use this command on servers only.", ephemeral  = True)


@bot.slash_command(name="qrread",description="🐞 Reads a QR image URL.")
@commands.cooldown(1, 7, BucketType.user)
async def qrreader(ctx,url): 
  await ctx.defer()
  async with aiohttp.ClientSession() as cs:
    async with cs.get(f'https://api.qrserver.com/v1/read-qr-code/?fileurl={url}') as r:
        qrObj = await r.json() 
        await ctx.respond(f'Decoded data: {qrObj[0]["symbol"][0]["data"]}')

@bot.slash_command(name="8ball",description="🎱 Random answers to questions.")
async def _8ball(ctx, question):
  responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."]
  await ctx.respond(f'`Question: {question}\nAnswer: {random.choice(responses)}`')

@bot.slash_command(name="curiosity",description="💫 Info about curiosity rover from Mars.")
async def curiosity(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get( "https://api.maas2.apollorion.com/") as r:
        qrObj = await r.json() 
        em = discord.Embed( title = "Curiosity Rover", description = "Data from Curiosity Rover on Mars.", color = ctx.author.color)
        em.add_field(name = 'Terrestrial Date', value = qrObj['terrestrial_date'])
        em.add_field(name = 'Martian Sols', value = qrObj['sol'])
        em.add_field(name = 'Season', value = qrObj['season'])
        em.add_field(name = 'Min Temp', value = f"{qrObj['min_temp']}°C")
        em.add_field(name = 'Max Temp', value = f"{qrObj['max_temp']}°C")
        em.add_field(name = 'Atmospheric Opacity', value = qrObj['atmo_opacity'])
        em.add_field(name = 'Sunrise', value = qrObj['sunrise'])
        em.add_field(name = 'Sunset', value = qrObj['sunset'])
        em.add_field(name = 'UV Radiation', value = qrObj['local_uv_irradiance_index'])
        em.add_field(name = 'Pressure', value = f"{qrObj['pressure']} Pascals")
        em.add_field(name = 'TimeZone of Data', value = qrObj['TZ_Data'])
        await ctx.respond(embed = em)

@bot.slash_command(name="ping",description="🏓 It tells the latency speed.")
async def ping(ctx):
  msg = await ctx.respond(f' {round(bot.latency*1000)} ms')  

bot.launch_time = datetime.utcnow()

@bot.slash_command(name="stats",description="📊 Stats and info about the bot.")
async def stats(ctx):
  delta_uptime = datetime.utcnow() - bot.launch_time
  hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
  minutes, seconds = divmod(remainder, 60)
  days, hours = divmod(hours, 24)
  embed = discord.Embed(title = "__Bot Info__", description =    f"""
```yaml
Creator: Anni#1714
Uptime: {days}d {hours}h {minutes}m {seconds}s
Created on: March 17, 2021 (19:21)
```
  """, color = ctx.author.color)
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
    members += guild.member_count - 1
  pythonVersion = platform.python_version()
  dpyVersion = discord.__version__
  serverCount = len(bot.guilds)
  memberCount = len(set(bot.get_all_members()))
  embed.add_field(
            name="__Stats__",
            value=f"""
```yaml
Users: {members}
Servers in: {servers}
```
            """,
            inline=True
      )
  embed.add_field(
            name="__Version__",
            value=f"""
```yaml
Python: {pythonVersion}
Pycord: {dpyVersion}
```
            """,
            inline=True
      ) 
  await ctx.respond(embed = embed)

bot.run(os.getenv('TOKEN'))
