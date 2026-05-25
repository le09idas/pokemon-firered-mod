# Lesson 09 — Writing a Custom Script From Scratch

**Level:** Intermediate → Advanced
**Status:** In Progress

---

## The Concept

In Lesson 8 you read and modified existing scripts. This lesson you write one
from scratch. No copy-paste — you'll build the logic yourself, using existing
scripts only as reference for syntax.

The target is the Fat Man NPC in Pallet Town. Right now he says one line about PCs
and that's it, forever. You'll give him a two-state script:

- **First time** you talk to him: he gives the PC explanation, then a follow-up line
- **Every time after**: he says something different — he's been thinking about it

This requires a **flag** — a persistent boolean stored in the save file that
remembers whether you've spoken to him before.

---

## Flags: Temporary vs Permanent

There are two kinds of flags:

**Temporary (`FLAG_TEMP_1` through `FLAG_TEMP_A`):**
Stored in RAM, cleared every time you change maps. Good for "did I trigger this
thing during this visit" — not useful for "did I ever talk to this NPC."

**Permanent (everything else):**
Stored in the save file. Once set, they stay set across saves, loads, and map
transitions. This is what you want for NPC state.

At the bottom of `include/constants/flags.h` there are a block of unnamed permanent
flags reserved for custom use:

```c
#define FLAG_0x8F7    (SYS_FLAGS + 0xF7)
#define FLAG_0x8F8    (SYS_FLAGS + 0xF8)
// ... etc
```

These are yours to use. To make the script readable, define a named alias at the
top of `data/maps/PalletTown/scripts.inc` using `.equ`:

```asm
.equ FLAG_MET_FAT_MAN, FLAG_0x8F7
```

Now you can use `FLAG_MET_FAT_MAN` in your script and it maps to that flag slot.
Pick any unused `FLAG_0x8__` value — just be consistent and don't reuse the same
flag for two different purposes across the game.

---

## The Script Commands You Need

```asm
goto_if_set <FLAG>, <label>    @ jump to label if flag is set
setflag <FLAG>                  @ permanently set a flag
lock                            @ freeze the NPC you're talking to
release                         @ release the NPC
msgbox <text>, MSGBOX_NPC       @ show text, auto-release
end                             @ end the script
```

---

## The Script to Write

Add this to `data/maps/PalletTown/scripts.inc`, replacing the existing
`PalletTown_EventScript_FatMan` entry:

```asm
PalletTown_EventScript_FatMan::
    lock
    goto_if_set FLAG_MET_FAT_MAN, PalletTown_EventScript_FatManReturn
    setflag FLAG_MET_FAT_MAN
    msgbox PalletTown_Text_CanStoreItemsAndMonsInPC, MSGBOX_NPC
    release
    end

PalletTown_EventScript_FatManReturn::
    msgbox PalletTown_Text_FatManReturn, MSGBOX_NPC
    release
    end
```

**Walk through the logic:**
1. `lock` — freeze the NPC so he faces you while talking
2. `goto_if_set` — if the flag is already set, skip to the return script
3. `setflag` — set the flag NOW, before the msgbox (so even if something goes wrong, it's recorded)
4. `msgbox` — show the first-time dialogue
5. `release` + `end` — done

On every subsequent talk: the flag is set, so we jump straight to `FatManReturn`.

---

## The Text to Add

Add a new entry to `data/maps/PalletTown/text.inc` for the return dialogue:

```asm
PalletTown_Text_FatManReturn::
    .string "You know, I've been thinking…\p"
    .string "If POKéMON can be stored as data,\n"
    .string "what even ARE they?\p"
    .string "Don't tell OAK I said that.$"
```

Write whatever you want him to say — this is just an example. Keep line lengths
under 18–20 characters, use `\p` between thoughts, end with `$`.

---

## Assignment

### Task 1 — Define the flag alias

At the top of `data/maps/PalletTown/scripts.inc`, find the existing `.equ` line:

```asm
.equ SIGN_LADY_READY, VAR_TEMP_2
```

Add yours below it:

```asm
.equ FLAG_MET_FAT_MAN, FLAG_0x8F7
```

### Task 2 — Write the script

Replace `PalletTown_EventScript_FatMan` in `scripts.inc` with the two-label
version above. Write the return dialogue yourself — don't use the example text.

### Task 3 — Add the text entry

Add `PalletTown_Text_FatManReturn` to `text.inc`. Put it near the existing Fat Man
text entry so it's easy to find later.

### Task 4 — Build and test

```bash
make
```

Talk to the Fat Man twice. First time: PC dialogue. Second time: your new text.
Leave the map and come back — confirm the second state persists after map transition
(proof the permanent flag is working, not a temp flag).

---

## What to observe

- `setflag` before `msgbox` is intentional. If you set the flag after, and the
  game crashes or is reset during the msgbox, the flag never gets set and the
  player sees the first-time dialogue again. Set state before showing the result.
- The `.equ` alias is cosmetic — the assembler replaces it with the raw value at
  compile time. It doesn't create anything new, it just makes your script readable.
- Label naming follows the map prefix convention: `PalletTown_EventScript_` for
  scripts, `PalletTown_Text_` for text. Stick to this — when the project has
  hundreds of scripts, the prefix is the only thing keeping them organized.
- `MSGBOX_NPC` handles `release` internally when the player presses A. But you
  still need the explicit `release` before `end` in case the engine path doesn't
  go through the msgbox (e.g. branching). It's a safety habit.

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
