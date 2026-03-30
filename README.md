# Chalant in Careers

> A career simulation RPG built for Hackiethon — where AI meets communication skills training.

---

## What is it?

Chalant in Careers is a top-down pixel RPG where you walk around a town, enter buildings, and role-play as professionals in different career fields. An AI acts as your client, patient, or guest — and at the end of each session, grades your **communication skills** in real time.

No multiple choice. No scripted answers. Just you, typing naturally, and an AI judging how well you communicate.

---

## Career Roles

| Building | Role | Who you talk to |
|---|---|---|
| The Clinic | Doctor | A patient with a physical complaint |
| The Clinic | Psychologist | A client seeking therapy |
| The Hotel | Hotel Front Desk | A tired traveller checking in |
| The Avenue | Real Estate Agent | A buyer looking for a property |

Every session generates a **completely new character** — different name, background, problem, and personality — so no two runs are the same.

---

## Scoring

Your responses are graded semantically by AI after 7 messages:

| Band | Coins | What it means |
|---|---|---|
| Outstanding | 500 | Genuinely excellent communication |
| Solid Work | 250 | Good but room to improve |
| Keep Practising | 100 | Needs more effort |
| End early / Error | 0 | Always complete the full session |

---

## How to Run

### Requirements
- Python 3.10+
- An OpenAI API key

### Installation

```bash
# Clone the repo
git clone https://github.com/raniamnda/hackiethon-chalant-in-careers.git
cd hackiethon-chalant-in-careers

# Install dependencies
pip install pygame numpy openai python-dotenv

# Create your .env file
echo OPENAI_API_KEY=your-key-here > .env

# Run the game
python main.py
```

### Controls

| Key | Action |
|---|---|
| WASD / Arrow keys | Move character |
| E or Enter | Enter a building |
| ESC | Exit a building |
| F1 | Toggle debug zones |

---

## Optional: Music

Create a `music/` folder and add lofi `.mp3` files named:
- `world.mp3` — world map
- `clinic.mp3` — clinic scenes
- `hotel.mp3` — hotel scene
- `realestate.mp3` — real estate scenes

The game runs silently if no music files are present.

---

## Tech Stack

- **Python** — core language
- **Pygame** — game engine and rendering
- **NumPy** — character sprite generation and movement physics
- **OpenAI API** — AI character generation, NPC conversation, and semantic grading

---

## File Structure

```
chalant-in-careers/
├── main.py          # Game loop entry point
├── constants.py     # Screen size, colours, building zones
├── assets.py        # NumPy-generated character sprites
├── player.py        # Movable character with 4-direction animation
├── world_map.py     # Top-down map with entry zones
├── scenes.py        # All game screens and UI
├── game.py          # State machine
├── ai_model.py      # OpenAI integration — generation, NPC, grading
├── dialogue.py      # Hardcoded fallback scripts
├── ui.py            # Reusable UI components
└── images/
    └── world_map.png
```

---

## Team

Built by Team Chalant in Careers for Hackiethon 2026.

---

*Tip: Outstanding scores require genuine communication — greet warmly, ask open questions, listen actively, and make the other person feel heard.*
