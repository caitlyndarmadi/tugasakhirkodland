#import random

#chars = "+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
#random_string = ""
#x = int(input("Mau berapa password?"))
#for i in range(x):
    #random_string += random.choice(chars)
#print(random_string)

import random

climate_words = {
    "reuse": {
        "topic": "waste management",
        "hint": "Part of the famous 3R", 
        "explanation": "Using items multiple times reduces waste and lowers carbon emissions."
    },
    "reduce": {
        "topic": "waste management",
        "hint": "Part of the famous 3R", 
        "explanation": "Reducing waste is crucial for environmental protection as it conserves resources, reduces pollution, and minimizes the impact of waste disposal."
    },
    "recycle": {
        "topic": "waste management",
        "hint": "Part of the famous 3R", 
        "explanation": "Recycling items saves resources, prevents pollution."
    },
    "bike": {
        "topic": "transport",
        "hint": "has two wheels", 
        "explanation": "Cycling instead of driving reduces fuel use and pollution."
    },
    "walk": {
        "topic": "transport",
        "hint": "anyone can do this", 
        "explanation": "Walking to places near you can instead of using fuel-powered vehicles reduce fuel use and pollution."
    },
    "compost": {
        "topic": "waste management",
        "hint": "a better version of a trash bin", 
        "explanation": "Composting food waste helps cut methane emissions from landfills."
    },
    "solar": {
        "topic": "renewable energy",
        "hint": "only appears during the daytime", 
        "explanation": "Solar energy can significantly benefit the environment by reducing carbon emissions, decreasing reliance on fossil fuels, and improving air and water quality."
    },
    "wind": {
        "topic": "renewable energy",
        "hint": "cannot be seen, but can be felt", 
        "explanation": "Wind energy can significantly benefit the environment by providing a clean, renewable energy source that reduces reliance on fossil fuels and their associated emissions."
    },
    "hydropower": {
        "topic": "renewable energy",
        "hint": "energy from moving water", 
        "explanation": "Hydropower—energy derived from moving water—can significantly benefit the environment by reducing reliance on fossil fuels and mitigating climate change."
    },
    
}
  
class GameSession:
    def __init__(self, word):
        self.word = word
        self.display = ["_"] * len(word)
        self.attempts = 0
        self.max_attempts = 5
        self.guessed = False
        self.hint_used = False  # track whether hint was used

    def guess(self, user_input):
        user_input = user_input.lower()

        if user_input == self.word:
            self.guessed = True
            self.display = list(self.word)
            return True
        else:
            # Reveal correct letters in correct positions (green/🟩)
            for i in range(min(len(user_input), len(self.word))):
                if user_input[i] == self.word[i]:
                    self.display[i] = self.word[i]
            self.attempts += 1
            return False

    def reveal_hint(self):
        unrevealed_indices = [i for i, c in enumerate(self.display) if c == "_"]
        if unrevealed_indices:
            idx = random.choice(unrevealed_indices)
            self.display[idx] = self.word[idx]

    def is_game_over(self):
        return self.guessed or self.attempts >= self.max_attempts
    
def get_wordle_feedback(secret_word, guess_word):
    feedback = ["⬜"] * len(secret_word)
    secret_word = secret_word.lower()
    guess_word = guess_word.lower()
    
    # Track which letters have been matched
    secret_used = [False] * len(secret_word)

    # First pass: check for correct letters in correct position (🟩)
    for i in range(len(guess_word)):
        if i < len(secret_word) and guess_word[i] == secret_word[i]:
            feedback[i] = "🟩"
            secret_used[i] = True

    # Second pass: check for correct letters in wrong position (🟨)
    for i in range(len(guess_word)):
        if feedback[i] == "🟩":
            continue
        for j in range(len(secret_word)):
            if not secret_used[j] and guess_word[i] == secret_word[j]:
                feedback[i] = "🟨"
                secret_used[j] = True
                break

    return "".join(feedback)
    return "".join(result)
