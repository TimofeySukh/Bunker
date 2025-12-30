# Bunker Game Bot 🏚️

A Telegram bot for the social survival game "Bunker" powered by Google's Gemini AI.

## Overview

This bot acts as a game master for the popular party game "Bunker", where players receive character cards with various attributes (profession, age, health condition, hobbies, phobias, etc.) and must convince others why they deserve a place in the bunker during an apocalypse.

**⚠️ Note: The game is in Russian language.**

## Features

- 🎲 Generates balanced character cards with unique attributes
- 🤖 AI-powered game master using Gemini 2.5 Flash
- 📝 Tracks character traits: profession, age, gender, health, hobby, phobia, and special cards
- 🎭 Creates engaging roleplay scenarios

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Usage

- `/start` - Begin a new game
- `/new` - Generate a new character card
- Send messages to interact with the AI game master

## Requirements

- Python 3.8+
- python-telegram-bot
- google-genai
- python-dotenv

## License

MIT
