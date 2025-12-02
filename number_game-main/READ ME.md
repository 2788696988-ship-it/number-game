# AI Number Guessing Game - Course Assignment

## 📋 Assignment Submission
**Student:** [Your Name]  
**Course:** [Course Name]  
**Date:** [Submission Date]  
**GitHub Repository:** [Your Repository Link]

## 🎯 Project Objective
Design and implement an AI-powered game that demonstrates multi-agent interaction, strategic thinking, and machine learning principles through a number guessing game framework.

## 🎮 Game Overview

### Core Concept
Two AI agents engage in a strategic battle:
1. **Number Setter AI**: Chooses and defends a secret number (1-100)
2. **Number Guesser AI**: Deduces the number through logical reasoning

### Key Features
1. **AI vs AI Competition**: Two intelligent agents with different objectives
2. **Strategic Dialogue**: AIs communicate and analyze each other's strategies
3. **Memory System**: Learning from historical games to improve performance
4. **Complete Analysis**: Post-game review and statistical reporting
5. **Modular Architecture**: Single-file design for easy understanding and modification

## 🏗️ Technical Architecture

### System Components
- **Game Engine** (`NumberGame`): Controls game flow and rules
- **AI Agents** (`NumberSetter`, `NumberGuesser`): Implement strategic decision-making
- **API Client** (`DeepSeekClient`): Connects to DeepSeek AI service
- **Memory Manager** (`MemoryManager`): Handles cross-game learning
- **Configuration** (`NumberGameConfig`): Centralized game settings

### Design Patterns Used
1. **Strategy Pattern**: Different AI roles implement unique guessing/setting strategies
2. **Observer Pattern**: Game state monitoring and response triggering
3. **Singleton Pattern**: Single API client instance management
4. **Template Method**: Common AI interaction patterns with role-specific implementations

## 🚀 Implementation Steps

### Step 1: Environment Setup
```bash
# 1. Clone repository
git clone <repository-url>
cd ai-number-game

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add your DeepSeek API key