# Presenter archetype library

14 ready-made, hyper-real presenter portraits (openai/gpt-image-2, quality high, 9:16, 1152×2048) generated against `refs/persona-reference.jpg` as the style reference. `contact-sheet.jpg` shows all of them at once — deliver it in onboarding step 3 and ask "would any of these work for your audience, or should I make your own?"

Adopting one = copy `<slug>.jpg` to `ads/assets/<new-slug>-portrait.jpg` and add a roster row in `presenters.md` (the same portrait file is then reused for every clip). Each company gets its own copies, so several companies may share an archetype without sharing a roster.

| Slug | Person | Setting / light | Suggested voice direction | Reads as |
|---|---|---|---|---|
| genz-dorm-m | Man early 20s, Latino, buzzcut, black oversized hoodie | Dorm room, LED strip + warm desk lamp, gaming chair, posters | Fast, casual, meme-adjacent, medium-high energy | Student / young creator, consumer & prosumer apps |
| genz-bedroom-f | Woman early 20s, East Asian, claw clip, vintage band tee | Bedroom, overcast window + fairy lights, unmade bed | Casual, quick, wry | Student / early-career, lifestyle & consumer |
| kitchen-founder-f | Woman early 30s, messy bun, grey zip hoodie, leaning on counter | Kitchen, overcast window + warm ceiling spill, mug + grocery bag | Warm, dry, conversational | Solo founder / small-business owner |
| night-desk-dev-m | Man mid 20s, South Asian, glasses, wrinkled navy tee | Cluttered desk at night, monitor spill + desk lamp | Understated, precise, a little tired-funny | Developer / technical buyer |
| car-ops-m | Man late 30s, stubble, quarter-zip, in a parked car | Broken windshield sunlight, blown side-window highlight | Direct, no-nonsense, between-meetings energy | Ops / sales manager, field-heavy roles |
| study-expert-f | Woman ~50, grey flyaways, reading glasses pushed up, linen shirt | Home study, window + warm lamp, stacked papers | Calm, authoritative, explains-to-a-friend | Consultant / senior expert, professional services |
| coworking-founder-m | Man early 30s, Black, short fade, open collar under light knit | Coworking space, bright overcast windows, whiteboard | Confident, upbeat, founder energy | Startup founder / team lead, B2B SaaS |
| shop-owner-f | Woman 40s, Latina, hair tied back, canvas apron | Retail back office, fluorescent + doorway daylight, boxes, label printer | Practical, warm, slightly rushed | Small retail / e-commerce owner |
| home-office-mom-f | Woman mid 30s, Black, natural hair, soft cardigan | Home office, window light, kid's drawing on the wall, plant | Warm, grounded, relatable | Remote knowledge worker / parent, productivity & finance |
| field-tech-m | Man 40s, weathered, hi-vis vest, by an open van door | Warehouse loading area, flat overcast daylight | Blunt, plain-spoken, trades register | Trades / logistics / field services |
| post-run-m | Man ~35, mixed race, flushed after a run, earbud in | Park path, overcast, slightly underexposed | Breathy, energetic, candid | Health, fitness, habit & lifestyle apps |
| exec-hotel-m | Man mid 50s, grey hair, open-collar dress shirt | Hotel room, warm bedside lamp + cool window | Measured, senior, low energy but certain | Executive / enterprise buyer, travel-heavy roles |
| nurse-breakroom-f | Woman late 20s, Filipino, low ponytail, blue scrubs, lanyard | Hospital break room, fluorescent, vending machine | Kind, quick, matter-of-fact | Healthcare staff, shift-based professions |
| creative-studio-x | Person mid 20s, androgynous, bleached short hair, septum ring, paint-flecked sweatshirt | Art studio, big north window, canvases and brushes | Playful, deadpan, creative-scene register | Designers / creators / creative tools |

Gaps worth generating on demand (via `generate-talking-head/generate_library.py` — add an entry and run): teacher in a classroom, restaurant kitchen, farmer / outdoor worker, older woman 60+, teen (use with care), non-Western settings matching the company's market. Always keep the frame contract (chest-up, face upper third, looking into lens) and the capture-process prompt structure.
