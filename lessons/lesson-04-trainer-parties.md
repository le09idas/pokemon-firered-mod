# Lesson 04 — Trainer Parties: Shaping the Difficulty Curve

**Level:** Beginner → Intermediate
**Status:** Complete

---

## The Concept

Wild encounters fill the world. Trainer parties shape the *challenge*. Every trainer
in the game — from the first kid on Route 1 to the Champion — has a party defined
in one file:

```
src/data/trainer_parties.h
```

This lesson introduces two things: the two party struct types, and the `.iv` field
that quietly controls how strong a trainer's Pokemon actually are.

---

## Two Struct Types

You've already seen both of these in earlier lessons. Now you need to understand
when each is used.

### `TrainerMonNoItemDefaultMoves`

```c
static const struct TrainerMonNoItemDefaultMoves sParty_RivalOaksLabSquirtle[] = {
    {
        .iv = 0,
        .lvl = 5,
        .species = SPECIES_SQUIRTLE,
    },
};
```

No moves specified. The Pokemon uses whatever moves it knows at that level from
its learnset. This is what the rival uses in Oak's Lab — which is why your learnset
changes from Lesson 1 automatically applied there.

### `TrainerMonNoItemCustomMoves`

```c
static const struct TrainerMonNoItemCustomMoves sParty_RivalRoute22EarlySquirtle[] = {
    {
        .iv = 50,
        .lvl = 9,
        .species = SPECIES_SQUIRTLE,
        .moves = {MOVE_TACKLE, MOVE_TAIL_WHIP, MOVE_NONE, MOVE_NONE},
    },
};
```

Moves are hardcoded. The learnset is **ignored**. This trainer's Squirtle will
always use exactly those four moves regardless of what you put in the learnset.

This is why the rival at Route 22 still uses Tackle and Tail Whip — even though
you gave Squirtle Bubble at level 4 back in Lesson 1. His party is custom moves,
so your learnset change didn't reach him. You have to update the party directly.

**The rule:** default moves = learnset drives it. Custom moves = you drive it.
Gym leaders and important battles use custom moves so the designer has full control.

---

## The `.iv` Field

IVs (Individual Values) determine how strong a Pokemon's stats are on top of its
base stats. In the player's party, IVs are randomly rolled. For trainers, they're
set directly in the party struct.

| `.iv` value | Effect |
|---|---|
| `0` | Minimum stats — weakest possible for that level |
| `31` | Roughly "average" for most uses |
| `50` (or `100` for older entries) | Above average — a noticeable step up |
| `255` | Maximum — elite-tier strength |

Brock uses `.iv = 0` — his Geodude and Onix are intentionally weak because you're
meant to beat them at the start of the game. The rival at Route 22 steps up to
`.iv = 50`. Late-game gym leaders and the rival in his final battles use higher
values still.

This is the primary difficulty knob for trainers, separate from level. A level 14
Onix with `.iv = 0` is significantly weaker than a level 14 Onix with `.iv = 100`.

---

## Assignment

Two tasks. Together they close the loop on the rival changes from Lesson 1 and
let you start shaping the gym difficulty curve.

### Task 1 — Fix the rival's Route 22 battle

File: `src/data/trainer_parties.h`, around line 3744

The rival at Route 22 has custom moves that don't reflect your Lesson 1 changes.
Update all three variants (Squirtle, Bulbasaur, Charmander) to give the rival's
starter the STAB move you added:

```c
// Example — if player picked Charmander, rival has Squirtle:
.moves = {MOVE_TACKLE, MOVE_TAIL_WHIP, MOVE_BUBBLE, MOVE_NONE},
```

While you're there, bump the `.iv` on the rival's starter from 50 to something
higher — he should be getting stronger as the game progresses.

### Task 2 — Redesign Brock

File: `src/data/trainer_parties.h`, around line 5604

Vanilla Brock is famously easy. His Geodude and Onix both use `.iv = 0` and have
weak moves. Make him a real fight:

- Raise `.iv` on both Pokemon
- Give Onix a move that isn't just Bind and Tackle — look at what Rock-type moves
  exist by searching:
  ```bash
  grep "MOVE_ROCK\|MOVE_SAND\|MOVE_MUD" include/constants/moves.h
  ```
- Optionally add a third Pokemon (just copy the struct format and add another entry)

You have full control. Keep his level range (12–14) but make the fight feel
like it requires a strategy.

---

## What to observe

- When you add or change moves in a `CustomMoves` struct, you must always fill
  all four move slots. Use `MOVE_NONE` for empty slots — never leave the array
  short or it will compile incorrectly.
- There are also `WithItem` variants of these structs (`TrainerMonWithItemCustomMoves`)
  for trainers that give their Pokemon held items. You'll see these on later gym
  leaders and the rival's final battles. Same format, just adds a `.heldItem` field.
- The `trainers.h` file defines trainer metadata (name, AI flags, which party they use).
  The `trainer_parties.h` file defines the actual Pokemon. They're linked by name —
  `sParty_LeaderBrock` in parties maps to `TRAINER_LEADER_BROCK` in trainers.

---

## Completion Notes

**Rival Route 22 (all three variants):**
- IV: 50 → 65
- Starters now carry their STAB move (Bubble / Absorb / Ember)
- Pidgey upgraded from Tackle/Sand Attack to Tackle/Sand Attack/Gust (unprompted, good call)

**Brock:**
- IV: 0 → 40 across all three Pokemon
- Added second Geodude (lv 13) with Self Destruct as a surprise move
- First Geodude now uses Rollout + Rock Tomb instead of just Tackle + Defense Curl
- Onix gets Rock Blast added alongside Rock Tomb
- Expanded from 2 → 3 Pokemon
