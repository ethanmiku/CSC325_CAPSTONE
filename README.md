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

## Evidence discovery (Issue #25)

The Godot evidence feature provides a mobile Interact button, local range checks,
an evidence information panel, and discovery tracking for the current game run.
It does not require Django or MongoDB. Player movement is developed separately.

Open `game/maps/evidence_demo.tscn` in Godot and run the current scene with **F6**
to try the stationary demonstration. See the [evidence integration and testing
guide](game/docs/evidence-discovery.md) for player integration, authoring objects,
automated tests, and mobile manual checks.
