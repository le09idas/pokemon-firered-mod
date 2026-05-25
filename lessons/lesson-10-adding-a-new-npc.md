# Lesson 10 — Adding a New NPC to a Map

**Level:** Intermediate → Advanced
**Status:** In Progress

---

## The Concept

Every NPC you've touched so far already existed — you changed what they say, how
their scripts branch, but the NPC was already in the world. This lesson you add
one from scratch.

NPCs are placed by editing `map.json`. That file is the single source of truth
for everything on a map. The build system reads it and generates two files
automatically:

| File | Generated from |
|---|---|
| `data/maps/PalletTown/events.inc` | Placement, warps, triggers, signs |
| `include/constants/map_event_ids.h` | LOCALID constants for every NPC |

Both start with the warning `DO NOT MODIFY THIS FILE! It is auto-generated from
data/maps/PalletTown/map.json`. They get overwritten every build. Any edit you
make to them directly will be silently destroyed.

**The only file you edit is `map.json`.**

---

## Anatomy of an object_event Entry

Open `data/maps/PalletTown/map.json` and look at the Fat Man entry:

```json
{
    "local_id": "LOCALID_PALLET_FAT_MAN",
    "type": "object",
    "graphics_id": "OBJ_EVENT_GFX_FAT_MAN",
    "x": 13,
    "y": 17,
    "elevation": 3,
    "movement_type": "MOVEMENT_TYPE_WANDER_AROUND",
    "movement_range_x": 6,
    "movement_range_y": 2,
    "trainer_type": "TRAINER_TYPE_NONE",
    "trainer_sight_or_berry_tree_id": "0",
    "script": "PalletTown_EventScript_FatMan",
    "flag": "0"
}
```

Field by field:

| Field | What it does |
|---|---|
| `local_id` | The LOCALID constant name — must be unique within this map |
| `type` | Always `"object"` for NPCs |
| `graphics_id` | Which sprite to use — constant from `event_objects.h` |
| `x`, `y` | Tile coordinates on the map |
| `elevation` | Almost always `3` — only change for elevated tiles (bridges, etc.) |
| `movement_type` | How the NPC moves when idle |
| `movement_range_x/y` | How many tiles they can wander in each direction |
| `trainer_type` | `TRAINER_TYPE_NONE` for non-trainers |
| `trainer_sight_or_berry_tree_id` | `"0"` for non-trainers |
| `script` | The script to run when talked to |
| `flag` | `"0"` for NPCs that are always present; a `FLAG_HIDE_*` value hides them |

---

## Sprite Options

From `include/constants/event_objects.h` — a few useful ones:

```c
OBJ_EVENT_GFX_LITTLE_BOY      // small kid
OBJ_EVENT_GFX_LITTLE_GIRL     // small girl
OBJ_EVENT_GFX_BOY             // teenage boy
OBJ_EVENT_GFX_WOMAN_1         // woman (same as Sign Lady)
OBJ_EVENT_GFX_MAN             // standard adult man
OBJ_EVENT_GFX_FAT_MAN         // the fat man
OBJ_EVENT_GFX_OLD_MAN_1       // old man
OBJ_EVENT_GFX_OLD_WOMAN       // old woman
OBJ_EVENT_GFX_GENTLEMAN       // suited man
OBJ_EVENT_GFX_POLICEMAN       // officer
```

---

## Movement Types

From `include/constants/event_object_movement.h`:

```c
MOVEMENT_TYPE_NONE              // frozen, facing default direction
MOVEMENT_TYPE_LOOK_AROUND       // stands still, randomly turns to look
MOVEMENT_TYPE_WANDER_AROUND     // walks randomly within range
MOVEMENT_TYPE_FACE_UP
MOVEMENT_TYPE_FACE_DOWN
MOVEMENT_TYPE_FACE_LEFT
MOVEMENT_TYPE_FACE_RIGHT
```

For a wandering NPC, use `MOVEMENT_TYPE_WANDER_AROUND` with a movement range.
For a fixed NPC who just turns their head, use `MOVEMENT_TYPE_LOOK_AROUND` with
range `1, 1`.

---

## What the Build Does

When you run `make`, the build system calls a Python tool that reads every
`map.json` in the project and regenerates:

1. `events.inc` — the actual map event data in assembler format
2. `map_event_ids.h` — the `#define LOCALID_*` constants

This means your new `local_id` string in `map.json` becomes a usable `#define`
automatically. You never write the `#define` yourself.

The generated LOCALID value is just the order of the object in the `object_events`
array. The first object in the array gets `1`, the second gets `2`, etc. Right now
Pallet Town has:

```
LOCALID_PALLET_SIGN_LADY   = 1
LOCALID_PALLET_FAT_MAN     = 2
LOCALID_PALLET_PROF_OAK    = 3
```

Your new NPC appended to the end of the array will get `4`.

---

## Assignment

You're adding a new NPC to Pallet Town: a little boy standing near the pond at
the south edge of town. He's excited about Pokémon and has something to say —
write whatever you want him to say.

### Task 1 — Add the NPC to map.json

Open `data/maps/PalletTown/map.json`. At the end of the `object_events` array
(after Prof. Oak's entry), add a new entry:

```json
{
    "local_id": "LOCALID_PALLET_KID",
    "type": "object",
    "graphics_id": "OBJ_EVENT_GFX_LITTLE_BOY",
    "x": 7,
    "y": 19,
    "elevation": 3,
    "movement_type": "MOVEMENT_TYPE_LOOK_AROUND",
    "movement_range_x": 1,
    "movement_range_y": 1,
    "trainer_type": "TRAINER_TYPE_NONE",
    "trainer_sight_or_berry_tree_id": "0",
    "script": "PalletTown_EventScript_Kid",
    "flag": "0"
}
```

Important: `map.json` is strict JSON. That means:
- No trailing comma on the last entry in an array
- The Prof. Oak entry before yours needs a comma after its closing `}`
- Your new entry does **not** get a trailing comma (it's last in the array)

### Task 2 — Write the script

Add to `data/maps/PalletTown/scripts.inc`:

```asm
PalletTown_EventScript_Kid::
    msgbox PalletTown_Text_Kid, MSGBOX_NPC
    end
```

This can go at the bottom of the file after the Fat Man scripts.

### Task 3 — Write the text

Add to `data/maps/PalletTown/text.inc`:

```asm
PalletTown_Text_Kid::
    .string "Write your own dialogue here.$"
```

Write something that fits a kid in Pallet Town. Keep lines under 18–20 characters,
`\n` for second line, `\p` for page breaks, `$` at the end.

### Task 4 — Build and test

```bash
make
```

After the build, check that the generated file was updated:

```bash
grep "LOCALID_PALLET_KID" include/constants/map_event_ids.h
```

If the line appears, the build system saw your new entry and created the constant.
Load the ROM and walk to the south edge of Pallet Town. The kid should be there.

---

## What to observe

- You never wrote a `#define` for `LOCALID_PALLET_KID`. The build generated it.
  This is the same pattern as `wild_encounters.h` from `wild_encounters.json` —
  the project uses JSON as the human-editable layer and generates the assembler
  and header files from it.
- `flag: "0"` means the NPC is always visible. To make an NPC appear only after
  a certain event (like Oak after you get the Pokédex), set `flag` to a
  `FLAG_HIDE_*` constant. The NPC is hidden until `clearflag` runs in a script.
  This is how Oak appears in cutscenes without being permanently present on the map.
- The `trainer_sight_or_berry_tree_id` field: for a trainer, this is their sight
  range in tiles. For a berry tree, it's the tree's ID. For everyone else, `"0"`.
  You'll use this in a later lesson when you add a trainer to the overworld.
- Coordinates are (x, y) from the top-left of the map. If your NPC ends up
  clipping into a wall or floating in water, adjust x/y. The Pallet Town layout
  has walkable ground roughly between x=3–17, y=7–20 for the main landmass.

---

## Completion Notes

_(fill in after completing the assignment)_
