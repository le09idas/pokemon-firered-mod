# Lesson 08 — Event Scripting and Dialogue: Making the World Yours

**Level:** Intermediate
**Status:** In Progress

---

## The Concept

Every NPC conversation, sign, cutscene, and triggered event in the game is driven
by a scripting system — a custom GBA assembly-like language that runs separately
from the C engine. It's not C. It's not JSON. It's its own thing, and it's powerful.

Each map has its own folder under `data/maps/` containing these files:

| File | Purpose |
|---|---|
| `text.inc` | All dialogue strings for this map |
| `scripts.inc` | Event logic — what happens when things are triggered |
| `events.inc` | NPC placement, warp points, trigger zones (**auto-generated**) |
| `map.json` | Source of truth for events.inc — edit this, not events.inc |

The split between `text.inc` and `scripts.inc` mirrors the data/logic split you
already know. Text is data. Scripts are behavior.

---

## Text Formatting

Open `data/maps/PalletTown/text.inc`. Every string ends with `$` — that's the
string terminator. The formatting codes inside strings:

| Code | Meaning |
|---|---|
| `\n` | New line within the same message box |
| `\l` | New line, second line of a two-line box |
| `\p` | Next page — player must press A to continue |
| `$` | End of string (required on every string) |
| `{PLAYER}` | Substituted with the player's name at runtime |
| `{RIVAL}` | Substituted with the rival's name |
| `{STR_VAR_1}` | Dynamic variable — filled by script before msgbox |

Example from Pallet Town:

```
PalletTown_Text_OakDontGoOut::
    .string "OAK: Hey! Wait!\n"
    .string "Don't go out!$"
```

Two `.string` lines that get concatenated. The `\n` puts "Don't go out!" on the
second line of the same box. Note the `$` on the last line only.

---

## Script Commands

Open `data/maps/PalletTown/scripts.inc`. The commands read almost like English:

```
PalletTown_EventScript_FatMan::
    msgbox PalletTown_Text_CanStoreItemsAndMonsInPC, MSGBOX_NPC
    end
```

This is the "Fat Man" NPC near the PC. When you talk to him:
1. `msgbox` — display the text, wait for A, auto-close (MSGBOX_NPC style)
2. `end` — script finishes

Compare to a more involved script:

```
PalletTown_EventScript_SignLadyDone::
    applymovement LOCALID_PALLET_SIGN_LADY, Common_Movement_FacePlayer
    waitmovement 0
    msgbox PalletTown_Text_RaisingMonsToo
    release
    end
```

1. `applymovement` — make the NPC turn to face the player
2. `waitmovement 0` — wait until all movements finish
3. `msgbox` — show dialogue (no MSGBOX_NPC = manual close handled elsewhere)
4. `release` — give control back to the player
5. `end` — script finishes

### Key commands you'll use

| Command | What it does |
|---|---|
| `msgbox <text>, MSGBOX_NPC` | Show text, auto-close, release player |
| `msgbox <text>, MSGBOX_SIGN` | Show text in sign-style box |
| `msgbox <text>` | Show text, you control close/release |
| `closemessage` | Close the message box manually |
| `lock` / `release` | Lock/release the NPC you're talking to |
| `lockall` / `releaseall` | Lock/release all NPCs on the map |
| `applymovement <id>, <movement>` | Make an NPC or player move |
| `waitmovement 0` | Wait for all movements to complete |
| `setflag <FLAG>` | Set a flag (marks something as done, permanently) |
| `setvar <VAR>, <value>` | Set a variable to a value |
| `goto <label>` | Jump to another script label |
| `call <label>` | Jump and return (like a function call) |
| `end` | End the script |

### `lock` vs `lockall`

`lock` freezes only the NPC you're talking to. `lockall` freezes every NPC on
the map. Simple NPCs with one-line dialogue use `lock`/`release`. Cutscenes use
`lockall`/`releaseall`.

---

## The events.inc Warning

```
data/maps/PalletTown/events.inc
```

First line: `@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/PalletTown/map.json`

Same pattern as `wild_encounters.h`. The NPC placement comes from `map.json`.
If you want to move an NPC or add one, you edit `map.json`. For this lesson
you won't need to — you're only changing what existing NPCs say.

---

## Assignment

### Task 1 — Personalize three dialogues in Pallet Town

File: `data/maps/PalletTown/text.inc`

Change at minimum:
- The town sign (`PalletTown_Text_TownSign`) — make it yours
- The Fat Man PC dialogue (`PalletTown_Text_CanStoreItemsAndMonsInPC`) — rewrite it
- One other dialogue of your choice

Rules:
- Keep `\n` to break lines at roughly 18–20 characters — the text box only fits two lines
- Keep `\p` between long thoughts — don't let a wall of text fly by without a pause
- Every string must end with `$`

### Task 2 — Read and trace a script

In `data/maps/PalletTown/scripts.inc`, find `PalletTown_EventScript_SignLady`.
It branches based on the value of `VAR_MAP_SCENE_PALLET_TOWN_SIGN_LADY`. Read it
and in your completion notes, describe in plain English what happens when:
- The value is `0`
- The value is `1`
- The value is `2`

You don't need to change anything. This is a reading exercise — tracing conditional
logic in a script you've never touched.

### Task 3 — Change a sign in Viridian City or Route 1

Pick one sign on Route 1 or in Viridian City and rewrite it. Find the map folder:

```
data/maps/Route1/
data/maps/ViridianCity/
```

Open its `text.inc`, find a sign string, change it. These are simple `MSGBOX_SIGN`
scripts — one line of script, one line of text. Good practice before touching
more complex NPC scripts.

```bash
make
```

Walk through Pallet Town and read your new dialogue in-game.

---

## What to observe

- Script labels always end with `::` (double colon). Single colon is an address
  reference. Double colon means "this label is exported and can be referenced
  from other files." You'll always use `::` for new scripts.
- `MSGBOX_NPC` handles `lock`/`release` automatically. If you use plain `msgbox`
  you must `lock` before and `release` after, or the player will be able to
  walk away mid-dialogue.
- `{PLAYER}` and `{RIVAL}` only work inside strings — not in script logic.
  The substitution happens at the text rendering layer.
- Flags are permanent (saved to the save file). Variables can be temporary or
  permanent depending on which VAR_ prefix they use. You'll use flags more in
  later lessons when you start scripting custom events.

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
