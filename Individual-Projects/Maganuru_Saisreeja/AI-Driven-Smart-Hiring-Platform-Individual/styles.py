def load_css(theme):

    if theme == "Light":

        bg = "#E8F1FC"
        card = "#F5F9FF"
        card_hover = "#DCEAFB"
        text = "#0F172A"
        secondary = "#475569"
        sidebar = "#DDEAFA"
        border = "#BFD9F5"
        input_bg = "#FFFFFF"
        muted = "#5B7A9E"
        popup_bg = "#FFFFFF"
        popup_text = "#0F172A"
        metric_bg = "#F0F6FE"
        accent = "#2563EB"
        success = "#16A34A"
        warning = "#EA580C"
        error = "#DC2626"
        scheme = "light"

    else:

        bg = "#0F172A"
        card = "#1E293B"
        card_hover = "#273548"
        text = "#F8FAFC"
        secondary = "#CBD5E1"
        sidebar = "#111827"
        border = "#334155"
        input_bg = "#1E293B"
        muted = "#94A3B8"
        popup_bg = "#1E293B"
        popup_text = "#F8FAFC"
        metric_bg = "#162233"
        accent = "#3B82F6"
        success = "#22C55E"
        warning = "#F97316"
        error = "#EF4444"
        scheme = "dark"

    on_accent = "#FFFFFF"  # text color placed on top of accent-colored backgrounds

    return f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ==========================================================
   ROOT / THEME TOKENS

   st.dataframe / st.data_editor render their grid on a <canvas>
   element (glide-data-grid), so ordinary CSS selectors like
   `td {{ color: ... }}` never reach that text. Its colors come
   exclusively from these --gdg-* custom properties, which is
   why table text can look "invisible" even when every other
   rule below is correct. Setting them here keeps dataframes in
   sync with the rest of the theme.
========================================================== */

html {{

    color-scheme:{scheme};

}}

:root, .stApp {{

    --gdg-bg-cell:{card};
    --gdg-bg-cell-medium:{card_hover};
    --gdg-bg-header:{metric_bg};
    --gdg-bg-header-hovered:{card_hover};
    --gdg-bg-header-has-focus:{card_hover};
    --gdg-bg-icon-header:{card};
    --gdg-bg-bubble:{card};
    --gdg-bg-bubble-selected:{card_hover};
    --gdg-bg-search-result:{accent}33;
    --gdg-bg-group-header:{metric_bg};
    --gdg-bg-group-header-hovered:{card_hover};
    --gdg-border-color:{border};
    --gdg-horizontal-border-color:{border};
    --gdg-header-bottom-border-color:{border};
    --gdg-drilldown-border:{accent};
    --gdg-text-dark:{text};
    --gdg-text-medium:{secondary};
    --gdg-text-light:{muted};
    --gdg-text-bubble:{text};
    --gdg-text-header:{text};
    --gdg-text-header-selected:{on_accent};
    --gdg-text-group-header:{secondary};
    --gdg-fg-icon-header:{secondary};
    --gdg-accent-color:{accent};
    --gdg-accent-fg:{on_accent};
    --gdg-accent-light:{accent}22;
    --gdg-link-color:{accent};
    --gdg-resize-indicator-color:{accent};

}}

/* ==========================================================
   BASE / TYPOGRAPHY
========================================================== */

html,
body,
[class*="css"] {{

    font-family:'Inter',sans-serif;

}}

html {{

    scroll-behavior:smooth;

}}

body {{

    background:{bg};
    color:{text};

}}

[data-testid="stAppViewContainer"] {{

    background:{bg};

}}

.stApp {{

    background:{bg};
    color:{text};

}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{

    display:none;

}}

header {{

    visibility:hidden;
    height:0;

}}

.block-container {{

    max-width:96rem;
    padding-top:1.5rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;

}}

h1,
h2,
h3,
h4,
h5,
h6 {{

    color:{text}!important;
    font-weight:700;

}}

/* Base text color. Deliberately NOT !important so that any
   element which sets its own explicit color further down
   this file (buttons, table headers, tags, links...) always
   wins, instead of fighting a blanket override. */
p,
span,
label,
small,
div {{

    color:{text};

}}

small,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {{

    color:{secondary}!important;

}}

hr {{

    border:0;
    border-top:1px solid {border};

}}

a,
a * {{

    color:{accent}!important;
    text-decoration:none;

}}

a:hover,
a:hover * {{

    color:#1D4ED8!important;

}}

/* ==========================================================
   SIDEBAR
========================================================== */
section[data-testid="stSidebar"]{{

    background:{sidebar};
    border-right:1px solid {border};

}}

section[data-testid="stSidebar"] *{{

    color:{text}!important;

}}

section[data-testid="stSidebar"] button:hover{{

    background:{accent}22!important;
    border-radius:8px;

}}

/* ==========================================================
   METRIC CARDS
========================================================== */

[data-testid="metric-container"]{{

    background:{metric_bg};
    border:1px solid {border};
    border-radius:14px;
    padding:18px;
    transition:all .25s ease;
    box-shadow:0 2px 8px rgba(0,0,0,.04);

}}

[data-testid="metric-container"]:hover{{

    background:{card_hover};
    transform:translateY(-2px);
    box-shadow:0 8px 20px rgba(0,0,0,.10);

}}

[data-testid="metric-container"] label,
[data-testid="metric-container"] label *{{

    color:{secondary}!important;
    font-weight:600;

}}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] *{{

    color:{text}!important;
    font-size:28px;
    font-weight:700;

}}

[data-testid="stMetricDelta"] svg {{

    color:inherit;

}}

/* ==========================================================
   BUTTONS
   (covers st.button, st.form_submit_button, st.download_button
   and any other native BaseButton variant, both wrapper and
   inner text/icon nodes so the blanket text-color rule above
   can never dim them back to the default text color)
========================================================== */

.stButton > button,
.stButton > button *,
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button *,
[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] button *,
button[data-testid^="stBaseButton-primary"],
button[data-testid^="stBaseButton-primary"] *,
button[data-testid^="stBaseButton-secondary"],
button[data-testid^="stBaseButton-secondary"] *{{

    color:{on_accent}!important;

}}

.stButton > button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button,
button[data-testid^="stBaseButton-primary"],
button[data-testid^="stBaseButton-secondary"]{{

    background:{accent}!important;
    border:none!important;
    border-radius:10px;
    padding:0.65rem;
    font-weight:600;
    width:100%;
    transition:.2s;
    box-shadow:0 3px 8px rgba(0,0,0,.08);

}}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stDownloadButton"] button:hover,
button[data-testid^="stBaseButton-primary"]:hover,
button[data-testid^="stBaseButton-secondary"]:hover{{

    background:#1D4ED8!important;
    transform:translateY(-1px);

}}

/* ==========================================================
   INPUTS
========================================================== */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div{{

    background:{input_bg}!important;
    color:{text}!important;
    border:1px solid {border}!important;
    border-radius:10px!important;

}}

.stTextArea textarea{{

    min-height:140px;

}}

.stTextInput input:focus,
.stTextArea textarea:focus{{

    border:1px solid {accent}!important;

}}

input::placeholder,
textarea::placeholder{{

    color:{muted}!important;
    opacity:1;

}}

/* Password show/hide toggle icon */
button[aria-label="Show password"],
button[aria-label="Hide password"]{{

    background:transparent!important;
    border:none!important;
    box-shadow:none!important;
    color:{muted}!important;

}}

button[aria-label="Show password"] svg,
button[aria-label="Hide password"] svg,
button[aria-label="Show password"] svg path,
button[aria-label="Hide password"] svg path{{

    fill:{muted}!important;
    color:{muted}!important;

}}

/* Selected chips inside multiselect / selectbox use BaseWeb's
   accent-filled "tag" component — force readable text on them. */
span[data-baseweb="tag"],
span[data-baseweb="tag"] *{{

    color:{on_accent}!important;
    background:{accent}!important;

}}

/* ==========================================================
   DROPDOWNS
========================================================== */

div[data-baseweb="popover"]{{

    background:{popup_bg}!important;

}}

div[data-baseweb="popover"] ul{{

    background:{popup_bg}!important;

}}

div[data-baseweb="popover"] li{{

    background:{popup_bg}!important;
    color:{popup_text}!important;

}}

div[data-baseweb="popover"] *{{

    color:{popup_text}!important;

}}

li[role="option"]:hover{{

    background:{accent}22!important;

}}

li[aria-selected="true"]{{

    background:{accent}33!important;
    color:{accent}!important;
    font-weight:600;

}}

/* ==========================================================
   FILE UPLOADER
========================================================== */

[data-testid="stFileUploader"]{{

    background:{card};
    border:2px dashed {border};
    border-radius:14px;
    transition:.2s;

}}

[data-testid="stFileUploader"] section{{

    background:{card};

}}

[data-testid="stFileUploaderDropzoneInstructions"] *{{

    color:{secondary}!important;

}}

[data-testid="stFileUploader"]:hover{{

    border-color:{accent};
    box-shadow:0 0 12px rgba(37,99,235,.15);

}}

/* Browse-files button inside the uploader is its own BaseButton */
[data-testid="stFileUploader"] button{{

    color:{text}!important;
    background:{card};
    border:1px solid {border};

}}

[data-testid="stFileUploader"] button *{{

    color:{text}!important;

}}

/* ==========================================================
   PROGRESS BAR
========================================================== */

.stProgress div{{

    border-radius:10px;

}}

.stProgress > div > div > div{{

    background:{accent};

}}

/* ==========================================================
   TABS
========================================================== */

button[role="tab"],
button[role="tab"] *{{

    color:{text}!important;
    border-radius:8px;

}}

button[role="tab"][aria-selected="true"],
button[role="tab"][aria-selected="true"] *{{

    background:{accent}22!important;
    color:{accent}!important;

}}

/* ==========================================================
   TABLES (markdown / st.table — plain HTML)
   NOTE: st.dataframe / st.data_editor are canvas-rendered and
   are themed separately via the --gdg-* variables at the top
   of this file, not by the rules below.
========================================================== */
table{{

    border-collapse:collapse;
    width:100%;

}}

thead tr{{

    background:{accent};

}}

th,
th *{{

    background:{accent}!important;
    color:{on_accent}!important;
    font-weight:600!important;
    border:none!important;

}}

td,
td *{{

    background:{card}!important;
    color:{text}!important;
    border-bottom:1px solid {border}!important;

}}

tbody tr:hover td{{

    background:{accent}11!important;

}}

[data-testid="stDataFrame"],
[data-testid="stDataEditor"]{{

    border:1px solid {border};
    border-radius:12px;
    overflow:hidden;

}}

[data-testid="stDataFrame"]:hover,
[data-testid="stDataEditor"]:hover{{

    box-shadow:0 6px 18px rgba(0,0,0,.08);

}}

/* ==========================================================
   PLOTLY
========================================================== */

.js-plotly-plot{{

    background:{card}!important;
    border:1px solid {border};
    border-radius:14px;
    padding:8px;

}}

.js-plotly-plot .bg{{

    fill:{card}!important;

}}

/* ==========================================================
   CHAT
========================================================== */

[data-testid="stChatMessage"]{{

    background:{card};
    border:1px solid {border};
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;

}}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span{{

    color:{text}!important;

}}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input{{

    background:{input_bg}!important;
    color:{text}!important;

}}

[data-testid="stChatInput"] button,
[data-testid="stChatInput"] button *{{

    color:{accent}!important;

}}

/* ==========================================================
   EXPANDERS
========================================================== */

details{{

    background:{card};
    border:1px solid {border};
    border-radius:12px;
    margin-bottom:10px;

}}

summary,
summary *{{

    color:{text}!important;
    font-weight:600;

}}

/* ==========================================================
   ALERTS (st.success / st.info / st.warning / st.error)
========================================================== */

[data-testid="stSuccess"],
[data-testid="stInfo"],
[data-testid="stWarning"],
[data-testid="stError"]{{

    border-radius:12px;

}}

[data-testid="stSuccess"], [data-testid="stSuccess"] *{{ color:{success}!important; }}
[data-testid="stWarning"], [data-testid="stWarning"] *{{ color:{warning}!important; }}
[data-testid="stError"],   [data-testid="stError"]   *{{ color:{error}!important; }}
[data-testid="stInfo"],    [data-testid="stInfo"]    *{{ color:{accent}!important; }}

/* ==========================================================
   CONTAINERS
========================================================== */

div[data-testid="stVerticalBlock"]{{

    border-radius:12px;

}}

div[data-testid="stContainer"]{{

    background:{card};
    border:1px solid {border};
    border-radius:12px;

}}

/* ==========================================================
   SCROLLBAR
========================================================== */

::-webkit-scrollbar{{

    width:10px;
    height:10px;

}}

::-webkit-scrollbar-track{{

    background:{bg};

}}

::-webkit-scrollbar-thumb{{

    background:{border};
    border-radius:20px;

}}

::-webkit-scrollbar-thumb:hover{{

    background:{accent};

}}

/* ==========================================================
   CHECKBOX & RADIO
========================================================== */

.stCheckbox label,
.stCheckbox label *,
.stRadio label,
.stRadio label *{{

    color:{text}!important;

}}

/* ==========================================================
   SLIDER
========================================================== */

.stSlider{{

    color:{accent}!important;

}}

[data-testid="stSliderThumbValue"],
[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"]{{

    color:{secondary}!important;

}}

/* ==========================================================
   HOVER EFFECTS
========================================================== */

[data-testid="metric-container"]:hover,
[data-testid="stFileUploader"]:hover,
details:hover,
div[data-testid="stContainer"]:hover{{

    box-shadow:0 8px 20px rgba(0,0,0,.10);

}}

</style>
"""