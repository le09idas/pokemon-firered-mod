# Lesson 11 — Adding an Overworld Trainer

**Level:** Advanced
**Status:** Complete

---

## The Concept

An overworld trainer is an NPC who battles the player on sight. When the player
walks into their line of sight, the trainer walks up, says something, and the
battle starts. After losing, they stay on the map but don't fight again.

This lesson wires together four separate systems that haven't touched each other
yet:

1. **Trainer data** — who this trainer is and what they use
2. **Trainer ID constant** — the number that connects everything
3. **Map placement** — where they stand and how far they can see
4. **Script** — what they say before, during, and after the battle

You'll add a Youngster trainer to Route 1.

---

## System Overview

```
opponents.h        ←  trainer ID constant (TRAINER_ROUTE1_YOUNGSTER_JAKE = 743)
trainer_parties.h  ←  party data (sParty_Route1YoungsterJake)
trainers.h         ←  trainer struct entry (name, class, pic, party pointer)
map.json           ←  NPC placement (trainer_type, sight range, script name)
scripts.inc        ←  trainerbattle_single command
text.inc           ←  intro, defeat, and post-battle dialogue
```

The engine connects them: the trainer ID is the key. `trainerbattle_single`
takes the ID, looks up the party and defeat flag from it, and runs the battle.
The defeat flag is tracked internally — you don't define it manually.

---

## Step 1 — Add the Trainer ID Constant

Open `include/constants/opponents.h`. At the very bottom, before `#endif`:

```c
#define TRAINER_ROUTE1_YOUNGSTER_JAKE            743
```

Then update `NUM_TRAINERS`:

```c
#define NUM_TRAINERS                             744
```

The comment above this line says there are 25 slots before `MAX_TRAINERS_COUNT`
(768) is exceeded. You're using one.

---

## Step 2 — Add the Party Data

Open `src/data/trainer_parties.h`. At the very end of the file, after
`sParty_CueBallPaxton`, add:

```c
static const struct TrainerMonNoItemDefaultMoves sParty_Route1YoungsterJake[] = {
    {
        .iv = 20,
        .lvl = 5,
        .species = SPECIES_RATTATA,
    },
};
```

One Rattata, level 5, default moves (Tackle + Tail Whip). The `.iv = 20` gives
it slightly better stats than the base iv=0 trainers you've seen — appropriate
for an early-route opponent but not as strong as you made Brock.

---

## Step 3 — Add the Trainer Struct

Open `src/data/trainers.h`. The file ends with the `sParty_CueBallPaxton` entry
followed by `};`. Add your trainer **before** that closing `};`:

```c
    [TRAINER_ROUTE1_YOUNGSTER_JAKE] = {
        .trainerClass = TRAINER_CLASS_YOUNGSTER,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,
        .trainerPic = TRAINER_PIC_YOUNGSTER,
        .trainerName = _("JAKE"),
        .items = {},
        .doubleBattle = FALSE,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE,
        .party = NO_ITEM_DEFAULT_MOVES(sParty_Route1YoungsterJake),
    },
```

The name string has a max length — keep it under 7 characters.

**Field reference:**

| Field | What it does |
|---|---|
| `trainerClass` | Displayed class name ("YOUNGSTER", "BUG CATCHER", etc.) |
| `encounterMusic_gender` | Music when they spot you; also encodes gender for some trainers |
| `trainerPic` | Trainer sprite shown in battle |
| `trainerName` | Name displayed in battle UI |
| `aiFlags` | `AI_SCRIPT_CHECK_BAD_MOVE` is the baseline — avoids self-damaging moves |
| `party` | Points to the party array |

---

## Step 4 — Place the Trainer on the Map

Open `data/maps/Route1/map.json`. In the `object_events` array, after the
existing Boy entry, add:

```json
{
    "local_id": "LOCALID_ROUTE1_JAKE",
    "type": "object",
    "graphics_id": "OBJ_EVENT_GFX_YOUNGSTER",
    "x": 7,
    "y": 14,
    "elevation": 3,
    "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
    "movement_range_x": 1,
    "movement_range_y": 1,
    "trainer_type": "TRAINER_TYPE_NORMAL",
    "trainer_sight_or_berry_tree_id": "4",
    "script": "Route1_EventScript_Jake",
    "flag": "0"
}
```

**What's different from the kid in Lesson 10:**

- `trainer_type: "TRAINER_TYPE_NORMAL"` — this is what makes the engine treat
  them as a battling trainer instead of a regular NPC
- `trainer_sight_or_berry_tree_id: "4"` — sight range in tiles. Jake faces DOWN
  (south), so he can see 4 tiles below him. The player walking north from Pallet
  Town walks into that line of sight.
- `movement_type: "MOVEMENT_TYPE_FACE_DOWN"` — frozen, facing south. The
  direction they face IS their line of sight direction.
- `flag: "0"` — the defeat flag is tracked by the engine using the trainer ID,
  not via the flag field here. Leave this at `"0"`.

**Also:** the existing Boy and Clerk entries in `map.json` don't have `local_id`
fields — they were placed before that convention and aren't referenced by any
script. Your entry needs one because we'll add it to scripts. Don't add
`local_id` to the existing entries; leave them alone.

---

## Step 5 — Write the Script

Add to `data/maps/Route1/scripts.inc`:

```asm
Route1_EventScript_Jake::
    trainerbattle_single TRAINER_ROUTE1_YOUNGSTER_JAKE, Route1_Text_JakeIntro, Route1_Text_JakeDefeat
    msgbox Route1_Text_JakePostBattle, MSGBOX_AUTOCLOSE
    end
```

Walk through the logic:

- `trainerbattle_single` does everything: spots the player, walks toward them,
  shows intro text, runs the battle, shows defeat text when you win.
- If Jake is already defeated (flag set by engine), `trainerbattle_single` skips
  straight to the next line.
- `msgbox ..., MSGBOX_AUTOCLOSE` — shows post-battle dialogue when you talk to
  Jake after defeating him. `MSGBOX_AUTOCLOSE` auto-closes and releases.
- `end` — done.

No `lock`/`release` needed. `trainerbattle_single` handles the player/NPC
locking internally.

---

## Step 6 — Write the Text

Add to `data/maps/Route1/text.inc`:

```asm
Route1_Text_JakeIntro::
    .string "Hey! I'm gonna battle you!\n"
    .string "I've been training all week!$"

Route1_Text_JakeDefeat::
    .string "No way… I lost!\n"
    .string "But I'll keep training!$"

Route1_Text_JakePostBattle::
    .string "You're really strong.\n"
    .string "What's your secret?$"
```

Write your own lines — these are just examples. Rules:
- Keep line lengths under 18–20 characters
- `\n` for second line in the same box
- `\p` for page breaks
- End with `$`

---

## Step 7 — Build and Test

```bash
make
```

Walk north from Pallet Town into Route 1. Jake should spot you and walk toward
you once you enter his 4-tile sight line. Battle him, win, then walk up to him
again — he should say the post-battle line.

If Jake is in the wrong spot (wall, tree, water), adjust `x` by ±1-2 and
rebuild. The x=7 west-side path on Route 1 should be clear, but terrain can vary
by a tile.

---

## What to observe

- The trainer's facing direction = their sight direction. `MOVEMENT_TYPE_FACE_DOWN`
  faces south = sees tiles at higher y values. Route 1's player entry from Pallet
  Town is at the south edge (high y), so facing DOWN catches the player heading
  north.
- `trainer_sight_or_berry_tree_id` is not the trainer's index in the party — it's
  the number of tiles ahead they can see. 3–5 is typical for route trainers.
- `TRAINER_TYPE_NORMAL` is the trigger for the sight system. Without it, the NPC
  is just a regular talker.
- The defeat flag lives in the save file indexed by trainer ID. That's why
  `NUM_TRAINERS` matters — it determines array sizes. Adding to `opponents.h`
  without incrementing `NUM_TRAINERS` would silently corrupt save data.
- `AI_SCRIPT_CHECK_BAD_MOVE` is the minimal AI flag — prevents using moves that
  damage yourself (like using Explosion when at full health). Higher-level trainers
  use multiple flags combined with `|`.

---

## Completion Notes

- Added `TRAINER_ROUTE1_YOUNGSTER_JAKE = 743` to `opponents.h`, bumped `NUM_TRAINERS` to 744
- Added `sParty_Route1YoungsterJake` (Rattata lv5) to `trainer_parties.h`
- Added trainer struct entry to `trainers.h` using `TRAINER_CLASS_YOUNGSTER`
- Placed trainer in `Route1/map.json` at x=9, y=27 with `TRAINER_TYPE_NORMAL` and sight 4
- Initial coordinates (x=11, y=10) landed on a ledge — corrected using Porymap to find clean walkable tile
- Wrote `trainerbattle_single` script and three text entries in `scripts.inc` / `text.inc`
- Trainer battles correctly: intro on sight, defeat text after win, post-battle text on re-talk
- Installed Porymap for visual map editing going forward — see TOOLS.md
