"""Markdown -> Gmail-safe HTML email (inline styles only, table-based layout)."""

import re

import markdown as md

BG = "#030712"
ACCENT = "#5294ff"
INK = "#111827"
MUTED = "#6b7280"
LINE = "#e5e7eb"
PAGE = "#f3f4f6"

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# Gmail strips <style> blocks in several clients, so every rule is inlined per tag.
TAG_STYLES = {
    "h1": f"margin:28px 0 10px;font:700 22px/1.3 {FONT};color:{INK};",
    "h2": (
        f"margin:32px 0 12px;padding:0 0 0 12px;border-left:4px solid {ACCENT};"
        f"font:700 17px/1.35 {FONT};color:{INK};"
    ),
    "h3": f"margin:22px 0 8px;font:600 15px/1.4 {FONT};color:{INK};",
    "h4": f"margin:18px 0 6px;font:600 14px/1.4 {FONT};color:{MUTED};",
    "p": f"margin:0 0 14px;font:400 15px/1.6 {FONT};color:#374151;",
    "ul": f"margin:0 0 14px;padding-left:22px;font:400 15px/1.6 {FONT};color:#374151;",
    "ol": f"margin:0 0 14px;padding-left:22px;font:400 15px/1.6 {FONT};color:#374151;",
    "li": "margin:0 0 6px;",
    "table": (
        "width:100%;border-collapse:collapse;margin:0 0 18px;"
        f"border:1px solid {LINE};font:400 13px/1.45 {FONT};"
    ),
    "th": (
        f"padding:8px 10px;background:#f9fafb;border:1px solid {LINE};"
        f"text-align:left;font-weight:600;color:{INK};white-space:nowrap;"
    ),
    "td": f"padding:8px 10px;border:1px solid {LINE};color:#374151;vertical-align:top;",
    "a": f"color:{ACCENT};text-decoration:underline;",
    "strong": f"font-weight:700;color:{INK};",
    "blockquote": (
        f"margin:0 0 16px;padding:10px 14px;background:#f9fafb;"
        f"border-left:3px solid {LINE};font:400 15px/1.6 {FONT};color:{MUTED};"
    ),
    "code": (
        "padding:2px 5px;background:#f3f4f6;border-radius:3px;"
        "font:400 13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#b91c1c;"
    ),
    "pre": (
        f"margin:0 0 16px;padding:12px 14px;background:{BG};border-radius:6px;"
        "overflow-x:auto;font:400 13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
        "color:#e5e7eb;"
    ),
    "hr": f"margin:26px 0;border:0;border-top:1px solid {LINE};",
}

UP = "#047857"
DOWN = "#b91c1c"
DELTA_RE = re.compile(r"^(?:<strong[^>]*>)?\s*([+\-−])\s*[\d$]")


def _inline(html: str) -> str:
    for tag, style in TAG_STYLES.items():
        html = re.sub(
            rf"<{tag}(\s[^>]*)?>",
            lambda m, t=tag, s=style: f"<{t}{m.group(1) or ''} style=\"{s}\">",
            html,
        )
    # <pre><code> shouldn't get the inline-code chip treatment
    html = html.replace(
        f'<pre style="{TAG_STYLES["pre"]}"><code style="{TAG_STYLES["code"]}">',
        f'<pre style="{TAG_STYLES["pre"]}"><code>',
    )
    return html


def _color_deltas(html: str) -> str:
    """Tint numeric +/- cells so WoW movement is readable at a glance."""

    def repl(m):
        style, inner = m.group(1), m.group(2)
        hit = DELTA_RE.match(inner.strip())
        if not hit:
            return m.group(0)
        color = UP if hit.group(1) == "+" else DOWN
        return f'<td style="{style};color:{color};font-weight:600">{inner}</td>'

    return re.sub(r'<td style="([^"]*?);?">(.*?)</td>', repl, html, flags=re.S)


def _zebra(html: str) -> str:
    rows = html.split("<tr>")
    out = [rows[0]]
    body_idx = 0
    for row in rows[1:]:
        if "<th" in row:
            out.append("<tr>" + row)
            continue
        shade = ' bgcolor="#fbfcfd"' if body_idx % 2 else ""
        out.append(f"<tr{shade}>" + row)
        body_idx += 1
    return "".join(out)


def _split_title(html: str):
    """Pull a leading <h1> out of the body to use as the email header."""
    m = re.match(r"\s*<h1[^>]*>(.*?)</h1>", html, flags=re.S)
    if not m:
        return None, html
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return title, html[m.end():]


ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+\.)\s+\S")
ROW_RE = re.compile(r"\s*\|")


def _blank_line_before_blocks(text: str) -> str:
    """Reports often write a bold lead-in directly above a bullet list or table;
    markdown needs a blank line there or the block collapses into one paragraph —
    a table degrades all the way to raw pipes."""
    out = []
    block = "blank"  # blank | list | table | other
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            block = "other"
            continue
        if in_fence:
            out.append(line)
            continue

        if not line.strip():
            kind = "blank"
        elif ITEM_RE.match(line):
            kind = "list"
        elif ROW_RE.match(line):
            kind = "table"
        elif block == "list" and line[:1].isspace():
            kind = "list"  # indented continuation of the current item
        else:
            kind = "other"

        if kind in ("list", "table") and block not in ("blank", kind):
            out.append("")
        out.append(line)
        block = kind
    return "\n".join(out)


def render(markdown_text: str, title: str | None = None, summary: str = "", preheader: str = "", footer: str = "", brand: str = "SEO Agent") -> str:
    body = md.markdown(
        _blank_line_before_blocks(markdown_text),
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    body = _inline(body)
    doc_title, body = _split_title(body)
    title = title or doc_title or "Report"
    body = _color_deltas(_zebra(body))

    summary_html = ""
    if summary:
        inner = _inline(
            md.markdown(
                _blank_line_before_blocks(summary), extensions=["tables", "sane_lists"]
            )
        )
        summary_html = f"""
          <tr><td style="padding:22px 28px 4px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background:#f8fafc;border:1px solid {LINE};border-radius:8px;">
              <tr><td style="padding:16px 18px;">
                <div style="margin:0 0 10px;font:700 11px/1 {FONT};letter-spacing:.09em;
                            text-transform:uppercase;color:{MUTED};">Highlights</div>
                {inner}
              </td></tr>
            </table>
          </td></tr>"""

    footer_html = (
        f"""<tr><td style="padding:8px 28px 30px;">
              <div style="border-top:1px solid {LINE};padding-top:14px;
                          font:400 12px/1.6 {FONT};color:{MUTED};">{footer}</div>
            </td></tr>"""
        if footer
        else ""
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{PAGE};">
<div style="display:none;font-size:1px;color:{PAGE};max-height:0;overflow:hidden;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{PAGE};">
  <tr><td align="center" style="padding:24px 12px;">
    <table role="presentation" width="680" cellpadding="0" cellspacing="0" border="0"
           style="width:100%;max-width:680px;background:#ffffff;border-radius:12px;
                  border:1px solid {LINE};overflow:hidden;">
      <tr><td style="background:{BG};padding:22px 28px;">
        <div style="font:700 12px/1 {FONT};letter-spacing:.14em;text-transform:uppercase;color:{ACCENT};">{brand}</div>
        <div style="margin-top:8px;font:700 21px/1.3 {FONT};color:#ffffff;">{title}</div>
      </td></tr>
      <tr><td style="height:3px;background:{ACCENT};line-height:3px;font-size:0;">&nbsp;</td></tr>
      {summary_html}
      <tr><td style="padding:14px 28px 8px;">{body}</td></tr>
      {footer_html}
    </table>
  </td></tr>
</table>
</body></html>"""
