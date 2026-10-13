# Footwear Reference Lock — Shoe-Lift Spec Film

Version 2 · October 13, 2026 · Independent spec concept for @MamaCarrieOfficial (not a commissioned American Heelers ad)

## Locked references

| File | Role | What it locks |
|---|---|---|
| `refs/REF_C_left_shoe_AFTER_lift.jpg` | **Master shoe reference** | Finished external lift construction |
| `refs/REF_B_left_shoe_BEFORE.jpg` | Before state | Same upper, original sole height |
| `refs/REF_A_rear_demonstrator_scrubs.png` | Demonstrator + wardrobe | Rear view, ceil-blue scrubs, black shoes, left heel visibly taller |

## The shoe (never changes)

- Black Brooks Ghost-style running shoe. Black engineered mesh upper with a raised triangle texture.
- Dark charcoal collar lining. Black laces. Small silver reflective stripe at the toe. Silver reflective oval on the heel counter.
- Both side photos show the **outer side of the LEFT shoe, toe pointing screen-left**.

**Lift construction (after state):**
1. Original black midsole stays intact, including its sidewall line.
2. A matte-black added layer sits **between the midsole and the outsole**.
3. The layer is fullest under the heel and arch and tapers slightly toward the toe.
4. The original tread outsole is reattached on the bottom.
5. Edges are finished flush with the midsole sidewall.

**Not locked:**
- The "5/8 inch" label. It describes that example only. Never show a number on screen.
- Readable logo text. AI tools garble small brand text, so prompts say "subtle dark side logo" and ask for no legible text.

## Side rules (do not break)

| Camera view | Where the lifted LEFT shoe appears |
|---|---|
| Rear | Screen-LEFT (matches REF_A) |
| Front | Screen-RIGHT |
| Side, camera on her left | Nearest the camera; she faces and walks toward screen-LEFT |

**Never flip or mirror a clip.** Mirroring moves the lift to the right foot.

## Recommended production split

- **Static shoe detail (00:00–00:07, 01:03–01:10):** Use the real REF_C photo with the arrow and label removed, if American Heelers gives permission. Otherwise use Prompt 1.
- **Before/after reveal:** Crossfade REF_B → REF_C in CapCut, aligned on the upper. No AI is needed.
- **Workshop, packing and gait:** AI shots from the locked still, one action per clip.

---

## Prompt 1 — Shoe lock still
**Tool:** Higgsfield → Nano Banana Pro (image). **References:** REF_C (primary), REF_B. **Aspect:** 16:9.

```
Photoreal studio product photograph of ONE black running shoe, the LEFT shoe, outer side view, toe pointing to the left of frame. Match the reference shoe exactly: black engineered mesh upper with small raised triangle texture, dark charcoal collar lining, black laces, small silver reflective stripe near the toe, silver reflective oval on the heel counter, subtle dark-gray side logo. Sole: the original black midsole is intact, and a matte black external shoe-lift layer is added BETWEEN the midsole and the original tread outsole. The added layer is fullest under the heel and arch and tapers slightly toward the toe, with clean edges finished flush to the midsole sidewall. Plain warm light-gray seamless background, soft diffused key light from the upper left, gentle contact shadow, sharp focus on the sole edge. No text, no labels, no arrows, no measurement numbers, no second shoe, no extra logos.
```

## Prompt 2 — Workbench still (start frame for workshop clip)
**Tool:** Nano Banana Pro. **References:** your approved Prompt 1 result.

```
The exact same LEFT shoe from the reference image, unchanged in every detail including the added black lift layer, resting on a warm oak workbench in a small, tidy shoe repair workshop. Outer side view, toe pointing left. Soft neutral window light, shallow depth of field, a few hand tools softly blurred in the background. Photoreal. No readable text, no labels, no second shoe.
```

## Prompt 3 — Workbench motion (stationary inspection)
**Tool:** Seedance 2.0, image-to-video. **Start image:** Prompt 2 result. **Duration:** 5s. **Aspect:** 16:9.

```
Locked camera. The shoe stays completely still on the workbench. A slow, subtle push-in of about 10 percent toward the sole edge. Soft light shifts gently. The shoe's shape, laces, upper and lift layer remain identical in every frame. No hands, no morphing, no growing sole, no new objects, no text.
```

## Prompt 4 — Demonstrator side start frame
**Tool:** Nano Banana Pro. **References:** REF_A (wardrobe/body) + approved Prompt 1 shoe. **Aspect:** 16:9.

```
Photoreal side view, lower body from the waist down, of the same adult woman from the reference wearing ceil-blue scrub pants and black socks. Her LEFT side faces the camera and she faces the left of the frame, standing naturally mid-stride on a plain light-gray studio floor. Her LEFT shoe is the referenced black running shoe with the added black lift layer between midsole and outsole. Her RIGHT shoe is the same model with NO lift (normal sole height). Both feet fully visible with natural contact shadows. Soft even studio light, seamless light-gray background. No text.
```

## Prompt 5 — Side gait clip
**Tool:** Seedance 2.0, image-to-video. **Start image:** Prompt 4 result. **Duration:** 6s (4s used + 1s handles each end).

```
Locked tripod camera, no camera movement. The woman takes three ordinary, relaxed steps toward the left of frame at a comfortable walking pace on a level floor. Natural heel strike, full foot contact, smooth toe-off, believable alternating weight transfer and natural knee bend. Her LEFT shoe keeps the same added lift layer in every frame; her RIGHT shoe stays unmodified. Feet stay planted when in contact with the floor, no sliding. No limping, no exaggerated motion, no speed ramp, no camera orbit, no extra legs or feet, no changes to the shoes or clothing, no text.
```

## Prompt 6 — Front gait clip
**Tool:** Nano Banana Pro for the start frame, then Seedance 2.0 for motion. Same references.

Start frame:
```
Photoreal front three-quarter view, waist down, the same woman in ceil-blue scrub pants walking toward the camera on a plain light-gray studio floor. Her LEFT foot appears on the RIGHT side of the frame and wears the referenced black shoe with the added black lift layer; her RIGHT foot, on the left side of the frame, wears the same shoe with no lift. Both feet fully visible. Soft even studio light. No text.
```
Motion:
```
Locked camera, no movement. She takes three relaxed, ordinary steps toward the camera with believable alternating weight transfer, natural heel contact and toe-off. The lift stays on the shoe on the right side of the frame in every frame. No sliding, no mirroring, no shoe changes, no limping, no camera orbit, no text.
```

## Prompt 7 — Packing clip (one left shoe only)
**Tool:** Nano Banana Pro start frame → Seedance 2.0, 5s.

```
Overhead three-quarter view of a plain kraft shipping box on a clean kitchen table. Two hands calmly place ONE black running shoe, the referenced LEFT shoe with no lift yet (original sole height), into the box beside a folded blank white paper form. Natural window light, realistic hands with five fingers each, steady grip. Locked camera. Only one shoe, no second shoe, no readable text on the paper or box, no logos.
```
Add any form or shipping text later in CapCut.

---

## QC per clip (reject if any fail)

- [ ] Lift is on the LEFT shoe (check against the side-rules table)
- [ ] Upper, laces and toe stripe match REF_C; lift shape doesn't grow or shrink
- [ ] No mirroring; no extra feet, limbs or shoes
- [ ] Feet don't slide; heel contact and toe-off are visible
- [ ] No garbled text, numbers or invented logos
- [ ] Wardrobe matches REF_A (ceil-blue scrubs, black socks)
- [ ] Label "AI illustration — not a clinical outcome" during gait shots
