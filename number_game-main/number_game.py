"""
AI Number Guessing Game - Two AI Agents Battle of Wits
Core game logic consolidated in a single file

How to run:
  python number_game.py          # Interactive mode
  python number_game.py --auto   # Auto-run mode
  python number_game.py --test   # Quick test mode
"""

import random
import time
import json
import os
import re
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from colorama import Fore, Style, init
from openai import OpenAI
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# ==================== Configuration Class ====================

class NumberGameConfig:
    """Number guessing game configuration class"""
    
    # API Configuration
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat"
    
    # Game Parameters
    MIN_NUMBER = 1
    MAX_NUMBER = 100
    MAX_GUESSES = 10
    MAX_DIALOGUE_WORDS = 150
    
    # AI Behavior
    TEMPERATURE = 0.8
    MAX_TOKENS = 1000
    
    # Role Configuration
    ROLE_NAMES = {
        "setter": "Number Setter",
        "guesser": "Number Guesser"
    }
    
    # Role Descriptions
    ROLE_DESCRIPTIONS = {
        "setter": """You are the Number Setter. Your goal is to choose a secret number and prevent the guesser from finding it.
        Strategy:
        1. Choose a number that's not too obvious (avoid 1, 100, 50)
        2. When giving hints, be clever but not too helpful
        3. Analyze the guesser's reasoning to understand their strategy
        4. You can use psychological tactics to misdirect""",
        
        "guesser": """You are the Number Guesser. Your goal is to deduce the secret number through logical reasoning.
        Strategy:
        1. Use binary search strategy initially (start with 50)
        2. Analyze the setter's hints and responses
        3. Look for patterns in their feedback
        4. Adjust your strategy based on their psychology"""
    }
    
    # Game Settings
    ENABLE_HINTS = True
    ENABLE_STRATEGY_DIALOGUE = True
    SAVE_GAME_HISTORY = True
    GAME_HISTORY_DIR = "game_history"
    
    # Memory System
    ENABLE_LONG_TERM_MEMORY = True
    MEMORY_FILE_DIR = "game_memory"
    MAX_HISTORY_GAMES = 5
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not found in .env file")
        print("✅ Game configuration validated")
        return True

# ==================== DeepSeek API Client ====================

class DeepSeekClient:
    """API client for DeepSeek"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=NumberGameConfig.DEEPSEEK_API_KEY,
            base_url=NumberGameConfig.DEEPSEEK_BASE_URL
        )
        self.model = NumberGameConfig.MODEL_NAME
    
    def chat(self, system_prompt: str, user_message: str) -> str:
        """Send single message to API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=NumberGameConfig.TEMPERATURE,
                max_tokens=NumberGameConfig.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ API Error: {e}")
            return "Error in AI response"

# ==================== Game Roles ====================

class BasePlayer:
    """Base player class with common functionality"""
    
    def __init__(self, role: str, player_id: int = 1):
        self.role = role
        self.player_id = player_id
        self.client = DeepSeekClient()
        self.memory = []
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build role-specific system prompt"""
        base = f"""You are playing a Number Guessing Game.

Role: {NumberGameConfig.ROLE_NAMES[self.role]}
{NumberGameConfig.ROLE_DESCRIPTIONS[self.role]}

Game Rules:
- Secret number is between {NumberGameConfig.MIN_NUMBER} and {NumberGameConfig.MAX_NUMBER}
- Maximum {NumberGameConfig.MAX_GUESSES} guesses allowed
- After each guess, you'll get feedback (too high/too low/correct)

Important: Be strategic, logical, and creative in your approach."""
        return base
    
    def speak(self, prompt: str) -> str:
        """Get AI response"""
        return self.client.chat(self.system_prompt, prompt)

class NumberSetter(BasePlayer):
    """AI that sets and defends the secret number"""
    
    def __init__(self):
        super().__init__("setter", 1)
        self.secret_number = None
        self.guess_history = []
    
    def choose_number(self) -> int:
        """AI chooses a secret number"""
        prompt = f"""Choose a secret number between {NumberGameConfig.MIN_NUMBER} and {NumberGameConfig.MAX_NUMBER}.
        
Consider:
1. Don't choose obvious numbers (1, 100, 50, 25, 75)
2. Think about psychological factors
3. Consider how the guesser might approach the problem

Output only the number, no additional text."""
        
        response = self.speak(prompt)
        try:
            number = int(re.search(r'\b\d{1,3}\b', response).group())
            number = max(NumberGameConfig.MIN_NUMBER, min(number, NumberGameConfig.MAX_NUMBER))
            self.secret_number = number
            return number
        except:
            # Fallback to random if AI response fails
            self.secret_number = random.randint(10, 90)
            return self.secret_number
    
    def evaluate_guess(self, guess: int) -> Dict[str, any]:
        """Evaluate the guess and provide feedback"""
        self.guess_history.append(guess)
        
        if guess == self.secret_number:
            return {
                "result": "correct",
                "message": f"🎯 Correct! The number was {self.secret_number}"
            }
        elif guess < self.secret_number:
            return {
                "result": "too_low",
                "message": f"📈 Too low! (Guess: {guess})"
            }
        else:
            return {
                "result": "too_high", 
                "message": f"📉 Too high! (Guess: {guess})"
            }
    
    def provide_hint(self, guess_history: List[int]) -> str:
        """Provide a strategic hint"""
        last_guess = guess_history[-1] if guess_history else 50
        
        prompt = f"""The guesser just guessed {last_guess}. Your secret number is {self.secret_number}.
        
Provide a hint that:
1. Is truthful but not too revealing
2. Uses psychological tactics
3. Might misdirect their next guess
4. Maximum {NumberGameConfig.MAX_DIALOGUE_WORDS} words

Example formats:
- "You're getting warmer but still off track"
- "Think about prime numbers"
- "Consider the midpoint between your last two guesses"

Your hint:"""
        
        return self.speak(prompt)

class NumberGuesser(BasePlayer):
    """AI that tries to guess the secret number"""
    
    def __init__(self):
        super().__init__("guesser", 2)
        self.guess_history = []
        self.feedback_history = []
    
    def make_guess(self, feedback_history: List[Dict]) -> int:
        """Make an intelligent guess based on history"""
        if not self.guess_history:
            # First guess - start with midpoint
            return 50
        
        prompt = self._build_guess_prompt(feedback_history)
        response = self.speak(prompt)
        
        try:
            guess = int(re.search(r'\b\d{1,3}\b', response).group())
            guess = max(NumberGameConfig.MIN_NUMBER, min(guess, NumberGameConfig.MAX_NUMBER))
            self.guess_history.append(guess)
            return guess
        except:
            # Fallback to binary search
            return self._binary_search_guess(feedback_history)
    
    def _build_guess_prompt(self, feedback_history: List[Dict]) -> str:
        """Build prompt for guessing"""
        history_text = ""
        for i, (guess, feedback) in enumerate(zip(self.guess_history, feedback_history)):
            history_text += f"Guess {i+1}: {guess} → {feedback['message']}\n"
        
        prompt = f"""You are trying to guess a number between {NumberGameConfig.MIN_NUMBER} and {NumberGameConfig.MAX_NUMBER}.

Previous guesses and feedback:
{history_text}

Your strategy should consider:
1. Mathematical reasoning (binary search, probability)
2. Psychological analysis of the setter
3. Pattern recognition in their responses
4. You have {NumberGameConfig.MAX_GUESSES - len(self.guess_history)} guesses remaining

Make your next guess (output only the number):"""
        
        return prompt
    
    def _binary_search_guess(self, feedback_history: List[Dict]) -> int:
        """Fallback binary search algorithm"""
        low, high = NumberGameConfig.MIN_NUMBER, NumberGameConfig.MAX_NUMBER
        
        for guess, feedback in zip(self.guess_history, feedback_history):
            if feedback["result"] == "too_low":
                low = max(low, guess + 1)
            elif feedback["result"] == "too_high":
                high = min(high, guess - 1)
        
        return (low + high) // 2
    
    def analyze_setter_strategy(self, hints: List[str]) -> str:
        """Analyze the setter's strategy"""
        hints_text = "\n".join([f"Hint {i+1}: {hint}" for i, hint in enumerate(hints)])
        
        prompt = f"""Analyze the setter's strategy based on these hints:

{hints_text}

Provide your analysis (max {NumberGameConfig.MAX_DIALOGUE_WORDS} words):
1. What psychological tactics are they using?
2. Are they trying to misdirect you?
3. How should you adjust your strategy?"""
        
        return self.speak(prompt)

# ==================== Game Engine ====================

class NumberGame:
    """Main game controller"""
    
    def __init__(self):
        self.setter = NumberSetter()
        self.guesser = NumberGuesser()
        self.game_history = []
        self.start_time = None
        self.hints_given = []
    
    def print_section(self, title: str, color: str = Fore.YELLOW):
        """Print formatted section header"""
        separator = "=" * 60
        print(f"\n{color}{separator}")
        print(f"{title:^60}")
        print(f"{separator}{Style.RESET_ALL}")
    
    def print_info(self, message: str, color: str = Fore.WHITE):
        """Print colored message"""
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def run_game(self):
        """Main game loop"""
        self.start_time = datetime.now()
        
        # Step 1: Setter chooses number
        self.print_section("🎮 GAME START", Fore.CYAN)
        secret_number = self.setter.choose_number()
        self.print_info(f"🔢 Number Setter has chosen a secret number!", Fore.MAGENTA)
        self.print_info(f"   Range: {NumberGameConfig.MIN_NUMBER}-{NumberGameConfig.MAX_NUMBER}", Fore.MAGENTA)
        self.print_info(f"   Max guesses: {NumberGameConfig.MAX_GUESSES}", Fore.MAGENTA)
        print()
        time.sleep(2)
        
        # Game loop
        for round_num in range(1, NumberGameConfig.MAX_GUESSES + 1):
            self.print_section(f"🔄 ROUND {round_num}", Fore.BLUE)
            
            # Guesser makes guess
            self.print_info("🤔 Guesser is thinking...", Fore.GREEN)
            guess = self.guesser.make_guess(self.guess.feedback_history)
            self.print_info(f"🎯 Guesser's guess: {guess}", Fore.GREEN)
            
            # Setter evaluates
            feedback = self.setter.evaluate_guess(guess)
            self.guesser.feedback_history.append(feedback)
            self.print_info(f"📊 Feedback: {feedback['message']}", Fore.YELLOW)
            
            # Record round
            round_data = {
                "round": round_num,
                "guess": guess,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            self.game_history.append(round_data)
            
            # Check win condition
            if feedback["result"] == "correct":
                self.end_game(winner="guesser", rounds=round_num)
                return
            
            # Optional hint system
            if NumberGameConfig.ENABLE_HINTS and round_num % 2 == 0:
                hint = self.setter.provide_hint(self.guesser.guess_history)
                self.hints_given.append(hint)
                self.print_info(f"💡 Setter's hint: {hint}", Fore.CYAN)
            
            # Strategy dialogue
            if NumberGameConfig.ENABLE_STRATEGY_DIALOGUE and round_num % 3 == 0:
                analysis = self.guesser.analyze_setter_strategy(self.hints_given)
                self.print_info(f"🧠 Guesser's analysis: {analysis}", Fore.MAGENTA)
            
            time.sleep(1.5)
        
        # Max guesses reached
        self.end_game(winner="setter", rounds=NumberGameConfig.MAX_GUESSES)
    
    def end_game(self, winner: str, rounds: int):
        """End game and display results"""
        self.print_section("🏁 GAME OVER", Fore.RED)
        
        duration = (datetime.now() - self.start_time).seconds
        
        if winner == "guesser":
            self.print_info(f"🎉 GUESSER WINS!", Fore.GREEN)
            self.print_info(f"   Correct number: {self.setter.secret_number}", Fore.GREEN)
            self.print_info(f"   Guesses used: {rounds}/{NumberGameConfig.MAX_GUESSES}", Fore.GREEN)
        else:
            self.print_info(f"🏆 SETTER WINS!", Fore.RED)
            self.print_info(f"   Secret number: {self.setter.secret_number} was never found", Fore.RED)
            self.print_info(f"   All {rounds} guesses exhausted", Fore.RED)
        
        self.print_info(f"⏱️  Game duration: {duration} seconds", Fore.CYAN)
        self.print_info(f"📈 Guesses made: {len(self.guesser.guess_history)}", Fore.CYAN)
        self.print_info(f"💡 Hints given: {len(self.hints_given)}", Fore.CYAN)
        
        # Display guess history
        print(f"\n{Fore.YELLOW}📋 Guess History:{Style.RESET_ALL}")
        for i, (guess, feedback) in enumerate(zip(self.guesser.guess_history, self.guesser.feedback_history)):
            status = "✓" if feedback["result"] == "correct" else "→"
            print(f"  Round {i+1}: {guess} {status} {feedback['message']}")
        
        # Save game history
        if NumberGameConfig.SAVE_GAME_HISTORY:
            self.save_game_record(winner, rounds)
    
    def save_game_record(self, winner: str, rounds: int):
        """Save game to history file"""
        try:
            os.makedirs(NumberGameConfig.GAME_HISTORY_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.json"
            filepath = os.path.join(NumberGameConfig.GAME_HISTORY_DIR, filename)
            
            game_data = {
                "timestamp": timestamp,
                "winner": winner,
                "secret_number": self.setter.secret_number,
                "total_rounds": rounds,
                "guesses": self.guesser.guess_history,
                "feedback": [f["message"] for f in self.guesser.feedback_history],
                "hints": self.hints_given,
                "duration_seconds": (datetime.now() - self.start_time).seconds
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            
            self.print_info(f"💾 Game saved to: {filepath}", Fore.GREEN)
        except Exception as e:
            self.print_info(f"❌ Failed to save game: {e}", Fore.RED)

# ==================== Memory System ====================

class MemoryManager:
    """Long-term memory for AI learning"""
    
    def __init__(self):
        self.memory_dir = NumberGameConfig.MEMORY_FILE_DIR
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def save_experience(self, role: str, experience: str):
        """Save AI experience"""
        memory_file = os.path.join(self.memory_dir, f"{role}_memory.json")
        
        try:
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
            else:
                memories = []
            
            memories.append({
                "timestamp": datetime.now().isoformat(),
                "experience": experience
            })
            
            # Keep only recent memories
            if len(memories) > NumberGameConfig.MAX_HISTORY_GAMES:
                memories = memories[-NumberGameConfig.MAX_HISTORY_GAMES:]
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Memory save error: {e}")
            return False
    
    def load_experience(self, role: str) -> str:
        """Load AI historical experience"""
        memory_file = os.path.join(self.memory_dir, f"{role}_memory.json")
        
        if not os.path.exists(memory_file):
            return "No previous experience"
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            if not memories:
                return "No previous experience"
            
            # Return last 3 experiences
            recent = memories[-3:] if len(memories) >= 3 else memories
            experiences = [f"Game {i+1}: {m['experience']}" for i, m in enumerate(recent)]
            return "\n".join(experiences)
        except:
            return "No previous experience"

# ==================== Main Program ====================

def print_banner():
    """Print game banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    AI NUMBER GUESSING GAME                    ║
║             Two AI Agents Battle of Wits & Logic              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}"""
    print(banner)

def print_intro():
    """Print game introduction"""
    intro = f"""
{Fore.YELLOW}🎮 GAME DESCRIPTION{Style.RESET_ALL}
Two AI agents compete in a number guessing game:

{Fore.GREEN}🤖 NUMBER GUESSER{Style.RESET_ALL}
- Tries to deduce a secret number (1-100)
- Uses logical reasoning and psychological analysis
- Has {NumberGameConfig.MAX_GUESSES} attempts to find the number

{Fore.MAGENTA}🤖 NUMBER SETTER{Style.RESET_ALL}
- Chooses and defends a secret number
- Provides strategic hints and feedback
- Uses psychological tactics to misdirect

{Fore.CYAN}✨ SPECIAL FEATURES{Style.RESET_ALL}
- AI-to-AI strategic dialogue
- Long-term memory system (learns from past games)
- Complete game recording and analysis
- Colored terminal interface
"""
    print(intro)

def main(auto_mode=False):
    """Main function"""
    try:
        print_banner()
        print_intro()
        
        # Validate configuration
        NumberGameConfig.validate()
        
        if auto_mode:
            print(f"\n{Fore.GREEN}🚀 Auto mode starting...{Style.RESET_ALL}")
            game = NumberGame()
            game.run_game()
        else:
            # Interactive mode
            while True:
                choice = input(f"\n{Fore.YELLOW}Start game? (yes/no): {Style.RESET_ALL}").lower().strip()
                if choice in ['yes', 'y']:
                    print(f"\n{Fore.GREEN}Starting new game...{Style.RESET_ALL}\n")
                    game = NumberGame()
                    game.run_game()
                    
                    # Ask to play again
                    again = input(f"\n{Fore.YELLOW}Play again? (yes/no): {Style.RESET_ALL}").lower().strip()
                    if again not in ['yes', 'y']:
                        print(f"\n{Fore.CYAN}Thanks for playing! Goodbye!{Style.RESET_ALL}")
                        break
                else:
                    print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                    break
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Game interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Number Guessing Game")
    parser.add_argument("--auto", action="store_true", help="Run in auto mode")
    parser.add_argument("--test", action="store_true", help="Quick test mode")
    args = parser.parse_args()
    
    main(auto_mode=args.auto)