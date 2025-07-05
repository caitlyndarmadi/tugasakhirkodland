import discord
import os
import random 
import requests
from discord.ext import commands
from main import climate_words
from main import GameSession
from main import get_wordle_feedback

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)



games = {}

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





bot.run("code")
