# Lesson 14 — Map Scripts and Cutscenes

**Level:** Advanced
**Status:** Complete

---

## The Concept

Every one-time story moment in the game — Oak stopping you at the town border,
the parcel scene at Viridian Mart, the bike ride cutscene — is triggered by the
same mechanism: a **map script** that fires when a scene variable matches a
specific value, then advances that variable so the scene never fires again.

You've been seeing this machinery in `PalletTown/scripts.inc` since Lesson 8
without writing it yourself. This lesson closes that gap. You'll add a short
cutscene to Pallet Town: the first time the player loads in, the merchant NPC
reacts with an exclamation mark, turns toward the player, and calls out a line.

---

## The Map Script System

Every map has a `MapScripts` block at the top of its `scripts.inc`:

```asm
PalletTown_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, PalletTown_OnTransition
    map_script MAP_SCRIPT_ON_FRAME_TABLE, PalletTown_OnFrame
    .byte 0
```

Each `map_script` line pairs a **hook type** with a **handler script**. The
five hooks you'll use in practice:

| Hook | When it fires |
|---|---|
| `MAP_SCRIPT_ON_LOAD` | Every time map tiles and objects are loaded (warping in, coming back from a battle) |
| `MAP_SCRIPT_ON_TRANSITION` | Once per map entry, before the fade-in (good for repositioning NPCs) |
| `MAP_SCRIPT_ON_RESUME` | When control returns to the field (after a battle, after a menu) |
| `MAP_SCRIPT_ON_FRAME_TABLE` | Every frame — checked against a table of `(var, value, script)` entries |
| `MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE` | When the player warps in via a specific warp — checked against a warp table |

**`MAP_SCRIPT_ON_FRAME_TABLE` is where cutscenes live.** Its handler is a
table of `map_script_2` entries, each of which says: "if `VAR_X` equals
`VALUE`, run this script." The engine checks the table every frame until the
scene advances the variable.

```asm
PalletTown_OnFrame::
    map_script_2 VAR_MAP_SCENE_PALLET_TOWN_OAK, 2, PalletTown_EventScript_OakRatingScene
    map_script_2 VAR_SCENE_MERCHANT_ARRIVES, 0, PalletTown_EventScript_MerchantArrivesScene
    .2byte 0
```

The table ends with `.2byte 0`.

**Important:** The frame table fires on every frame. Your scene script must
call `setvar VAR_SCENE_MERCHANT_ARRIVES, 1` before it ends — otherwise the
scene replays endlessly.

---

## `lockall` vs `lock`

You've used `lock` + `release` for NPC interaction scripts. Cutscenes use
`lockall` + `releaseall` instead.

| Command | What it does |
|---|---|
| `lock` | Freezes only the NPC whose script is running |
| `lockall` | Freezes the player AND all NPCs on the map |
| `release` | Unfreezes the one NPC |
| `releaseall` | Unfreezes everyone |

Cutscenes need `lockall` because they move NPCs and the player independently.
If you only called `lock`, the player could walk away mid-scene.

---

## `applymovement` and Movement Scripts

```asm
applymovement LOCALID_PALLET_MERCHANT, PalletTown_Movement_MerchantNotice
waitmovement 0
```

`applymovement` tells an NPC (or `LOCALID_PLAYER`) to execute a **movement
script** — a list of step commands ending with `step_end`. `waitmovement 0`
blocks until all active movements on the map finish. You can fire multiple
`applymovement` calls before `waitmovement` to move several characters
simultaneously.

Movement script format:

```asm
PalletTown_Movement_MerchantNotice::
    walk_in_place_faster_down
    delay_16
    walk_in_place_faster_left
    step_end
```

Useful step commands:

| Command | What it does |
|---|---|
| `walk_up` / `walk_down` / `walk_left` / `walk_right` | Move one tile |
| `walk_in_place_faster_up` / `_down` / `_left` / `_right` | Turn without moving |
| `delay_16` / `delay_32` / `delay_48` | Pause for N frames |
| `set_invisible` / `set_visible` | Hide or show the NPC |
| `step_end` | Required terminator |

Common movement scripts you can reuse without defining your own (from
`data/scripts/movement.inc`): `Common_Movement_ExclamationMark`,
`Common_Movement_FacePlayer`, `Common_Movement_WalkInPlaceFasterDown`, etc.

---

## Assignment

### Task 1 — Define the scene variable

At the top of `data/maps/PalletTown/scripts.inc`, add:

```asm
.equ VAR_SCENE_MERCHANT_ARRIVES, VAR_0x409F
```

Put it below the existing `.equ` lines.

### Task 2 — Add an entry to the frame table

Find `PalletTown_OnFrame` in `scripts.inc` and add your new entry:

```asm
PalletTown_OnFrame::
    map_script_2 VAR_MAP_SCENE_PALLET_TOWN_OAK, 2, PalletTown_EventScript_OakRatingScene
    map_script_2 VAR_SCENE_MERCHANT_ARRIVES, 0, PalletTown_EventScript_MerchantArrivesScene
    .2byte 0
```

### Task 3 — Write the cutscene script

Add this after the frame table's existing scripts (a good spot is just before
`PalletTown_EventScript_OaksLabSign`):

```asm
PalletTown_EventScript_MerchantArrivesScene::
    setvar VAR_SCENE_MERCHANT_ARRIVES, 1
    lockall
    applymovement LOCALID_PALLET_MERCHANT, Common_Movement_ExclamationMark
    waitmovement 0
    applymovement LOCALID_PALLET_MERCHANT, Common_Movement_FacePlayer
    waitmovement 0
    msgbox PalletTown_Text_MerchantArrives
    releaseall
    end
```

**Why `setvar` is first:**
The frame table fires every frame. If the scene script gets interrupted before
it reaches `setvar`, it would restart. Setting the var immediately prevents
re-entry — the scene runs once regardless of what happens after.

### Task 4 — Add the text

In `text.inc`, add anywhere in the file:

```asm
PalletTown_Text_MerchantArrives::
    .string "Hey there, traveler!\p"
    .string "I just set up shop here.\n"
    .string "Come check out my wares!$"
```

Write whatever you want him to say.

### Task 5 — Add the NPC's local ID

Porymap assigns a local ID to each NPC object. Open `data/maps/PalletTown/map.json`
and find the merchant object — note its `"local_id"` field. Then add a
`.equ` for it at the top of `scripts.inc`:

```asm
.equ LOCALID_PALLET_MERCHANT, <the number from map.json>
```

Put it with the other `.equ` lines at the top.

### Task 6 — Build and test

```bash
make
```

Load into Pallet Town. The merchant should do an exclamation mark, turn to
face the player, then say his line. Load in again — he should do nothing,
just stand there normally.

---

## What to observe

- The cutscene fires from the frame table, not from talking to the NPC. It
  runs as soon as the map loads and the engine's frame loop starts checking.
- `setvar VAR_SCENE_MERCHANT_ARRIVES, 1` at the top of the script is what
  prevents it from looping. The frame table checks the var on the next frame,
  sees it's no longer 0, and skips the entry.
- `Common_Movement_ExclamationMark` plays the "!" pop animation. This is a
  shared movement script — look at `data/scripts/movement.inc` to see exactly
  what steps it runs. You can use it freely without defining anything.
- `waitmovement 0` waits for *all* active movements to finish, not a specific
  NPC. Pass a specific local ID to wait for only that NPC.
- `msgbox` inside a `lockall` block is fine — it auto-handles wait for player
  input and does not need `waitmessage`. The difference from the clerk script:
  you don't need `release` here because you'll call `releaseall` at the end.
- `VAR_0x409F` is a permanently saved game variable, not a temp var. The
  player won't see the scene again even after resetting, as long as they saved
  after it fired. If you wanted a scene that resets every session, you'd use a
  `VAR_TEMP_*` instead.

---

## Completion Notes

Added a one-time cutscene to Pallet Town triggered via `MAP_SCRIPT_ON_FRAME_TABLE`.
The merchant NPC plays an exclamation mark, turns to face the player, and
delivers a greeting line. State tracked with `VAR_SCENE_MERCHANT_ARRIVES`
aliased to `VAR_0x409F`. `setvar` placed first in the scene script to prevent
re-entry. Used `lockall` / `releaseall` correctly. NPC local ID aliased via
`LOCALID_PALLET_GFX_MAN` — noted that this name is Porymap-generated from the
sprite type and would break if the sprite is ever changed; raw value is 5.
