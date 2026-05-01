import os
import asyncio
import random
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

song_history = []

def get_spotify():
    auth = SpotifyOAuth(
        client_id=SPOTIFYID,
        client_secret=SPOTIFYSECRET,
        redirect_uri='http://127.0.0.1:8888/callback',
        scope='playlist-modify-public user-read-currently-playing'
    )
    token_info = auth.refresh_access_token(REFRESH_TOKEN)
    return spotipy.Spotify(auth=token_info['access_token'])

async def add_song_to_playlist(song_url, playlist_id):
    sp = get_spotify()
    song_id = song_url.split('track/')[1]
    song_id = song_id.split('?')[0]
    song_id = ("spotify:track:" + song_id)
    sp.playlist_add_items(playlist_id=PLAYLISTID, items=[song_id], position=None)
    track_id = song_id.split(':')[2]
    track = sp.track(track_id)
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    result = f"{track_name} by {artist_name}"
    song_history.append(result)
    return result

async def search_and_add_song(song_name, position=None):
    sp = get_spotify()
    results = sp.search(q=song_name, limit=1, type='track')
    tracks = results['tracks']['items']
    if not tracks:
        return None
    track = tracks[0]
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    song_id = "spotify:track:" + track['id']
    sp.playlist_add_items(playlist_id=PLAYLISTID, items=[song_id], position=position)
    result = f"{track_name} by {artist_name}"
    song_history.append(result)
    return result

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async def delete_user_message():
        try:
            await message.delete()
        except discord.Forbidden:
            print("Missing permissions to delete message")
        except discord.HTTPException as e:
            print(f"Failed to delete message: {e}")

    # !help
    if message.content == '!help':
        embed = discord.Embed(
            title="MuzikBot Commands 🎵",
            description="Here are all the available commands:",
            color=0x1DB954
        )
        embed.add_field(name="!next", value="Skips to the next track on Spotify", inline=False)
        embed.add_field(name="!back", value="Goes back to the previous track on Spotify", inline=False)
        embed.add_field(name="!playlist", value="Shows the link to the server playlist", inline=False)
        embed.add_field(name="!upcoming", value="Shows the next 5 songs in the playlist", inline=False)
        embed.add_field(name="!playlist stats", value="Shows the number of songs and total duration", inline=False)
        embed.add_field(name="!add [song name]", value="Adds a song to the playlist by name", inline=False)
        embed.add_field(name="!queue [song name]", value="Adds a song to the top of the playlist", inline=False)
        embed.add_field(name="!remove [song name]", value="Removes a song from the playlist by name", inline=False)
        embed.add_field(name="!search [song name]", value="Search Spotify and pick from top 5 results", inline=False)
        embed.add_field(name="!random", value="Posts a random song from the playlist", inline=False)
        embed.add_field(name="!recommend", value="Suggests a song based on the playlist", inline=False)
        embed.add_field(name="!np", value="Shows what's currently playing on Spotify", inline=False)
        embed.add_field(name="!history", value="Shows the last 5 songs added this session", inline=False)
        embed.add_field(name="Spotify link", value="Paste any Spotify track link to add it directly", inline=False)
        await message.channel.send(embed=embed)

    # !next
    elif message.content == '!next':
        sp = get_spotify()
        sp.next_track()
        embed = discord.Embed(title="⏭️ Skipped to next track!", color=0x1DB954)
        await message.channel.send(embed=embed, delete_after=10)

    # !back
    elif message.content == '!back':
        sp = get_spotify()
        sp.previous_track()
        embed = discord.Embed(title="⏮️ Going back to previous track!", color=0x1DB954)
        await message.channel.send(embed=embed, delete_after=10)
        
    # !playlist or !playlist stats
    elif message.content == '!playlist':
        await message.channel.send(f"🎵 **Our Server Playlist:**\nhttps://open.spotify.com/playlist/0eLWLQj1sKm3KZjY9x14ZC")

    elif message.content == '!playlist stats':
        sp = get_spotify()
        playlist = sp.playlist(PLAYLISTID)
        tracks = playlist['tracks']
        total_songs = tracks['total']
        total_ms = sum(item['track']['duration_ms'] for item in tracks['items'] if item['track'])
        total_minutes = total_ms // 60000
        hours = total_minutes // 60
        minutes = total_minutes % 60
        embed = discord.Embed(
            title="Playlist Stats 📊",
            color=0x1DB954
        )
        embed.add_field(name="Total Songs", value=str(total_songs), inline=True)
        embed.add_field(name="Total Duration", value=f"{hours}h {minutes}m", inline=True)
        await message.channel.send(embed=embed)

    # !upcoming
    elif message.content == '!upcoming':
        sp = get_spotify()
        playlist = sp.playlist(PLAYLISTID)
        tracks = playlist['tracks']['items']
        if not tracks:
            embed = discord.Embed(title="The playlist is empty!", color=0xFF0000)
        else:
            upcoming = tracks[:5]
            description = ""
            for i, item in enumerate(upcoming):
                track = item['track']
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                description += f"{i+1}. {track_name} — {artist_name}\n"
            embed = discord.Embed(
                title="🎵 Up Next in the Playlist",
                description=description,
                color=0x1DB954
            )
        await message.channel.send(embed=embed)

    # !add [song name]
    elif message.content.startswith('!add '):
        song_name = message.content[5:]
        await delete_user_message()
        result = await search_and_add_song(song_name)
        if result:
            embed = discord.Embed(title=f"Adding '{result}' to the playlist!", color=0x1DB954)
        else:
            embed = discord.Embed(title="Song not found on Spotify!", color=0xFF0000)
        await message.channel.send(embed=embed, delete_after=10)

    # !queue [song name]
    elif message.content.startswith('!queue '):
        song_name = message.content[7:]
        await delete_user_message()
        result = await search_and_add_song(song_name, position=0)
        if result:
            embed = discord.Embed(title=f"Added '{result}' to the top of the playlist!", color=0x1DB954)
        else:
            embed = discord.Embed(title="Song not found on Spotify!", color=0xFF0000)
        await message.channel.send(embed=embed, delete_after=10)

    # !remove [song name]
    elif message.content.startswith('!remove '):
        song_name = message.content[8:]
        await delete_user_message()
        sp = get_spotify()
        results = sp.search(q=song_name, limit=1, type='track')
        tracks = results['tracks']['items']
        if tracks:
            track = tracks[0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            song_id = "spotify:track:" + track['id']
            sp.playlist_remove_all_occurrences_of_items(playlist_id=PLAYLISTID, items=[song_id])
            embed = discord.Embed(title=f"Removed '{track_name} by {artist_name}' from the playlist!", color=0xFF0000)
        else:
            embed = discord.Embed(title="Song not found on Spotify!", color=0xFF0000)
        await message.channel.send(embed=embed, delete_after=10)

    # !search [song name]
    elif message.content.startswith('!search '):
        song_name = message.content[8:]
        await delete_user_message()
        sp = get_spotify()
        results = sp.search(q=song_name, limit=5, type='track')
        tracks = results['tracks']['items']
        if not tracks:
            embed = discord.Embed(title="No results found!", color=0xFF0000)
            await message.channel.send(embed=embed, delete_after=10)
            return

        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        description = ""
        for i, track in enumerate(tracks):
            description += f"{emojis[i]} {track['name']} — {track['artists'][0]['name']}\n"

        embed = discord.Embed(
            title=f"Search Results for '{song_name}' 🔍",
            description=description,
            color=0x1DB954
        )
        embed.set_footer(text="React with a number to add a song!")
        search_msg = await message.channel.send(embed=embed)

        for emoji in emojis[:len(tracks)]:
            await search_msg.add_reaction(emoji)

        def check(reaction, user):
            return (
                user != client.user and
                str(reaction.emoji) in emojis and
                reaction.message.id == search_msg.id
            )

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
            chosen_index = emojis.index(str(reaction.emoji))
            chosen_track = tracks[chosen_index]
            track_name = chosen_track['name']
            artist_name = chosen_track['artists'][0]['name']
            song_id = "spotify:track:" + chosen_track['id']
            sp.playlist_add_items(playlist_id=PLAYLISTID, items=[song_id], position=None)
            song_history.append(f"{track_name} by {artist_name}")
            await search_msg.delete()
            embed = discord.Embed(title=f"Adding '{track_name} by {artist_name}' to the playlist!", color=0x1DB954)
            await message.channel.send(embed=embed, delete_after=10)
        except asyncio.TimeoutError:
            await search_msg.delete()
            embed = discord.Embed(title="Search timed out — no song selected!", color=0xFF0000)
            await message.channel.send(embed=embed, delete_after=10)

    # !random
    elif message.content == '!random':
        sp = get_spotify()
        playlist = sp.playlist(PLAYLISTID)
        tracks = playlist['tracks']['items']
        if not tracks:
            embed = discord.Embed(title="The playlist is empty!", color=0xFF0000)
        else:
            random_track = random.choice(tracks)['track']
            track_name = random_track['name']
            artist_name = random_track['artists'][0]['name']
            track_url = random_track['external_urls']['spotify']
            embed = discord.Embed(
                title="🎲 Random Song from the Playlist",
                description=f"[{track_name} — {artist_name}]({track_url})",
                color=0x1DB954
            )
        await message.channel.send(embed=embed)

    # !recommend
    elif message.content == '!recommend':
        sp = get_spotify()
        playlist = sp.playlist(PLAYLISTID)
        tracks = playlist['tracks']['items']
        if not tracks:
            embed = discord.Embed(title="The playlist is empty — add some songs first!", color=0xFF0000)
            await message.channel.send(embed=embed, delete_after=10)
            return
        seed_tracks = [item['track']['id'] for item in random.sample(tracks, min(5, len(tracks)))]
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=1)
        rec_track = recommendations['tracks'][0]
        track_name = rec_track['name']
        artist_name = rec_track['artists'][0]['name']
        track_url = rec_track['external_urls']['spotify']
        embed = discord.Embed(
            title="🎵 Recommended Song",
            description=f"[{track_name} — {artist_name}]({track_url})",
            color=0x1DB954
        )
        embed.set_footer(text="Use !add or paste the link to add it to the playlist!")
        await message.channel.send(embed=embed)

    # !np
    elif message.content == '!np':
        sp = get_spotify()
        current = sp.current_user_playing_track()
        if current and current['is_playing']:
            track = current['item']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_url = track['external_urls']['spotify']
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"[{track_name} — {artist_name}]({track_url})",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(title="Nothing is playing right now!", color=0xFF0000)
        await message.channel.send(embed=embed)

    # !history
    elif message.content == '!history':
        if not song_history:
            embed = discord.Embed(title="No songs added this session yet!", color=0xFF0000)
        else:
            last_five = song_history[-5:][::-1]
            description = "\n".join(f"{i+1}. {song}" for i, song in enumerate(last_five))
            embed = discord.Embed(
                title="Recently Added Songs 📜",
                description=description,
                color=0x1DB954
            )
        await message.channel.send(embed=embed)

    # Spotify link
    elif message.content.startswith('https://open.spotify.com/track/'):
        result = await add_song_to_playlist(message.content, PLAYLISTID)
        try:
            await message.delete()
        except discord.Forbidden:
            print("Missing permissions to delete message")
        except discord.HTTPException as e:
            print(f"Failed to delete message: {e}")
        embed = discord.Embed(title=f"Adding '{result}' to the playlist!", color=0x1DB954)
        await message.channel.send(embed=embed, delete_after=10)

client.run(TOKEN)
