# Compiling a map past Half-Life's limits for Xash3D FWGS

This kit is SDHLT v1.3.1-xash and the two game folder changes that let a map too big for Half-Life load
and play in Xash3D FWGS. It was put together for fiskcity_chazville_combined, FiskCity and Chazville in
one map, which stock SDHLT stops on with "Exceeded MAX_MAP_VERTS".

The map does not fit Half-Life's map format (version 30). Counted with the limits lifted, it has 96640
vertexes, 41725 nodes and 93394 marksurfaces, where version 30 holds 65535, 32767 and 65535. No compile
option gets it under those: they are 16-bit numbers in the file itself. Xash3D FWGS also reads BSP2, the
same map with 32-bit numbers, and loads it as a Half-Life map (textures, coloured light, hulls). This
SDHLT writes BSP2 when you give it `-engine xash`. Stock Half-Life on Steam will not load a BSP2 map.

## What is in the kit

    sdhlt-v1.3.1-xash/      the compilers: tools\Win64, tools\Win32, tools\Linux, sdhlt.wad, sdhlt.fgd
    ts/delta.lst            TS 3.0's delta.lst with the entity origins widened (see below)
    ts/liblist.gam          TS 3.0's liblist.gam with edicts "4096" added
    README.md               this file

## 1. The compilers

Point J.A.C.K. (or your batch file) at the new tools in `sdhlt-v1.3.1-xash\tools\Win64`:
sdHLCSG_x64.exe, sdHLBSP_x64.exe, sdHLVIS_x64.exe, sdHLRAD_x64.exe. Keep your old folder until you are
happy with the new one. A map that fits version 30 compiles exactly as before, byte for byte, so the new
tools can replace the old ones for every map.

## 2. Compile with -engine xash

Add `-engine xash` to all four tools. VIS and RAD refuse a BSP2 map without it. Your command lines, with
that added:

    hlcsg:  -engine xash -nowadtextures -texdata 262144 -wadinclude halflife.wad -wadinclude ts_ph.wad -wadinclude specialists.wad -cliptype Precise -estimate
    hlbsp:  -engine xash -texdata 262144 -notjunc -maxnodesize 8192 -nohull2 -estimate
    hlvis:  -engine xash -texdata 262144 -estimate
    hlrad:  -engine xash -texdata 262144 -estimate   (plus your usual RAD options, -ao and the like)

Three things changed from what you ran:

- `-subdivide 512` is gone from hlbsp. It makes faces wider than hlrad can light: hlrad stops with "Bad
  surface extents" and crashes. That happens with stock SDHLT too; it just never got that far before.
  The default subdivide is fine now, since the vertex limit is no longer the problem.
- Run a full hlvis (no `-fast`) for the real map. With everything visible from everywhere, the server
  overflows each player's packets ("Datagram overflowed" in the console) and some entities stop updating.
- `-texdata 262144` stays on every tool: the map's textures come to about 41 MB, past SDHLT's default 32.

hlbsp's log says when it writes BSP2:

    96640 vertexes (v30: 65535), 41725 nodes (v30: 32767), 93394 marksurfaces (v30: 65535): writing Xash BSP2

The map stays a .bsp; copy it to ts/maps as usual.

## 3. Two changes to the game folder

Both go in the ts folder of the Xash3D FWGS install that runs the map: the server, and the players' too to
be safe (see the note under delta.lst). They change nothing for maps that fit Half-Life's limits.

### liblist.gam: edicts "4096"

Add this line:

    edicts "4096"

The combined map has about 1980 entities that stay in the game, and Xash holds 1200 unless the mod says
more. Without the line the map stops loading with "SV_AllocEdict: no free edicts (max is 1200)". Xash takes
up to 8192.

### delta.lst: wider origins

Every Half-Life mod's delta.lst sends an entity's position in 16 bits, which covers -4096 to 4096. Chazville
sits at about z -4450 in the combined map, so every door, model, sprite and player there arrives at the
players' game wrapped to the wrong place. The server still has them where they are: you can open a door you
cannot see, because it is drawn somewhere else. hlcsg's warnings "origin outside +/-4096" are this.

The kit's ts/delta.lst is TS 3.0's own with only these twelve lines changed, three in each of four blocks
(origin[0], origin[1] and origin[2] alike):

    entity_state_t           DT_SIGNED | DT_FLOAT, 16, 8.0    ->  19, 8.0
    entity_state_player_t    DT_SIGNED | DT_FLOAT, 18, 32.0   ->  21, 32.0
    custom_entity_state_t    DT_SIGNED | DT_FLOAT, 17, 8.0    ->  20, 8.0
    event_t                  DT_SIGNED | DT_FLOAT, 16, 8.0    ->  19, 8.0

That covers -32768 to 32768. If your delta.lst is not TS 3.0's (another mod, or edited), make the same
twelve changes in it rather than copying the kit's over it.

A Xash server sends its delta tables to each player as they connect, so the server's file is the one that
counts. That was tested with the server and the game on one machine only; put the file on the players' side
too until a dedicated server with outside players has been tried.

The other way out of this is to move the map so that every entity is inside +/-4096 and leave delta.lst
alone. The two cities could be stacked closer: FiskCity's brushes span z -1533 to 1120 and Chazville's 3700
units, which fits in 8192 with room between, though a few entities also sit past 4096 in x and y.

## What was tested, and what was not

Tested, on Linux, from fiskcity_chazville_combined.map: the four tools with -engine xash, then the map loaded
in Xash3D FWGS (upstream, August 2026) with TS. It reports coloured lighting, runs with about 2040
entities, and looks the same as FiskCity_XMAS.bsp and chazville_SEPT26-X3.bsp from the same spots, but for
content that changed between versions. With the wider delta.lst the shop doors and fronts in Chazville are
where they belong. hlrad baked the 370 model shadows and ambient occlusion.

The textures came from your own compiled maps; 30 newer ones were in none of them (fc-penthouse,
fc-signs2026a and the like) and were stand-ins here. Your lights.rad was not used, so rooms lit by
texture lights were darker than yours.

The Windows tools were run under Wine: hlcsg and hlbsp turn the combined map into BSP2 as the Linux ones do,
and a small map forced to BSP2 comes out byte for byte the same from both.

Not tested: the Windows tools on Windows itself, hlvis and hlrad from the Windows build, a full hlvis, a
dedicated server with outside players, and Steam Half-Life, which cannot load this map at all.

## The options

    -engine goldsrc   the default: Half-Life's limits, version 30, as stock SDHLT
    -engine xash      Xash3D FWGS's limits; version 30 when the map fits, bsp30ext past 32767 clipnodes,
                      BSP2 past any other 16-bit number (-xash is the same)
    -format bsp30|bsp30ext|bsp2   that layout rather than the smallest that fits; refused if the map does not
                      fit it, and bsp30ext and bsp2 need -engine xash

The SDHLT README in the compilers' folder has the limits each engine is held to.
