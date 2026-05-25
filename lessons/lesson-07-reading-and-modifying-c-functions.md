# Lesson 07 — Reading and Modifying C Functions: Removing the HM Lock

**Level:** Intermediate
**Status:** In Progress

---

## The Concept

In Lesson 6 you used grep to hunt down a function you'd never seen before and
described what it does. That was the detective half. This lesson is the surgeon
half — you take a function you now understand and make a precise, targeted change.

The target: the HM forgetting restriction. On a solo emulator run, being unable
to forget HM moves is a gameplay annoyance with no upside. You already found
both functions involved. Now you'll understand exactly why they work and remove
the lock with a single line change.

---

## Reading the Call Chain

You identified this in Lesson 6. Here it is laid out as a chain:

**Step 1 — Player tries to select a move to forget**

`src/pokemon_summary_screen.c:3766`

```c
static u8 PokeSum_CanForgetSelectedMove(void)
{
    u16 move;

    move = GetMonMoveBySlotId(&sMonSummaryScreen->currentMon, sMoveSelectionCursorPos);

    if (IsMoveHm(move) == TRUE && sMonSummaryScreen->mode != PSS_MODE_FORGET_MOVE)
        return FALSE;

    return TRUE;
}
```

This function gets whatever move is in the currently highlighted slot and asks
`IsMoveHm()` about it. If it's an HM *and* the screen isn't in forced-forget mode
(used by the Move Deleter NPC), it returns FALSE — can't forget.

**Step 2 — The HM check itself**

`src/party_menu.c:4724`

```c
bool8 IsMoveHm(u16 move)
{
    u8 i;

    for (i = 0; i < NUM_HIDDEN_MACHINES - 1; ++i) // no dive
        if (sTMHMMoves[i + NUM_TECHNICAL_MACHINES] == move)
            return TRUE;
    return FALSE;
}
```

This loops through the HM section of the `sTMHMMoves` array and checks if the
given move ID matches any of them. `NUM_TECHNICAL_MACHINES` is 50, so it starts
at index 50 (after all TMs). `NUM_HIDDEN_MACHINES` is 8, but the loop only goes
to `8 - 1 = 7` — notice the comment: `// no dive`. Dive (HM08) is deliberately
excluded from the lock. The original devs made Dive forgettable, possibly because
it was less essential to progression.

**Step 3 — Back in the summary screen**

`src/pokemon_summary_screen.c:3855`

```c
if (PokeSum_CanForgetSelectedMove() == TRUE || sMoveSelectionCursorPos == 4)
{
    // allow the player to proceed
}
else
{
    PlaySE(SE_FAILURE);  // the "bonk" sound when you can't do something
}
```

The bonk sound you hear when trying to forget Cut or Surf is triggered right here.

---

## The Anatomy of a Targeted Change

You now know the full chain. There are three ways to remove this restriction,
ranging in precision:

**Option A — Remove the check in the gate function (recommended):**

```c
// Before
static u8 PokeSum_CanForgetSelectedMove(void)
{
    u16 move;
    move = GetMonMoveBySlotId(&sMonSummaryScreen->currentMon, sMoveSelectionCursorPos);
    if (IsMoveHm(move) == TRUE && sMonSummaryScreen->mode != PSS_MODE_FORGET_MOVE)
        return FALSE;
    return TRUE;
}

// After — remove the if block entirely
static u8 PokeSum_CanForgetSelectedMove(void)
{
    return TRUE;
}
```

The function now always returns TRUE. Clean, minimal, surgical. `IsMoveHm()` is
untouched and still works for the other places in the code that call it.

**Option B — Make `IsMoveHm` always return FALSE:**

```c
bool8 IsMoveHm(u16 move)
{
    return FALSE;
}
```

This removes the concept of HM moves from the whole game — every place that calls
`IsMoveHm()` will now get FALSE. That includes battle checks, quest log checks, and
anywhere else you found in Lesson 6. Broader blast radius.

**Option C — Delete just the if statement, keep the function structure:**

```c
static u8 PokeSum_CanForgetSelectedMove(void)
{
    u16 move;
    move = GetMonMoveBySlotId(&sMonSummaryScreen->currentMon, sMoveSelectionCursorPos);
    return TRUE;
}
```

Same result as Option A, just leaves the dead variable in place. No practical
difference but slightly less clean.

**Option A is the right move.** Change the smallest surface area possible. You
preserve `IsMoveHm()` for everywhere else it's used, and the intent of your change
is obvious to anyone reading the function.

---

## Assignment

### Task 1 — Remove the HM forgetting restriction

File: `src/pokemon_summary_screen.c`, line 3766

Apply Option A. The function body becomes a single `return TRUE;`.

### Task 2 — Decide what to do about Dive

The `// no dive` comment in `IsMoveHm()` means Dive was already forgettable in
vanilla. After your change it doesn't matter — everything is forgettable. But read
that comment and the loop again and make sure you understand *why* `- 1` makes
Dive excluded. Write your explanation in the completion notes.

### Task 3 — Build and test

```bash
make
```

Get a Pokemon that knows Cut or Surf (you may need to cheat one in via an emulator
save editor for testing). Confirm you can now forget it from the summary screen.

---

## What to observe

- The `PSS_MODE_FORGET_MOVE` exception in the original code is how the Move Deleter
  NPC works — he triggers a special mode that bypasses this same check. By making
  the function always return TRUE, you've effectively made every player their own
  Move Deleter.
- `bool8` is a GBA-era typedef for an 8-bit boolean — just a `u8` that's used as
  true/false. You'll see it throughout the codebase. It's not a standard C type,
  it's defined in the project headers.
- This is your first function-level modification. Notice how small the change is
  relative to how much code you had to read to understand it. That ratio — lots of
  reading, small change — is normal and correct. Confidence without reading leads
  to bugs you can't explain.

---

## Completion Notes

*(Record what you changed and what you observed here once done.)*
