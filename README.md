# CSC325_CAPSTONE

## Group Members:

- Ethan Mikucki
- Jeffery Jean
- Fred Zhang
- Sean Wallace
- Angel Mendez Reyes
- John Rosario Castro

## Description:

Murder Mystery Game (title subject to change)

Project Overview:

MMG is an interactive mystery-solving application developed for our CSC325 Software Engineering course at Farmingdale State College.

Players will investigate a murder case by exploring locations, collecting evidence, interviewing suspects, and using clues to determine who committed the crime.

The goal is to create an engaging detective experience where players use logical reasoning and critical thinking to solve a mystery.

## Backend development

- [Windows setup](backend/SETUP_WIN.md)
- [macOS setup](backend/SETUP_MAC.md)
- [NPC dialogue API contract and Godot handoff](backend/docs/dialogue-api.md)

The local dialogue MVP supports one predefined NPC with Claude-generated replies.
The backend owns NPC data, validation, prompts, and Claude access. The Godot client
owns the conversation UI and supplies recent history with each message.
