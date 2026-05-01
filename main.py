import os
import asyncio
import discord
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SPOTIFYID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFYSECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
PLAYLISTID = os.getenv('SPOTIFY_PLAYLIST_ID')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')
PLAYLIST_URL = f"https://open.spotify.com/playlist/{PLAYLISTID}"

intents = discord.Intents.all()
client = discord.Client(intents=intents)

async def add_song_to_playlist(song_url, playlist_id):
    auth = SpotifyOAuth(
        client_id=SPOTIFYID,
        client_secret=SPOTIFYSECRET,
        redirect_uri='http://127.0.0.1:8888/callback',
        scope='playlist-modify-public'
    )
    token_info = auth.refresh_access_token(REFRESH_TOKEN)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    song_id = song_url.split('track/')[1]
    song_id = song_id.split('?')[0]
    song_id = ("spotify:track:" + song_id)
    print(song_id)

    sp.playlist_add_items(playlist_id=PLAYLISTID, items=[song_id], position=None)

    track_id = song_id.split(':')[2]
    track = sp.track(track_id)
    track_name = track['name']
    print(track_name)
    return track_name

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!playlist':
        embed = discord.Embed(
            title="Our Server Playlist 🎵",
            description="Click below to open and add songs!",
            color=0x1DB954
        )
        embed.add_field(
            name="Open Playlist",
            value=f"[Click here to open on Spotify]({PLAYLIST_URL})"
        )
        embed.set_footer(text="Add songs by pasting a Spotify track link in this channel")
        await message.channel.send(embed=embed)

    if message.content.startswith('https://open.spotify.com/track/'):
        track_name = await add_song_to_playlist(message.content, PLAimport os
import asyncio
import discord
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SPOTIFYID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFYSECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
PLAYLISTID = os.getenv('SPOTIFY_PLAYLIST_ID')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')
PLAYLIST_URL = f"https://open.spotify.com/playlist/{PLAYLISTID}"

intents = discord.Intents.all()
client = discord.Client(intents=intents)

async def add_song_to_playlist(song_url, playlist_id):
    auth = SpotifyOAuth(
        client_id=SPOTIFYID,
        client_secret=SPOTIFYSECRET,
        redirect_uri='http://127.0.0.1:8888/callback',
        scope='playlist-modify-public'
    )

    token_info = auth.refresh_access_token(REFRESH_TOKEN)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    song_id = song_url.split('track/')[1]
    song_id = song_id.split('?')[0]
    song_id = ("spotify:track:" + song_id)
    print(song_id)

    sp.playlist_add_items(playlist_id=PLAYLISTID, items=[song_id], position=None)

    track_id = song_id.split(':')[2]
    track = sp.track(track_id)
    track_name = track['name']
    print(track_name)
    return track_name

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!playlist':
        embed = discord.Embed(
            title="Our Server Playlist 🎵",
            description="Click below to open and add songs!",
            color=0x1DB954
        )
        embed.add_field(
            name="Open Playlist",
            value=f"[Click here to open on Spotify]({PLAYLIST_URL})"
        )
        embed.set_footer(text="Add songs by pasting a Spotify track link in this channel")
        await message.channel.send(embed=embed)

if message.content.startswith('https://open.spotify.com/track/'):
    track_name = await add_song_to_playlist(message.content, PLAYLISTID)
    try:
        await message.delete()
    except discord.Forbidden:
        print("Missing permissions to delete message")
    except discord.HTTPException as e:
        print(f"Failed to delete message: {e}")
    embed = discord.Embed(
        title=f"Adding '{track_name}' to the playlist!",
        color=0x1DB954
    )
    await message.channel.send(embed=embed, delete_after=10)

client.run(TOKEN)
