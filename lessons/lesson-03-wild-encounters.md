# Lesson 03 — Wild Encounters: Controlling What Lives Where

**Level:** Beginner
**Status:** In Progress

---

## The Concept

Every patch of grass, body of water, and fishing spot in the game has a table that
says exactly which Pokemon can appear there, at what levels, and how often. This
lesson is about owning that table.

This is still the data layer — but with a twist. There are two files involved and
only one of them you're allowed to touch.

---

## The Two-File Trap

Open this file and read the first line:

```
src/data/wild_encounters.h
```

```c
// DO NOT MODIFY THIS FILE! It is auto-generated from
// src/data/wild_encounters.json and Inja template src/data/wild_encounters.json.txt
```

This is a generated file. `make` builds it automatically from the JSON source.
If you edit the `.h` directly, your changes get wiped on the next build.

**The file you edit is:**

```
src/data/wild_encounters.json
```

This is the source of truth. Edit it, run `make`, and the `.h` regenerates itself.
This pattern — JSON as the human-editable source, `.h` as the machine-generated
output — shows up in several places in this codebase. Always check for the
auto-generated warning before editing a data file.

---

## The Slot System

Each area's land encounters have exactly **12 slots**. The slot you put a Pokemon in
determines how often players see it. The encounter rates are fixed and baked into
the engine:

| Slots | Encounter chance |
|---|---|
| 0 and 1 | 20% each — most common, seen constantly |
| 2 and 3 | 10% each |
| 4 and 5 | 10% each |
| 6 and 7 | 5% each |
| 8 and 9 | 4% each |
| 10 and 11 | 1% each — rare, requires patience |

You don't set the percentages directly. You set the Pokemon, and its rarity comes
from which slot you put it in. Slots 0–1 is Pidgey territory. Slot 10–11 is
"I've been in this grass for 20 minutes" territory.

Here's what Route 1 looks like right now in the JSON:

```json
"base_label": "sRoute1_FireRed",
"land_mons": {
  "encounter_rate": 21,
  "mons": [
    { "min_level": 3, "max_level": 3, "species": "SPECIES_PIDGEY" },    // slot 0  - 20%
    { "min_level": 3, "max_level": 3, "species": "SPECIES_RATTATA" },   // slot 1  - 20%
    { "min_level": 3, "max_level": 3, "species": "SPECIES_PIDGEY" },    // slot 2  - 10%
    { "min_level": 3, "max_level": 3, "species": "SPECIES_RATTATA" },   // slot 3  - 10%
    { "min_level": 2, "max_level": 2, "species": "SPECIES_PIDGEY" },    // slot 4  - 10%
    { "min_level": 2, "max_level": 2, "species": "SPECIES_RATTATA" },   // slot 5  - 10%
    { "min_level": 3, "max_level": 3, "species": "SPECIES_PIDGEY" },    // slot 6  -  5%
    { "min_level": 3, "max_level": 3, "species": "SPECIES_RATTATA" },   // slot 7  -  5%
    { "min_level": 4, "max_level": 4, "species": "SPECIES_PIDGEY" },    // slot 8  -  4%
    { "min_level": 4, "max_level": 4, "species": "SPECIES_RATTATA" },   // slot 9  -  4%
    { "min_level": 5, "max_level": 5, "species": "SPECIES_PIDGEY" },    // slot 10 -  1%
    { "min_level": 4, "max_level": 4, "species": "SPECIES_RATTATA" },   // slot 11 -  1%
  ]
}
```

Notice also `"encounter_rate": 21` — this is the per-step chance of triggering
any encounter at all while in tall grass. It's separate from the slot rarities.
Higher = more frequent encounters overall.

---

## The Level Range

Each slot has `min_level` and `max_level`. When a Pokemon from that slot appears,
the game picks a random level between those two values. Route 1 uses fixed levels
(min == max), but you can spread them:

```json
{ "min_level": 3, "max_level": 6, "species": "SPECIES_EEVEE" }
```

This gives you Eevee anywhere from level 3 to 6. Useful for making encounters
feel less mechanical.

---

## Assignment

Route 1 is just Pidgey and Rattata — two Pokemon, spammed across all 12 slots.
That's fine for vanilla but this is your mod. Redesign Route 1 (and optionally
Route 2) to feel like your game.

### Task 1 — Add variety to Route 1

File: `src/data/wild_encounters.json` (search for `sRoute1_FireRed`)

Replace some of the Pidgey/Rattata slots with other Pokemon. Some guidelines:
- Keep slots 0–1 as the dominant encounter — this defines the "feel" of the route
- Put anything rare or interesting in slots 10–11
- Use `min_level`/`max_level` ranges instead of fixed levels to add texture
- Keep levels low (2–6) since this is the first route

Example: put an Eevee at slot 11 with a level range of 3–5. It'll show up rarely
but finding one will feel like a discovery.

Species constants are all in `include/constants/species.h` — grep for anything
you want to place:

```bash
grep "SPECIES_" include/constants/species.h | grep -i "eevee\|abra\|gastly"
```

### Task 2 — Build and verify

```bash
make
```

Walk in the Route 1 grass and confirm your new encounters appear. If you put
something in slots 10–11 you may need to walk for a while before it shows up —
that's expected.

---

## What to observe

- The `.h` file regenerates automatically on `make`. Open it after building and
  find Route 1 — you'll see your JSON changes reflected as C structs. This is
  what the engine actually reads.
- All 12 slots must be filled. If you remove entries rather than replacing them,
  the build will likely error or the encounter table will be malformed.
- The same slot system applies to water (`water_mons`) and fishing (`fishing_mons`),
  but with fewer slots (5 for water, grouped by rod type for fishing).

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
