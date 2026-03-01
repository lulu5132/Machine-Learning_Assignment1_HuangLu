# Assignment 1 - HuangLu: Autism Supermarket Guide (Q-Learning)

## Project Overview
This project implements a **Q-Learning based Reinforcement Learning agent** that acts as a "Shadow Guide" for an autistic child in a supermarket. The goal is to learn when to provide visual cues (arrows or highlights) to help the child navigate a random grid world efficiently while encouraging independence.

## Features
- **Simulation Environment**: A 10x10 grid supermarket with aisles (shelves).
- **Pixel Art Visuals**: Procedurally generated graphics for shelves, floor, items, and characters.
- **Child Model**: Simulates semi-stochastic movement behavior.
- **Q-Learning Agent**: Learns an optimal policy to guide the child.
- **Interactive Mode**: Allows you to play as the child and receive AI guidance.

## Directory Structure
- `main.py`: Main entry point. Handles training, demo recording, and interactive play.
- `visuals.py`: Procedural pixel art generation.
- `agent.py`: Q-Learning algorithm.
- `environment.py`: Grid world logic.
- `config.py`: Hyperparameters.
- `outputs/`: Generated artifacts (`learning_curve.png`, `trained_agent_demo.gif`, etc.).

## How to Run

### 0. Install Dependencies
```bash
pip install -r requirements.txt
```

> Note: this project uses `pygame-ce` for better compatibility on Python 3.14, while code imports it as `import pygame`.

### 1. Training & Demo (Default)
Run this command to train the agent and generate a demo GIF:
```bash
python main.py
```
**Output:**
- `q_table.npy`: Trained model.
- `outputs/trained_agent_demo.gif`: A video showing the AI guiding the child in the supermarket.
- `outputs/learning_curve.png`: Performance graph.

### 2. Watch Mode (No GIF)
Use an existing trained model and open a live window without saving GIF:
```bash
python main.py --watch
```

### 3. Regenerate Demo GIF (No Retraining)
Use an existing `q_table.npy` and regenerate `trained_agent_demo.gif`:
```bash
python main.py --demo
```
Output file: `outputs/trained_agent_demo.gif`

### 4. Interactive Mode (Playable)
If you are running on a local machine with a display, you can control the child character yourself:
```bash
python main.py --play
```
- **Controls**: Arrow Keys to move.
- **Goal**: Reach the highlighted item.
- **AI Role**: The AI will display arrows or highlights to guide you. (Note: Run training first!).

## Notes on Remote/Headless Servers
If you are running on a server (like AutoDL) without a display:
- The Interactive Mode (`--play`) will **not work** because it requires a window.
- The default mode (`python main.py`) will automatically detect the server environment and save a **GIF recording** instead of trying to open a window. Download the GIF to view the results.
