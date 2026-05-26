# Tools

Optional but recommended tools for working on this ROM hack.

---

## Porymap — Visual Map Editor

Porymap is the official map editor for the pokefirered decomp. It lets you:

- View the full tilemap visually and click tiles to see their metatile ID
- Drag and drop NPCs, trainers, signs, and warps onto the map
- Saves directly to `map.json` — no manual coordinate guessing

**Without Porymap:** placing NPCs requires decoding `data/layouts/<Map>/map.bin`
from binary to find walkable tile coordinates. Error-prone and slow.

**With Porymap:** click where you want the NPC, save, done.

### Installation

```bash
# Install Qt6 dependency
sudo apt install qt6-base-dev qmake6-bin

# Symlink qmake6 so build scripts find it
sudo ln -s /usr/bin/qmake6 /usr/local/bin/qmake

# Clone and build Porymap
git clone https://github.com/huderlem/porymap ~/Desktop/projects/porymap
cd ~/Desktop/projects/porymap
qmake porymap.pro
make
```

The `porymap` executable will be in `~/Desktop/projects/porymap/`.

### PATH Setup

Add to `~/.zshrc` so `porymap` is available from any terminal:

```bash
export PATH="$HOME/Desktop/projects/porymap:$PATH"
```

Then reload:

```bash
source ~/.zshrc
```

### Usage

```bash
porymap
```

On first launch, set the project directory to `~/Desktop/projects/pokemon-mod-rom`.
Porymap reads the pokefirered project structure automatically.

---

## GBA Emulator

Any GBA emulator works for testing. The built ROM is at:

```
~/Desktop/projects/pokemon-mod-rom/pokefirered.gba
```

Rebuild after changes with `make` (or `make clean && make` if make reports
nothing to do despite recent edits).

---

## PKHeX — Save File Editor

PKHeX edits save files directly — useful for testing specific scenarios without
playing through the game. It targets Windows (WinForms) but runs under Wine on
Linux.

Not required for development. Use it if you want to set up a specific game state
to test a change quickly.
