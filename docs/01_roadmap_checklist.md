# Roadmap — Phase by Phase (Checklist Style)

> How this works:
> 1. I give you a Phase with a checklist.
> 2. YOU do the tasks, in your own terminal, one at a time.
> 3. When a step gives a red error, don't panic — copy the error text and paste it to me.
> 4. When the checklist is done, say "Phase N done" and tell me what you saw.
> 5. I review your work, we talk, then I unlock the next phase.

Each phase has a Goal. If the goal is met, the phase is done.

---

## Phase 1 — Make the project breathe (UNLOCKED)
**Goal:** You see a Django welcome page in your browser.

1. Open your project folder in Windows Explorer
   (it's `Documents\Default Project`).
2. Click the address bar at the top of the window (where the folder path is),
   type `powershell`, press Enter.
   A window opens. This is your terminal, already standing inside the project.
3. Type `Get-ChildItem` and press Enter.
   You should see: `.gitignore`, `.venv`, `backend`, `docs`, `frontend`.
   (This command lists what's in the folder.)
4. Type `.venv\Scripts\python.exe --version` and press Enter.
   You should see `Python 3.13.x`.
   This is YOUR project's Python — the one inside the private room.
5. Type `.venv\Scripts\pip.exe install django` and press Enter.
   Wait for it to finish. (It was interrupted earlier, so re-run it.)
   This brings Django into the room.
6. Type `cd backend` and press Enter (walk into the backend drawer).
   Then type `..\.venv\Scripts\python.exe -m django startproject core .` and press Enter.
   No error = good. You just created the brain.
7. Type `Get-ChildItem`. You should now see a file `manage.py` and a folder `core`.
8. Type `..\.venv\Scripts\python.exe manage.py runserver` and press Enter.
   You'll see "Starting development server..." with a link like http://127.0.0.1:8000/
9. Open that link in your browser. You should see a Django welcome page.
10. Go back to the terminal, press `Ctrl+C` to stop the server.
11. Tell me "Phase 1 done" + what the welcome page looked like.

---

## Phase 2 — The brain's first heartbeat (LOCKED)
**Goal:** Your project speaks its first words (a working API that says "hello").
Preview: apps, models, the admin panel, your first save to the database.

---

## Phase 3 — The story of your business (LOCKED)
**Goal:** The database can hold products, customers, suppliers, purchases, sales.
Preview: your first real data models.

---

## Phase 4 — Talk to the brain (LOCKED)
**Goal:** The frontend can ask the backend for data.
Preview: React's first page.

---

## Phase 5 — The AI joins the team (LOCKED)
**Goal:** A chat that answers real questions about the business's own data.
Preview: tool calling, permissions, the draft purchase order.

---

## Phase 6 — Ship it to the world (LOCKED)
**Goal:** Someone else can use it.
Preview: Docker, deployment, monitoring.

---

*We'll write the detailed checklist of each phase only when we unlock it — so you never feel buried.*
