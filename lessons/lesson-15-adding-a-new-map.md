# Lesson 15 — Adding a New Map

**Level:** Advanced → Expert
**Status:** Complete

---

## The Concept

Every location in the game — every house, cave, city, route — is a **map**.
You've been working inside Pallet Town's existing map since Lesson 8. This
lesson teaches you to create a brand-new map and wire it into the world.

You'll build a small **Merchant's Hut** — an interior you can enter from
Pallet Town, with a sign inside. By the end you'll understand every file a map
touches and how to connect two maps with a bidirectional warp.

---

## What Porymap Does (and Doesn't Do)

When you create a new map in Porymap, it automatically generates and updates:

| File | What changes |
|---|---|
| `data/maps/MapName/map.json` | Created — map metadata, events, warps |
| `data/maps/MapName/scripts.inc` | Created — empty `MapScripts::` stub |
| `data/maps/MapName/text.inc` | Created — empty file |
| `data/layouts/MapName/map.bin` | Created — tile data (binary) |
| `data/layouts/MapName/border.bin` | Created — border tile data |
| `data/layouts/layouts.json` | Updated — new layout entry added |
| `include/constants/layouts.h` | Updated — new `LAYOUT_MAPNAME` constant |
| `data/maps/map_groups.json` | Updated — map added to a group |
| `include/constants/map_groups.h` | Updated — new `MAP_MAPNAME` constant |

**What Porymap does NOT do:**
- Add `.include` lines to `data/event_scripts.s` for your new `scripts.inc`
  and `text.inc`. You must do this manually or the assembler won't see your
  scripts.

---

## Assignment

### Task 1 — Create the map in Porymap

Launch Porymap:
```bash
porymap
```

Go to **File → New Map**. Fill in:

| Field | Value |
|---|---|
| Map Name | `PalletTown_MerchantHut` |
| Map Group | `gMapGroup_TownsAndRoutes` (same group as PalletTown) |
| Width / Height | `13 × 10` (same as the Player's House) |
| Primary Tileset | `gTileset_Building` |
| Secondary Tileset | `gTileset_GenericBuilding1` |
| Music | `MUS_PALLET` |
| Map Type | `MAP_TYPE_INDOOR` |
| Weather | `WEATHER_NONE` |
| Battle Scene | `MAP_BATTLE_SCENE_NORMAL` |
| Show Map Name | unchecked |
| Allow Running | unchecked |

Click OK. Porymap creates the map and opens it. Paint tiles however you like
— a simple room with a floor, walls, and a doormat at the bottom center is
enough.

### Task 2 — Place the exit warp inside the hut

Inside the new map in Porymap, switch to the **Events** tab and add a
**Warp** event on the doormat tile (or wherever you want the exit to be).
Set:

| Field | Value |
|---|---|
| Destination Map | `MAP_PALLET_TOWN` |
| Destination Warp | `3` (you'll create this warp in Task 3) |

Note the warp's index in the hut — it will be `0` since it's the first warp.

### Task 3 — Place the entrance warp in Pallet Town

Open the `MAP_PALLET_TOWN` map in Porymap. Add a **Warp** event on the tile
in front of where you want the hut door to be (near the merchant NPC works
well). Set:

| Field | Value |
|---|---|
| Destination Map | `MAP_PALLET_TOWN_MERCHANT_HUT` |
| Destination Warp | `0` (the warp you placed in Task 2) |

Note the warp's index in Pallet Town — it will be `3` (the existing ones are
0, 1, 2). Go back to the hut's warp and confirm its destination warp is `3`.
Save both maps.

**Warps are always bidirectional:** warp A points to warp B's index, and warp
B points to warp A's index. If the indexes don't match, you'll warp to a
random location.

### Task 4 — Register the scripts in `event_scripts.s`

Porymap does not add the `.include` lines. Find where the other PalletTown
maps are registered in `data/event_scripts.s` and add two lines for your new
map:

Scripts section (around line 344):
```asm
    .include "data/maps/PalletTown_MerchantHut/scripts.inc"
```

Text section (around line 670):
```asm
    .include "data/maps/PalletTown_MerchantHut/text.inc"
```

Put each one right after the existing `PalletTown_ProfessorOaksLab` entries
to keep related maps grouped together.

### Task 5 — Write a minimal MapScripts block

Porymap generates a stub like this in `scripts.inc`:

```asm
PalletTown_MerchantHut_MapScripts::
	.byte 0
```

That's all you need for a map with no map-level scripting. Leave it as-is.

### Task 6 — Add a sign

In Porymap, add a **Background (Sign)** event inside the hut. Set its script
to `PalletTown_MerchantHut_EventScript_Sign`. Then in `scripts.inc`:

```asm
PalletTown_MerchantHut_EventScript_Sign::
    msgbox PalletTown_MerchantHut_Text_Sign, MSGBOX_SIGN
    end
```

And in `text.inc`:

```asm
PalletTown_MerchantHut_Text_Sign::
    .string "MERCHANT'S HUT\n"
    .string "Open for business!$"
```

### Task 7 — Build and test

```bash
make
```

Walk up to the door you placed in Pallet Town — you should warp into the hut.
Read the sign. Walk to the exit warp — you should warp back out to Pallet Town.

---

## What to observe

- `MAP_PALLET_TOWN_MERCHANT_HUT` is the constant Porymap generated in
  `include/constants/map_groups.h`. This is what you use in scripts to
  reference the map (e.g. in a `warp` command).
- `LAYOUT_PALLET_TOWN_MERCHANT_HUT` is the layout constant in
  `include/constants/layouts.h`. Layouts and maps are separate — a layout is
  just the tile grid. Multiple maps can share one layout (though in practice,
  most don't).
- Warp index mismatches are the most common new-map bug. If you land in the
  wrong spot or the game crashes on warp, double-check that each warp's
  "Destination Warp" matches the index of the warp on the other side.
- `MSGBOX_SIGN` for signs, `MSGBOX_NPC` for NPCs that auto-release, and
  `MSGBOX_DEFAULT` when you need to keep control after the box closes — these
  apply to your new map exactly as they do in PalletTown.
- The `.include` entries in `event_scripts.s` must go in the correct sections:
  `scripts.inc` near other scripts includes, `text.inc` near other text
  includes. Putting a `text.inc` in the scripts section (or vice versa) will
  assemble fine but is wrong — same mistake as Lesson 13.
- If `make` reports "no such file" for your new `scripts.inc` or `text.inc`,
  the map name in `event_scripts.s` doesn't match the folder name Porymap
  created. Check `data/maps/` for the exact folder name.

---

## Completion Notes

Created `PalletTown_MerchantHut` as a new interior map connected to Pallet
Town. Bidirectional warp wired correctly: Pallet Town warp [3] ↔ hut warp [0].
Sign added with `MSGBOX_SIGN`. Manually added `.include` entries to
`event_scripts.s` in the correct scripts and text sections.

Two bugs encountered and fixed:
- **Duplicate includes**: Porymap auto-appended `.include` lines to the end of
  `event_scripts.s` after manual lines were already added. Removed the
  Porymap-appended duplicates. Going forward: let Porymap add them OR add them
  manually — not both.
- **`warp_id: "MAP_PALLET_TOWN"`**: The hut's exit warp had its local ID
  accidentally set to the destination map's name. Porymap read that string and
  generated a conflicting `#define MAP_PALLET_TOWN 0` in `map_event_ids.h` on
  every save. Fixed by setting `warp_id` to `"0"` (the correct numeric index).
  Also noted: `map_event_ids.h` is auto-generated — edits to it are overwritten
  by Porymap; fix the source (map.json) instead.
