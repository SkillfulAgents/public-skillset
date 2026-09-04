"""Regenerate (or extend) the presenter archetype library. Skips slugs whose portrait
already exists, so add a new entry to A and run to grow the library.
gpt-image-2 $0.128 per portrait — confirm cost with the user first.

  uv run --env-file /workspace/.env generate_library.py
"""
import subprocess, sys, json, os
from concurrent.futures import ThreadPoolExecutor

OUT = "/workspace/ads/assets/presenter-library"
os.makedirs(OUT, exist_ok=True)
PORTRAIT = "/workspace/.claude/skills/generate-talking-head/portrait.py"
REF = "/workspace/ads/refs/persona-reference.jpg"

HEAD = ("Match the photographic style, lighting realism, skin texture and camera feel of the reference photo exactly, "
        "but a completely different person and a different room. Unedited vertical iPhone front-camera selfie, arm's-length framing, "
        "slightly off-center with a small tilt, mild wide-angle edge distortion, deep phone-camera focus, computational HDR, "
        "faint sensor noise and JPEG compression. ")
TAIL = (" Chest-up, face in the upper third of the frame, looking into the lens, caught mid-sentence with a relaxed natural expression, "
        "lips slightly parted, natural facial asymmetry. Skin: visible pores, peach fuzz, under-eye texture, slight T-zone shine, "
        "a little uneven redness, a couple of small blemishes, flyaway hairs. Ordinary camera-roll photo, not a studio portrait, "
        "not airbrushed, no beauty filter, not CGI.")

A = {
 "genz-dorm-m": "A young man in his early twenties, Latino, short dark buzzcut, black oversized hoodie with creases. Light: cool LED strip along the ceiling mixed with warm desk lamp, uneven exposure. Setting: lived-in dorm room, gaming chair, snack wrappers, posters, slightly out of focus.",
 "genz-bedroom-f": "A young woman in her early twenties, East Asian, hair up in a claw clip, oversized vintage band tee. Light: overcast window light from camera-right mixed with a warm string of fairy lights, slightly imperfect white balance. Setting: small bedroom with an unmade bed, a mirror with photos taped on, a charging cable, slightly out of focus.",
 "kitchen-founder-f": "A woman in her early thirties, white, hair up in a messy bun, grey zip hoodie, leaning on a kitchen counter mid-explanation. Light: overcast window light plus warm ceiling spill, soft shadow falloff. Setting: ordinary kitchen with a mug, an open grocery bag, a dish rack, slightly out of focus.",
 "night-desk-dev-m": "A man in his mid twenties, South Asian, thin-framed glasses, wrinkled navy tee, just glanced back from a laptop. Light: bluish monitor spill on one cheek and a single warm desk lamp, noisy shadows. Setting: cluttered desk at night, cables, a second monitor, sticky notes, slightly out of focus.",
 "car-ops-m": "A man in his late thirties, white, slight stubble, quarter-zip fleece, sitting in the driver's seat of a parked car, phone held slightly below eye level. Light: broken windshield sunlight, blown-out highlight in the side window, imperfect exposure. Setting: ordinary car interior, seatbelt, coffee cup in the holder, slightly out of focus.",
 "study-expert-f": "A woman around fifty, white, grey flyaway hair, reading glasses pushed up on her head, linen shirt. Light: window light from camera-left with a warm lamp behind her, soft falloff. Setting: home study with stacked papers, bookshelves, a printer, slightly out of focus.",
 "coworking-founder-m": "A man in his early thirties, Black, short fade, open-collar shirt under a light knit, seated at a shared table. Light: bright overcast daylight from large windows, slightly clipped, imperfect auto white balance. Setting: coworking space with other laptops, a water bottle, a whiteboard behind, slightly out of focus.",
 "shop-owner-f": "A woman in her forties, Latina, hair tied back, canvas work apron over a tee. Light: fluorescent overhead mixed with daylight from an open doorway, slight green cast. Setting: small retail back office with shelving, boxes, a label printer, slightly out of focus.",
 "home-office-mom-f": "A woman in her mid thirties, Black, natural hair, soft cardigan, at a home desk. Light: window light from camera-right, warm bounce, uneven exposure. Setting: home office with a laptop, a child's drawing taped to the wall, a plant, a coffee mug, slightly out of focus.",
 "field-tech-m": "A man in his forties, white, weathered skin, hi-vis vest over a work shirt, standing by an open van door. Light: flat overcast daylight, slight motion softness. Setting: warehouse loading area with pallets and a van, slightly out of focus.",
 "post-run-m": "A man around thirty-five, mixed race, flushed cheeks and uneven sweat after a run, running tee, earbuds in one ear. Light: overcast park daylight, soft, slightly underexposed. Setting: park path with trees and a bench, slightly out of focus.",
 "exec-hotel-m": "A man in his mid fifties, white, grey hair, open-collar dress shirt with the tie removed. Light: single warm bedside lamp mixed with cool window light, uneven exposure. Setting: hotel room with a suitcase and a laptop on the desk, slightly out of focus.",
 "nurse-breakroom-f": "A woman in her late twenties, Filipino, hair in a low ponytail, blue scrubs, lanyard. Light: harsh fluorescent overhead with a hint of daylight from a small window, slight green cast. Setting: hospital break room with a fridge, vending machine, and a stack of paper cups, slightly out of focus.",
 "creative-studio-x": "A person in their mid twenties, androgynous, bleached short hair, septum ring, paint-flecked black sweatshirt. Light: big north-facing studio window from camera-left, soft grey daylight, slightly clipped highlights. Setting: art studio with canvases, jars of brushes, a laptop, slightly out of focus.",
}

def run(item):
    slug, desc = item
    out = f"{OUT}/{slug}.jpg"
    if os.path.exists(out):
        return slug, "exists"
    cmd = ["uv", "run", "--env-file", "/workspace/.env", PORTRAIT, "--prompt", HEAD + desc + TAIL, "--ref", REF, "--out", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return slug, ("ok" if r.returncode == 0 else "FAIL " + (r.stdout + r.stderr)[-400:])

with ThreadPoolExecutor(max_workers=7) as ex:
    for slug, res in ex.map(run, A.items()):
        print(slug, res, flush=True)
