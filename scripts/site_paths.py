"""Shared slug validation and TOS key-prefix building for publish_site.py and
unpublish_site.py, so both always target exactly the same objects.

A slug becomes part of an object-key prefix, and unpublish deletes everything
under that prefix — so an empty slug, or one containing "/" or "..", could
reach other sites' files. Only short lowercase kebab-case slugs are accepted.
"""
import re

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
DEFAULT_PREFIX_TEMPLATE = "site/manual/{slug}"


def validate_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug or ""):
        raise ValueError(
            f"Invalid slug {slug!r}: use 1-64 lowercase letters, digits, and hyphens "
            f"(not starting or ending with a hyphen), e.g. 'jane-doe-portfolio'."
        )
    return slug


def site_prefix(config: dict, slug: str) -> str:
    """Object-key prefix for a site, with no trailing slash."""
    validate_slug(slug)
    template = config.get("tos_key_prefix_template", DEFAULT_PREFIX_TEMPLATE)
    if "{slug}" not in template:
        raise ValueError(f"tos_key_prefix_template must contain '{{slug}}', got {template!r}")
    prefix = template.replace("{slug}", slug).strip("/")
    if not prefix.endswith(slug):
        raise ValueError(f"tos_key_prefix_template must end with '{{slug}}', got {template!r}")
    return prefix
