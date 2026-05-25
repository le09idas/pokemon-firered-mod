# Lesson 06 — Entering the Logic Layer: Type Effectiveness

**Level:** Intermediate
**Status:** Complete

---

## The Turning Point

Every lesson so far has been a `.h` file or a `.json` file — pure data. Numbers in
tables. You changed values, the engine read them, things changed in-game.

Starting now you'll be working in `.c` files. This is where behavior actually lives.
The distinction matters:

```
.h files  → declarations, data tables, constants. The "what."
.c files  → logic, functions, behavior. The "how."
```

Your first `.c` file is a gentle entry — the type effectiveness table lives in C
but looks almost identical to the data tables you've already been editing. The real
lesson here is two things at once: the type system, and **how to navigate a C codebase**.

---

## How to Find Anything in This Codebase

This skill is more important than any single file. When you want to change something
and don't know where it is, there are two moves:

**Move 1 — grep for the name:**
```bash
grep -rn "gTypeEffectiveness" src/
```
`-r` = recursive through all subdirectories. `-n` = show line numbers. This finds
every reference to that symbol. The definition will be the one that looks like
`const u8 gTypeEffectiveness[...] =`.

**Move 2 — grep for what you're looking for, not just the name:**
```bash
grep -rn "TYPE_FIRE, TYPE_WATER" src/
```
When you don't know what something is called, search for content you'd expect to
find near it. Works for constants, strings, comments — anything.

You'll use these two moves constantly from here on. Before asking "where is X?",
grep for it.

---

## The Type Effectiveness Table

File: `src/battle_main.c`, line 312

```c
const u8 gTypeEffectiveness[336] =
{
    TYPE_NORMAL,   TYPE_ROCK,   TYPE_MUL_NOT_EFFECTIVE,
    TYPE_NORMAL,   TYPE_STEEL,  TYPE_MUL_NOT_EFFECTIVE,
    TYPE_FIRE,     TYPE_FIRE,   TYPE_MUL_NOT_EFFECTIVE,
    TYPE_FIRE,     TYPE_WATER,  TYPE_MUL_NOT_EFFECTIVE,
    TYPE_FIRE,     TYPE_GRASS,  TYPE_MUL_SUPER_EFFECTIVE,
    ...
    TYPE_ENDTABLE,
};
```

Every row is three values: **attacker type, defender type, multiplier**.

The multipliers are defined in `include/battle_main.h`:

| Constant | Value | Meaning |
|---|---|---|
| `TYPE_MUL_NO_EFFECT` | 0 | Immune — 0× damage |
| `TYPE_MUL_NOT_EFFECTIVE` | 5 | Resisted — 0.5× damage |
| `TYPE_MUL_NORMAL` | 10 | Normal — 1× (not listed) |
| `TYPE_MUL_SUPER_EFFECTIVE` | 20 | Super effective — 2× damage |

**The most important thing:** normal effectiveness (1×) is **not listed at all**.
The engine assumes normal unless a row says otherwise. The table is sparse —
it only stores exceptions. That's why the array is 336 bytes, not 18×18=324
entries for every possible combination.

The table ends with `TYPE_ENDTABLE` (0xFF) as a sentinel — the engine reads rows
until it hits that value and stops.

---

## How the Engine Reads It

In `src/battle_script_commands.c` around line 1305, there's a loop:

```c
while (TYPE_EFFECT_ATK_TYPE(i) != TYPE_ENDTABLE)
{
    if (TYPE_EFFECT_ATK_TYPE(i) == moveType)
    {
        if (TYPE_EFFECT_DEF_TYPE(i) == defType)
            // apply the multiplier
    }
    i++;
}
```

It scans every row until it finds a match for the attacking type vs defending type,
then applies the multiplier. If it reaches `TYPE_ENDTABLE` without a match, normal
damage applies. You don't need to change this code — just understand it's what
reads your table.

---

## Assignment

### Task 1 — Change two or three type matchups

File: `src/battle_main.c`

Pick matchups that make your mod feel distinct. Some ideas — pick what fits your
vision, or use your own:

**Make Fire resist Dragon less** (lore: dragons breathe fire, but fire also burns them):
```c
// Add this row — Fire attacks do neutral damage to Dragon
// Simply remove the existing NOT_EFFECTIVE row:
TYPE_FIRE, TYPE_DRAGON, TYPE_MUL_NOT_EFFECTIVE,   // ← delete this line
```

**Make Bug hit Poison super effectively** (bugs eat plants, plants are poisonous):
```c
// Add this row somewhere in the Bug section:
TYPE_BUG, TYPE_POISON, TYPE_MUL_SUPER_EFFECTIVE,
```

**Make Ghost immune to Normal instead of just resisted** (Ghost already has quirks):
Look at what's there and consider whether the current matchups feel right.

You're not rewriting game logic. You're editing a lookup table. The engine handles
everything else automatically.

### Task 2 — Navigate to something you haven't seen yet

Using only `grep`, find where the game checks if a Pokemon can learn a move via HM
(can't forget HM moves). The relevant function will be somewhere in `src/pokemon.c`
or `src/item_use.c`.

```bash
grep -rn "HM\|CanForget\|IsHM" src/ --include="*.c" | head -20
```

You don't need to change anything — just find it, read the function, and describe
in your completion notes what you found and how the check works. This is the
reverse engineering part of the lesson.

---

## What to observe

- Adding a row is how you make a matchup more effective. Removing a row returns
  it to normal (1×). Changing the third value changes the multiplier.
- The rows have no required ordering — the engine scans all of them linearly.
  Keep attacker types grouped together for readability, but the engine doesn't care.
- Don't remove `TYPE_ENDTABLE` from the end. Ever. The engine will read past the
  array into garbage memory until it randomly finds 0xFF.
- The array is declared as exactly 336 bytes. If you add rows, the size declaration
  doesn't update automatically — but in practice the compiler handles this if you
  remove the explicit size or just let it calculate. Watch for compiler warnings.

---

## Completion Notes

**Type matchup changes:**
- Removed FIRE vs WATER resistance — Fire now deals full damage to Water types
- Added FIRE vs GROUND super effective — lore: fire dries earth
- Changed WATER vs WATER to NO_EFFECT (immune) — intentional: water added to water is just more water
- Removed ICE vs WATER resistance — Ice now normal vs Water
- Added ICE vs FIRE as NO_EFFECT (immune) — intentional: fire overwhelms ice, Ice attacks can't hurt Fire types
- Added FIRE vs FLYING super effective — fire ignites birds, added post-review
- Changed POISON vs POISON to NO_EFFECT (immune) — Poison immune to Poison, lore-solid

**HM investigation findings:**
- Key finding: `pokemon_summary_screen.c:3766` — `PokeSum_CanForgetSelectedMove()` calls `IsMoveHm(move)` and returns FALSE if true; this is the actual gate
- Supporting: `quest_log_events.c`, `battle_script_commands.c:5210`, `item.c:67/495/508`, `load_save.c:22/224/256`
- Note: `menu2.c:15` was grep noise — unrelated UI coordinate comment
