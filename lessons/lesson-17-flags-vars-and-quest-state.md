# Lesson 17 — Flags, Vars, and Quest State

**Level:** Advanced
**Status:** In Progress

---

## The Concept

Right now the merchant has no memory. Talk to him once, talk to him a hundred
times — same dialogue, same shop, no awareness of who you are or what you've
done. He's a vending machine with a face.

Flags and variables are how the game stores everything that changes as you play.
Every badge you've earned, every NPC you've spoken to, every cutscene you've
seen — all of it is a flag or a variable saved to the game file. This lesson
teaches you to create your own and put them to work.

By the end you'll have a merchant who:
- Greets you differently the first time you meet him properly
- Gives you a one-time welcome gift
- Offers a simple fetch quest that you can complete for a reward
- Remembers which stage you're at across sessions

---

## Two Primitives

### Flags — 1 bit, on or off

A flag is either set (1) or unset (0). Use it for anything that is simply
true or false: has this event happened, has this NPC been spoken to, has this
item been picked up.

```
checkflag FLAG_X        @ sets RESULT to 1 if set, 0 if unset
goto_if_set FLAG_X, label   @ jump if flag is set
goto_if_unset FLAG_X, label @ jump if flag is unset
setflag FLAG_X          @ turn it on
clearflag FLAG_X        @ turn it off
```

Flags live in `include/constants/flags.h`. The safe range for custom flags is
`0x4E0`–`0x4EF` — these are defined as numbered placeholders (`FLAG_0x4E0`
etc.) with no assigned meaning.

### Variables — 16 bits, 0–65535

A variable holds a number. Use it for anything with more than two states: which
stage of a quest you're on, how many times something has happened, which branch
of a story the player is in.

```
setvar VAR_X, value         @ set variable to a value
addvar VAR_X, value         @ add to variable
compare VAR_X, value        @ compare variable to value, then branch:
goto_if_eq label            @   jump if VAR_X == value
goto_if_lt label            @   jump if VAR_X < value
goto_if_ge label            @   jump if VAR_X >= value
copyvar VAR_DEST, VAR_SRC   @ copy one var into another
```

Variables live in `include/constants/vars.h`. `VARS_END` is `0x40FF`.
The range `0x40FA`–`0x40FE` is unclaimed — safe for custom use.

---

## Two Lifetimes

Both flags and vars come in two lifetimes:

| Prefix | Cleared when |
|---|---|
| `FLAG_TEMP_*` / `VAR_TEMP_*` | Every map load |
| Everything else | Never (until New Game) |

Temp flags/vars are for within-map state ("has this NPC already turned to face
me this visit"). Persistent flags/vars are for everything that should survive
saving and loading.

---

## Existing Flags You Can Read

You don't have to set a flag yourself to check it. The game already tracks
things you can branch on. Useful ones:

```c
FLAG_BADGE01_GET   // Boulder Badge
FLAG_BADGE02_GET   // Cascade Badge
// ... through ...
FLAG_BADGE08_GET   // Earth Badge
```

Check these exactly like your own flags — `goto_if_set FLAG_BADGE01_GET, label`.

---

## New Script Commands

Two commands you haven't used yet, needed for the quest:

```
checkitem ITEM_X, count
```
Checks whether the player has at least `count` of `ITEM_X` in their bag.
Sets `VAR_RESULT` to 1 if yes, 0 if no. Use `compare VAR_RESULT, 1` after.

```
removeitem ITEM_X, count
```
Removes `count` of `ITEM_X` from the bag. Always pair this with a `checkitem`
first — never remove an item you haven't confirmed the player has.

---

## Assignment

You're modifying the existing merchant in Pallet Town. He currently always
opens his shop. After this lesson he'll have three behavioral states tracked
across saves.

### Task 1 — Define your flag and variable

In `include/constants/flags.h`, find `FLAG_0x4E0` and replace it with a named
constant:

```c
#define FLAG_MET_MERCHANT   0x4E0
```

In `include/constants/vars.h`, find `VAR_0x40FA` and replace it with:

```c
#define VAR_MERCHANT_QUEST  0x40FA
```

These names will now be usable in any script file.

### Task 2 — First meeting (flag-gated)

The merchant should behave differently the first time the player talks to him
properly versus every visit after. Open
`data/maps/PalletTown/scripts.inc` and replace the existing
`PalletTown_EventScript_Merchant` with this:

```
PalletTown_EventScript_Merchant::
    lock
    faceplayer
    goto_if_set FLAG_MET_MERCHANT, PalletTown_EventScript_MerchantReturningCustomer
    @ First meeting
    setflag FLAG_MET_MERCHANT
    msgbox PalletTown_Text_MerchantFirstMeeting
    giveitem ITEM_POTION, 3
    msgbox PalletTown_Text_MerchantFirstMeetingShop
    goto PalletTown_EventScript_MerchantOpenShop
    end

PalletTown_EventScript_MerchantReturningCustomer::
    compare VAR_MERCHANT_QUEST, 0
    goto_if_eq PalletTown_EventScript_MerchantQuestOffer
    compare VAR_MERCHANT_QUEST, 1
    goto_if_eq PalletTown_EventScript_MerchantQuestCheck
    @ Quest complete — normal visit
    msgbox PalletTown_Text_MayIHelpYou
    goto PalletTown_EventScript_MerchantOpenShop
    end

PalletTown_EventScript_MerchantOpenShop::
    pokemart PalletTown_MerchantItems
    msgbox PalletTown_Text_PleaseComeAgain
    release
    end
```

Add two new text entries in your text block:

```
PalletTown_Text_MerchantFirstMeeting:
    .string "Ah, a new face! Welcome.\p"
    .string "I just set up shop here in Pallet.\n"
    .string "Take these — on the house.$"

PalletTown_Text_MerchantFirstMeetingShop:
    .string "Come back anytime.$"
```

**What this does:** `goto_if_set FLAG_MET_MERCHANT` jumps past the first-meeting
block on every visit after the first. The first visit sets the flag, gives 3
Potions, then falls through to the shop.

### Task 3 — The fetch quest (var-gated)

The merchant will ask the player to bring him an Antidote. When you bring it,
he expands his shop inventory as a reward. Add these scripts:

```
PalletTown_EventScript_MerchantQuestOffer::
    @ Quest not yet started — offer it
    msgbox PalletTown_Text_MerchantQuestOffer
    setvar VAR_MERCHANT_QUEST, 1
    release
    end

PalletTown_EventScript_MerchantQuestCheck::
    @ Quest in progress — check for the item
    checkitem ITEM_ANTIDOTE, 1
    compare VAR_RESULT, 1
    goto_if_eq PalletTown_EventScript_MerchantQuestComplete
    msgbox PalletTown_Text_MerchantQuestReminder
    release
    end

PalletTown_EventScript_MerchantQuestComplete::
    removeitem ITEM_ANTIDOTE, 1
    setvar VAR_MERCHANT_QUEST, 2
    msgbox PalletTown_Text_MerchantQuestReward
    giveitem ITEM_GREAT_BALL, 5
    release
    end
```

Add the text:

```
PalletTown_Text_MerchantQuestOffer:
    .string "Actually, could you help me out?\p"
    .string "I'm running low on stock.\n"
    .string "Bring me an Antidote and\n"
    .string "I'll make it worth your while.$"

PalletTown_Text_MerchantQuestReminder:
    .string "Still looking for that Antidote.\n"
    .string "You can find them at most shops.$"

PalletTown_Text_MerchantQuestReward:
    .string "An Antidote! Perfect, thank you.\p"
    .string "Here, take these Great Balls.\n"
    .string "Consider it a business arrangement.$"
```

**What this does:** `VAR_MERCHANT_QUEST` has three states: 0 (quest offered),
1 (quest in progress, waiting for item), 2 (quest complete, normal visits).
`checkitem ITEM_ANTIDOTE, 1` sets `VAR_RESULT` which you then `compare` to
branch between "has it" and "doesn't have it."

### Task 4 — Build and test

```bash
make
```

Walk through all three states in order:
1. Talk to merchant for the first time — get 3 Potions, shop opens
2. Talk again — quest offer
3. Talk again without Antidote — reminder
4. Buy an Antidote, talk again — quest completes, get 5 Great Balls
5. Talk again — normal shop visit

---

## What to observe

- `goto_if_set` and `goto_if_unset` are the flag versions of an if-statement.
  The flag is the condition, the label is the branch target. There is no else
  — you achieve else by falling through to code that runs when the jump
  doesn't happen.

- `compare` + `goto_if_eq` / `goto_if_ge` / `goto_if_lt` work the same way
  for variables. `compare` loads VAR_X into the comparison register;
  the goto reads that register. They must always be adjacent — don't put
  other commands between `compare` and its `goto`.

- The quest state being a var (not a flag) is intentional. Flags are binary.
  A quest with more than two states needs a var so you can tell the difference
  between "not started," "in progress," and "complete." If you only needed
  "done / not done," a flag would be cleaner.

- `VAR_RESULT` is a special variable the engine uses to report back from
  commands like `checkitem`. It gets overwritten by the next command that
  produces a result — read it immediately after the command that sets it.

- The flag and var you defined are now part of the save file structure. If you
  ever change their numeric values in `flags.h` or `vars.h`, existing save
  files will misread them. Names can be renamed freely; the hex value is what
  matters.

---

## Completion Notes

_(fill in after completing the assignment)_
