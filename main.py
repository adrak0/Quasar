import asyncio
import os
import platform
import random
import re
import traceback
from datetime import datetime, timezone
from io import BytesIO
from math import log

import aiohttp
import discord
import pyfiglet
import qrcode
from discord.ext import commands
from discord.ext.commands import BucketType
from dotenv import load_dotenv
from PIL import Image, ImageFilter, ImageOps

load_dotenv()

TOKEN = os.environ["TOKEN"]
OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
OWNER_IDS = {int(i) for i in os.getenv("OWNER_IDS", "").split(",") if i.strip()}

LAUNCH_API = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
APOD_PAGE = "https://apod.nasa.gov/apod/astropix.html"
MAX_MESSAGE = 2000

MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....",
    "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.",
    ")": "-.--.-", "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-", "+": ".-.-.", "-": "-....-",
    "_": "..--.-", '"': ".-..-.", "$": "...-..-", "@": ".--.-.",
}
MORSE_REVERSE = {code: char for char, code in MORSE_CODE.items()}

EIGHT_BALL = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
    "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
    "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
    "My sources say no.", "Outlook not so good.", "Very doubtful.",
]


class Quasar(discord.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.launch_time = datetime.now(timezone.utc)
        self.session = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
        return self.session

    async def fetch_json(self, url, **params):
        session = await self.get_session()
        async with session.get(url, params=params) as response:
            return await response.json(content_type=None)

    async def fetch_bytes(self, url):
        session = await self.get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()


bot = Quasar()


def owner_only():
    return commands.check(lambda ctx: ctx.author.id in OWNER_IDS)


def relative_time(iso_string):
    moment = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return f"<t:{int(moment.timestamp())}:R>"


def text_to_morse(text):
    return " ".join("/" if char == " " else MORSE_CODE.get(char.upper(), char) for char in text)


def morse_to_text(code):
    words = re.split(r"\s*/\s*|\s{3,}", code.strip())
    decoded = ("".join(MORSE_REVERSE.get(letter, "") for letter in word.split()) for word in words)
    return " ".join(word for word in decoded if word)


def image_file(image, filename):
    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    return discord.File(buffer, filename=filename)


async def respond_text(ctx, content, lang=""):
    safe = content.replace("```", "`\u200b``")
    block = f"```{lang}\n{safe}\n```"
    if len(block) <= MAX_MESSAGE:
        await ctx.respond(block)
    else:
        file = discord.File(BytesIO(content.encode()), filename="output.txt")
        await ctx.respond("The output was too long, so here it is as a file.", file=file)


async def send_avatar_edit(ctx, user, transform, title):
    user = user or ctx.author
    await ctx.defer()
    data = await bot.fetch_bytes(user.display_avatar.with_format("png").with_size(512).url)
    image = await asyncio.to_thread(lambda: transform(Image.open(BytesIO(data))))
    embed = discord.Embed(title=title.format(name=user.display_name))
    embed.set_image(url="attachment://avatar.png")
    await ctx.respond(embed=embed, file=image_file(image, "avatar.png"))


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Streaming(name="a song ❄️🔥", url="https://www.youtube.com/watch?v=OgvLej8ln2w")
    )
    print(f"Logged in as {bot.user}")


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        message = f"You're on cooldown. Try again in {error.retry_after:.1f}s."
    elif isinstance(error, discord.CheckFailure):
        message = "Only the owner of this bot can run this command."
    else:
        message = "Something went wrong while running that command."
        traceback.print_exception(type(error), error, error.__traceback__)
    await ctx.respond(message, ephemeral=True)


@bot.slash_command(name="chgsts", description="🦎 Changes status of the bot remotely (owner only).")
@owner_only()
async def change_presence(ctx, text: str):
    await bot.change_presence(activity=discord.Game(name=text), status=discord.Status.idle)
    await ctx.respond("Presence changed.", ephemeral=True)


@bot.slash_command(name="echo", description="🗣️ Repeats a message provided by a user.")
@owner_only()
async def echo(ctx, text: str, message_id: str = None):
    if message_id:
        message = await ctx.channel.fetch_message(int(message_id))
        await message.reply(text)
    else:
        await ctx.channel.send(text)
    await ctx.respond("Posted your message.", ephemeral=True)


@bot.slash_command(name="servers", description="📃 Name list of all the servers the bot is in.")
@owner_only()
async def servers(ctx):
    names = "\n".join(sorted(guild.name for guild in bot.guilds))
    await ctx.author.send(file=discord.File(BytesIO(names.encode()), filename="servers.txt"))
    await ctx.respond("The file has been sent to your DMs.", ephemeral=True)


@bot.slash_command(name="embed", description="Just for embed.")
@owner_only()
async def embed(ctx, msg: str, link: str):
    await ctx.channel.send(embed=discord.Embed(description=f"[{msg}]({link})"))
    await ctx.respond("Posted your embed.", ephemeral=True)


@bot.slash_command(name="help", description="📰 Help menu.")
async def help(ctx):
    embed = discord.Embed(
        description="Thank you for using this command as a slash command.\nㅤ\nGo ahead and hit `/` to discover all my commands!"
    )
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="privacy", description="🔏 Info about privacy policy.")
async def privacy(ctx):
    embed = discord.Embed(
        title="🔏 Privacy Policy",
        description="[We don't collect/store any user or guild data.](https://github.com/anniwth/Quasar#privacy-policy)",
    )
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name="invite", description="➕ Invite link for the bot.")
async def invite(ctx):
    url = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(2147765248),
        scopes=("bot", "applications.commands"),
    )
    await ctx.respond(f"[Add Quasar to your server!]({url})", ephemeral=True)


@bot.slash_command(name="github", description="👩‍💻 GitHub link for the bot.")
async def github(ctx):
    await ctx.respond("[Here's the link!](https://github.com/anniwth/quasar)", ephemeral=True)


@bot.slash_command(name="ping", description="🏓 It tells the latency speed.")
async def ping(ctx):
    await ctx.respond(f"{round(bot.latency * 1000)} ms")


@bot.slash_command(name="stats", description="📊 Stats and info about the bot.")
async def stats(ctx):
    uptime = datetime.now(timezone.utc) - bot.launch_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    members = sum((guild.member_count or 1) - 1 for guild in bot.guilds)

    embed = discord.Embed(
        title="__Bot Info__",
        description=f"```yaml\nUptime: {days}d {hours}h {minutes}m {seconds}s\n```",
        color=ctx.author.color,
    )
    embed.add_field(name="__Stats__", value=f"```yaml\nUsers: {members}\nServers in: {len(bot.guilds)}\n```")
    embed.add_field(
        name="__Version__",
        value=f"```yaml\nPython: {platform.python_version()}\nPycord: {discord.__version__}\n```",
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="avatar", description="📷 Fetches User Avatar.")
async def avatar(ctx, user: discord.Member = None):
    title = f"{user}'s avatar" if user else "Your avatar"
    user = user or ctx.author
    embed = discord.Embed(title=title)
    embed.set_image(url=user.display_avatar.url)
    await ctx.respond(embed=embed)


@bot.slash_command(name="gray", description="🖼️ Converts a user avatar into grayscale.")
@commands.cooldown(1, 6, BucketType.user)
async def grayscale(ctx, user: discord.Member = None):
    await send_avatar_edit(ctx, user, lambda img: img.convert("L"), "{name}'s avatar has been converted to grayscale.")


@bot.slash_command(name="blur", description="🖼️ Blurs a user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def blur(ctx, user: discord.Member = None):
    await send_avatar_edit(
        ctx, user, lambda img: img.convert("RGBA").filter(ImageFilter.GaussianBlur(7)), "{name}'s avatar has been blurred."
    )


@bot.slash_command(name="invert", description="🖼️ Inverts the colors for a user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def invert(ctx, user: discord.Member = None):
    await send_avatar_edit(ctx, user, lambda img: ImageOps.invert(img.convert("RGB")), "{name}'s avatar has been inverted.")


@bot.slash_command(name="flip", description="💸 Flips a coin randomly.")
async def flip(ctx):
    await ctx.respond(embed=discord.Embed(title="Flipping a coin... <a:flipcoin:915827162311966740>"))
    await asyncio.sleep(3)
    await ctx.edit(embed=discord.Embed(title=random.choice(["*Heads*", "*Tails*"])))


@bot.slash_command(name="8ball", description="🎱 Random answers to questions.")
async def eight_ball(ctx, question: str):
    await ctx.respond(f"`Question: {question}\nAnswer: {random.choice(EIGHT_BALL)}`")


@bot.slash_command(name="react", description="React with an emoji to a specific message.")
async def react(ctx, message_id: str, emoji: str):
    try:
        message = await ctx.channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)
    except (ValueError, discord.HTTPException):
        await ctx.respond("Couldn't add that reaction. Check the message ID and emoji.", ephemeral=True)
        return
    await ctx.respond("Your reaction has been added.", ephemeral=True)


@bot.slash_command(name="inspire", description="🐜 Sends inspirational quotes.")
async def inspire(ctx):
    data = await bot.fetch_json("https://zenquotes.io/api/random")
    await ctx.respond(f"```{data[0]['q']}\n - {data[0]['a']}```")


@bot.slash_command(name="ascii", description="🧬 Convert texts into isometric font.")
async def ascii_art(ctx, text: str):
    await respond_text(ctx, pyfiglet.figlet_format(text))


@bot.slash_command(name="reverse", description="◀️ Reverses the text form.")
async def reverse(ctx, text: str):
    await ctx.respond(f"🔁 {text[::-1]}", allowed_mentions=discord.AllowedMentions.none())


@bot.slash_command(name="mock", description="😵‍💫 Makes texts look weird.")
async def mock(ctx, text: str):
    mocked = "".join(random.choice((str.upper, str.lower))(char) for char in text)
    await ctx.respond(discord.utils.escape_markdown(mocked)[:MAX_MESSAGE], allowed_mentions=discord.AllowedMentions.none())


@bot.slash_command(name="qrcode", description="🐉 Generates a QR for a specific text.")
@commands.cooldown(1, 5, BucketType.user)
async def qr(ctx, text: str):
    embed = discord.Embed()
    embed.set_image(url="attachment://QR.png")
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.channel.send(file=image_file(qrcode.make(text), "QR.png"), embed=embed, silent=True)
    await ctx.respond("Posted your QR code.", ephemeral=True)


@bot.slash_command(name="morse", description="🧮 Converts the text into Morse code.")
async def morse(ctx, text: str):
    await respond_text(ctx, text_to_morse(text), "yaml")


@bot.slash_command(name="unmorse", description="🧮 Converts a morse code into text.")
async def unmorse(ctx, content: str):
    decoded = morse_to_text(content)
    if not decoded:
        await ctx.respond("There were no valid morse chars in the passed content.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="morsetable", description="📊 Look-up for the morse code table.")
async def morsetable(ctx, num_per_row: int = 5):
    per_row = max(1, min(num_per_row, 8))
    entries = [f"{char} : {code}" for char, code in sorted(MORSE_CODE.items()) if char.isalnum()]
    width = max(map(len, entries))
    rows = ["  ".join(entry.ljust(width) for entry in entries[i:i + per_row]) for i in range(0, len(entries), per_row)]
    await ctx.respond("__**Morse Code Lookup Table:**__\n```\n" + "\n".join(rows) + "\n```")


@bot.slash_command(name="texttohex", description="🧮 Convert texts into hexadecimal.")
async def texttohex(ctx, text: str):
    await respond_text(ctx, " ".join(f"{ord(char):02x}" for char in text), "fix")


@bot.slash_command(name="hextotext", description="🧮 Converts hexadecimal to a text.")
async def hextotext(ctx, text: str):
    try:
        decoded = bytes.fromhex(text).decode()
    except ValueError as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="texttobinary", description="🧮 Converts text into binary numbers.")
async def texttobinary(ctx, text: str):
    await respond_text(ctx, " ".join(f"{ord(char):08b}" for char in text), "fix")


@bot.slash_command(name="binarytotext", description="🧮 Converts binary numbers into a text.")
async def binarytotext(ctx, text: str):
    try:
        decoded = "".join(chr(int(chunk, 2)) for chunk in text.split())
    except (ValueError, OverflowError) as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="weather", description="☁️ Forecast for a specific location.")
@commands.cooldown(1, 2, BucketType.user)
async def weather(ctx, location: str):
    await ctx.defer(ephemeral=True)
    data = await bot.fetch_json(
        "https://api.openweathermap.org/data/2.5/weather",
        q=location,
        appid=OPENWEATHER_API_KEY,
        units="metric",
    )
    if str(data.get("cod")) != "200":
        await ctx.respond(f"`{data.get('message', 'Unknown error')}`", ephemeral=True)
        return

    main = data["main"]
    embed = discord.Embed(
        title=f"Forecast for {data['name']}",
        description=f"**{data['weather'][0]['description'].capitalize()}**",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Temperature", value=f"{main['temp']} °C")
    embed.add_field(name="Feels like", value=f"{main['feels_like']} °C")
    embed.add_field(name="Humidity", value=f"{main['humidity']} %", inline=False)
    embed.add_field(name="Pressure", value=f"{main['pressure']} hPa", inline=False)
    embed.add_field(name="Sunrise", value=f"<t:{data['sys']['sunrise']}:R>")
    embed.add_field(name="Sunset", value=f"<t:{data['sys']['sunset']}:R>")
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.channel.send(embed=embed, silent=True)
    await ctx.respond("Posted the weather.", ephemeral=True)


@bot.slash_command(name="apod", description="🌌 Astronomy Picture of the Day.")
async def apod(ctx):
    await ctx.defer()
    data = await bot.fetch_json("https://api.nasa.gov/planetary/apod", api_key=NASA_API_KEY)
    embed = discord.Embed(title=f"🔭 APOD of {data['date']}", color=discord.Color.purple())
    embed.add_field(name=data["title"], value=f"{data['explanation'][:900]}...\n[Learn more]({APOD_PAGE})")

    image = data.get("hdurl") or (data.get("url") if data.get("media_type") == "image" else None)
    if image:
        embed.set_image(url=image)
    else:
        embed.add_field(name="Discord doesn't support video URLs.", value=f"[Click here to view it.]({APOD_PAGE})", inline=False)

    embed.set_footer(text="The API refreshes once every 24 hours.")
    await ctx.respond(embed=embed)


@bot.slash_command(name="epic", description="🌎 DSCOVR's view of planet earth.")
async def epic(ctx):
    await ctx.defer()
    data = await bot.fetch_json("https://api.nasa.gov/EPIC/api/natural", api_key=NASA_API_KEY)
    latest = data[0]
    date_path = latest["date"].split()[0].replace("-", "/")
    embed = discord.Embed(
        title="EPIC (Earth Polychromatic Imaging Camera)",
        description=(
            "Uniquely positioned at the Earth-Sun Lagrange point, EPIC provides full disc imagery of the Earth "
            "and captures unique perspectives of certain astronomical events such as lunar transits using a "
            "2048x2048 pixel CCD (Charge Coupled Device) detector coupled to a 30-cm aperture Cassegrain telescope."
        ),
    )
    embed.add_field(name="Date", value=latest["date"], inline=False)
    embed.set_image(url=f"https://epic.gsfc.nasa.gov/archive/natural/{date_path}/png/{latest['image']}.png")
    await ctx.respond(embed=embed)


@bot.slash_command(name="rover", description="🪐 Images taken by curiosity rover on Mars.")
async def rover(ctx):
    await ctx.defer()
    data = await bot.fetch_json(
        "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos", sol=1000, api_key=NASA_API_KEY
    )
    photos = data.get("photos") or []
    if not photos:
        await ctx.respond("No rover photos are available right now.")
        return
    embed = discord.Embed(title="📸 Image taken by Curiosity Rover on Mars.", color=ctx.author.color)
    embed.set_image(url=random.choice(photos)["img_src"])
    await ctx.respond(embed=embed)


@bot.slash_command(name="curiosity", description="💫 Info about curiosity rover from Mars.")
async def curiosity(ctx):
    await ctx.defer()
    data = await bot.fetch_json("https://api.maas2.apollorion.com/")
    fields = {
        "Terrestrial Date": data["terrestrial_date"],
        "Martian Sols": data["sol"],
        "Season": data["season"],
        "Min Temp": f"{data['min_temp']}°C",
        "Max Temp": f"{data['max_temp']}°C",
        "Atmospheric Opacity": data["atmo_opacity"],
        "Sunrise": data["sunrise"],
        "Sunset": data["sunset"],
        "UV Radiation": data["local_uv_irradiance_index"],
        "Pressure": f"{data['pressure']} Pascals",
        "TimeZone of Data": data["TZ_Data"],
    }
    embed = discord.Embed(title="Curiosity Rover", description="Data from Curiosity Rover on Mars.", color=ctx.author.color)
    for name, value in fields.items():
        embed.add_field(name=name, value=value)
    await ctx.respond(embed=embed)


@bot.slash_command(name="deltav", description="👨‍🔬 Calculate DeltaV.")
async def deltav(ctx, engineimpulse: float, wetmass: float, drymass: float):
    if drymass <= 0 or wetmass <= drymass:
        await ctx.respond("Wet mass must be greater than dry mass, and both must be positive.", ephemeral=True)
        return
    dv = engineimpulse * 9.80665 * log(wetmass / drymass)
    embed = discord.Embed(
        title="🚀 DeltaV (Ideal Rocket Equation)",
        description=(
            "DeltaV is the maximum change of velocity of the vehicle (with no external forces acting). It is a "
            "measure of the impulse per unit of spacecraft mass needed to perform a maneuver such as launching "
            "from or landing on a planet or moon, or an in-space orbital maneuver.\nㅤ\n"
            "Equation: [ΔV = Isp × g₀ × ln(WetMass / DryMass)](https://en.wikipedia.org/wiki/Tsiolkovsky_rocket_equation)"
        ),
    )
    embed.add_field(name="Results", value=f"{int(dv)} m/s")
    embed.set_image(url="https://c.tenor.com/YKLoTukF75UAAAAC/spacex-falcon9.gif")
    await ctx.respond(embed=embed)


@bot.slash_command(name="iss", description="🛰️ Coordinates for International Space Station.")
async def iss(ctx):
    data = await bot.fetch_json("http://api.open-notify.org/iss-now.json")
    position = data["iss_position"]
    embed = discord.Embed(
        title="🛰 Current position for ISS",
        description="Coordinates for International Space Station.",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Latitude", value=position["latitude"])
    embed.add_field(name="Longitude", value=position["longitude"])
    embed.add_field(name="TimeStamp", value=f"<t:{data['timestamp']}:R>")
    embed.add_field(name="Live Tracker", value="http://www.isstracker.com/")
    embed.set_image(
        url="https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/spacestation_images/international2520space2520station_image_20190220215716.jpeg"
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="astronauts", description="👩‍🚀 People outside our atmosphere.")
async def astronauts(ctx):
    data = await bot.fetch_json("http://api.open-notify.org/astros.json")
    crew = "\n".join(f"{person['name']} : {person['craft']}" for person in data["people"])
    embed = discord.Embed(
        title="👩‍🚀 Astronauts currently in space.",
        description="People who are currently outside our atmosphere.",
        color=ctx.author.color,
    )
    embed.add_field(name="Names and Crafts.", value=f"```yaml\n{crew}\n```")
    await ctx.respond(embed=embed)


@bot.slash_command(name="nextlaunch", description="🚀 Detailed info about the next rocket launch.")
async def nextlaunch(ctx):
    await ctx.defer()
    data = await bot.fetch_json(LAUNCH_API, format="json", limit=1)
    launch = data["results"][0]
    mission = launch.get("mission") or {}
    orbit = (mission.get("orbit") or {}).get("name") or "No orbit was provided."

    embed = discord.Embed(
        title=f"🚀 {launch['name']}",
        description=mission.get("description") or "No description was provided.",
    )
    embed.add_field(name="Start Window", value=f"Launch window: {relative_time(launch['window_start'])}")
    embed.add_field(name="End Window", value=f"Launch window: {relative_time(launch['window_end'])}")
    embed.add_field(name="Orbit", value=orbit)
    embed.add_field(name="Agency", value=launch["launch_service_provider"]["name"])
    embed.add_field(name="Location", value=launch["pad"]["location"]["name"])
    embed.add_field(name="Co-ordinates", value=f"[Google Maps]({launch['pad']['map_url']})")
    if launch.get("image"):
        embed.set_image(url=launch["image"])
    await ctx.respond(embed=embed)


@bot.slash_command(name="launches", description="☄️ Info about upcoming rocket launches.")
async def launches(ctx):
    await ctx.defer()
    data = await bot.fetch_json(LAUNCH_API, format="json", limit=10)
    embed = discord.Embed(title="🚀 Upcoming launches")
    for launch in data["results"][:10]:
        embed.add_field(
            name=launch["name"],
            value=f"Launch window: {relative_time(launch['window_start'])}",
            inline=False,
        )
    await ctx.respond(embed=embed)


bot.run(TOKEN)
