# Lesson 05 — Evolutions: When and How Pokemon Change

**Level:** Intermediate
**Status:** In Progress

---

## The Concept

Every Pokemon's evolution conditions live in one table:

```
src/data/pokemon/evolution.h
```

The format is compact and readable. Each entry is:

```c
[SPECIES_BULBASAUR] = {{EVO_LEVEL, 16, SPECIES_IVYSAUR}},
```

Three values inside the inner braces:
1. **Evolution method** — how it triggers
2. **Parameter** — the level, item, or condition depending on the method
3. **Target species** — what it evolves into

Multiple evolutions (branching) use multiple inner entries:

```c
[SPECIES_GLOOM] = {{EVO_ITEM, ITEM_LEAF_STONE, SPECIES_VILEPLUME},
                   {EVO_ITEM, ITEM_SUN_STONE, SPECIES_BELLOSSOM}},
```

---

## All Evolution Methods

Defined in `include/constants/pokemon.h`:

| Constant | Parameter | Triggers when... |
|---|---|---|
| `EVO_LEVEL` | level number | Pokemon reaches that level |
| `EVO_ITEM` | item constant | Item is used on Pokemon |
| `EVO_TRADE` | `0` | Pokemon is traded |
| `EVO_TRADE_ITEM` | item constant | Traded while holding that item |
| `EVO_FRIENDSHIP` | `0` | Levels up with friendship ≥ 220 |
| `EVO_FRIENDSHIP_DAY` | `0` | Same, but only during the day |
| `EVO_FRIENDSHIP_NIGHT` | `0` | Same, but only at night |
| `EVO_LEVEL_ATK_GT_DEF` | level number | Levels up with Attack > Defense |
| `EVO_LEVEL_ATK_EQ_DEF` | level number | Levels up with Attack = Defense |
| `EVO_LEVEL_ATK_LT_DEF` | level number | Levels up with Attack < Defense |
| `EVO_BEAUTY` | beauty value | Levels up with beauty ≥ that value |

---

## The Trade Evolution Problem

Several Pokemon in Gen 1 only evolve by trading:

```c
[SPECIES_KADABRA]  = {{EVO_TRADE, 0, SPECIES_ALAKAZAM}},
[SPECIES_HAUNTER]  = {{EVO_TRADE, 0, SPECIES_GENGAR}},
[SPECIES_GRAVELER] = {{EVO_TRADE, 0, SPECIES_GOLEM}},
[SPECIES_MACHOKE]  = {{EVO_TRADE, 0, SPECIES_MACHAMP}},
```

On an emulator playing solo, you can't trade. These Pokemon are permanently
stuck in their middle forms unless you change the evolution method. This is one
of the most common and practical changes in any FireRed mod.

The fix is simple — swap `EVO_TRADE` for `EVO_LEVEL` and pick a level:

```c
[SPECIES_KADABRA]  = {{EVO_LEVEL, 36, SPECIES_ALAKAZAM}},
```

---

## Assignment

### Task 1 — Fix all trade evolutions

File: `src/data/pokemon/evolution.h`

Find and convert all four trade-evolution lines. Pick levels that feel balanced
relative to when you'd normally get those Pokemon:

- Kadabra (Abra evolves at 16 → Kadabra, so ~36 for Alakazam feels right)
- Haunter (Gastly → 25 → Haunter, so ~36–38 for Gengar)
- Graveler (Geodude → 25 → Graveler, so ~36–40 for Golem)
- Machoke (Machop → 28 → Machoke, so ~36–40 for Machamp)

Also check for `EVO_TRADE_ITEM` entries (Politoed, Slowking, etc.) and decide
whether to convert those too.

### Task 2 — Tune the starter evolution levels

The starters currently evolve at 16 → 36. That's vanilla. In your mod the starters
are already buffed, so consider whether you want them to evolve earlier (more
rewarding) or later (longer mid-form, higher payoff). 

Change the levels in all six entries (Bulbasaur, Ivysaur, Charmander, Charmeleon,
Squirtle, Wartortle) to fit your difficulty vision. Changing the first evolution
changes early-game pacing significantly — keep that in mind.

### Task 3 — Add a branching evolution to one Pokemon (optional but interesting)

Pick any Pokemon that currently has a single evolution and give it a second path.
The format from Gloom is your template:

```c
[SPECIES_EEVEE] = {{EVO_ITEM, ITEM_FIRE_STONE,   SPECIES_FLAREON},
                   {EVO_ITEM, ITEM_WATER_STONE,  SPECIES_VAPOREON},
                   {EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_JOLTEON}},
```

Eevee already has this — it's a good reference. Try giving a Pokemon like Growlithe
a level-based alternative to its Fire Stone evolution, so players who don't have
the stone yet aren't stuck.

---

## What to observe

- The parameter field means different things for different methods. For `EVO_LEVEL`
  it's a level number. For `EVO_ITEM` it's an item constant (find them in
  `include/constants/items.h`). For `EVO_TRADE` and `EVO_FRIENDSHIP` it's always `0`
  — the method itself carries the full meaning, no extra parameter needed.
- `EVOS_PER_MON` caps how many branching paths one Pokemon can have. It's defined
  in the engine — you'll hit a compile error if you add more entries than it allows.
  In Gen 3 this is typically 5, so you have headroom.
- Changing evolution levels does **not** automatically change the moves learned at
  evolution. Those come from the learnset. A Pokemon that evolves at level 20 instead
  of 16 will simply learn its post-evolution learnset moves at the levels already
  defined — the learnset doesn't shift with the evolution level.

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
