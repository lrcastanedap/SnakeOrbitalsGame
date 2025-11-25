🐍 Electron Snake Game
Overview
Welcome to Electron Snake, a chemistry-themed version of the classic Snake game!
You’ll guide your snake — representing an atom’s electron configuration — as it eats orbitals and fills electrons to earn points.

The goal is to fill orbitals in the correct order, just like how electrons fill atomic orbitals (1s → 2s → 2p → 3s, etc.).

🎯 Learning Goals
This project connects chemistry and computer science by reinforcing two ideas:

Electron Configuration: Students practice orbital filling order and electron capacity.
Programming Concepts: Students explore event loops, game logic, and basic graphics with pygame.
🧩 Gameplay Concept
The snake starts small — representing an atom with few or no electrons.
When it eats an orbital symbol (like “1s”, “2p”), can start filling that orbital.
Each electron the snake collects after that adds to the current orbital until it’s full.
Once an orbital is filled, it disappears, and a new one appears — following the correct order of electron filling.
Players score points for each completed orbital and for each electron successfully placed!
💻 Requirements
You only need:

Python 3.8+
Pygame library
If pygame isn’t installed, open a terminal or command prompt and run:

bash
pip install pygame
No admin privileges are required — you can install pygame in user mode:

bash
pip install --user pygame
🚀 How to Run the Game
Download or copy the single Python file (e.g., orbitals.py).
Open a terminal/command prompt in the same folder.
Run:
bash
python orbitals.py
Use the arrow keys to move your snake!
See if you can reach Argon (1s²2s²2p⁶3s²3p⁶) before crashing!
🧠 Extensions & Ideas
Teachers and students can expand the project by:

Adding energy levels or electron shells as backgrounds or levels.
Showing a periodic table to select different elements as targets.
Including a “Quantum Mode” where orbitals appear in the real 3D order.
Letting the snake lose points if orbitals are filled out of order.
👩‍🔬 Educational Connection
This game demonstrates the Aufbau principle — electrons fill the lowest energy orbitals first.
By “playing chemistry,” students strengthen both programming and conceptual understanding of atomic structure.

🖊️ Credits
Created for a high school chemistry class at North High School, by Luis Raul Castaneda Perea
