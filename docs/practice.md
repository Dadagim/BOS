Domain: "Buna & Friends" — a small coffee shop in Addis. Nothing fancy, one counter.

They need to remember:

What's on the menu and what it costs (macchiato, tea, sambusa, juice…)
Every order at the counter, and exactly what was in it
How each order was paid (cash / Telebirr / card)
Daily sales — which items sell, how much came in


## User

- id   IntegerField
- name        CharField
- email       EmailField
- phone       CharField
- password    CharField

## Menu

- id                        →   IntegerField
- item                      →   CharField
- Price                        → DecimalField
- created_at                 →  DateTimeField
- created_by -> ForeignKey User


## Order

- id                       →    IntegerField
- payment_method              → ChoiceFiled (telebirr/cash/mobilebankings)
- created_by                →   ForeignKey → User
- created_at                 →  DateTimeField

* We can calculate the total from the ordered Items table

## Ordered_Items

- id     IntegerField
- item_id  ForeignKey -> Menu                   
- Order_id  ForeignKey -> Order      
- price_At_time   DecimalField
- quantity        IntegerField

## Exercise Two

Domain: "Seeds & Sacks" — a wholesale shop that buys rice, flour, sugar, cooking oil from suppliers, and sells them by the sack to retailers.

They need to remember:

Products — what they sell, and their current price
Suppliers — where they buy from
Purchases — what they bought, from whom, at what cost
Sales — what they sold, to whom, at what price
Current stock — at any moment, how many sacks of rice do we have?


**
## Customer

- id   IntegerField
- name        CharField
- email       EmailField
- phone       CharField
# Supplier
** Records Product suppliers
- id -> IntegerField
- name -> CharField
- email -> Email

# Products
** tracks what products or Items are available

- id -> IntegerField
- name -> CharField
- price -> DecimalField
- created_at -> DateTimeField

**We can use the purchase table to show the supplier rather than attaching it to the products table itself**


# Purchases
    **tracks expenses and Import Items and cost**
      - id          -> IntegerField
      - supplier_id -> ForeignKey Supplier
      - status       → Choice (draft -> pending -> Confirmed)
      - created_at -> DateTimeField

# PurchaseItems
    ** records items in purchases
    
       - id            -> IntegerField
      - Purchase_id   -> ForeginKey purchase
      - item_id      -> FoereignKey -> Products
      - cost_at_time -> DecimalField
      - quantity     → IntegerField


# Sales 
    ** Records daily selling history
    
        - id      →  IntegerFields
      - customer →  ForeignKey Customers
      - status       → Choice (draft -> pending -> Confirmed)
      - created_at →  DateTimeFIELD


# SalesItems
    ** Records the items in sales
    - id            → IntegerField
      - sale_id      → ForeignKey Sales
      - item_id      -> FoereignKey -> Products
      - quantity      → Integer
      - price_at_time →  DecimalField
      - created_at →  DateTimeFIELD


**
stock is not a data that can be stored itself but calculated from purchase and sale
**
### Relationships

    Purchases has many PurchaseItems
    Sales has many SaleItems
    Products  has one to many r/n purchaseItems
    Products  has one to many r/n SaleItems 
    Product has many supplires -> Supplies
    
    Customers has many Sales -> buys
    

