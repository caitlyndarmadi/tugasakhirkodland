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

# Try to load stats from file when bot starts
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r") as f:
        player_stats = json.load(f)
else:
    player_stats = {}

games = {}

def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump(player_stats, f)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def climatewordle(ctx):
    word, data = random.choice(list(climate_words.items()))
    topic = data["topic"]
    games[ctx.author.id] = GameSession(word)
    await ctx.send(
        f"🌍 Let's play Climate Wordle!\n**Topic:** {topic}\n"
        f"Your word has {len(word)} letters: `{' '.join(games[ctx.author.id].display)}`\n"
        f"Type your guess using `$guess <word>`.\n"
        f"🟩 = Letter is in the word and in the correct position.\n"
        f"🟨 = Letter is in the word but in the wrong position.\n"
        f"⬜️ = Letter is not in the word.\n"
    )

@bot.command()
async def guess(ctx, *, user_input: str):
    """Handle user guesses."""
    session = games.get(ctx.author.id)

    if not session:
        await ctx.send("❗ You don't have an active game. Start one using `$climatewordle`.")
        return
    
    if len(user_input) != len(session.word):
        await ctx.send(f"❗ Your guess must be exactly {len(session.word)} letters long.")
        return

    if session.guess(user_input):
        await ctx.send(
            f"✅ Correct! The word was `{session.word}`.\n"
            f"**How this helps the climate:** {climate_words[session.word]['explanation']}"
        )
        # Ambil ID pemain
        user_id = ctx.author.id

        if user_id not in player_stats:
            player_stats[user_id] = {"wins": 0, "losses": 0}
        player_stats[user_id]["wins"] += 1
        save_stats()

        del games[ctx.author.id]

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
                f"**How this helps the climate:** {climate_words[session.word]['explanation']}"
            )

            user_id = ctx.author.id
            if user_id not in player_stats:
                player_stats[user_id] = {"wins": 0, "losses": 0}
            player_stats[user_id]["losses"] += 1
            save_stats()

            del games[ctx.author.id]
            del games[ctx.author.id]

@bot.command()
async def hint(ctx):
    """Optional hint for the current climate word."""
    session = games.get(ctx.author.id)

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
    user_id = ctx.author.id
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

    leaderboard = sorted(player_stats.items(), key=lambda item: item[1]["wins"], reverse=True)
    message = "🏆 **Leaderboard Climate Wordle** 🏆\n"

    for i, (user_id, stats) in enumerate(leaderboard[:10], start=1):
        user = await bot.fetch_user(user_id)
        message += f"{i}. {user.name} - {stats['wins']} wins, {stats['losses']} losses\n"

    await ctx.send(message)





bot.run("code")
