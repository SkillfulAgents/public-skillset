"""Agent avatar vocabulary, shared by the index generator and the importer.

Dependency-free so ``scripts/import_botdirectory.py`` can use it under a plain
``python3``.
"""

# Mirrors AGENT_AVATAR_COLORS and AGENT_AVATAR_SHAPES in SuperAgent's
# src/shared/lib/types/agent-avatar.ts, which rejects anything else.
AVATAR_COLORS = (
    "tonal-red", "tonal-orange", "tonal-amber", "tonal-green", "tonal-forest",
    "tonal-teal", "tonal-blue", "tonal-cobalt", "tonal-purple", "tonal-blush",
    "tonal-pink", "tonal-brown", "tonal-chocolate", "tonal-white", "tonal-grey",
    "tonal-black",
    "duo-red-amber", "duo-green-amber", "duo-forest-teal", "duo-teal-blush",
    "duo-blue-amber", "duo-cobalt-teal", "duo-pink-blue", "duo-brown-amber",
)
AVATAR_SHAPES = ("circle", "squircle", "triangle", "diamond", "hexagon", "pill", "arch", "bloom")


def _name_hash(value: str) -> int:
    """SuperAgent's ``hashString`` (explore/template-meta.ts), over UTF-16 code units."""
    units = value.encode("utf-16-le")
    hash_ = 0
    for i in range(0, len(units), 2):
        hash_ = (hash_ * 31 + int.from_bytes(units[i : i + 2], "little")) & 0xFFFFFFFF
    hash_ ^= hash_ >> 16
    hash_ = (hash_ * 0x7FEB352D) & 0xFFFFFFFF
    hash_ ^= hash_ >> 15
    return hash_


def default_avatar(name: str) -> dict[str, str]:
    """The avatar SuperAgent draws for a template without one: a tonal colour
    and a shape, each hashed from the name. New templates start from this."""
    tonal = [color for color in AVATAR_COLORS if color.startswith("tonal-")]
    return {
        "color": tonal[_name_hash(name) % len(tonal)],
        "shape": AVATAR_SHAPES[_name_hash(f"{name}:shape") % len(AVATAR_SHAPES)],
    }
