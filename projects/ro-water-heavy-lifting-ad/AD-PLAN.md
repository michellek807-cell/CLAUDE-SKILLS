# "Heavy Lifting" — Luxury RO Water Ad (Higgsfield production package)

**Concept:** Relatability + convenience. Stop hauling cases of bottled water. Get clean water from the tap.
**Look:** Premium appliance commercial. Golden-hour heat outside, then a calm, sunlit marble kitchen inside.
Slow motion, shallow depth of field, brushed-nickel and crystal glass. The outside is warm and harsh (the struggle). The inside is cool, clean and quiet (the reward).
**Runtime:** 30 s master, plus a 15 s cutdown. **Aspect:** 9:16 (Reels / TikTok / Shorts), with a 16:9 reframe for YouTube and Facebook in-feed.
**Brand:** replace `[BRAND]`, `[PHONE]`, `[CITY]` everywhere before generating.

---

## 1. Characters (lock these first, reuse in every shot)

**Homeowner:** woman, late 30s, Black, natural hair in a loose puff, fitted cream linen tee, olive chinos, white sneakers, small gold hoops. Real skin texture with a light sheen of sweat.

**Technician (the hero):** man, mid 40s, warm and confident, close-cropped salt-and-pepper beard. Tailored charcoal work shirt with a small embroidered `[BRAND]` logo on the chest, dark navy work pants, a black leather tool roll. Clean, premium, never sloppy.

**Palette:** deep navy, brushed nickel, crystal clear water, warm gold sunlight, cream. Keep the burgundy/gold MamaCarrie palette out of this ad, because it belongs to a different brand.

---

## 2. Step-by-step in Higgsfield

1. **Character refs.** Generate one reference sheet per character (prompts in section 3) with **Nano Banana Pro**. Pick the best of each and save as `homeowner.png` and `tech.png`.
2. **Keyframes.** Generate the first frame of every shot (section 4) with **GPT Image 2** at 9:16 / 2K, passing the character refs with `--image`.
3. **Motion.** Animate each keyframe with **Seedance 2.0** (image-to-video, `--start-image`), at 1080p, 9:16.
4. **Voiceover.** Record the VO (section 5) in ElevenLabs (warm, confident male or female narrator) or Higgsfield Seed Audio. Higgsfield's Seedance 2.0 takes reference audio via `--audio`, not `--generate-audio`.
5. **Music + SFX.** Generate the SFX stingers with **Seed Audio 1.0** (section 6).
6. **Assemble** in CapCut: cut on the beats in section 4, add captions, end card, export at 1080x1920.
7. **Score it** before you spend money on ads: run the finished cut through Higgsfield's **Virality Predictor**.

---

## 3. Character reference prompts (Nano Banana Pro)

**Homeowner sheet**
```
Character reference sheet, photorealistic: a Black woman in her late 30s, natural hair in a loose puff, small gold hoop earrings, fitted cream linen t-shirt, olive chinos, white sneakers. Three views: front, three-quarter, profile. Neutral warm-grey studio backdrop, soft key light, realistic skin texture with visible pores, no retouching, 85mm lens, editorial commercial photography.
```

**Technician sheet**
```
Character reference sheet, photorealistic: a friendly, confident man in his mid 40s, close-cropped salt-and-pepper beard, tailored charcoal work shirt with a small embroidered logo on the chest, dark navy work pants, black leather tool roll in hand. Three views: front, three-quarter, profile. Neutral warm-grey studio backdrop, soft key light, realistic skin texture, premium trade-service brand photography, 85mm lens.
```

---

## 4. Shot list, 30 s master (9:16)

| # | Time | Beat | On-screen text |
|---|---|---|---|
| 1 | 0.0–3.0 | **HOOK:** plastic tears, bottles explode down the driveway in slow motion | *"There's a better way to get water."* |
| 2 | 3.0–7.0 | Homeowner straining up the driveway, two 40-packs, heat shimmer | — |
| 3 | 7.0–10.0 | Bottles roll past her feet, she drops her head, exhausted | *"Again?"* |
| 4 | 10.0–14.0 | Technician steps into frame and delivers the line | *"Stop breaking your back for water that tastes like plastic."* |
| 5 | 14.0–20.0 | Install montage: macro chrome fittings, filter stages, sleek faucet | *"Under-sink reverse osmosis. Installed in one visit."* |
| 6 | 20.0–25.0 | **REWARD:** she fills a crystal glass from the tap, sips, exhales | *"Clean water. Straight from your sink."* |
| 7 | 25.0–30.0 | End card: product + logo + CTA | *"[BRAND] · Free water test · [PHONE]"* |

### Keyframe prompts (GPT Image 2) + motion prompts (Seedance 2.0)

**Shot 1, Hook (3 s)**
Keyframe:
```
Ultra-low-angle cinematic close-up on a sunlit suburban driveway at golden hour. A clear plastic wrap on a 40-pack of bottled water is tearing open; dozens of water bottles burst outward and bounce toward the camera, droplets and sunlight flares frozen in the air. A woman's white sneakers and olive chinos in soft focus behind. Warm amber backlight, heat haze, anamorphic lens flare, shallow depth of field, premium commercial cinematography, 9:16.
```
Motion:
```
Extreme slow motion. The plastic wrap rips fully open and the bottles cascade and bounce down the driveway toward the lens, sunlight glinting off each bottle. Camera holds low and steady, then a subtle push-in. Photorealistic, high-end commercial.
```

**Shot 2, The Struggle (4 s)**
Keyframe (pass `--image homeowner.png`):
```
Medium-wide shot: the woman from the reference carries two heavy 40-pack cases of bottled water up a long concrete driveway toward an elegant modern home. Arms trembling, light sweat on her skin, jaw set. Harsh golden-hour sun behind her, visible heat shimmer off the concrete, manicured lawn, luxury suburban home. Cinematic, 35mm, realistic skin texture, 9:16.
```
Motion:
```
Slow tracking shot moving backward in front of her as she struggles uphill one step at a time; her grip slips slightly and she hitches the cases higher. Heat shimmer ripples. Natural, grounded movement, no exaggeration.
```

**Shot 3, The Conflict (3 s)**
Keyframe (pass `--image homeowner.png`):
```
Close-up: the woman stands still on the driveway, shoulders dropped, eyes closed, exhaling in frustration. Out-of-focus water bottles roll past her sneakers in the foreground. Warm backlight rims her hair. Emotional, realistic, cinematic, 85mm, 9:16.
```
Motion:
```
She lets one case drop to the ground beside her and exhales, head tilting back. Bottles keep rolling slowly past the foreground. Gentle handheld drift.
```

**Shot 4, The Turn (4 s)**
Keyframe (pass `--image tech.png --image homeowner.png`):
```
The technician from the reference steps confidently into the frame from the right on the sunlit driveway, smiling warmly, leather tool roll in one hand, a scattered water bottle at his feet. The woman looks up at him, surprised. Golden-hour backlight, clean premium trade-service look, shallow depth of field, cinematic, 9:16.
```
Motion:
```
The technician steps into frame, stops, and speaks directly to her with a calm, knowing smile and a small nod toward the house. She straightens up, curious. Camera eases in slowly toward him.
```
*(Add his line in the edit with the VO track, or pass the recorded line with `--audio` so Seedance lip-syncs it.)*

**Shot 5, The Install (6 s)**
Keyframe:
```
Luxury macro product shot inside a clean white under-sink cabinet: a sleek reverse osmosis filtration system with multiple clear filter housings and a compact storage tank, brushed-nickel fittings, a technician's hands in a charcoal shirt tightening a connection. Soft cool light, spotless, premium appliance commercial, shallow depth of field, 9:16.
```
Motion:
```
A three-cut montage: (1) macro of hands clicking a filter cartridge into its housing, (2) slow slider move across the clear filter stages, (3) a wrench giving a final quarter-turn on a brushed-nickel fitting. Smooth, precise, satisfying movement. Premium appliance commercial pacing.
```

**Shot 6, The Reward (5 s)**
Keyframe (pass `--image homeowner.png`):
```
Bright, airy luxury kitchen with white marble counters and morning-to-afternoon sunlight. The woman, relaxed and refreshed, holds a crystal glass under a slim brushed-nickel drinking-water faucet beside the main tap; clear water streams into the glass, catching the light. Calm, satisfied expression. Premium lifestyle commercial, 50mm, realistic skin, 9:16.
```
Motion:
```
Slow motion: clear water fills the crystal glass, light refracting through it. She lifts the glass, takes a sip, closes her eyes and exhales with relief, a small smile. Camera slowly pushes in. Serene, luxurious.
```

**Shot 7, End card (5 s)**
Keyframe:
```
Minimal luxury end card: a single crystal glass of clear water on white marble beside a slim brushed-nickel faucet, soft shadow, cool cream background with negative space at the top for a logo and at the center for a phone number. Elegant, premium, clean, 9:16.
```
Motion:
```
A single droplet falls into the glass in slow motion and the ripple settles. Camera locked off. Calm.
```
Add the logo, *"Free in-home water test"* and `[PHONE]` in CapCut, inside the safe zone (y 200–1620 px).

---

## 5. Voiceover script (30 s, ElevenLabs-ready)

Warm, assured narrator. Short sentences. Pauses marked with `—`.

```
[0–3]   There's a better way to get water.
[3–10]  (natural sound — strain, tearing plastic, bottles rolling)
[10–14] TECH (on camera): Stop breaking your back for water that tastes like plastic.
[14–20] With [BRAND], a reverse osmosis system goes right under your sink — installed in one visit.
[20–25] Clean, great-tasting water. Straight from your tap. No more hauling.
[25–30] Book your free in-home water test with [BRAND] today.
```

**15 s cutdown:** Shot 1 (0–3) → Shot 4 (3–7, the tech's line) → Shot 5, 2 s (7–9) → Shot 6 (9–13) → end card (13–15).

---

## 6. Sound design (Seed Audio 1.0)

```
Sharp plastic wrap tearing, followed by many plastic water bottles bouncing and rolling on concrete, outdoor summer ambience with cicadas
```
```
Satisfying mechanical click of a filter cartridge locking into place, then a soft metallic wrench turn, quiet clean room tone
```
```
Clear water pouring into a crystal glass in a quiet kitchen, gentle and close, soft room tone
```
Music: a warm, minimal piano-and-strings bed that starts tense (shots 1–3) and lifts at the tech's line (shot 4).

---

## 7. Commands (run on your own computer)

The Higgsfield CLI needs your login, so run this part yourself. Run each block on its own.

Install and log in:
```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
```
```bash
higgsfield auth login
```
Confirm the exact model IDs (names can change):
```bash
higgsfield model list --json | jq '.[].job_set_type'
```

Character refs:
```bash
higgsfield generate create nano_banana_pro --prompt "<Homeowner sheet prompt>" --aspect_ratio 16:9 --wait
```
```bash
higgsfield generate create nano_banana_pro --prompt "<Technician sheet prompt>" --aspect_ratio 16:9 --wait
```

Keyframe (example: shot 2):
```bash
higgsfield generate create gpt_image_2 --prompt "<Shot 2 keyframe prompt>" --image ./homeowner.png --aspect_ratio 9:16 --resolution 2k --wait
```

Motion (example: shot 2):
```bash
higgsfield generate create seedance_2_0 --prompt "<Shot 2 motion prompt>" --start-image ./shot2.png --duration 4 --resolution 1080p --aspect_ratio 9:16 --wait
```

SFX:
```bash
higgsfield generate create seed_audio --prompt "<SFX prompt>" --wait
```

Score the finished ad:
```bash
higgsfield generate create brain_activity --video ./heavy-lifting-30s.mp4 --wait
```

If a shot asks for a param the model does not accept, check it with `higgsfield model get seedance_2_0 --json`.

---

## 8. Captions (platform copy)

**Instagram / Facebook**
```
Still hauling cases of water up the driveway? 😮‍💨
There's a better way. [BRAND] installs reverse osmosis right under your sink, so clean, great-tasting water comes straight from your tap.
💧 Free in-home water test → [PHONE]
#ReverseOsmosis #CleanWater #WaterFiltration #HomeUpgrade #[CITY]
```
**TikTok:** `POV: you're done carrying water bottles forever 💧 #waterfilter #homehacks #reverseosmosis`
**YouTube Shorts title:** `Stop Hauling Bottled Water (Do This Instead)`

---

## 9. Claims check (read before publishing)

- **Don't say "infinite" or "unlimited" water.** Under-sink RO makes water at a set rate and stores a few gallons in a tank. Say *"on demand"* or *"straight from your tap"* instead.
- **Don't say "100% pure."** RO cuts many contaminants, but how much depends on the system and the local water. Back any reduction claim with the system's **NSF/ANSI 58** certification.
- *"Tastes like plastic"* works as a relatable line, but don't claim bottled water is unsafe.
- Keep the 1-visit install claim true for your service area.
