# Business OS — Database Design

## The Entities

The database may contain these tables:

- **Organization** — Every business is its own world; shop A's inventory must never leak to shop B. This is the tenant box from the architecture. Without it, you can't have more than one customer.
- **User** — the user of the system (owner, cashier, ...)
- **Products/Inventory** — the store's items available
- **Customer** — the shop's customers and their recordings
- **Suppliers** — from where the products are brought
- **Sales** — records each day's selling recordings
- **Purchase** — the money out; a business OS that knows sales but not purchases can't answer "what's my margin?"
- **Inventory Movement** — when you buy stock it goes in; when you sell it goes out. Every product's stock level is just the total of its movements. This is where the deterministic math lives — a human, not an AI, counts bananas.
- **Audit Log** — every change and every AI action recorded. When the AI drafts a purchase order, we need to know who asked, when, and why.

**Stock movement** = any event that changes the stock quantity.
**Stock** = how much of a product you currently have.

## 1. Entities (nouns from the requirements)

| Entity | Why it exists | Screen that revealed it |
|---|---|---|
| Organization | which shopping org is it | Dashboard, Create-Organization |
| User | who uses the app | AuthForm, Profile |
| Products/Inventory | what things are available in the organization | Products-list, Products-Detail |
| Customer | who is buying the org's products | List, CustomersHistory, Frequent customers, Customer-Detail |
| Suppliers | who provide the products | Create Product, Low-stock request, Supplier Detail |
| Sales | who bought which product on this day | Sales History, Dashboard |
| Purchases | products we imported and expenses of the stock | Supplier Detail, Purchase History |
| Inventory Movement | tracks the movement of stock in and out to calculate total movement | Inventories |
| Audit Log | every change and every AI action recorded | Audit logs |

## 2. The detail of the tables

### Organizations

| Field | Type |
|---|---|
| id | IntegerField PK |
| name | CharField |
| location | CharField |
| description | TextField |
| logo | ImageField |
| created_at | DateTimeField |

### Users

| Field | Type |
|---|---|
| id | BigInt PK |
| email | EmailField UNIQUE (used for login) |
| password | CharField (hashed, never plain text) |
| username | CharField UNIQUE |
| image | ImageField |
| first_name | CharField |
| last_name | CharField |
| phone | CharField |
| organization | ForeignKey -> Organization |
| role | CharField (cashier / owner / manager) |
| created_at | DateTimeField |

**For the future:** a Membership table (user_id, organization) if a person works at more than one shop. Not for MVP.

### Categories

| Field | Type |
|---|---|
| id | IntegerField PK |
| name | CharField UNIQUE |

Why a table? "Banana" and "banana" must be forced to be the same row.

### Products

| Field | Type |
|---|---|
| id | IntegerField PK |
| category | ForeignKey -> Categories |
| organization | ForeignKey -> Organization |
| name | CharField |
| price | DecimalField |
| created_at | DateTimeField |

Stock is calculated from movements — never stored. More dynamic, one fact one home.

**QR codes:** generated on the fly from the product's ID. Never store the image.

### Customers

| Field | Type |
|---|---|
| id | IntegerField PK |
| name | CharField |
| organization | ForeignKey -> Organization |
| email | EmailField |
| phone | CharField |

### Suppliers

| Field | Type |
|---|---|
| id | IntegerField PK |
| name | CharField |
| organization | ForeignKey -> Organization |
| location | CharField |
| description | TextField |

### Sales

| Field | Type |
|---|---|
| id | IntegerField PK |
| organization | ForeignKey -> Organization |
| customer | ForeignKey -> Customer |
| status | CharField (completed / cancelled / awaiting payment) |
| created_by | ForeignKey -> Users |
| created_at | DateTimeField |

Total is calculated live from SoldItems — never stored.

### SoldItems

| Field | Type |
|---|---|
| id | IntegerField PK |
| sale | ForeignKey -> Sales |
| product | ForeignKey -> Products |
| price_at_time | DecimalField |
| quantity | IntegerField |

price_at_time = the receipt tells the truth even after prices change.

### Purchases

| Field | Type |
|---|---|
| id | IntegerField PK |
| supplier | ForeignKey -> Suppliers |
| organization | ForeignKey -> Organization |
| status | CharField (draft / ordered / received) |
| created_at | DateTimeField |
| created_by | ForeignKey -> User |

The draft state is the AI feature: the AI creates drafts, a human confirms.

### PurchasedItems

| Field | Type |
|---|---|
| id | IntegerField PK |
| purchase | ForeignKey -> Purchases |
| product | ForeignKey -> Products |
| quantity | IntegerField |
| cost_at_time | DecimalField |

### Inventory Movements

| Field | Type |
|---|---|
| id | IntegerField PK |
| organization | ForeignKey -> Organization |
| product | ForeignKey -> Products |
| quantity | IntegerField (always a positive number) |
| type | ChoiceField (IN / OUT) |
| sale_item | ForeignKey -> SoldItems, nullable |
| purchase_item | ForeignKey -> PurchasedItems, nullable |
| created_by | ForeignKey -> User |
| created_at | DateTimeField |

Stock of any product = SUM(IN) - SUM(OUT). This table is the heart.

### Audit Logs

| Field | Type |
|---|---|
| id | IntegerField PK |
| organization | ForeignKey -> Organization |
| user | ForeignKey -> User |
| action | CharField (created sale #42, approved purchase, AI answered question...) |
| target | CharField (which record was touched: table + id) |
| details | TextField (extra info, e.g. AI tool called) |
| created_at | DateTimeField |

One row per event. It must answer: who, which shop, what, which record, when.
