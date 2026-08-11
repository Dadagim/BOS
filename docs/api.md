
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

GET     /supliers/              🔒  list my Supliers
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
DELETE  /purchase/{id}/           🔒  Update A purchase history
GET     /purchase/{id}/           🔒  Delete of purchase History




# now do the same for: customers, suppliers, sales, purchases
# and answer: where does the AI live? (the chat + the draft purchase order)