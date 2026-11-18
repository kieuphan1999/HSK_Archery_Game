# HSK Archery Game 🏹

A Chinese vocabulary learning game built with Python and Pygame. Players practice Chinese vocabulary by shooting targets and translating words between Chinese and Vietnamese.

## Features

- **Archery gameplay:** Shoot falling targets by typing the correct translation.
- **Vocabulary practice:** Supports Chinese vocabulary with multiple Vietnamese meanings.
- **Learning modes:** Chinese-to-Vietnamese and Vietnamese-to-Chinese translation.
- **Difficulty settings:** Adjust target falling speed.
- **Audio feedback:** Sound effects for correct and incorrect answers.
- **Chinese pronunciation:** Text-to-speech pronunciation using Microsoft Edge TTS.
- **Background music:** In-game background music.
- **Interactive menu:** Game menu and settings interface.

## Technologies Used

- Python
- Pygame
- Edge TTS
- Threading
- JSON / TXT-based vocabulary data

## Project Structure

```text
game_ban_cung/
├── main.py
├── menu.py
├── settings.py
├── audio_manager.py
├── word_loader.py
├── data/
│   └── HSK5_words.txt
├── sounds/
│   ├── hit.mp3
│   ├── wrong.mp3
│   └── background.mp3
└── README.md
```

## How to Run

### 1. Install Python

Make sure Python is installed on your computer.

### 2. Install dependencies

```bash
pip install pygame edge-tts
```

### 3. Run the game

```bash
python main.py
```

## How to Play

1. Launch the game.
2. Select your preferred game settings.
3. A Chinese vocabulary target will appear on the screen.
4. Type the Vietnamese meaning of the word.
5. Press Enter to submit your answer.
6. Correct answers launch an arrow toward the target and increase your score.
7. Incorrect answers trigger sound feedback, and the target remains on screen.
8. Try to prevent targets from reaching the ground.

## Audio System

The game uses Pygame for sound effects and background music, while Edge TTS generates Chinese pronunciation audio.

Pronunciation audio is generated in the background and cached to reduce waiting time during gameplay.

## Purpose

This project was created as a personal learning project to combine Chinese language learning with programming practice. It also serves as an opportunity to explore Python, game development, audio handling, threading, and user interface design.

---

*Developed as a personal project.*