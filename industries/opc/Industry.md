# OPC (One-Person Company)

Pages for one person selling their own skills or venture: a freelancer, consultant, solo founder,
architect or engineer, coach, creator, or a small studio that is mostly one person. The page is
a bio, résumé/CV, portfolio, startup pitch one-pager, or personal brand homepage. Small
agency/company homepages use the same templates.

This guide covers what's specific to OPC pages. For everything shared (precheck, previews,
build, §3.1 sample content, §4 responsive checklist, §6 no fabricated proof points, §7 output
contract), follow the root [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Design

An OPC page sells trust in one person, so the design has to match how that person wants to come
across to the people who hire them.

- **The person is the brand.** Name and role lead the hero. Put a real headshot in the hero or
  sidebar if the user has one. Use a logo only when the business has its own name.
- **Mood decides the template.** Clean & professional, bold & confident, warm & personal, or
  dark & technical are different templates, not one template recoloured. Ask if the brief
  doesn't say (Step 2 in §2 below).
- **Match the buyer's formality.** An advisor to enterprises needs medium-high formality, while
  a creator or coach can go low. Check the template's `formality` against who pays, not against
  the person's own taste.
- **Proof sits near the top.** Real numbers, client or employer names, or work samples should be
  visible within the first screen or two, not buried under a long story.
- **One clear call to action.** Usually "Get in touch" or "Book a call", repeated in the nav and
  at the end. Contact goes only to channels the user really has.
- **Printable.** Many OPC pages double as a CV, so the print stylesheet and the "Save as PDF"
  button must keep working (root §4).

## 2. Content

Check `_input/brief.md`'s `## If OPC (Profile/Bio)` block and `_input/images/` first (root
Step 1). Ask only for what's missing or ambiguous.

**Subject, purpose and mood** (ask before picking templates, unless the brief answers them):

> "A few quick questions before I pick a template:
> 1. **Is this for a person or a company?**
> 2. **What's the page for?** (e.g. freelance portfolio, résumé/CV, startup landing page,
>    consultant bio, product pitch, personal brand homepage)
> 3. **What mood do you want?** (e.g. clean & professional, bold & confident, warm & personal,
>    dark & technical)"

If the brief's **Mood** field is blank or vague (e.g. "nice"), ask. Don't guess the mood from
the rest of the brief.

**The content a page needs**, at minimum:

- Name (person) or company name
- One-line tagline / value proposition
- Short bio or "about" paragraph
- The core offer: services, experience, or **the business idea** (problem it solves, what it
  does, why it matters)
- 2–5 proof points: work samples, case studies, past roles, metrics, or testimonials
- Contact info: email, and any social/portfolio links. Never a home address or personal phone
  number (root §3); a city or country is enough.
- Any images (headshot, logo, product shots). Check `_input/images/` first; if none exist, keep
  the template's placeholder blocks.

If the user gives you a raw document (résumé PDF, LinkedIn export, company one-pager), extract
these from it instead of re-asking for everything. Long résumés: lead projects and experience
with the most recent work and trim older items rather than listing everything.

## 3. Relevant templates

Full metadata for each one (mood, tone, formality, sections, screenshots) is in the shared
[`templates/index.json`](../../templates/index.json). Use `profile_type` as the first filter,
then match mood and formality. **Pick three that look genuinely different** for the hero previews
(root Step 5).

| Template | Scheme | For | Pick it when |
|---|---|---|---|
| `minimal-professional` | light | person or company | The person must read as competent and low-risk: consultants, advisors, B2B one-pagers. Also works as a CV page. |
| `bold-creative` | light | person or company | Indie founders and creative freelancers who want to be memorable rather than corporate. |
| `warm-editorial` | light | person or company | The story is the pitch: writers, coaches, therapists, boutique studios. |
| `dark-tech-modern` | dark | person or company | Tech founders and developers pitching a product or idea (problem → solution → features). |
| `corporate-pitch` | light | company or person | Established and low-risk: enterprise sales, investor one-pagers, executive bios. |
| `playful-personal` | light | person or company | Creators, coaches and small-business owners who want to feel warm and human. |
| `luxury-portfolio` | dark | person or company | Photographers, architects, designers: the visuals are the pitch. |
| `academic-cv` | light | person | Academics, researchers and job-seekers who need a dense, print-friendly CV. |
| `technical-sidebar-profile` | light | person | Hands-on technical ICs (FDEs, solution and pre-sales architects, ML/platform engineers) showing end-to-end delivery. |
| `playful-dev-folio` | light | person | Developers covering a lot of ground: skills, experience, open source, talks. |
| `mono-minimal-dev` | light | person | Engineers who want a quiet, typographic page where the work speaks. |
| `illustrated-sky-folio` | light | person | Developers working across several areas, each with its own illustrated row. |
| `bold-blue-folio` | light | person | Freelance and frontend developers selling to clients with project screenshots. |
| `github-card-profile` | light | person | Developers whose best proof is repositories, papers and posts. |

## 4. Build notes

- No industry-specific JavaScript beyond the mobile menu (and the stage strip in Technical
  Sidebar Profile), so the root §3 rules cover the build.
- Sample copy (root §3.1) can cover the tagline, about paragraph and service descriptions.
  Never metrics, employers, clients, credentials or contact details.
