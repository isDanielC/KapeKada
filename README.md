# KapeKada Coffee Cart — Business Website

Interactive business website for **KapeKada Coffee Cart**, built with **PyScript** for the
Event-Driven Programming final project (EVD 31). It uses the same business concept as the
Business Analytics feasibility study: an affordable specialty-coffee cart on Leon Kilat St.,
Pahina Central, Cebu City, serving everyone on the corridor — not just students or employees.

## Tech stack

- Plain **HTML5 + CSS3** for structure and styling (no frameworks).
- **[PyScript](https://pyscript.net)** (core, 2024.11.1) running Python in the browser via Pyodide.
- All interactivity — calculations, form handling, DOM updates — is written in **Python** (`main.py`), not JavaScript.

## Features & where the Event-Driven Programming lives

| Feature | Event type(s) | Where |
|---|---|---|
| Mobile nav menu open/close | `click` | `toggle_nav()` |
| Live order price preview as you change drink/size/add-ons/qty | `change`, `input` | `update_preview()` |
| Add a configured drink to the order | `click` | `add_to_order()` |
| Remove a line item from the order (dynamically created buttons, bound with `create_proxy`) | `click` | `remove_item_by_id()` |
| Place order / generate an order code | `click` | `place_order()` |
| Loyalty rewards calculator (buy 9 get 1 free) | `click` | `calc_loyalty()` |
| Live character counter on the feedback textarea | `input` | `update_char_count()` |
| Submit customer feedback (prevents default page reload, prepends a new card) | `submit` | `handle_feedback_submit()` |

See `main.py` for the full implementation — every handler has a docstring explaining which
event it responds to.

## Running it locally

PyScript/Pyodide loads via `fetch`, which browsers block on the `file://` protocol. You must
serve the folder over HTTP:

```bash
# from inside this folder
python3 -m http.server 8000
```

Then open **http://localhost:8000** in your browser. (Any other static server — VS Code's
"Live Server" extension, `npx serve`, etc. — works too.)

> First load takes a few seconds while Pyodide downloads and initializes — a "Brewing the
> page…" loading screen is shown until it's ready.

## Deploying with GitHub Pages (recommended for submission)

1. Push this repository to GitHub (see below).
2. Go to **Settings → Pages** in the repository.
3. Under "Build and deployment", set **Source: Deploy from a branch**, branch **main**, folder **/ (root)**.
4. Save. GitHub will publish the site at `https://<username>.github.io/<repo-name>/` within a minute or two.
5. Use that live link in your video demonstration and share it with your instructor if asked.

## Project structure

```
kapekada-website/
├── index.html        # all page sections (home, about, menu, order, rewards, feedback, visit)
├── style.css          # styling — warm coffee palette, fully responsive
├── main.py            # PyScript app: all event handlers and business logic
├── pyscript.toml       # PyScript app config
└── README.md
```

## Setting up the GitHub repository (for your group)

1. One member creates a **new public repository** on GitHub (e.g. `kapekada-website`).
2. Push this project to it (commands below).
3. Go to **Settings → Collaborators** and add every group member by their GitHub username.
4. **Each member should make their own commits** — e.g., one person can own the menu/order
   section, another the feedback section, another the styling/responsiveness, another the
   README/deployment — and push with their own git identity so the commit history reflects
   individual contribution, per the rubric.

```bash
cd kapekada-website
git init                                   # already done for you
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

If `git init` was already run (it has, in this project), just add the remote and push:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Submission checklist (per the project brief)

- [ ] Repository is set to **Public**
- [ ] All group members added as **collaborators**
- [ ] Every member has **meaningful commits** in the history (not just being added as a collaborator)
- [ ] 10+ minute **video presentation**, every member appears and speaks, covering:
  - Introduction (business name, members, concept)
  - Business process and how the website supports it
  - Live website demonstration (order builder, rewards calculator, feedback form)
  - Code explanation — especially `main.py`'s event handlers
  - Each member explains their individual contribution
- [ ] Video included in the repo or submitted per your instructor's instructions
- [ ] Only the **GitHub repository link** is submitted
