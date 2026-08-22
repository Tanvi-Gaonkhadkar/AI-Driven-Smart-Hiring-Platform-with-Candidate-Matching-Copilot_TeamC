# YourTalentPilot

Smart Hiring. Better Tomorrow.

## Setup (do this once, don't skip steps)

```bash
# 1. Create the virtual environment (do NOT delete this folder later)
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

## Important

- Always confirm your terminal shows `(.venv)` before running anything.
- In VS Code, make sure the Python interpreter selected (bottom-right corner) points to `.venv`, not your system Python — this was the cause of most `ModuleNotFoundError` issues previously.
- Never delete the `.venv` folder. If it breaks, delete and recreate it deliberately, then reinstall requirements.

## Project Structure

```
YourTalentPilot/
├── app.py                   # Entry point / landing page
├── pages/                   # One file per module (Streamlit native multipage)
├── components/               # Shared, reusable UI pieces (cards, tables, charts, sidebar)
├── data/                    # Single source of truth for all mock data
├── styles/                  # Design tokens + global CSS injection
├── assets/                  # Logo and static files
└── requirements.txt
```

## Design system

All colors, spacing, and fonts live in `styles/theme.py`. Never hardcode a
color or inject page-specific CSS — add it to the theme file so every page
stays visually consistent.
