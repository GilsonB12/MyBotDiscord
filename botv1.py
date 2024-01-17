import discord
from discord.ext import commands
from pytube import YouTube

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
voice_channels = {}

@bot.event
async def on_ready():
    print(f'{bot.user} está conectado ao Discord!')

@bot.command(name='play', help='Reproduz uma música do YouTube.')
async def play(ctx, url):
    global voice_channels

    channel = ctx.author.voice.channel

    if channel is None:
        await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
        return

    if channel.guild.id not in voice_channels:
        try:
            voice_channels[channel.guild.id] = await channel.connect()
        except Exception as e:
            print(f"Erro ao conectar ao canal de voz: {e}")
            return

    voice_channel = voice_channels[channel.guild.id]

    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    download_path = video.download()

    ffmpeg_options = {
        'options': '-bufsize 64k'
    }

    voice_channel.play(discord.FFmpegPCMAudio(download_path, **ffmpeg_options), after=lambda e: print('done', e))
    await ctx.send(f"Tocando: {yt.title}")

@bot.command(name='leave', help='Desconecta o bot do canal de voz.')
async def leave(ctx):
    global voice_channels

    channel = ctx.author.voice.channel

    if channel.guild.id in voice_channels:
        voice_channel = voice_channels[channel.guild.id]
        if voice_channel.is_connected():
            await voice_channel.disconnect()
            del voice_channels[channel.guild.id]
        else:
            await ctx.send("O bot não está em um canal de voz.")
    else:
        await ctx.send("O bot não está em um canal de voz.")

bot.run('TOKEN_BOT')