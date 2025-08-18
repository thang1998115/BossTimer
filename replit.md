# Lineage 2M Boss Timer Discord Bot

## Overview

This is a Discord bot designed to track raid boss spawn timers for the mobile game Lineage 2M. The bot allows players to report boss kills and automatically calculates potential respawn windows based on each boss's respawn time and spawn rate probability. It uses Discord's slash commands and message interactions to provide real-time boss tracking functionality for gaming communities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Library**: Uses the discord.py library with the commands extension for structured command handling
- **Command System**: Implements a prefix-based command system (using "!" prefix) for user interactions
- **Intents Configuration**: Enables message content intents to read and process user messages

### Data Management
- **JSON File Storage**: Uses a simple JSON file (`data.json`) for persistent data storage of boss kill records
- **In-Memory Boss Configuration**: Boss locations, respawn times, spawn rates, and aliases are stored as Python dictionaries in the main application file
- **Timezone Handling**: Implements Asia/Ho_Chi_Minh timezone for consistent time calculations

### Boss Tracking System
- **Location Mapping**: Each boss location has multiple aliases to make user input flexible (e.g., "ant", "antb3", "queen ant" all refer to the same boss)
- **Respawn Calculation**: Combines fixed respawn times with probability-based spawn rates to calculate respawn windows
- **Time Management**: Uses Python's datetime and timedelta for precise time calculations and scheduling

### Hosting and Availability
- **Replit Integration**: Designed to run on Replit with environment variable configuration for the Discord token
- **Keep-Alive Mechanism**: Implements a Flask web server that runs in a separate thread to prevent the Replit instance from sleeping
- **Health Check Endpoint**: Provides a simple HTTP endpoint for external monitoring services

### Configuration Management
- **Environment Variables**: Discord bot token is stored as an environment variable for security
- **Modular Design**: Boss data and application logic are separated, making it easy to add new bosses or modify existing ones

## External Dependencies

### Discord Platform
- **Discord Bot API**: Requires a Discord application and bot token for authentication
- **Discord.py Library**: Python library for Discord bot development and API interaction

### Python Libraries
- **Flask**: Lightweight web framework used for the keep-alive functionality
- **Threading**: Standard library for running the web server in a separate thread
- **JSON**: Standard library for data serialization and storage
- **Datetime/Zoneinfo**: Standard libraries for time management and timezone handling
- **Regular Expressions**: Standard library for pattern matching in user input

### Hosting Platform
- **Replit**: Cloud-based development and hosting platform
- **Environment Configuration**: Relies on Replit's secrets management for secure token storage

### Optional Monitoring
- **UptimeRobot**: External service for monitoring and pinging the keep-alive endpoint (referenced in comments)