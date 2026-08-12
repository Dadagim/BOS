# Development Roadmap — Build the POS + AI System

> How this works:
> 1. Each phase has tasks with checkboxes.
> 2. You do a task, tick it, and tell me "phase X task Y done".
> 3. I review your work BEFORE you move to the next task in that phase.
> 4. When a phase is fully done, we unlock the next one.
> 5. Every task has a **Tool** recommendation: use that tool, in that way.

**Golden rules while building:**
- The database is the source of truth.
- Money math is always deterministic code — never AI, never by hand.
- Money is always `DecimalField`. Never `IntegerField`.
- Every sale/purchase writes an Inventory Movement.
- Test before you celebrate.

---

## PHASE 1 — Make the data alive (Auth + Admin + Basic API)

**Goal:** You can register, log in, and see/create products through a web page you built.

- [checked] **1.1 Install the API tools**
  Tool: PowerShell terminal in the project root.
  Run: `.venv\Scripts\pip.exe install djangorestframework djangorestframework-simplejwt`
  (This adds Django REST Framework — the tool that turns models into web routes — and JWT for login tokens.)

- [ checked] **1.2 Register the tools in settings**
  Tool: PyCharm → open `backend/core/settings.py`
  Add `rest_framework`, `rest_framework_simplejwt` to `INSTALLED_APPS`.
  This tells Django "we use these."

- [checked ] **1.3 Create a superuser (admin account)**
  Tool: PowerShell terminal → `cd backend`
  Run: `..\.venv\Scripts\python.exe manage.py createsuperuser`
  (Give it an email + password. This is YOUR admin login.)

- [checked] **1.4 Register models in the admin panel**
  Tool: PyCharm → `backend/inventory/admin.py`
  Register `Organization`, `Category`, `Product`, `Customer`, `Supplier`, `Sale`, `Purchase`, `InventoryMovement`, `AuditLog`.
  Then run the server and visit http://127.0.0.1:8000/admin/ — you should SEE your tables as web pages.

- [checked] **1.5 Create the auth routes (register + login)**
  Tool: DRF + SimpleJWT. Add URLs in `backend/core/urls.py` for:
  `POST /api/auth/register/`, `POST /api/auth/token/`, `POST /api/auth/token/refresh/`, `GET /api/auth/me/`
  Test in your browser at the browsable API or with Postman.

- [ ] **1.6 Build the product API (serializers + views)**
  Tool: DRF Serializers + ViewSets in PyCharm.
  Create: `GET/POST/PATCH/DELETE /api/products/` and `/api/categories/`.
  Rule: every query is scoped to the logged-in user's organization.

- [ ] **1.7 Build customer + supplier API**
  Tool: same pattern as products. `GET/POST/PATCH/DELETE /api/customers/`, `/api/suppliers/`.
  Same tenant scoping.

- [ ] **1.8 Commit**
  Tool: PowerShell terminal → `git add .` then `git commit -m "Phase 1: auth and basic API"`

**Definition of done:** you can register a new user, log in, and create products/customers/suppliers through the API, and every user only sees THEIR shop's data.

---

## PHASE 2 — The money flows (Sales, Purchases, Inventory)

**Goal:** A sale and a purchase actually change stock — automatically, correctly.

- [ ] **2.1 Create a sale with items — transactionally**
  Tool: Django shell (`..\.venv\Scripts\python.exe manage.py shell`).
  Write a small script: create a Sale + SoldItems. Verify the total calculates from lines.

- [ ] **2.2 Auto-create Inventory Movement on every sale**
  Tool: PyCharm → add logic in the sale-creation service.
  Every SoldItem creates a Movement (type=OUT, linked to that sale item).
  Test in the shell: after a sale, check movements exist.

- [ ] **2.3 The stock endpoint (calculated, never stored)**
  Tool: DRF + ORM aggregation in PyCharm.
  `GET /api/products/{id}/stock/` → returns SUM(IN) - SUM(OUT) from movements.
  Verify it matches a hand-calculated example.

- [ ] **2.4 Purchases: create → draft → ordered → received**
  Tool: Django shell.
  Create a Purchase (status=draft), add PurchasedItems, then a function that moves status forward.
  Verify status transitions only go forward (draft→ordered→received).

- [ ] **2.5 Receiving creates IN movements**
  Tool: PyCharm logic.
  When a purchase becomes `received`, create Movements (type=IN) linked to its items.
  Stock should now go UP after receiving.

- [ ] **2.6 Protect stock from going negative**
  Tool: transaction + validation in PyCharm.
  Selling 10 bananas when only 3 exist must FAIL with a clear error.
  Test it in the shell.

- [ ] **2.7 Write tests for money rules**
  Tool: PyCharm → `backend/inventory/tests.py`. Use Django's built-in `TestCase`.
  Test: total calculation, movement creation, negative stock blocked, status flow.
  Run: `..\.venv\Scripts\python.exe manage.py test`

- [ ] **2.8 Commit**
  Tool: `git add .` + `git commit -m "Phase 2: sales, purchases, inventory"`

**Definition of done:** sell → stock goes down + movement recorded. Receive purchase → stock goes up. You can't sell what you don't have. All covered by passing tests.

---

## PHASE 3 — POS features (Scan, Open Sale, Checkout, VAT, Import)

**Goal:** The cashier can scan, build a cart, checkout with VAT.

- [ ] **3.1 Add `barcode` to Product**
  Tool: PyCharm → `models.py`, add `barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)`.
  Run `..\.venv\Scripts\python.exe manage.py makemigrations` then `migrate`.

- [ ] **3.2 Add `payment_method` to Sale**
  Tool: PyCharm → `models.py`. Choices: cash / telebirr / card / credit.
  Also add a new Sale status: `open` (the cart). Migration again.

- [ ] **3.3 Scan endpoint**
  Tool: DRF. `GET /api/products/scan/{barcode}/` → returns the product or 404.
  If not found → frontend shows "new product" prompt (scan-to-learn).

- [ ] **3.4 Open sale (the cart lives in the database)**
  Tool: DRF. `POST /api/sales/` creates a Sale with status=open.
  `POST /api/sales/{id}/items/` adds a SoldItem to the open sale.
  No movements yet — nothing left the shelf.

- [ ] **3.5 Checkout**
  Tool: DRF. `POST /api/sales/{id}/checkout/` → sets status=completed, writes movements OUT, applies VAT.
  Test: open a sale, add 3 items, checkout, check movements + stock.

- [ ] **3.6 VAT**
  Tool: Python `Decimal` in PyCharm (NOT AI, NOT floats).
  `vat = total * Decimal("0.15")`. Store vat on the sale at checkout.
  Rule: rate stored as a setting, never hardcoded magic number in 10 places.

- [ ] **3.7 Bulk import from Excel**
  Tool: `openpyxl` package + a Django management command.
  Command: `..\.venv\Scripts\python.exe manage.py import_products file.xlsx`
  Reads name, barcode, price, category rows → creates products.
  Test with a sample file of 100 fake products.

- [ ] **3.8 Dashboard endpoint**
  Tool: DRF + ORM. `GET /api/dashboard/` → today's sales total, low-stock list, unpaid invoices count.

- [ ] **3.9 Tests + commit**
  Tool: tests.py + `git commit -m "Phase 3: POS features"`

**Definition of done:** scan a barcode → see product; build a cart that survives a crash; checkout applies VAT, records the payment, and moves stock. 100 products import from one Excel file.

---

## PHASE 4 — The cashier's screen (React frontend)

**Goal:** A web page the cashier can actually use.

- [ ] **4.1 Create the React app**
  Tool: PowerShell terminal → `cd frontend`, then
  `npm create vite@latest . -- --template react` (choose React).
  Then `npm install`. Open with WebStorm.

- [ ] **4.2 Login page**
  Tool: React + fetch. Calls `POST /api/auth/token/`, stores the access token.
  Show a clear error if wrong password.

- [ ] **4.3 The POS screen (the heart)**
  Tool: React. Layout: left = scan/search box, middle = cart, right = total.
  Scanning = typing a barcode into a box and pressing Enter (real scanners type like a keyboard).

- [ ] **4.4 Add-to-cart calls the API**
  Tool: React + fetch. Scan → `GET /products/scan/{code}` → add to open sale → `POST /sales/{id}/items/`.
  Every add updates the screen from the database (not from a local guess).

- [ ] **4.5 Checkout button**
  Tool: React. Calls `POST /api/sales/{id}/checkout/`. Shows total + VAT + payment method.
  After success: clear screen, show "sale complete".

- [ ] **4.6 Products page + dashboard page**
  Tool: React. Simple tables calling `GET /api/products/` and `GET /api/dashboard/`.

- [ ] **4.7 Test it yourself as the cashier**
  Tool: your browser. Register two users in different shops — make sure they NEVER see each other's products.
  Commit: `git commit -m "Phase 4: cashier screen"`

**Definition of done:** a cashier can scan items, see the cart, checkout with VAT, and the other shop's data never appears.

---

## PHASE 5 — The AI assistant

**Goal:** Ask the system questions in normal language; it answers from REAL data and can draft a purchase order — but never without approval.

- [ ] **5.1 Choose the AI provider and get an API key**
  Tool: your AI provider's dashboard (OpenAI or Anthropic). Create a key. Store it in an `.env` file (never commit it!).

- [ ] **5.2 Build the AI service module**
  Tool: the provider's Python SDK, in PyCharm. One small module: `backend/ai/client.py`.
  Keep it small: a function `ask(user_message, tools) -> answer`.

- [ ] **5.3 Define typed tools**
  Tool: the provider's function-calling format.
  Start with 3 safe tools: `get_low_stock`, `get_receivables`, `get_sales_summary`.
  Each tool runs OUR code against the user's organization — never the AI writing queries.

- [ ] **5.4 The chat route**
  Tool: DRF. `POST /api/ai/chat/` → auth → call AI → return answer with citations.

- [ ] **5.5 Draft purchase order tool (with approval)**
  Tool: the `create_draft_purchase_order` tool creates a Purchase with status=draft ONLY.
  The route returns "confirm?" and the human clicks approve on `POST /api/purchases/{id}/approve/`.

- [ ] **5.6 Audit every AI action**
  Tool: the `AuditLog` model. Log: who asked, what tool ran, what it returned, when.
  Never skip this — it's the receipt for the whole AI.

- [ ] **5.7 Evaluation set + cost tracking**
  Tool: a `docs/ai_tests.md` file with 10 fixed questions + the expected correct answers.
  Log cost per question. Run it every time you change the AI code.

- [ ] **5.8 Tests + commit**
  Tool: tests.py + `git commit -m "Phase 5: AI assistant"`

**Definition of done:** you can ask "what's almost out of stock?" and get a correct answer from YOUR data, and "draft a purchase order" produces a draft that only executes when YOU approve.

---

## PHASE 6 — Production ready (Docker, Postgres, safety)

**Goal:** The system runs like a real product, not a tutorial.

- [ ] **6.1 Switch the database to PostgreSQL**
  Tool: Docker Desktop → run a Postgres container. Change `settings.py` DATABASES.
  Rule: SQLite is for learning; Postgres is for real data and safety.

- [ ] **6.2 Environment config**
  Tool: `python-dotenv`. Move secret key + DB password into `.env` (never in code).

- [ ] **6.3 Observability**
  Tool: structured logging (Python `logging`). Log every request, error, and AI call with a timestamp + organization.

- [ ] **6.4 Rate limiting**
  Tool: DRF throttling. Limit AI calls per user per day — your cost control.

- [ ] **6.5 Dockerize the app**
  Tool: Docker Desktop. `Dockerfile` + `docker-compose.yml` (app + database).
  Goal: `docker compose up` runs the whole system.

- [ ] **6.6 Back up to GitHub**
  Tool: create a GitHub repo, `git push`. Your code is now safe on the internet.

- [ ] **6.7 Deploy to a host**
  Tool: a hosting platform. Get the system live where a real shop can use it.

- [ ] **6.8 Monitoring**
  Tool: an error tracker (e.g., Sentry). Get an alert when things break.

**Definition of done:** `docker compose up` starts the whole product, secrets are in `.env`, a stranger can sign up on the internet, and you get alerted on errors.

---

## The one rule that overrides everything

Between every phase: **go talk to a real shop.** The research package says it, and it's true — a beautiful product for nobody is a beautiful waste. After Phase 3, show the cashier screen to a real shop owner. Their reaction is your next task.
