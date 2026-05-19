# Lesson 01 — The Data Layer: Buff the Starters

**Level:** Beginner
**Status:** In Progress

---

## The Map of the Kingdom

Before you touch a single line, you need to understand how this codebase is organized. There are two fundamentally different layers:

```
DATA LAYER    → numbers, tables, text. No logic.
LOGIC LAYER   → C code that reads those tables and acts on them.
```

This is the most important mental model in ROM hacking. 90% of what players notice (stats, moves, encounters, dialogue) lives in the data layer. You rarely need to touch logic until you want to invent something that never existed.

Here's where things live:

| What | Where |
|---|---|
| Pokemon base stats, types, abilities | `src/data/pokemon/species_info.h` |
| Move power, accuracy, PP, type | `src/data/battle_moves.h` |
| Level-up move learnsets | `src/data/pokemon/level_up_learnsets.h` |
| Wild Pokemon per route | `src/data/wild_encounters.h` |
| Trainer teams | `src/data/trainer_parties.h` |
| Item definitions | `src/data/items.h` |
| NPC dialogue | `src/data/text/` |
| Event scripts (NPC behavior) | `data/scripts/` |
| Battle logic (move effects) | `src/battle_script_commands.c` |
| Battle AI | `src/battle_ai_script_commands.c` |

The rule of thumb: if it's a number someone at Game Freak typed into a spreadsheet, it's in `src/data/`. If it's behavior someone had to think about, it's in `src/*.c`.

---

## Background: How the Rival Works

Before touching any file, understand the chain:

The rival always picks the starter that **beats yours**:

| You pick | Rival gets |
|---|---|
| Bulbasaur | Charmander |
| Charmander | Squirtle |
| Squirtle | Bulbasaur |

The rival's Oak's Lab party is defined in `src/data/trainer_parties.h` around line 3720.
Each entry looks like this:

```c
static const struct TrainerMonNoItemDefaultMoves sParty_RivalOaksLabSquirtle[] = {
    {
        .iv = 0,
        .lvl = 5,
        .species = SPECIES_SQUIRTLE,
    },
};
```

Notice `.party = NO_ITEM_DEFAULT_MOVES(...)` — this means the rival's starter uses
**whatever moves the species knows at that level from its learnset**. There is no hardcoded
move list here. This is the key insight: **the learnset is the single source of truth for
both the player's starter and the rival's starter.**

The rival already has smart AI flags set:

```c
.aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
```

`AI_SCRIPT_CHECK_VIABILITY` means the AI will prefer moves that deal more damage —
including super-effective moves. So if the rival's starter has a STAB damaging move
in its learnset, the AI will use it aggressively. You don't need to touch the AI.

---

## Assignment

Three tasks, all in the data layer. No logic changes needed.

### Task 1 — Buff base stats for all 3 starters

File: `src/data/pokemon/species_info.h`

Find `[SPECIES_BULBASAUR]`, `[SPECIES_CHARMANDER]`, and `[SPECIES_SQUIRTLE]`.
Bump whatever stats feel right — Attack, Speed, HP. Keep changes modest so the
game stays playable (adding 10-20 points to a stat is a good starting range).

### Task 2 — Give each starter a powerful move at level 1

File: `src/data/pokemon/level_up_learnsets.h`

The current level-1 moves are weak (Tackle, Scratch). The starters don't get their
first STAB damaging move until level 7-13. Move it to level 1 so the rival battle
has teeth.

Find each learnset and add or move a move to level 1:

```c
// Before — Bulbasaur
static const u16 sBulbasaurLevelUpLearnset[] = {
    LEVEL_UP_MOVE( 1, MOVE_TACKLE),
    LEVEL_UP_MOVE( 4, MOVE_GROWL),
    LEVEL_UP_MOVE(10, MOVE_VINE_WHIP),   // ← this shows up too late
    ...

// After — add Vine Whip at level 1
static const u16 sBulbasaurLevelUpLearnset[] = {
    LEVEL_UP_MOVE( 1, MOVE_TACKLE),
    LEVEL_UP_MOVE( 1, MOVE_VINE_WHIP),   // ← now the rival has it too
    LEVEL_UP_MOVE( 4, MOVE_GROWL),
    ...
```

Do the same for Charmander (Ember, normally level 7) and Squirtle (Water Gun, normally level 13).

Move names are constants — if you're not sure of the exact name, grep for it:

```bash
grep -r "MOVE_VINE\|MOVE_EMBER\|MOVE_WATER_GUN" include/constants/moves.h
```

### Task 3 — Build and test

```bash
make
```

Load `pokefirered.gba`, start a new game, and pick any starter. When you battle the
rival in Oak's lab, watch the AI — it should lead with or strongly favor the
super-effective STAB move. Both your starter and the rival's starter should feel
noticeably stronger than vanilla.

---

## What to observe

- Multiple `LEVEL_UP_MOVE(1, ...)` entries on the same level is valid — Pokemon can
  know multiple moves from the start.
- The learnset change affects **every** Bulbasaur/Charmander/Squirtle in the game,
  not just the starter. If a trainer later has one, it'll have the move too.
- Named constants like `MOVE_VINE_WHIP` and `SPECIES_BULBASAUR` are defined in
  `include/constants/`. When you see an unfamiliar constant, that's where to look.

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
