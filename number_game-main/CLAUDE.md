#CLAUDE.md
This file provides guidance to Claude Code when working with the AI Number Guessing Game project.

##Project Overview
This is an AI-powered number guessing game system where two AI agents engage in strategic gameplay - one sets a secret number, the other tries to deduce it through logical reasoning.

The system uses DeepSeek API as the backend (called via OpenAI SDK format).

##Development Environment Setup

##Dependency Installation
bash
pip install -r requirements.txt
API Configuration
Create a .env file and configure DeepSeek API Key:

bash
DEEPSEEK_API_KEY=your_api_key_here
Run Commands
bash
# Run interactive game
python number_game.py

# Run automatic game (no interaction required)
python number_game.py --auto

# Run test mode (quick game)
python number_game.py --test

# Validate configuration
python -c "from number_game import NumberGameConfig; NumberGameConfig.validate()"
Core Architecture
Game Architecture
Core Components:

number_game.py - All-in-one game system (orchestrates number setting → guessing → feedback → strategy dialogue)

Contains game configuration (NumberGameConfig class)

Contains AI role implementations (NumberSetter, NumberGuesser)

Contains game flow management (NumberGame class)

Contains memory system (MemoryManager class)

Contains DeepSeek API client (DeepSeekClient class)

Role System:

Both roles inherit from BasePlayer

Each role has an independent system_prompt (defines identity and strategy)

Roles interact with DeepSeek API through the speak() method

Memory System:

Automatically generates experience summary after game ends

Extracts lessons learned and saves to game_memory/ directory

Automatically loads historical experience into role's system_prompt when next game starts

Supports role-level experience accumulation (each role has independent memory file)

Game Flow:

Initialization: NumberSetter chooses secret number (1-100)

Guessing Phase: NumberGuesser makes guesses, receives feedback

Strategy Dialogue: AI agents exchange strategic insights

Victory Determination:

Guesser wins if number found within 10 attempts

Setter wins if guesser fails to find number

DeepSeek API Client
DeepSeekClient class (in number_game.py):

Wraps OpenAI SDK, compatible with DeepSeek API

Provides chat() method for single-turn conversations

Automatically handles API errors and fallbacks

Important Design Principles
Game Balance
Maintains balanced difficulty:

Setter avoids obvious numbers (1, 100, 50)

Guesser starts with binary search strategy

Both roles have psychological analysis capabilities

Prompt Engineering
Uses detailed system_prompt to define role identity and strategy

Provides real-time game state and historical information in user prompts

Includes clear output format requirements (e.g., guessing must output only the number)

State Management
Uses simple state tracking for game progress

Maintains guess history and feedback log

Supports game replay and analysis

Output Format
Uses colorama for colored terminal output

Different phases use different colors (blue for rounds, green for guesser, magenta for setter)

Clear section separation with print_section() method

Modification and Extension Guide
Adding New Game Modes
Create new game mode method in NumberGame class

Add command line argument handling in main() function

Implement mode-specific game logic

Adjusting AI Behavior
Modify NumberGameConfig.TEMPERATURE to adjust creativity (0.7-1.0)

Modify role system_prompt in _build_system_prompt() methods

Adjust NumberGameConfig.MAX_DIALOGUE_WORDS to control hint length

Changing Game Parameters
To adjust difficulty:

Modify MIN_NUMBER and MAX_NUMBER in NumberGameConfig

Change MAX_GUESSES for different difficulty levels

Adjust ENABLE_HINTS and ENABLE_STRATEGY_DIALOGUE for game variations

Switching LLM Backend
To use other LLM APIs (like OpenAI, Claude):

Modify DEEPSEEK_BASE_URL and MODEL_NAME in NumberGameConfig class

Update API key environment variable name if needed

Data Storage
Game Records
Directory: game_history/

Format: game_YYYYMMDD_HHMMSS.json

Contains: Secret number, guess history, hints given, victory result

Long-term Memory
Directory: game_memory/

Format: {role}_memory.json (e.g., setter_memory.json, guesser_memory.json)

Contains: Historical game experiences for each role (keeps up to MAX_HISTORY_GAMES games)

Configuration Parameters
Key Parameters in NumberGameConfig
MIN_NUMBER, MAX_NUMBER - Number range (default 1-100)

MAX_GUESSES - Maximum guesses allowed (default 10)

MAX_DIALOGUE_WORDS - Maximum words in hints/analysis (default 150)

ENABLE_HINTS - Whether setter provides strategic hints (default True)

ENABLE_STRATEGY_DIALOGUE - Whether AI agents discuss strategy (default True)

ENABLE_LONG_TERM_MEMORY - Whether to enable memory system (default True)

MAX_HISTORY_GAMES - Number of historical games to keep in memory (default 5)

TEMPERATURE - API temperature parameter (default 0.8)

Common Issues
API Call Failure
Check if DEEPSEEK_API_KEY in .env file is correct

Check network connection

Confirm DeepSeek API balance is sufficient

Poor AI Performance
Adjust TEMPERATURE parameter (between 0.7-1.0)

Modify role's system_prompt, add more specific strategic guidance

Let AI play several games to accumulate experience (memory system will gradually optimize performance)

Game Takes Too Long
Reduce MAX_GUESSES (default 10)

Disable ENABLE_STRATEGY_DIALOGUE or ENABLE_HINTS

Reduce number range (MAX_NUMBER)

AI Returns Invalid Format
The system has fallback mechanisms (binary search for guesser)

Check if API response is being parsed correctly in _extract_number() method

Adjust prompt to request specific output format

Project Status
Current system is feature-complete, including:

✅ Two AI roles with distinct strategies

✅ Complete game flow with multiple rounds

✅ Strategic hint and dialogue system

✅ Game history recording and analysis

✅ Long-term memory system (cross-game experience accumulation)

✅ Colored terminal interface with clear game progress display

Code Structure Reference
Main Classes Overview:
text
NumberGameConfig       # Game settings and parameters
DeepSeekClient         # API communication wrapper
BasePlayer             # Base class for all AI roles
  ├── NumberSetter     # AI that chooses/defends secret number
  └── NumberGuesser    # AI that deduces number through logic
NumberGame             # Main game controller
MemoryManager          # Long-term experience storage
Key Methods:
BasePlayer._build_system_prompt() - Creates role-specific AI instructions

NumberSetter.choose_number() - AI selects secret number strategically

NumberGuesser.make_guess() - AI makes intelligent guess based on history

NumberGame.run_game() - Main game loop

MemoryManager.save_experience() - Stores game lessons for future learning

Testing and Debugging
Quick Tests
bash
# Test API connectivity
python -c "from number_game import DeepSeekClient; client = DeepSeekClient(); print('API client created successfully')"

# Test configuration validation
python number_game.py --test

# Run multiple games automatically
for i in {1..3}; do python number_game.py --auto; done
Debug Mode
To enable debug output, temporarily add:

python
import logging
logging.basicConfig(level=logging.DEBUG)
Performance Considerations
API Cost Optimization:

Limit maximum tokens per response

Cache frequent responses if needed

Consider batch processing for multiple games

Memory Usage:

History files are automatically trimmed to MAX_HISTORY_GAMES

Game records are stored as JSON with minimal metadata

Response Time:

Game waits between rounds for readability (adjustable in code)

API calls are sequential; consider async for parallel games

Contribution Guidelines
Code Style:

Follow existing naming conventions

Use descriptive variable names

Add comments for complex logic

New Features:

Add configuration options in NumberGameConfig

Include command-line arguments for new modes

Update documentation in README.md and CLAUDE.md

Testing:

Test with different API keys

Verify fallback mechanisms work

Check memory system persistence

Educational Value
This project demonstrates:

AI Strategy Design: How to create AI agents with distinct objectives

Game Theory: Competitive vs cooperative elements in game design

Machine Learning Principles: Experience-based learning without traditional training

API Integration: Practical use of cloud-based AI services

Software Architecture: Single-file design with clear separation of concerns

For classroom use, consider these discussion points:

How do the AI strategies evolve over multiple games?

What psychological tactics are most effective in number guessing?

How could this system be extended to more complex games?

What ethical considerations arise from AI vs AI competition?

