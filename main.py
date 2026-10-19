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

STAR_CHANNEL_IDS = {1164082942109290676, 1172907782765297747, 1172431577184206899}
STAR_EMOJI = "⭐"

STREAM_NAME = "a song ❄️🔥"
STREAM_URL = "https://www.youtube.com/watch?v=2Q9MqL83FeE"

APOD_URL = "https://api.nasa.gov/planetary/apod"
APOD_PAGE = "https://apod.nasa.gov/apod/astropix.html"
ASTROS_URL = "http://api.open-notify.org/astros.json"
CURIOSITY_URL = "https://api.maas2.apollorion.com/"
EPIC_URL = "https://api.nasa.gov/EPIC/api/natural"
EPIC_ARCHIVE = "https://epic.gsfc.nasa.gov/archive/natural"
ISS_URL = "http://api.open-notify.org/iss-now.json"
LAUNCH_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
MARS_PHOTOS_URL = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
QUOTE_URL = "https://zenquotes.io/api/random"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

DELTAV_GIF = "https://c.tenor.com/YKLoTukF75UAAAAC/spacex-falcon9.gif"
FLIP_EMOJI = "<a:flipcoin:915827162311966740>"
ISS_IMAGE = "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/spacestation_images/international2520space2520station_image_20190220215716.jpeg"
PRIVACY_URL = "https://github.com/anniwth/Quasar#privacy-policy"

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
        super().__init__(
            intents=discord.Intents.default(),
            default_command_integration_types={
                discord.IntegrationType.guild_install,
                discord.IntegrationType.user_install,
            },
        )
        self.launch_time = datetime.now(timezone.utc)
        self.session = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        return self.session

    async def fetch_json(self, url, params=None, check=True):
        session = await self.get_session()
        async with session.get(url, params=params) as response:
            if check:
                response.raise_for_status()
            return await response.json(content_type=None)

    async def fetch_bytes(self, url, retries=1):
        session = await self.get_session()
        for attempt in range(1, retries + 1):
            async with session.get(url) as response:
                if response.status == 200 or attempt == retries:
                    response.raise_for_status()
                    return await response.read()
            await asyncio.sleep(2)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()


bot = Quasar()


def owner_only():
    return commands.check(lambda ctx: ctx.author.id == OWNER_ID)


def dig(data, *keys, default=None):
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key)
    return default if data is None or data == "" else data


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


async def respond_text(ctx, content, lang="", code=True):
    if code:
        safe = content.replace("```", "`\u200b``")
        message = f"```{lang}\n{safe}\n```"
    else:
        message = content

    if len(message) <= MAX_MESSAGE:
        await ctx.respond(message, allowed_mentions=discord.AllowedMentions.none())
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
    await bot.change_presence(activity=discord.Streaming(name=STREAM_NAME, url=STREAM_URL))
    print(f"Bot is ready! Logged in as {bot.user}")
    print(f"Watching channels: {', '.join(map(str, STAR_CHANNEL_IDS))}")


@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id not in STAR_CHANNEL_IDS:
        return
    try:
        await message.add_reaction(STAR_EMOJI)
    except discord.HTTPException as e:
        print(f"Failed to add reaction in channel {message.channel.id}: {e}")


@bot.event
async def on_application_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, commands.CommandOnCooldown):
        message = f"You're on cooldown. Try again in {error.retry_after:.1f}s."
    elif isinstance(error, discord.CheckFailure):
        message = "You are not authorized to use this command."
    elif isinstance(error, aiohttp.ClientResponseError):
        message = f"The API returned an error ({error.status}). Please try again later."
    elif isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError)):
        message = "I'm having trouble reaching that API right now. Please try again later."
    else:
        message = "Something went wrong while running that command."
        traceback.print_exception(type(error), error, error.__traceback__)
    try:
        await ctx.respond(message, ephemeral=True)
    except discord.HTTPException:
        pass


@bot.slash_command(name="deletedm", description="🗑️ Deletes a specific message in the bot's DM by its ID.")
@owner_only()
async def deletedm(ctx, message_id: str):
    try:
        channel = await ctx.author.create_dm()
        message = await channel.fetch_message(int(message_id))
        await message.delete()
    except ValueError:
        await ctx.respond("Invalid message ID format. Please provide a valid numeric ID.", ephemeral=True)
    except discord.NotFound:
        await ctx.respond("Message not found. Ensure the ID is correct and it is located in the DM.", ephemeral=True)
    except discord.Forbidden:
        await ctx.respond("I can only delete my own messages in DMs.", ephemeral=True)
    else:
        await ctx.respond(f"Successfully deleted message `{message_id}` from DMs.", ephemeral=True)


@bot.slash_command(name="echo", description="🗣️ Repeats a message provided by a user.")
@owner_only()
async def echo(ctx, text: str, message_id: str = None):
    if message_id:
        message = await ctx.channel.fetch_message(int(message_id))
        await message.reply(text)
    else:
        await ctx.channel.send(text)
    await ctx.respond("Posted your message.", ephemeral=True)


@bot.slash_command(name="embed", description="Just for embed.")
@owner_only()
async def send_embed(ctx, msg: str, link: str):
    await ctx.channel.send(embed=discord.Embed(description=f"[{msg}]({link})"))
    await ctx.respond("Posted your embed.", ephemeral=True)


@bot.slash_command(name="servers", description="📃 Name list of all the servers the bot is in.")
@owner_only()
async def servers(ctx):
    names = "\n".join(sorted(guild.name for guild in bot.guilds))
    await ctx.author.send(file=discord.File(BytesIO(names.encode()), filename="servers.txt"))
    await ctx.respond("The file has been sent to your DMs.", ephemeral=True)


@bot.slash_command(name="avatar", description="📷 Fetches User Avatar.")
async def avatar(ctx, user: discord.Member = None):
    target = user or ctx.author
    embed = discord.Embed(title=f"{target}'s avatar" if user else "Your avatar")
    embed.set_image(url=target.display_avatar.url)
    await ctx.respond(embed=embed)


@bot.slash_command(name="ping", description="🏓 It tells the latency speed.")
async def ping(ctx):
    await ctx.respond(f"{round(bot.latency * 1000)} ms")


@bot.slash_command(name="privacy", description="🔏 Info about privacy policy.")
async def privacy(ctx):
    embed = discord.Embed(
        title="🔏 Privacy Policy",
        description=f"[I don't collect/store any user or guild data.]({PRIVACY_URL})",
    )
    await ctx.respond(embed=embed, ephemeral=True)


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


@bot.slash_command(name="weather", description="☁️ Forecast for a specific location.")
@commands.cooldown(1, 2, BucketType.user)
async def weather(ctx, location: str):
    data = await bot.fetch_json(
        WEATHER_URL,
        {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        check=False,
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
    await ctx.respond(embed=embed)


@bot.slash_command(name="8ball", description="🎱 Random answers to questions.")
async def eight_ball(ctx, question: str):
    await ctx.respond(
        f"`Question: {question}\nAnswer: {random.choice(EIGHT_BALL)}`",
        allowed_mentions=discord.AllowedMentions.none(),
    )


@bot.slash_command(name="flip", description="💸 Flips a coin randomly.")
async def flip(ctx):
    await ctx.respond(embed=discord.Embed(title=f"Flipping a coin... {FLIP_EMOJI}"))
    await asyncio.sleep(3)
    await ctx.edit(embed=discord.Embed(title=random.choice(["*Heads*", "*Tails*"])))


@bot.slash_command(name="inspire", description="🐜 Sends inspirational quotes.")
async def inspire(ctx):
    data = await bot.fetch_json(QUOTE_URL)
    await ctx.respond(f"```{data[0]['q']}\n - {data[0]['a']}```")


@bot.slash_command(name="mock", description="😵‍💫 Makes texts look weird.")
async def mock(ctx, text: str):
    mocked = "".join(random.choice((str.upper, str.lower))(char) for char in text)
    await respond_text(ctx, discord.utils.escape_markdown(mocked), code=False)


@bot.slash_command(name="react", description="React with an emoji to a specific message.")
async def react(ctx, message_id: str, emoji: str):
    try:
        message = await ctx.channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)
    except (ValueError, discord.HTTPException):
        await ctx.respond("There was some error, please check the details before you enter.", ephemeral=True)
        return
    await ctx.respond("Your reaction has been added.", ephemeral=True)


@bot.slash_command(name="reverse", description="◀️ Reverses the text form.")
async def reverse(ctx, text: str):
    await respond_text(ctx, f"🔁 {text[::-1]}", code=False)


@bot.slash_command(name="ascii", description="🧬 Convert texts into isometric font.")
async def ascii_art(ctx, text: str):
    await respond_text(ctx, pyfiglet.figlet_format(text))


@bot.slash_command(name="binarytotext", description="🧮 Converts binary numbers into a text.")
async def binarytotext(ctx, text: str):
    try:
        decoded = "".join(chr(int(chunk, 2)) for chunk in text.split())
    except (ValueError, OverflowError) as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="hextotext", description="🧮 Converts hexadecimal to a text.")
async def hextotext(ctx, text: str):
    try:
        decoded = bytes.fromhex(text).decode()
    except ValueError as e:
        await ctx.respond(f"Error: `{e}`.\nThis probably means the text is malformed.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="morse", description="🧮 Converts the text into Morse code.")
async def morse(ctx, text: str):
    await respond_text(ctx, text_to_morse(text), "yaml")


@bot.slash_command(name="morsetable", description="📊 Look-up for the morse code table.")
async def morsetable(ctx, num_per_row: int = 5):
    per_row = max(1, min(num_per_row, 8))
    entries = [f"{char} : {code}" for char, code in sorted(MORSE_CODE.items()) if char.isalnum()]
    width = max(map(len, entries))
    rows = ["  ".join(entry.ljust(width) for entry in entries[i:i + per_row]) for i in range(0, len(entries), per_row)]
    await ctx.respond("__**Morse Code Lookup Table:**__\n```\n" + "\n".join(rows) + "\n```")


@bot.slash_command(name="qrcode", description="🐉 Generates a QR for a specific text.")
@commands.cooldown(1, 5, BucketType.user)
async def qr(ctx, text: str):
    embed = discord.Embed()
    embed.set_image(url="attachment://QR.png")
    await ctx.respond(embed=embed, file=image_file(qrcode.make(text), "QR.png"))


@bot.slash_command(name="texttobinary", description="🧮 Converts text into binary numbers.")
async def texttobinary(ctx, text: str):
    await respond_text(ctx, " ".join(f"{ord(char):08b}" for char in text), "fix")


@bot.slash_command(name="texttohex", description="🧮 Convert texts into hexadecimal.")
async def texttohex(ctx, text: str):
    await respond_text(ctx, " ".join(f"{ord(char):02x}" for char in text), "fix")


@bot.slash_command(name="unmorse", description="🧮 Converts a morse code into text.")
async def unmorse(ctx, content: str):
    decoded = morse_to_text(content)
    if not decoded:
        await ctx.respond("There were no valid morse chars in the passed content.", ephemeral=True)
        return
    await respond_text(ctx, decoded)


@bot.slash_command(name="blur", description="🖼️ Blurs a user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def blur(ctx, user: discord.Member = None):
    await send_avatar_edit(
        ctx, user, lambda img: img.convert("RGBA").filter(ImageFilter.GaussianBlur(7)), "{name}'s avatar has been blurred."
    )


@bot.slash_command(name="gray", description="🖼️ Converts a user avatar into grayscale.")
@commands.cooldown(1, 6, BucketType.user)
async def grayscale(ctx, user: discord.Member = None):
    await send_avatar_edit(ctx, user, lambda img: img.convert("L"), "{name}'s avatar has been converted to grayscale.")


@bot.slash_command(name="invert", description="🖼️ Inverts the colors for a user avatar.")
@commands.cooldown(1, 6, BucketType.user)
async def invert(ctx, user: discord.Member = None):
    await send_avatar_edit(ctx, user, lambda img: ImageOps.invert(img.convert("RGB")), "{name}'s avatar has been inverted.")


@bot.slash_command(name="apod", description="🌌 Astronomy Picture of the Day.")
async def apod(ctx):
    await ctx.defer()
    data = await bot.fetch_json(APOD_URL, {"api_key": NASA_API_KEY})
    embed = discord.Embed(title=f"🔭 APOD of {data['date']}", color=discord.Color.purple())
    embed.add_field(name=data["title"], value=f"{data['explanation'][:900]}...\n[Learn more]({APOD_PAGE})")

    image = data.get("hdurl") or (data.get("url") if data.get("media_type") == "image" else None)
    if image:
        embed.set_image(url=image)
    else:
        embed.add_field(name="Discord doesn't support video URLs.", value=f"[Click here to view it.]({APOD_PAGE})", inline=False)

    embed.set_footer(text="The API refreshes once every 24 hours.")
    await ctx.respond(embed=embed)


@bot.slash_command(name="astronauts", description="👩‍🚀 People outside our atmosphere.")
async def astronauts(ctx):
    data = await bot.fetch_json(ASTROS_URL)
    crew = "\n".join(f"{person['name']} : {person['craft']}" for person in data["people"])
    embed = discord.Embed(
        title="👩‍🚀 Astronauts currently in space.",
        description="People who are currently outside our atmosphere.",
        color=ctx.author.color,
    )
    embed.add_field(name="Names and Crafts.", value=f"```yaml\n{crew}\n```")
    await ctx.respond(embed=embed)


@bot.slash_command(name="curiosity", description="💫 Info about curiosity rover from Mars.")
async def curiosity(ctx):
    await ctx.defer()
    data = await bot.fetch_json(CURIOSITY_URL)
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
    embed.set_image(url=DELTAV_GIF)
    await ctx.respond(embed=embed)


@bot.slash_command(name="epic", description="🌎 DSCOVR's view of planet earth.")
async def epic(ctx):
    await ctx.defer()
    data = await bot.fetch_json(EPIC_URL, {"api_key": NASA_API_KEY})
    if not data:
        await ctx.respond("NASA's EPIC API returned no images at the moment. Please try again later.")
        return

    latest = data[0]
    date_path = latest["date"].split()[0].replace("-", "/")
    try:
        image = await bot.fetch_bytes(f"{EPIC_ARCHIVE}/{date_path}/png/{latest['image']}.png", retries=3)
    except aiohttp.ClientError:
        await ctx.respond("I found the latest image data, but couldn't download the image from NASA. Please try again in a moment.")
        return

    embed = discord.Embed(
        title="EPIC (Earth Polychromatic Imaging Camera)",
        description="Uniquely positioned at the Earth-Sun Lagrange point, EPIC provides full disc imagery of the Earth...",
        color=discord.Color.dark_blue(),
    )
    embed.add_field(name="Image Captured On", value=f"{latest['date']} UTC", inline=False)
    embed.set_image(url="attachment://epic.png")
    embed.set_footer(text="Image courtesy of NASA EPIC team.")
    await ctx.respond(embed=embed, file=discord.File(BytesIO(image), filename="epic.png"))


@bot.slash_command(name="iss", description="🛰️ Coordinates for International Space Station.")
async def iss(ctx):
    data = await bot.fetch_json(ISS_URL)
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
    embed.set_image(url=ISS_IMAGE)
    await ctx.respond(embed=embed)


@bot.slash_command(name="launches", description="☄️ Info about upcoming rocket launches.")
async def launches(ctx):
    await ctx.defer()
    data = await bot.fetch_json(LAUNCH_URL, {"format": "json", "limit": 10})
    results = data.get("results")
    if not results:
        await ctx.respond("I couldn't find any upcoming launches at the moment.")
        return

    embed = discord.Embed(title="🚀 Top 10 Upcoming Launches", color=discord.Color.blue())
    for launch in results[:10]:
        start = launch.get("window_start")
        embed.add_field(
            name=launch.get("name", "Name not available"),
            value=f"Launch window: {relative_time(start)}" if start else "Launch time not available.",
            inline=False,
        )
    await ctx.respond(embed=embed)


@bot.slash_command(name="nextlaunch", description="🚀 Detailed info about the next rocket launch.")
async def nextlaunch(ctx):
    await ctx.defer()
    data = await bot.fetch_json(LAUNCH_URL, {"format": "json", "limit": 1})
    results = data.get("results")
    if not results:
        await ctx.respond("I couldn't find any upcoming launches at the moment.")
        return

    launch = results[0]
    map_url = dig(launch, "pad", "map_url")
    embed = discord.Embed(
        title=f"🚀 {dig(launch, 'name', default='N/A')}",
        description=dig(launch, "mission", "description", default="No description provided."),
        color=discord.Color.green(),
    )
    if launch.get("window_start"):
        embed.add_field(name="Start Window", value=relative_time(launch["window_start"]))
    if launch.get("window_end"):
        embed.add_field(name="End Window", value=relative_time(launch["window_end"]))
    embed.add_field(name="Orbit", value=dig(launch, "mission", "orbit", "name", default="N/A"))
    embed.add_field(name="Agency", value=dig(launch, "launch_service_provider", "name", default="N/A"))
    embed.add_field(name="Location", value=dig(launch, "pad", "location", "name", default="N/A"))
    embed.add_field(name="Coordinates", value=f"[Google Maps]({map_url})" if map_url else "Not Available")
    if launch.get("image"):
        embed.set_image(url=launch["image"])
    await ctx.respond(embed=embed)


@bot.slash_command(name="rover", description="🪐 Images taken by curiosity rover on Mars.")
async def rover(ctx):
    await ctx.defer()
    data = await bot.fetch_json(MARS_PHOTOS_URL, {"sol": 1000, "api_key": NASA_API_KEY})
    photos = data.get("photos") or []
    if not photos:
        await ctx.respond("No rover photos are available right now.")
        return
    embed = discord.Embed(title="📸 Image taken by Curiosity Rover on Mars.", color=ctx.author.color)
    embed.set_image(url=random.choice(photos)["img_src"])
    await ctx.respond(embed=embed)
bot.run(TOKEN)
