
Base URL: http://127.0.0.1:8000/api/


## Api endpoints and their jobs

POST   /auth/register/         ✅  create account
POST   /auth/token/            ✅  login → {access, refresh}
GET    /auth/me/               🔒  who am I
GET    /organizations/{id}/    🔒  my business's info

GET    /products/              🔒  list my products
POST   /products/              🔒  Create new Products
PUT    /products/{id}/         🔒  Update a product
DELETE  /products/{id}/        🔒  Delete A product
GET     /products/{id}/        🔒  Detail of Product

GET    /customers/             🔒  list my CUstomers
POST   /customers/             🔒  Create new Products
PUT    /customers/{id}/        🔒  Update a customers
DELETE /customers/{id}/        🔒  Delete A customers
GET    /customers/{id}/        🔒  Detail of customers

GET     /supliers/              🔒  list my Suppliers
POST    /supliers/              🔒  Create new supplier
PUT     /supliers/{id}/         🔒  Update a supplier
DELETE  /supliers/{id}/         🔒  Delete A supplier
GET     /supliers/{id}/         🔒  Detail of supplier


GET     /sales/                 🔒  list Sales History
POST    /Sales/                 🔒  sale a product -> the POST system like
PUT     /Sales/{id}/            🔒  Sale Detail
DELETE  /Sales/{id}/            🔒  UPdate A Sale history
GET     /Sales/{id}/            🔒  Delete of Sales History



GET     /purchase/                 🔒  purchase History
POST    /purchase/                 🔒  Purchase new products
PUT     /purchase/{id}/            🔒  purchase Detail
DELETE  /purchase/{id}/            🔒  Update A purchase history
GET     /purchase/{id}/            🔒  Delete of purchase History




# now do the same for: customers, suppliers, sales, purchases
# and answer: where does the AI live? (the chat + the draft purchase order)


Base URL: http://127.0.0.1:8000/api/

🔐 Auth (5)

Route	Purpose
POST /auth/register/	create account
POST /auth/token/	login → get {access, refresh}
POST /auth/token/refresh/	get a new access token when old expires
GET /auth/me/	who am I (my profile)
POST /auth/password/change/	change my password


🏢 Organization (2)


Route	Purpose
GET /organizations/{id}/	my business's info
PATCH /organizations/{id}/	edit my business (owner only)


📦 Catalog (Categories + Products)


Route	Purpose
GET /categories/	list categories
POST /categories/	create category
PATCH /categories/{id}/	rename category

GET /products/	list my products (filter by category, low stock)
POST /products/	create product
GET /products/{id}/	one product
PATCH /products/{id}/	edit product (price, name)
DELETE /products/{id}/	delete product
GET /products/{id}/stock/	current stock — calculated, never stored


👥 Customers & Suppliers (5 each — same shape)


Route	Purpose
GET /customers/	list
POST /customers/	create
GET /customers/{id}/	detail
PATCH /customers/{id}/	edit
DELETE /customers/{id}/	delete
(same for /suppliers/)



💰 Sales (5)

Route	Purpose
GET /sales/	sales history
POST /sales/	record a sale → also writes inventory movements OUT
GET /sales/{id}/	one sale
PATCH /sales/{id}/	change status (cancel, mark paid)


📥 Purchases (6) — the AI lives here

Route	Purpose
GET /purchases/	purchase history
POST /purchases/	create purchase — the AI creates this as a DRAFT
GET /purchases/{id}/	one purchase
PATCH /purchases/{id}/	edit a draft
POST /purchases/{id}/approve/	human signs the draft → ordered
POST /purchases/{id}/receive/	goods arrived → stock IN
🧾 Inventory & Dashboard
Route	Purpose
GET /inventory-movements/	full movement history (the traceability heart)
GET /dashboard/	one page: today's sales, low stock, who owes us


🤖 AI (1)

Route	Purpose

POST /ai/chat/	the assistant — answers questions, drafts purchase orders (never executes without approval)
What was wrong in your version (3 fixes)
/Sales/ and /purchase/ had their verbs shifted — GET was labeled "Update", DELETE was labeled "Detail". Every verb must match its job. In my table, read each row: verb → job → straight line.
PUT → use PATCH. PUT means "replace the whole thing." PATCH means "change a few fields." PATCH is what you'll want 99% of the time.
Missing routes you never had: categories, stock (calculated), inventory-movements, dashboard, password change, and the two human-action routes (approve, receive).
The two ideas I most want you to remember
POST /sales/ and POST /purchases/{id}/receive/ write inventory movements. The sale route isn't just "record money in" — it's "record money in and count bananas out." That's the deterministic heart we designed.
The AI has exactly ONE route (/ai/chat/), and it can only draft. It asks permission through approve/. The human is always the last signature.


Review the table. Tell me:

Any route whose purpose you don't understand — I'll explain it
When you're happy, we save this as the new docs/api.md — and then we build the routes for real (DRF serializers + views, one table at a time)
Which route confuses you the most right now?

