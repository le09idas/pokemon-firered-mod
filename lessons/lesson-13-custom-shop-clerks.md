# Lesson 13 — Custom Shop Clerks: Building a Pokémart

**Level:** Advanced
**Status:** In Progress

---

## The Concept

Every Pokémart in the game is just a clerk NPC whose script calls `pokemart`
with a pointer to a list of items. The list is a simple `.2byte` array
terminated by `ITEM_NONE`. You can drop this pattern on any NPC, in any map,
selling anything.

You'll add a traveling merchant to Pallet Town who sells a small custom
inventory. By the end you'll understand the full clerk script flow and how to
build a shop item list from scratch.

---

## How a Clerk Script Works

```asm
PalletTown_EventScript_Merchant::
    lock
    faceplayer
    message Text_MayIHelpYou
    waitmessage
    pokemart PalletTown_MerchantItems
    msgbox Text_PleaseComeAgain
    release
    end

    .align 2
PalletTown_MerchantItems::
    .2byte ITEM_POKE_BALL
    .2byte ITEM_SUPER_POTION
    .2byte ITEM_REPEL
    .2byte ITEM_NONE
```

Step by step:

| Line | What it does |
|---|---|
| `lock` / `faceplayer` | Freeze NPC, turn to face player |
| `message Text_MayIHelpYou` | Display greeting (raw `message`, not `msgbox`) |
| `waitmessage` | Block until player presses A |
| `pokemart PalletTown_MerchantItems` | Open the shop UI with the given item list |
| `msgbox Text_PleaseComeAgain` | Display "Please come again!" after the shop closes |
| `release` / `end` | Done |

**Why `message` + `waitmessage` instead of `msgbox`?**
`msgbox` auto-closes and returns when the player presses A. `message` +
`waitmessage` does the same thing functionally, but it's the established
convention for clerk scripts — it matches how every stock mart clerk in the
game is written. You'll see this pairing frequently in shop context.

**The item list format:**
- Each entry is `.2byte ITEM_CONSTANT` — two bytes for the item ID.
- The list is terminated by `.2byte ITEM_NONE` (value 0).
- `.align 2` before the label ensures 2-byte alignment (required by the engine).
- Prices are pulled automatically from the item's base price in the item data
  table — you don't set them here.

**`Text_MayIHelpYou` and `Text_PleaseComeAgain`** are shared globals defined in
`data/text/poke_mart.inc`. Every mart in the game reuses them. You don't
define them yourself.

---

## Assignment

### Task 1 — Add the NPC to the map

Open `data/maps/PalletTown/map.json` in Porymap. Add a new NPC object with
these properties:

| Field | Value |
|---|---|
| Graphics | `EVENT_OBJ_GFX_MAN_4` (or any vendor-looking sprite) |
| Script | `PalletTown_EventScript_Merchant` |
| Movement | `MOVEMENT_TYPE_FACE_DOWN` |
| Trainer type | `TRAINER_TYPE_NONE` |

Pick a tile near the pond or the south side of town. Note the X/Y coordinates
and the local ID Porymap assigns.

### Task 2 — Write the script

In `data/maps/PalletTown/scripts.inc`, add the merchant script and item list
after the kid's script block:

```asm
PalletTown_EventScript_Merchant::
    lock
    faceplayer
    message Text_MayIHelpYou
    waitmessage
    pokemart PalletTown_MerchantItems
    msgbox Text_PleaseComeAgain
    release
    end

    .align 2
PalletTown_MerchantItems::
    .2byte ITEM_POKE_BALL
    .2byte ITEM_SUPER_POTION
    .2byte ITEM_REPEL
    .2byte ITEM_NONE
```

Choose whatever items you want — item constants are in
`include/constants/items.h`. Any item with a non-zero price can be sold.

### Task 3 — Build and test

```bash
make
```

Talk to the merchant. The "May I help you?" greeting should appear, then the
shop UI opens with your item list. Buy something and check your bag. After
closing the shop, "Please come again!" should display.

---

## What to observe

- The shop UI (`pokemart`) handles everything — currency check, quantity
  selection, bag insertion, "You don't have enough money" messages. You write
  zero battle or economy logic yourself.
- After `pokemart` returns, control flows to the next line in the script. This
  is how you chain "please come again" dialogue — the script just keeps going
  after the shop closes.
- If you put an item with price `0` in the list, it appears in the shop but
  can't be purchased (the engine rejects 0-price sales). Avoid this unless you
  intend to.
- Item order in the list is display order in the shop. Put frequently-bought
  items first.
- The item list lives in the script file, not a separate data file. You can
  define as many different merchants as you want by giving each their own label
  and list.

---

## Going further (optional)

**Conditional inventory:** You can gate item availability behind a flag. Write
two item lists and two scripts — use `goto_if_set` on a flag to decide which
`pokemart` call to make. This is how you'd implement a merchant who expands
their stock after a story event.

**Custom greeting:** Swap `Text_MayIHelpYou` for your own text label to give
the merchant a personality. Just define it in `text.inc`.

---

## Completion Notes

_(fill in after completing the assignment)_
