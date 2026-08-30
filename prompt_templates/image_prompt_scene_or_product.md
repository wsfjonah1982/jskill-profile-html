# Hero / product / scene image prompt formula

Fill in the brackets below, write the result as **one flowing sentence or two** into a `.txt`
file, then pass it to `scripts/generate_image.py --prompt <file> --output <path>`. Use this for a
hero background, a product photo, a menu-item shot, or any other scene/object image a template
needs.

**Formula:**
`[Style] photograph of [subject: the product/scene/interior, with enough specific detail to be
distinctive], [composition: e.g. wide interior shot / studio product shot on white / close-up],
[lighting: e.g. warm low amber lamplight / bright even studio light], [mood/atmosphere],
[technical: shallow depth of field, fine film grain, realistic materials], [aspect note: wide
16:9 framing for a hero / square framing for a product tile — match the template's slot].`

Leave clear **negative space** in the composition wherever text will overlay the image (e.g. "a
dark, empty upper-left third of the frame") — call this out explicitly for hero images.

**Example** (used for the Jonah Wang sofa page's hero background):

> Cinematic realism wide interior photograph, a single curated three-seater sofa in a dim
> upscale showroom or living space at night, warm low amber lamplight pooling on the sofa from
> the right side, rest of the room falls into near-black shadow, negative empty dark space in the
> upper-left third of the frame for text overlay, moody atmospheric haze, fine film grain,
> shallow depth of field, luxury interior editorial photography style, wide 16:9 framing.
