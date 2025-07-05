import discord
import os
import random 
import requests
import json
from discord.ext import commands
from main import climate_words
from main import GameSession
from main import get_wordle_feedback

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

STATS_FILE = "stats.json"

def merge_duplicate_stats():
    cleaned_stats = {}
    for user_id, stats in player_stats.items():
        uid = str(user_id)
        if uid not in cleaned_stats:
            cleaned_stats[uid] = {"wins": 0, "losses": 0}
        cleaned_stats[uid]["wins"] += stats.get("wins", 0)
        cleaned_stats[uid]["losses"] += stats.get("losses", 0)
    return cleaned_stats

# Try to load stats from file when bot starts
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r") as f:
        player_stats = json.load(f)
    player_stats = merge_duplicate_stats()
else:
    player_stats = {}

games = {}

def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump(player_stats, f)

def start_new_game(user_id, ctx):
    word, info = random.choice(list(climate_words.items()))
    session = GameSession(word)
    games[user_id] = session

    return (
        f"🌍 Let's play Climate Wordle!\n"
        f"**Topic:** {info['topic']}\n"
        f"Your word has {len(word)} letters: `{' '.join(session.display)}`\n"
        f"Type your guess using `$guess <word>`.\n"
        f"🟩 = Letter is in the word and in the correct position.\n"
        f"🟨 = Letter is in the word but in the wrong position.\n"
        f"⬜️ = Letter is not in the word.\n"
    )


@bot.command()
async def climatewordle(ctx):
    user_id = str(ctx.author.id)

    if user_id in games:
        await ctx.send("🟡 You already have an active game! Finish it or use `$giveup` if you're stuck.")
        return

    message = start_new_game(user_id, ctx)
    await ctx.send(message)


@bot.command()
async def guess(ctx, *, user_input: str):
    """Handle user guesses."""
    user_id = str(ctx.author.id)
    session = games.get(user_id)

    if not session:
        await ctx.send("❗ You don't have an active game. Start one using `$climatewordle`.")
        return
    
    if len(user_input) != len(session.word):
        await ctx.send(f"❗ Your guess must be exactly {len(session.word)} letters long.")
        return

    if session.guess(user_input):
        await ctx.send(
            f"✅ Correct! The word was `{session.word}`.\n"
            f"**How this helps the climate:** {climate_words[session.word]['explanation']} \n"
            f"Type $playagain to keep playing!"
        )
        # Ambil ID pemain
        user_id = str(ctx.author.id)

        if user_id not in player_stats:
            player_stats[user_id] = {"wins": 0, "losses": 0}
        player_stats[user_id]["wins"] += 1
        save_stats()

        del games[user_id]


    else:
        feedback = get_wordle_feedback(session.word, user_input)
        if not session.is_game_over():
            if session.attempts == 3 and not session.hint_used:
                await ctx.send("🤔 Stuck? Type `$hint` to get a clue about the word.")
            
            await ctx.send(
                f"❌ Wrong guess! You have {session.max_attempts - session.attempts} tries left.\n"
                f"Feedback: `{feedback}`\n"
                f"Current word: `{' '.join(session.display)}`"
            )
        else:
            await ctx.send(
                f"🛑 Game over! The word was `{session.word}`.\n"
                f"**How this helps the climate:** {climate_words[session.word]['explanation']} \n"
                f"Type $playagain to keep playing!"
            )

            user_id = str(ctx.author.id)
            if user_id not in player_stats:
                player_stats[user_id] = {"wins": 0, "losses": 0}
            player_stats[user_id]["losses"] += 1
            save_stats()

            del games[user_id]


@bot.command()
async def hint(ctx):
    """Optional hint for the current climate word."""
    user_id = str(ctx.author.id)
    session = games.get(user_id)


    if not session:
        await ctx.send("❗ You don't have an active game. Start one using `$climatewordle`.")
        return

    if session.hint_used:
        await ctx.send("⚠️ You've already used your hint for this round!")
    else:
        session.hint_used = True
        hint_text = climate_words[session.word]["hint"]
        await ctx.send(f"💡 Hint: {hint_text}")

@bot.command()
async def stats(ctx):
    user_id = str(ctx.author.id)
    stats = player_stats.get(user_id)

    if not stats:
        await ctx.send("You haven't started a game yet! Start one with `$climatewordle`.")
        return

    wins = stats["wins"]
    losses = stats["losses"]
    total = wins + losses
    accuracy = (wins / total) * 100 if total > 0 else 0

    await ctx.send(
        f"📊 Your Stats:\n"
        f"🏆 Wins: {wins}\n"
        f"💀 Losses: {losses}\n"
        f"🎯 Accuracy: {accuracy:.2f}%"
    )

@bot.command()
async def leaderboard(ctx):
    if not player_stats:
        await ctx.send("🏁 No one has played yet!")
        return

    sorted_leaderboard = sorted(
        player_stats.items(),
        key=lambda item: item[1]["wins"],
        reverse=True
    )

    message = "🏆 **Leaderboard Climate Wordle** 🏆\n"
    medals = ["🥇", "🥈", "🥉"]

    seen = set()
    rank = 1

    for user_id, stats in sorted_leaderboard:
        if user_id in seen:
            continue
        seen.add(user_id)

        user = await bot.fetch_user(int(user_id))
        medal = medals[rank - 1] if rank <= 3 else f"{rank}."
        message += f"{medal} {user.name} - {stats['wins']} wins, {stats['losses']} losses\n"
        rank += 1

    await ctx.send(message)

@bot.command()
async def playagain(ctx):
    user_id = str(ctx.author.id)

    if user_id in games:
        await ctx.send("🟡 You already have an active game! Finish it or use `$giveup`.")
        return

    message = start_new_game(user_id, ctx)
    await ctx.send(message)





bot.run("code")
