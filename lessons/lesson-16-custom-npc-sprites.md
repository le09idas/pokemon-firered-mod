# Lesson 16 — Custom NPC Sprites

**Level:** Expert
**Status:** Complete

---

## The Concept

Every NPC sprite in the game flows through a five-file pipeline before it
appears on screen. You've been using `OBJ_EVENT_GFX_MAN` for the merchant
since Lesson 10 — a generic sprite that doesn't match the character you've
been building. This lesson walks the full pipeline and gives the merchant his
own sprite.

The assignment is intentionally minimal on pixel art: copy an existing sprite
sheet, swap its colors, and wire it up. The goal is to understand the pipeline.
The art is yours to develop separately.

---

## The Five-File Pipeline

```
graphics/object_events/pics/people/merchant.png
    ↓  (referenced by)
src/data/object_events/object_event_graphics.h
    ↓  (pic array used by)
src/data/object_events/object_event_pic_tables.h
    ↓  (pic table used by)
src/data/object_events/object_event_graphics_info.h
    ↓  (graphics info pointed to by)
src/data/object_events/object_event_graphics_info_pointers.h
    ↓  (index exposed as)
include/constants/event_objects.h  →  OBJ_EVENT_GFX_MERCHANT
```

Each file has exactly one job. You touch all five when adding a new sprite.

---

## Sprite Sheet Format

NPC sprites use a 4-bit indexed PNG (16 colors). The standard walking NPC
size is **16×32 pixels per frame**, laid out in a single row. The man sprite
is 160×32 — ten 16×32 frames side by side.

Frame layout for a standard walking NPC (left to right):

| Index | Content |
|---|---|
| 0 | Walk down — step left |
| 1 | Stand down |
| 2 | Walk down — step right |
| 3 | Walk up — step left |
| 4 | Stand up |
| 5 | Walk up — step right |
| 6 | Walk left — step 1 |
| 7 | Stand left |
| 8 | Walk right — step 1 |
| 9 | Stand right |

The engine mirrors left/right automatically — you only need one side.

**Palette:** the PNG must use an indexed palette where color index 0 is the
transparent color (magenta: `#F8F8F8` is convention, but exact value depends
on the tileset). Match the format of an existing sprite exactly — same bit
depth, same dimensions.

---

## Assignment

### Task 1 — Create the sprite sheet

Copy the man sprite as a starting point:

```bash
cp graphics/object_events/pics/people/man.png \
   graphics/object_events/pics/people/merchant.png
```

Open `merchant.png` in an image editor that supports indexed PNGs (GIMP works
well). Change the color palette — give the merchant a distinct look. A simple
color swap of the shirt or hair is enough. Save as an indexed PNG, same
160×32 dimensions, same 4-bit depth. Do not resize or add frames.

### Task 2 — Register the raw image data

In `src/data/object_events/object_event_graphics.h`, find the `Man` entry and
add a new line for the merchant directly after it:

```c
const u16 gObjectEventPic_Man[] = INCBIN_U16("graphics/object_events/pics/people/man.4bpp");
const u16 gObjectEventPic_Merchant[] = INCBIN_U16("graphics/object_events/pics/people/merchant.4bpp");
```

The build system converts `merchant.png` → `merchant.4bpp` automatically
during `make`. You reference the `.4bpp` path, not `.png`.

### Task 3 — Define the frame table

In `src/data/object_events/object_event_pic_tables.h`, find `sPicTable_Man`
and add a new table after it:

```c
static const struct SpriteFrameImage sPicTable_Merchant[] = {
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 0),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 1),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 2),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 3),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 4),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 5),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 6),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 7),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 8),
    overworld_frame(gObjectEventPic_Merchant, 2, 4, 9),
};
```

`overworld_frame(pic_array, width_in_tiles, height_in_tiles, frame_index)` —
2 tiles wide × 4 tiles tall = 16×32px. Ten entries for ten frames.

### Task 4 — Define the graphics info struct

In `src/data/object_events/object_event_graphics_info.h`, find
`gObjectEventGraphicsInfo_Man` and add a new struct after it:

```c
const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_Merchant = {
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_NPC_WHITE,
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,
    .size = 256,
    .width = 16,
    .height = 32,
    .paletteSlot = PALSLOT_NPC_4,
    .shadowSize = SHADOW_SIZE_M,
    .inanimate = FALSE,
    .disableReflectionPaletteLoad = FALSE,
    .tracks = TRACKS_FOOT,
    .oam = &gObjectEventBaseOam_16x32,
    .subspriteTables = gObjectEventSpriteOamTables_16x32,
    .anims = sAnimTable_Standard,
    .images = sPicTable_Merchant,
    .affineAnims = gDummySpriteAffineAnimTable,
};
```

This is identical to the Man struct except `.images = sPicTable_Merchant`.
The palette tag `OBJ_EVENT_PAL_TAG_NPC_WHITE` is a shared NPC palette — your
sprite's indexed colors will be remapped to this palette at runtime. If your
colors look wrong in-game, this is why — you'll need to match your sprite's
palette to the NPC palette entries.

### Task 5 — Add the pointer

In `src/data/object_events/object_event_graphics_info_pointers.h`, find the
`Man` entry in the array:

```c
[OBJ_EVENT_GFX_MAN]  = &gObjectEventGraphicsInfo_Man,
```

Add a forward declaration at the top of the file (near the other `extern`
declarations):

```c
extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_Merchant;
```

Then add the array entry after the Man entry:

```c
[OBJ_EVENT_GFX_MERCHANT] = &gObjectEventGraphicsInfo_Merchant,
```

### Task 6 — Define the constant

In `include/constants/event_objects.h`, find `OBJ_EVENT_GFX_MAN` and add a
new constant after it:

```c
#define OBJ_EVENT_GFX_MAN      25
#define OBJ_EVENT_GFX_MERCHANT 26
```

The value must be the next unused number. Check what value comes after 25 in
the file and use the slot before it, or append at the end of the list if
there's room. You'll also need to update `NUM_OBJ_EVENT_GFX` if your new
value exceeds the current max.

### Task 7 — Update the merchant NPC

In Porymap, open Pallet Town and change the merchant NPC's `graphics_id` from
`OBJ_EVENT_GFX_MAN` to `OBJ_EVENT_GFX_MERCHANT`. Save.

Also update the `.equ` alias at the top of `data/maps/PalletTown/scripts.inc`
— the Porymap-generated `LOCALID_PALLET_GFX_MAN` constant will have been
renamed by Porymap to match the new sprite name.

### Task 8 — Build and test

```bash
make
```

Load Pallet Town. The merchant should now use your new sprite.

---

## What to observe

- The `.4bpp` file is auto-generated from `.png` by the build system. You
  never edit `.4bpp` directly — always edit the `.png` and let `make` convert
  it.
- `OBJ_EVENT_PAL_TAG_NPC_WHITE` is a shared runtime palette. All NPCs using
  this tag share one palette slot — their colors are loaded from the first NPC
  with this tag who appears on screen. If you need fully independent colors
  (for a unique character), you'd define a new palette tag and a new palette
  file. That's out of scope here but worth knowing exists.
- `PALSLOT_NPC_4` is the palette memory slot. Four NPC palette slots are
  available (`NPC_1` through `NPC_4`). If all four are occupied by other NPCs
  on the same map, your sprite's colors may load incorrectly. Pallet Town is
  sparse enough that this won't be an issue.
- The `size = 256` field is the sprite's tile data size in bytes: 16×32 pixels
  at 4 bits per pixel = 16×32/2 = 256 bytes.
- If you see a garbled or all-black sprite in-game, the most common cause is
  a palette mismatch. Open the original `man.png`, note its exact palette, and
  match your `merchant.png` to the same color index layout.

---

## Completion Notes

Merchant sprite wired up and visible in Pallet Town. Two non-obvious pitfalls encountered:

1. **`spritesheet_rules.mk` requires an explicit rule** for every NPC sprite — the default `%.4bpp: %.png` rule doesn't pass `-mwidth 2 -mheight 4`, which causes gbagfx to tile the spritesheet in the wrong order and produce all-zero frames. Added the merchant entry between man and mg_deliveryman.

2. **PNG palette format must be a 16-entry RGB palette with no per-entry alpha.** Saving from some editors produces a non-standard PLTE/tRNS structure that causes gbagfx to silently output transparent tiles. Fixed via pypng rewrite. A better sprite authoring workflow (tooling that guarantees the correct format) is a future lesson topic.

Sprite art is a color-swapped man sprite as a placeholder — final art to be revisited in a dedicated visuals lesson.
