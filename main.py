import binascii
import io
import json
import traceback
import os, glob
import random
import time
import platform
from asyncio import sleep
from datetime import datetime
from platform import python_version
from random import choice, randint
from discord.utils import get
from dateutil import parser
from dotenv import load_dotenv

import aiohttp
import discord
import PIL.ImageOps
import pyfiglet
import qrcode
import requests
import numpy as np
import math as math
import base64
from io import BytesIO
from math import *
from aiohttp import request
from discord import Embed, Member
from discord.ext import commands, tasks
from discord.ext.commands import (BadArgument, Bot, BucketType, clean_content,
                                  command, cooldown)
from PIL import Image, ImageFilter
from requests import Request

load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = discord.Bot(intents=intents, command_prefix="=")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name='a song ❄️🔥', url='https://www.youtube.com/watch?v=OgvLej8ln2w'))
    print("Bot is ready!")

@bot.slash_command(
  name="chgsts",
  description="🦎 Changes status of the bot remotely(Owner only command).")
async def change_presence(ctx, text):
  if ctx.author.id == 514119980518735903:
      await bot.change_presence(activity=discord.Game(name=text),
                                status=discord.Status.idle)
      await ctx.respond("Presence changed.", ephemeral=True)
  else:
      em = discord.Embed(
          title="Only the owner of this bot can run this command.")
      await ctx.respond(embed=em, ephemeral=True)


@bot.slash_command(name="help", description="📰 Help menu.")
async def help(ctx):
  em = discord.Embed(
      description=
      "Thank you for using this command as a slash command.\nㅤ\nGo ahead and hit `/` to discover my all commands!"
  )
  await ctx.respond(embed=em, ephemeral=True)


@bot.slash_command(name="privacy", description="🔏 Info about privacy policy.")
async def privacy(ctx):
  em = discord.Embed(
      title="🔏 Privacy Policy",
      description=
      "[We don't collect/store any user or guild data.](https://github.com/anniwth/Quasar#privacy-policy)"
  )
  await ctx.respond(embed=em, ephemeral=True)


@bot.slash_command(name="avatar", description="📷 Fetches User Avatar.")
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


@bot.slash_command(name="flip", description="💸 Flips a coin randomly.")
async def flip(ctx):
  coin_flip = ["*Heads*", "*Tails*"]
  em = discord.Embed(
      title="Flipping a coin... <a:flipcoin:915827162311966740>")
  message = await ctx.respond(embed=em)
  await asyncio.sleep(3)
  embed = discord.Embed(title=f"{random.choice(coin_flip)}")
  await message.edit(embed=embed)


@bot.slash_command(name="invite", description="➕ Invite link for the bot.")
async def invite(ctx):
  await ctx.respond(
      "[Add Quasar to your server!](https://discord.com/api/oauth2/authorize?client_id=1085413206186541076&permissions=2147765248&scope=bot+applications.commands)",
      ephemeral=True)


@bot.slash_command(name="github", description="👩‍💻 GitHub link for the bot.")
async def github(ctx):
  await ctx.respond("[Here's the link!](https://github.com/anniwth/quasar)",
                    ephemeral=True)


@bot.slash_command(name="echo",
   description="🗣️ Repeats a message provided by a user.")
async def echo(ctx, text, message_id: str = None):
  allowed_user_id = 1066171848640958487
  if ctx.author.id != allowed_user_id:
    await ctx.respond("You are not authorized to use this command.", ephemeral=True)
    return

  if message_id is None:
    await ctx.channel.send(text)
    await ctx.respond('Posted your message.', ephemeral=True)
  else:
    message = await ctx.channel.fetch_message(message_id)
    await message.reply(text)
    await ctx.respond('Posted your message.', ephemeral=True)

@bot.slash_command(name="react",
                 description="React with an emoji to a specific message.")
async def react(ctx, message_id: str, emoji: str):
  message = await ctx.channel.fetch_message(message_id)
  try:
      await message.add_reaction(emoji)
      await ctx.respond(f'Your Reaction has been added.', ephemeral=True)
  except:
      await ctx.respond(
          f'There was some error, please check the details before you enter.',
          ephemeral=True)


@bot.slash_command(name="inspire", description="🐜 Sends inspirational quotes.")
async def inspire(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get("https://zenquotes.io/api/random") as r:
          fact = await r.json()
          quote = fact[0]['q'] + " \n - " + fact[0]['a']
          await ctx.respond(f"```{quote}```")


@bot.slash_command(name="ascii",
                 description="🧬 Convert texts into isometric font.")
async def ascii(ctx, text):
  try:
      ascii = pyfiglet.figlet_format(text)
      await ctx.respond(f"```{ascii}```")
  except Exception as e:
      await ctx.respond(f'Error:\n{e}', ephemeral=True)


MORSE_CODE_DICT = {
'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
'Y': '-.--', 'Z': '--..',
'0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....',
'7': '--...', '8': '---..', '9': '----.',
'.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.',
')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
'_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.'
}

def text_to_morse(text):
  morse_code = ' '.join([MORSE_CODE_DICT.get(char.upper(), char) for char in text])
  return morse_code


@bot.slash_command(name="morse", description="🧮 Converts the text into Morse code.")
async def morse(ctx, text):
  morse_code = text_to_morse(text)
  await ctx.respond(f'```yaml\n{morse_code}```')



@bot.slash_command(name="weather", description="☁️ Forecast for a specific location.")
@commands.cooldown(1, 2, BucketType.user)
async def weather(ctx, location):
    try:
        api_key = '32b8ecd9bedc347b672f76041ea2568d'

        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric") as r:
                data = await r.json()
                if data['cod'] != 200:
                    await ctx.respond(f"`{data['message']}`", ephemeral=True)
                    return

                weather_data = data['weather'][0]
                weather_description = weather_data['description'].capitalize()
                main_data = data['main']

                embed = discord.Embed(
                    title=f"Forecast for {data['name']}",
                    description=f"**{weather_description}**",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Temperature", value=f"{main_data['temp']} °C", inline=True)
                embed.add_field(name="Feels like", value=f"{main_data['feels_like']} °C", inline=True)
                embed.add_field(name="Humidity", value=f"{main_data['humidity']} %", inline=False)
                embed.add_field(name="Pressure", value=f"{main_data['pressure']} hPa", inline=False)
                embed.add_field(name="Sunrise", value=f"<t:{data['sys']['sunrise']}:R>", inline=True)
                embed.add_field(name="Sunset", value=f"<t:{data['sys']['sunset']}:R>", inline=True)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.channel.send(embed=embed, silent=True)
                await ctx.respond("Posted the weather.", ephemeral=True)
    except Exception as e:
        error_traceback = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        await ctx.respond(f"```py\n{error_traceback}\n```", ephemeral=True)
    except commands.errors.CommandOnCooldown:
        await ctx.respond("You are on cooldown.", ephemeral=True)


@bot.slash_command(name="morsetable",
                 description="📊 Look-up for the morse code table.")
async def morsetable(ctx, num_per_row=None):
  morse_code = {
      "a": ".-",
      "b": "-...",
      "c": "-.-.",
      "d": "-..",
      "e": ".",
      "f": "..-.",
      "g": "--.",
      "h": "....",
      "i": "..",
      "j": ".---",
      "k": "-.-",
      "l": ".-..",
      "m": "--",
      "n": "-.",
      "o": "---",
      "p": ".--.",
      "q": "--.-",
      "r": ".-.",
      "s": "...",
      "t": "-",
      "u": "..-",
      "v": "...-",
      "w": ".--",
      "x": "-..-",
      "y": "-.--",
      "z": "--..",
      "1": ".----",
      "2": "..---",
      "3": "...--",
      "4": "....-",
      "5": ".....",
      "6": "-....",
      "7": "--...",
      "8": "---..",
      "9": "----.",
      "0": "-----"
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
      row_list[len(row_list) - 1].append(entry)
      if len(row_list[len(row_list) - 1]) >= num_per_row:
          row_list.append([])
          current_row += 1

  for row in row_list:
      for entry in row:
          entry = entry.ljust(max_length)
          msg += entry + "  "
      msg += "\n"

  msg += "```"
  await ctx.respond(msg)


@bot.slash_command(name="servers",
                 description="📃 Name list of all the servers the bot is in.")
async def servers(ctx):
  if ctx.author.id == 1066171848640958487:
      list1 = []
      for guild in bot.guilds:
          list1.append(guild.name)
      f = open("servers.txt", "w")
      f.write("\n".join(sorted(list1)))
      f.close()
      await ctx.author.send(file=discord.File("servers.txt"))
      await ctx.respond("The file has been sent to your DMs.",
                        ephemeral=True)
      os.remove(f.name)
  else:
      em = discord.Embed(
          title="Only the owner of this bot can run this command.")
      await ctx.respond(embed=em, ephemeral=True)


@bot.slash_command(name="unmorse",
                 description="🧮 Converts a morse code into text.")
async def unmorse(ctx, content):
  morse_code = {
      "a": ".-",
      "b": "-...",
      "c": "-.-.",
      "d": "-..",
      "e": ".",
      "f": "..-.",
      "g": "--.",
      "h": "....",
      "i": "..",
      "j": ".---",
      "k": "-.-",
      "l": ".-..",
      "m": "--",
      "n": "-.",
      "o": "---",
      "p": ".--.",
      "q": "--.-",
      "r": ".-.",
      "s": "...",
      "t": "-",
      "u": "..-",
      "v": "...-",
      "w": ".--",
      "x": "-..-",
      "y": "-.--",
      "z": "--..",
      "1": ".----",
      "2": "..---",
      "3": "...--",
      "4": "....-",
      "5": ".....",
      "6": "-....",
      "7": "--...",
      "8": "---..",
      "9": "----.",
      "0": "-----"
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
      await ctx.respond(
          "There were no valid morse chars in the passed content.")
      return
  msg = " ".join(ascii_list)
  msg = "```\n" + msg + "```"
  await ctx.respond(msg)


@bot.slash_command(name="texttohex",
                 description="🧮 Convert texts into hexadecimal.")
async def texttohex(ctx, text):
  try:
      hexoutput = discord.utils.escape_markdown(
          (" ".join("{:02x}".format(ord(c)) for c in text)))
  except Exception as e:
      await ctx.respond(
          f"Error: `{e}`.\nThis probably means the text is malformed.",
          ephemeral=True)
  if len(hexoutput) <= 479:
      await ctx.respond(f"```fix\n{hexoutput}```")
  else:
      try:
          await ctx.author.send(f"```fix\n{hexoutput}```")
          await ctx.respond(
              f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",
              ephemeral=True)
      except Exception:
          await ctx.respond(
              f"There was a problem, and I could not send the output. It may be too large or malformed",
              ephemeral=True)


@bot.slash_command(name="apod", description="🌌 Astronomy Picture of the Day.")
async def apod(ctx):
  nasaapi = '8NqA6bEbhvT3rqnkkyYfBI4zEP89v9ihLJmvqDgv'
  async with aiohttp.ClientSession() as cs:
      async with cs.get(
              f'https://api.nasa.gov/planetary/apod?api_key={nasaapi}') as r:
          qrObj = await r.json()
          try:
              embed = discord.Embed(title=f"🔭APOD of {qrObj['date']}",
                                    color=discord.Color.purple())
              embed.add_field(
                  name=qrObj['title'],
                  value=
                  f"{qrObj['explanation'][:900]}...\n[Learn more](https://apod.nasa.gov/apod/astropix.html)"
              )
              embed.set_image(url=qrObj['hdurl'])
              embed.set_footer(
                  text=f"The API refreshes once every 24 hours.")
              await ctx.respond(embed=embed)
          except KeyError:
              embed = discord.Embed(title=f"🔭APOD of {qrObj['date']}",
                                    color=discord.Color.purple())
              embed.add_field(
                  name=qrObj['title'],
                  value=
                  f"{qrObj['explanation'][:900]}...\n[Learn more](https://apod.nasa.gov/apod/astropix.html)"
              )
              embed.add_field(
                  name="Discord doesn't support video URLs.",
                  value=
                  "[Click here to view all.](https://apod.nasa.gov/apod/astropix.html)",
                  inline=False)
              embed.set_footer(
                  text=f"The API refreshes once every 24 hours.")
              await ctx.respond(embed=embed)


@bot.slash_command(name="deltav", description="👨‍🔬 Calculate DeltaV.")
async def deltav(ctx, engineimpulse: int, wetmass: int, drymass: int):
  embed = discord.Embed(
      title="🚀 DeltaV (Ideal Rocket Equation)",
      description=
      "DeltaV is the maximum change of velocity of the vehicle (with no external forces acting), is a measure of the impulse per unit of spacecraft mass that is needed to perform a maneuver such as launching from or landing on a planet or moon, or an in-space orbital maneuver. \nㅤ\nEquation: [ΔV == Isp * 9.82 * log(WetMass/DryMass)](https://en.wikipedia.org/wiki/Tsiolkovsky_rocket_equation)"
  )
  dv = engineimpulse * 9.806 * (np.log(wetmass / drymass))
  embed.add_field(name="Results", value=f"{int(dv)} m/s")
  embed.set_image(
      url="https://c.tenor.com/YKLoTukF75UAAAAC/spacex-falcon9.gif")
  await ctx.respond(embed=embed)


@bot.slash_command(
  name="iss", description="🛰️ Coordinates for International Space Station.")
async def iss(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get(f'http://api.open-notify.org/iss-now.json') as r:
          qrObj = await r.json()
          embed = discord.Embed(
              title="🛰Current position for ISS",
              description='Coordinates for International Space Station.',
              color=discord.Color.purple())
          embed.add_field(name='Latitude',
                          value=(qrObj['iss_position'])['latitude'])
          embed.add_field(name='Longitude',
                          value=(qrObj['iss_position'])['longitude'])
          embed.add_field(name='TimeStamp',
                          value=f"<t:{qrObj['timestamp']}:R>")
          embed.add_field(name='Live Tracker',
                          value="http://www.isstracker.com/")
          embed.set_image(
              url=
              "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/spacestation_images/international2520space2520station_image_20190220215716.jpeg"
          )
          await ctx.respond(embed=embed)


@bot.slash_command(name="nextlaunch",
                 description="🚀 Detailed info about the next rocket launch.")
async def nextlaunch(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get(
              f'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json'
      ) as r:
          try:
              qrObj = await r.json()
              embed = discord.Embed(
                  title=f"🚀 {qrObj['results'][0]['name']}",
                  description=
                  f"{qrObj['results'][0]['mission']['description']}")
              embed.add_field(
                  name="Start Window",
                  value=
                  f"Launch window: <t:{int(parser.parse(qrObj['results'][0]['window_start']).timestamp())}:R>",
                  inline=True)
              embed.add_field(
                  name="End Window",
                  value=
                  f"Launch window: <t:{int(parser.parse(qrObj['results'][0]['window_end']).timestamp())}:R>",
                  inline=True)
              embed.add_field(
                  name="Orbit",
                  value=f"{qrObj['results'][0]['mission']['orbit']['name']}",
                  inline=True)
              embed.add_field(
                  name="Agency",
                  value=
                  f"{qrObj['results'][0]['launch_service_provider']['name']}",
                  inline=True)
              embed.add_field(
                  name=f"Location",
                  value=f"{qrObj['results'][0]['pad']['location']['name']}",
                  inline=True)
              embed.add_field(
                  name=f"Co-ordinates",
                  value=
                  f"[Google Maps]({qrObj['results'][0]['pad']['map_url']})",
                  inline=True)
              embed.set_image(url=f"{qrObj['results'][0]['image']}")
              await ctx.respond(embed=embed)
          except TypeError:
              qrObj = await r.json()
              embed = discord.Embed(
                  title=f"🚀 {qrObj['results'][0]['name']}",
                  description="No description was provided.")
              embed.add_field(
                  name="Start Window",
                  value=
                  f"<t:{parser.parse(qrObj['results'][0]['window_start']).strftime('%s')}:R>",
                  inline=True)
              embed.add_field(
                  name="End Window",
                  value=
                  f"<t:{parser.parse(qrObj['results'][0]['window_end']).strftime('%s')}:R>",
                  inline=True)
              embed.add_field(name="Orbit",
                              value="No orbit was provided.",
                              inline=True)
              embed.add_field(
                  name="Agency",
                  value=
                  f"{qrObj['results'][0]['launch_service_provider']['name']}",
                  inline=True)
              embed.add_field(
                  name=f"Location",
                  value=f"{qrObj['results'][0]['pad']['location']['name']}",
                  inline=True)
              embed.add_field(
                  name=f"Co-ordinates",
                  value=
                  f"[Google Maps]({qrObj['results'][0]['pad']['map_url']})",
                  inline=True)
              embed.set_image(url=f"{qrObj['results'][0]['image']}")
              await ctx.respond(embed=embed)


@bot.slash_command(name="epic", description="🌎 DSCVR's view of planet earth.")
async def epic(ctx):
  nasaapi = '8NqA6bEbhvT3rqnkkyYfBI4zEP89v9ihLJmvqDgv'
  async with aiohttp.ClientSession() as cs:
      async with cs.get(
              f'https://api.nasa.gov/EPIC/api/natural?api_key={nasaapi}'
      ) as r:
          json_data = await r.json()
          date = json_data[0]["date"].split(None, 1)[0].replace('-', '/')
          embed = discord.Embed(
              title="EPIC (Earth Polychromatic Imaging Camera)",
              description=
              "Uniquely positioned at the Earth-Sun Lagrange point, EPIC provides full disc imagery of the Earth and captures unique perspectives of certain astronomical events such as lunar transits using a 2048x2048 pixel CCD (Charge Coupled Device) detector coupled to a 30-cm aperture Cassegrain telescope."
          )
          embed.add_field(name='Date',
                          value=json_data[0]['date'],
                          inline=False)
          embed.set_image(
              url=
              f'https://epic.gsfc.nasa.gov/archive/natural/{date}/png/{json_data[0]["image"]}.png'
          )
          await ctx.respond(embed=embed)


@bot.slash_command(name="embed",
                 description="Just for embed.")
async def embed(ctx, msg, link):
  embed = discord.Embed(title="",description=f"[{msg}]({link})")
  await ctx.channel.send(embed = embed)


@bot.slash_command(name="launches",
                 description="☄️ Info about upcoming rocket launches.")
async def launches(ctx):
  embed = discord.Embed(title="🚀 Upcoming launches")
  async with aiohttp.ClientSession() as cs:
      async with cs.get(
              f'https://ll.thespacedevs.com/2.2.0/launch/upcoming/?format=json'
      ) as r:
          qrObj = await r.json()
  for i in range(len(qrObj["results"])):
      if not i > 9:
          embed.add_field(
              name=f"{qrObj['results'][i]['name']}",
              value=
              f"Launch window: <t:{int(parser.parse(qrObj['results'][i]['window_start']).timestamp())}:R>",
              inline=False)
  await ctx.respond(embed=embed)


@bot.slash_command(name="rover",
                 description="🪐 Images taken by curiosity rover on Mars.")
async def rover(ctx):
  nasaapi = '8NqA6bEbhvT3rqnkkyYfBI4zEP89v9ihLJmvqDgv'
  async with aiohttp.ClientSession() as cs:
      async with cs.get(
              f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={nasaapi}"
      ) as r:
          qrObj = await r.json()
          em = discord.Embed(
              title="📸Image taken by Curiosity Rover on Mars.",
              color=ctx.author.color)
          em.set_image(url=random.choice(qrObj['photos'])['img_src'])
          await ctx.respond(embed=em)


@bot.slash_command(name="astronauts",
                 description="👩‍🚀 People outside our atmosphere.")
async def astronauts(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get('http://api.open-notify.org/astros.json') as r:
          qrObj = await r.json()
          strnamecraft = ""
          for i in qrObj['people']:
              strnamecraft += i['name'] + " : " + i['craft'] + "\n"
          em = discord.Embed(
              title="👩‍🚀Astronauts currently in space.",
              description="People who are currently outside our atmosphere.",
              color=ctx.author.color)
          em.add_field(name="Names and Crafts.",
                       value=f"""
```yaml
{strnamecraft}
```
""",
                       inline=True)
          await ctx.respond(embed=em)


@bot.slash_command(name="hextotext",
                 description="🧮 Converts hexadecimal to a text.")
async def hextotext(ctx, text):
  try:
      cleanS = discord.utils.escape_markdown(
          bytearray.fromhex(text).decode())
  except Exception as e:
      await ctx.respond(
          f"Error: `{e}`.\nThis probably means the text is malformed.",
          ephemeral=True)
  if len(cleanS) <= 479:
      await ctx.respond(f"```{cleanS}```")
  else:
      try:
          await ctx.author.send(f"```{cleanS}```")
          await ctx.respond(
              f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:"
          )
      except Exception:
          await ctx.respond(
              f"There was a problem, and I could not send the output. It may be too large or malformed",
              ephemeral=True)


@bot.slash_command(name="texttobinary",
                 description="🧮 Converts text into binary numbers.")
async def texttobinary(ctx, text):
  try:
      cleanS = discord.utils.escape_markdown(' '.join(
          format(ord(x), 'b') for x in text))
  except Exception as e:
      return await ctx.respond(
          f"Error: `{e}`.\nThis probably means the text is malformed.",
          ephemeral=True)
  if len(cleanS) <= 479:
      await ctx.respond(f"```fix\n{cleanS}```")
  else:
      try:
          await ctx.author.send(f"```fix\n{cleanS}```")
          await ctx.respond(
              f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",
              ephemeral=True)
      except Exception:
          await ctx.respond(
              f"There was a problem, and I could not send the output. It may be too large or malformed",
              ephemeral=True)


@bot.slash_command(name="binarytotext",
                 description="🧮 Converts binary numbers into a text.")
async def binarytotext(ctx, text):
  try:
      cleanS = discord.utils.escape_markdown(''.join(
          [chr(int(text, 2)) for text in text.split()]))
  except Exception as e:
      await ctx.respond(
          f"Error: `{e}`.\nThis probably means the text is malformed. Sorry, you can always try here: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data",
          ephemeral=True)
  if len(cleanS) <= 479:
      await ctx.respond(f"```{cleanS}```")
  else:
      try:
          await ctx.author.send(f"```{cleanS}```")
          await ctx.respond(
              f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",
              ephemeral=True)
      except Exception:
          await ctx.respond(
              f" There was a problem, and I could not send the output. It may be too large or malformed",
              ephemeral=True)


@bot.slash_command(name="reverse", description="◀️ Reverses the text form.")
async def reverse(ctx, text):
  if text == None:
      await ctx.respond("Provid a text with the command.")
  else:
      t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
      await ctx.respond(f"🔁 {t_rev}")


@bot.slash_command(name="mock", description="😵‍💫 Makes texts look weird.")
async def drunkify(ctx, text):
  lst = [str.upper, str.lower]
  newText = discord.utils.escape_markdown(''.join(
      random.choice(lst)(c) for c in text))
  if len(newText) <= 380:
      await ctx.respond(newText)
  else:
      try:
          await ctx.author.send(newText)
          await ctx.respond(
              f"The output too was too large, so I sent it to your DMs! :mailbox_with_mail:",
              ephemeral=True)
      except Exception:
          await ctx.respond(
              f"There was a problem, and I could not send the output. It may be too large or malformed",
              ephemeral=True)

@bot.slash_command(name="qrcode",
                 description="🐉 Generates a QR for a specific text.")
@commands.cooldown(1, 5, BucketType.user)
async def qr(ctx, text):
  img = qrcode.make(text)
  img.save("databases/qrcodes/QR.png")
  embed = discord.Embed()
  file = discord.File("databases/qrcodes/QR.png", filename="QR.png")
  embed.set_image(url="attachment://QR.png")
  embed.set_footer(text=f"Requested by {ctx.author}")
  await ctx.channel.send(file=file, embed=embed, silent=True)
  await ctx.respond("Posted your qrcode.", ephemeral=True)
  os.remove("databases/qrcodes/QR.png")


@bot.slash_command(name="gray",
                 description="🖼️ Converts an user avatar into grayscale.")
@commands.cooldown(1, 6, BucketType.user)
async def grayscale(ctx, user: discord.Member):
  try:
      userAvatarUrl = user.avatar.url
      response = requests.get(userAvatarUrl)
      img = Image.open(BytesIO(response.content)).convert('L')
      img.save('databases/Gray.png')
      embed = discord.Embed(
          title=
          f"{user.display_name}'s avatar has been converted to grayscale.")
      file = discord.File("databases/Gray.png", filename="Gray.png")
      embed.set_image(url="attachment://Gray.png")
      await ctx.respond(file=file, embed=embed)
      os.remove("databases/Gray.png")
  except AttributeError:
      await ctx.respond("You can use this command on servers only.",
                        ephemeral=True)


@bot.slash_command(name="blur", description="🖼️ Blurs an user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def blur(ctx, user: discord.Member):
  try:
      userAvatarUrl = user.avatar.url
      response = requests.get(userAvatarUrl)
      OriImage = Image.open(BytesIO(response.content))
      gaussImage = OriImage.filter(ImageFilter.GaussianBlur(7))
      gaussImage.save('databases/blur.png')
      embed = discord.Embed(
          title=f"{user.display_name}'s avatar has been blurred.")
      file = discord.File("databases/blur.png", filename="blur.png")
      embed.set_image(url="attachment://blur.png")
      await ctx.respond(file=file, embed=embed)
      os.remove("databases/blur.png")
  except AttributeError:
      await ctx.respond("You can use this command on servers only.",
                        ephemeral=True)


@bot.slash_command(name="invert",
                 description="🖼️ Inverts the colors for an user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def invert(ctx, user: discord.Member):
  try:
      userAvatarUrl = user.avatar.url
      response = requests.get(userAvatarUrl)
      im = Image.open(BytesIO(response.content))
      im_invert = PIL.ImageOps.invert(im.convert('RGB'))
      im_invert.save('databases/invert.png', quality=100)
      embed = discord.Embed(
          title=f"{user.display_name}'s avatar has been inverted.")
      file = discord.File("databases/invert.png", filename="invert.png")
      embed.set_image(url="attachment://invert.png")
      await ctx.respond(file=file, embed=embed)
      os.remove("databases/invert.png")
  except AttributeError:
      await ctx.respond("You can use this command on servers only.",
                        ephemeral=True)



@bot.slash_command(name="8ball", description="🎱 Random answers to questions.")
async def _8ball(ctx, question):
  responses = [
      "It is certain.", "It is decidedly so.", "Without a doubt.",
      "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
      "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
      "Reply hazy, try again.", "Ask again later.",
      "Better not tell you now.", "Cannot predict now.",
      "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
      "My sources say no.", "Outlook not so good.", "Very doubtful."
  ]
  await ctx.respond(
      f'`Question: {question}\nAnswer: {random.choice(responses)}`')


@bot.slash_command(name="curiosity",
                 description="💫 Info about curiosity rover from Mars.")
async def curiosity(ctx):
  async with aiohttp.ClientSession() as cs:
      async with cs.get("https://api.maas2.apollorion.com/") as r:
          qrObj = await r.json()
          em = discord.Embed(
              title="Curiosity Rover",
              description="Data from Curiosity Rover on Mars.",
              color=ctx.author.color)
          em.add_field(name='Terrestrial Date',
                       value=qrObj['terrestrial_date'])
          em.add_field(name='Martian Sols', value=qrObj['sol'])
          em.add_field(name='Season', value=qrObj['season'])
          em.add_field(name='Min Temp', value=f"{qrObj['min_temp']}°C")
          em.add_field(name='Max Temp', value=f"{qrObj['max_temp']}°C")
          em.add_field(name='Atmospheric Opacity',
                       value=qrObj['atmo_opacity'])
          em.add_field(name='Sunrise', value=qrObj['sunrise'])
          em.add_field(name='Sunset', value=qrObj['sunset'])
          em.add_field(name='UV Radiation',
                       value=qrObj['local_uv_irradiance_index'])
          em.add_field(name='Pressure', value=f"{qrObj['pressure']} Pascals")
          em.add_field(name='TimeZone of Data', value=qrObj['TZ_Data'])
          await ctx.respond(embed=em)


@bot.slash_command(name="ping", description="🏓 It tells the latency speed.")
async def ping(ctx):
  msg = await ctx.respond(f' {round(bot.latency*1000)} ms')


bot.launch_time = datetime.utcnow()


@bot.slash_command(name="stats", description="📊 Stats and info about the bot.")
async def stats(ctx):
  delta_uptime = datetime.utcnow() - bot.launch_time
  hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
  minutes, seconds = divmod(remainder, 60)
  days, hours = divmod(hours, 24)
  embed = discord.Embed(title="__Bot Info__",
                        description=f"""
```yaml
Uptime: {days}d {hours}h {minutes}m {seconds}s
```
""",
                        color=ctx.author.color)
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
      members += guild.member_count - 1
  pythonVersion = platform.python_version()
  dpyVersion = discord.__version__
  serverCount = len(bot.guilds)
  memberCount = len(set(bot.get_all_members()))
  embed.add_field(name="__Stats__",
                  value=f"""
```yaml
Users: {members}
Servers in: {servers}
```
          """,
                  inline=True)
  embed.add_field(name="__Version__",
                  value=f"""
```yaml
Python: {pythonVersion}
Pycord: {dpyVersion}
```
          """,
                  inline=True)
  await ctx.respond(embed=embed)


bot.run(os.getenv('TOKEN'))
