"""
One-click "copy to clipboard" button.

Streamlit has no built-in copy button, and a plain st.button can't touch
the clipboard (that's a browser-only capability). This renders a tiny
self-contained HTML/JS component instead: clicking it copies the given
text directly in the browser - no server round-trip, no page rerun, so it
doesn't disturb whatever else is on the page (generated email, chat, etc).
"""

import html
import streamlit.components.v1 as components
from styles.theme import COLORS, FONT_FAMILY


def copy_to_clipboard_button(text: str, key: str, label: str = "Copy Email"):
    """
    Renders a small copy button in the current column/container.

    text: the exact text that will be copied
    key: a unique id for this button (must be unique per page/section,
         e.g. include the candidate's name so two candidates' buttons
         on the same page don't collide)
    """
    if not text:
        return

    safe_text = html.escape(text)
    safe_key = "".join(ch if ch.isalnum() else "_" for ch in key)

    component_html = f"""
    <div style="position:relative; display:flex; justify-content:flex-end;
                font-family:{FONT_FAMILY};">
      <button id="btn-{safe_key}" style="
          background:{COLORS['primary']}; color:#fff; border:none;
          border-radius:8px; padding:6px 14px; font-family:{FONT_FAMILY};
          font-size:13px; font-weight:600; cursor:pointer; white-space:nowrap;
          flex-shrink:0;">
        {label}
      </button>
      <span id="msg-{safe_key}" style="
          position:absolute; top:100%; right:0; margin-top:6px;
          font-size:12px; font-weight:600; color:{COLORS['success']};
          white-space:nowrap; opacity:0; transition:opacity 0.2s ease;
          pointer-events:none;">
        Email copied successfully!
      </span>
    </div>
    <textarea id="src-{safe_key}" style="position:absolute; left:-9999px; top:-9999px;"
              readonly>{safe_text}</textarea>
    <script>
      (function() {{
        const btn = document.getElementById("btn-{safe_key}");
        const msg = document.getElementById("msg-{safe_key}");
        const src = document.getElementById("src-{safe_key}");
        btn.addEventListener("click", async function() {{
          try {{
            await navigator.clipboard.writeText(src.value);
          }} catch (err) {{
            src.select();
            document.execCommand("copy");
          }}
          msg.style.opacity = 1;
          setTimeout(function() {{ msg.style.opacity = 0; }}, 2000);
        }});
      }})();
    </script>
    """
    # Note: the confirmation message used to sit inline next to the button
    # (just invisible via opacity:0), but an invisible element still takes
    # up layout space - in a narrow column that squeezed the button and
    # wrapped its label onto two lines, which the fixed iframe height then
    # clipped. Positioning the message absolutely (so it doesn't affect
    # the button's box) plus a slightly taller iframe fixes both.
    components.html(component_html, height=56)
