# Lesson 02 — Move Data: What Moves Actually Are

**Level:** Beginner
**Status:** In Progress

---

## The Concept

In Lesson 1 you added moves to learnsets. You picked Absorb, Ember, and Bubble by name
and trusted they'd work. Now we pull back the curtain — what does a move *actually* consist of?

Every move in the game is a struct in one file:

```
src/data/battle_moves.h
```

Here's Ember, the one you gave Charmander:

```c
[MOVE_EMBER] =
{
    .effect = EFFECT_BURN_HIT,
    .power = 40,
    .type = TYPE_FIRE,
    .accuracy = 100,
    .pp = 25,
    .secondaryEffectChance = 10,
    .target = MOVE_TARGET_SELECTED,
    .priority = 0,
    .flags = FLAG_PROTECT_AFFECTED | FLAG_MIRROR_MOVE_AFFECTED,
},
```

And Absorb, what you gave Bulbasaur:

```c
[MOVE_ABSORB] =
{
    .effect = EFFECT_ABSORB,
    .power = 20,
    .type = TYPE_GRASS,
    .accuracy = 100,
    .pp = 20,
    .secondaryEffectChance = 0,
    .target = MOVE_TARGET_SELECTED,
    .priority = 0,
    .flags = FLAG_PROTECT_AFFECTED | FLAG_MIRROR_MOVE_AFFECTED,
},
```

And Bubble, what you gave Squirtle:

```c
[MOVE_BUBBLE] =
{
    .effect = EFFECT_SPEED_DOWN_HIT,
    .power = 20,
    .type = TYPE_WATER,
    .accuracy = 100,
    .pp = 30,
    .secondaryEffectChance = 10,
    .target = MOVE_TARGET_BOTH,
    .priority = 0,
    .flags = FLAG_PROTECT_AFFECTED | FLAG_MIRROR_MOVE_AFFECTED,
},
```

---

## Breaking Down Each Field

**`.effect`** — This is the most important field. It's an integer that points to a
battle script — the actual logic that runs when the move is used. All effects are
defined in `include/constants/battle_move_effects.h`.

Some key ones:
| Effect constant | What it does |
|---|---|
| `EFFECT_HIT` | Pure damage, nothing else |
| `EFFECT_ABSORB` | Deals damage, restores ½ to user (Absorb, Mega Drain, Giga Drain all share this) |
| `EFFECT_BURN_HIT` | Damage + chance to burn |
| `EFFECT_SPEED_DOWN_HIT` | Damage + chance to lower target's speed |
| `EFFECT_POISON_HIT` | Damage + chance to poison |
| `EFFECT_PARALYZE_HIT` | Damage + chance to paralyze |
| `EFFECT_FLINCH_HIT` | Damage + chance to flinch |

Notice: Absorb, Mega Drain, and Giga Drain all use `EFFECT_ABSORB`. The only
difference between them is `.power`. The effect itself is reused. This is the
data/logic split in action — the behavior lives in one place, the numbers vary.

**`.power`** — Base damage. 0 means the move does no damage (status moves).
Standard damaging moves range from 20 (weak) to 150 (nukes like Hyper Beam).

**`.secondaryEffectChance`** — Percentage chance (0–100) for the secondary
effect to trigger. Ember's burn chance is 10%. Bubble's speed drop is also 10%.
This is why those effects feel rare in-game.

**`.target`** — Who gets hit:
| Constant | Meaning |
|---|---|
| `MOVE_TARGET_SELECTED` | One chosen target |
| `MOVE_TARGET_BOTH` | Both opponents (double battle) |
| `MOVE_TARGET_USER` | The user itself |
| `MOVE_TARGET_RANDOM` | Random opponent |

Bubble currently uses `MOVE_TARGET_BOTH` — it hits every opponent in a double battle.
That's actually pretty powerful and most players don't know it.

**`.flags`** — Bitmask of mechanical interactions. Defined in `include/battle.h`.
Common ones:
| Flag | Meaning |
|---|---|
| `FLAG_MAKES_CONTACT` | Triggers contact-based abilities (Static, Rough Skin, etc.) |
| `FLAG_PROTECT_AFFECTED` | Can be blocked by Protect/Detect |
| `FLAG_MIRROR_MOVE_AFFECTED` | Can be copied by Mirror Move |
| `FLAG_KINGS_ROCK_AFFECTED` | King's Rock can add flinch chance |
| `FLAG_HIGH_CRIT_RATIO` | Boosted critical hit rate |

Notice Ember and Absorb do NOT have `FLAG_MAKES_CONTACT`. They're ranged moves —
fire and energy projectiles. Compare with Tackle or Scratch which have it.

---

## Assignment

Your three starter moves are underpowered for what should feel like a punchy early game.
Fix them — still one file, `src/data/battle_moves.h`.

### Task 1 — Buff Absorb's power

`EFFECT_ABSORB` with 20 power means Bulbasaur heals almost nothing. Raise the power
to something that makes the drain feel meaningful. Mega Drain is 40 — somewhere in
that range works. Don't go above 60 or early trainers become trivial.

### Task 2 — Raise secondary effect chances

Ember has a 10% burn chance. Bubble has a 10% speed drop chance. In a short early-game
battle you'll rarely see them trigger. Raise both `secondaryEffectChance` values to
something that makes the effects feel like part of each move's identity — 30% is a
good landmark (still unreliable, but you'll notice it).

### Task 3 — Observe the flag difference (no change required)

Open `src/data/battle_moves.h` and find `MOVE_TACKLE` and `MOVE_SCRATCH`. Compare
their flags to Ember and Absorb. Notice `FLAG_MAKES_CONTACT`. You don't need to
change anything — just read it. Understanding flags will matter a lot in later lessons
when we touch abilities.

### Build and test

```bash
make
```

In-game, watch how often Ember burns and Bubble drops speed now. Fight a few early
trainers and see how Absorb feels with higher power.

---

## The Bridge to the Logic Layer

You've now worked with two data files. Everything so far has been numbers.
At some point you'll want to create an effect that doesn't exist yet —
something no move has ever done. That's when `.effect` stops being a lookup
and starts being something you have to write yourself, in `src/battle_script_commands.c`.

That's a later lesson. For now, file this away: **every `.effect` value is a
named behavior that already exists. Your job as a data modder is to mix and match
them with new numbers.**

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
