# Portrait / headshot image prompt formula

Fill in the brackets below, write the result as **one flowing sentence or two** into a `.txt`
file, then pass it to `scripts/generate_image.py --prompt <file> --output <path>`. Use this for
an About section's `.portrait` slot or an instructor-bio photo.

**Formula:**
`[Style] portrait photograph of [subject: age range, gender/appearance if relevant, clothing],
[pose/framing: e.g. three-quarter view headshot], [lighting: e.g. low-key moody lighting with a
warm rim light], [background: e.g. near-black charcoal void / softly blurred office],
[technical: shallow depth of field, shot on an 85mm lens, realistic skin texture, subtle film
grain], [aspect note: vertical 3:4 framing for a portrait slot].`

Match `[Style]` and the lighting/background choice to the chosen template's mood — a
luxury-portfolio-skinned page wants moody/low-key, a playful-personal one wants bright/soft.

**Example** (used for the Jonah Wang sofa page's About portrait):

> Cinematic realism portrait photograph of a Chinese man in his mid-30s, confident and warm
> expression, short neat dark hair, wearing a dark charcoal button-up shirt, three-quarter view
> headshot, low-key moody lighting with a single warm amber rim light separating him from the
> background, background is a near-black charcoal void with subtle soft gradient, shallow depth
> of field, shot on 85mm portrait lens, skin texture realistic and detailed, subtle film grain,
> editorial luxury-brand photography style, vertical 3:4 framing.
