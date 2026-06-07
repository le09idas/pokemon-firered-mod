# Lesson 12 — Giving Items via Script

**Level:** Advanced
**Status:** Complete

---

## The Concept

Giving the player an item from a script is one of the most common patterns in
the game — Oak giving the Pokédex, clerks handing out samples, NPCs rewarding
you for favors. Every one of them follows the same sequence of commands.

You'll upgrade the kid in Pallet Town (from Lesson 10) to give the player a
Poké Ball the first time they talk to him. After that, he falls back to regular
dialogue.

---

## The Item-Giving Pattern

```asm
lock
faceplayer
goto_if_set FLAG_KID_GAVE_ITEM, PalletTown_EventScript_KidAfter
msgbox PalletTown_Text_KidIntro, MSGBOX_DEFAULT
textcolor NPC_TEXT_COLOR_NEUTRAL
checkitemspace ITEM_POKE_BALL
goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
bufferitemname STR_VAR_2, ITEM_POKE_BALL
playfanfare MUS_LEVEL_UP
message Text_ObtainedTheX
waitmessage
waitfanfare
additem ITEM_POKE_BALL
msgbox PalletTown_Text_KidGaveItem, MSGBOX_DEFAULT
setflag FLAG_KID_GAVE_ITEM
release
end
```

Command by command:

| Command | What it does |
|---|---|
| `lock` / `faceplayer` | Freeze NPC and make him face the player |
| `goto_if_set FLAG_...` | Skip the gift if already given |
| `msgbox ..., MSGBOX_DEFAULT` | Pre-give dialogue (player presses A to close) |
| `textcolor NPC_TEXT_COLOR_NEUTRAL` | Reset text color before the item fanfare |
| `checkitemspace ITEM_X` | Check if the bag has room; result goes into `VAR_RESULT` |
| `goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull` | If bag is full, jump to shared bag-full handler |
| `bufferitemname STR_VAR_2, ITEM_X` | Load item name into `{STR_VAR_2}` for use in the fanfare text |
| `playfanfare MUS_LEVEL_UP` | Play the item jingle |
| `message Text_ObtainedTheX` | Display "Obtained the [item]!" — uses `{STR_VAR_2}` |
| `waitmessage` / `waitfanfare` | Wait for both the text and jingle to finish |
| `additem ITEM_X` | Actually put the item in the bag |
| `msgbox ..., MSGBOX_DEFAULT` | Post-give dialogue |
| `setflag FLAG_...` | Mark as given — set AFTER the item is in the bag |
| `release` / `end` | Done |

**Why `additem` comes after the fanfare:**
The fanfare and message run simultaneously. `waitmessage` + `waitfanfare` block
until both finish. Only then do you call `additem` — this ensures the animation
plays fully before the bag updates.

**Why `setflag` is last:**
If the game crashes or resets during the fanfare, the flag isn't set yet, so the
player can try again. Once `additem` succeeds and the player sees the animation,
setting the flag locks the gift. This ordering is intentional.

**`EventScript_BagIsFull`** is a shared global script defined in
`data/scripts/bag_full.inc`. It shows "Too bad! The BAG is full…", releases the
NPC, and ends. You don't write it — you just jump to it.

**`Text_ObtainedTheX`** is a shared global text defined in
`data/text/obtain_item.inc`: `"Obtained the {STR_VAR_2}!$"`. The item name you
buffered into `STR_VAR_2` gets substituted at display time.

---

## Assignment

### Task 1 — Define the flag

At the top of `data/maps/PalletTown/scripts.inc`, add:

```asm
.equ FLAG_KID_GAVE_ITEM, FLAG_0x8F8
```

Put it below the `FLAG_MET_FAT_MAN` line from Lesson 9.

### Task 2 — Rewrite the kid's script

Replace `PalletTown_EventScript_Kid` in `scripts.inc` with the full item-giving
version:

```asm
PalletTown_EventScript_Kid::
    lock
    faceplayer
    goto_if_set FLAG_KID_GAVE_ITEM, PalletTown_EventScript_KidAfter
    msgbox PalletTown_Text_KidIntro, MSGBOX_DEFAULT
    textcolor NPC_TEXT_COLOR_NEUTRAL
    checkitemspace ITEM_POKE_BALL
    goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
    bufferitemname STR_VAR_2, ITEM_POKE_BALL
    playfanfare MUS_LEVEL_UP
    message Text_ObtainedTheX
    waitmessage
    waitfanfare
    additem ITEM_POKE_BALL
    msgbox PalletTown_Text_KidGaveItem, MSGBOX_DEFAULT
    setflag FLAG_KID_GAVE_ITEM
    release
    end

PalletTown_EventScript_KidAfter::
    msgbox PalletTown_Text_KidAfter, MSGBOX_NPC
    end
```

### Task 3 — Add the text entries

Replace `PalletTown_Text_Kid` in `text.inc` with three entries:

```asm
PalletTown_Text_KidIntro::
    .string "Hey, you look like you're\n"
    .string "about to go on a journey!\p"
    .string "Take this! You'll need it\n"
    .string "out there!$"

PalletTown_Text_KidGaveItem::
    .string "I found it near the pond.\n"
    .string "Hope it helps!$"

PalletTown_Text_KidAfter::
    .string "Have you caught anything\n"
    .string "good yet?$"
```

Write whatever you want him to say — these are just examples.

### Task 4 — Build and test

```bash
make
```

Talk to the kid. First time: intro dialogue → item fanfare → "Obtained the POKÉ
BALL!" → follow-up line. Check your bag — the Poké Ball should be there. Talk to
him again: the after-gift line only, no second ball.

Try filling your bag completely and talking to him — he should say "Too bad! The
BAG is full…" and not give the item or set the flag.

---

## What to observe

- `MSGBOX_DEFAULT` vs `MSGBOX_NPC`: `MSGBOX_DEFAULT` closes when the player
  presses A but does NOT auto-release the NPC. You need an explicit `release`
  before `end`. `MSGBOX_NPC` auto-releases. For item-giving scripts you use
  `MSGBOX_DEFAULT` because you need control to stay in the script between the
  dialogue and the fanfare.
- `message` (no MSGBOX type) is the raw form — it shows text but gives you full
  control over when it closes. `waitmessage` blocks until the player presses A.
  The fanfare plays underneath while the player reads "Obtained the POKÉ BALL!"
- `bufferitemname STR_VAR_2` loads the name into string variable slot 2.
  `Text_ObtainedTheX` contains `{STR_VAR_2}` which gets substituted at render
  time. If you forget `bufferitemname`, the text shows a blank or garbled name.
- The bag-full path skips `additem` AND `setflag`. If the player had a full bag,
  comes back with room, and talks to the kid again — they get the item. The flag
  only sets after a successful handoff.
- `FLAG_0x8F8` is the second of the custom permanent flag slots. You used
  `FLAG_0x8F7` for `FLAG_MET_FAT_MAN` in Lesson 9. Keep a mental note of which
  slots you've used — there's no enforced registry, just your `.equ` aliases.

---

## Completion Notes

Upgraded the Pallet Town kid from Lesson 10 to give the player a Poké Ball on
first interaction. Defined `FLAG_KID_GAVE_ITEM` at `FLAG_0x8F8` (the slot after
`FLAG_MET_FAT_MAN`). Rewrote the kid's script with the full item-giving
sequence: bag-space check, fanfare, `bufferitemname`/`message`/`waitmessage`/
`waitfanfare`, then `additem` and `setflag` after the animation completes.
Added three text entries (`KidIntro`, `KidGaveItem`, `KidAfter`) in `text.inc`.
Build passed cleanly. Verified the flag-ordering and bag-full bail path match
the pattern described in the lesson.
