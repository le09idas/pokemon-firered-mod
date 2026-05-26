# Pokemon FireRed ROM Hack — Setup Walkthrough

A personal log of every step taken to set up and build the pokefirered decomp project.

---

## Quick Start (New Machine Setup)

Clone the mod repo, then run through steps 1–4 below to get a working build environment.

```bash
# 1. Install dependencies
sudo apt install git python3 make libpng-dev binutils-arm-none-eabi build-essential gcc-arm-none-eabi

# 2. Clone this repo
git clone <your-github-repo-url> ~/Desktop/projects/pokemon-mod-rom
cd ~/Desktop/projects/pokemon-mod-rom

# 3. Build and install agbcc
git clone https://github.com/pret/agbcc.git /tmp/agbcc
cd /tmp/agbcc && ./build.sh && ./install.sh ~/Desktop/projects/pokemon-mod-rom
cd ~/Desktop/projects/pokemon-mod-rom

# 4. Provide your legally dumped ROM — place it here, named exactly:
#    ~/Desktop/projects/pokemon-mod-rom/pokefirered.gba

# 5. Build
make
```

A successful `make` produces `pokefirered.gba` in the `pokefirered/` directory. Load that file in your GBA emulator to test.

> **Note:** The `.gba` ROM file is in `.gitignore` and must never be committed. Each developer provides their own legally obtained copy.

---

## Prerequisites Check

Run these to verify your baseline tools are in place:

```bash
which git python3 make
python3 --version
make --version
git --version
```

**Status at start:**
- git: found (`/usr/bin/git`, version 2.43.0)
- python3: found (Python 3.14.0)
- make: found (GNU Make 4.3)
- libpng-dev: already installed
- arm-none-eabi-gcc: NOT FOUND (installed below)
- agbcc: NOT FOUND (built from source below)

---

## Step 1 — Install ARM Toolchain

```bash
sudo apt install binutils-arm-none-eabi build-essential
sudo apt install gcc-arm-none-eabi
```

Verify:

```bash
arm-none-eabi-gcc --version
```

---

## Step 2 — Clone pokefirered

```bash
git clone https://github.com/pret/pokefirered.git ~/Desktop/projects/pokemon-mod-rom
```

This clones the full reverse-engineered FireRed source directly into your project directory.

---

## Step 3 — Build and Install agbcc

`agbcc` is the original GBA C compiler used to produce byte-perfect builds that match the real ROM.

```bash
git clone https://github.com/pret/agbcc.git /tmp/agbcc
cd /tmp/agbcc
./build.sh
./install.sh ~/Desktop/projects/pokemon-mod-rom
```

---

## Step 4 — Provide the Base ROM

Place your legally dumped FireRed ROM in the project root, named exactly:

```
pokefirered.gba
```

The build system uses it to extract assets and verify your compiled output matches the original binary.

---

## Step 5 — Build the ROM

```bash
cd ~/Desktop/projects/pokemon-mod-rom
make
```

If successful, this produces `pokefirered.gba` (rebuilt from source). Load it in a GBA emulator to test. A clean build that matches the original SHA1 confirms your environment is working correctly.

---

## Step 6 — Initialize Git for Your Mod

```bash
cd ~/Desktop/projects/pokemon-mod-rom
git remote set-url origin <your-github-repo-url>
```

> **Important:** Never commit the `.gba` ROM file — it's already covered by `.gitignore`.
> Push source code and patch files only.

---

## Notes

- The decomp source lives in `src/` — this is where most gameplay programming happens.
- Data (moves, Pokemon stats, maps) lives in `data/`.
- Graphics assets live in `graphics/`.
- The build entry point is the `Makefile` at the project root.
- The built ROM output is `pokefirered.gba` — load this in your emulator after each `make`.
- Community resources: https://github.com/pret/pokefirered/wiki

---

## Optional Tools

See [TOOLS.md](TOOLS.md) for setup instructions for recommended tools including:

- **Porymap** — visual map editor for placing NPCs and reading tile data (strongly recommended before doing any map work)

---

*Last updated: 2026-05-18*
