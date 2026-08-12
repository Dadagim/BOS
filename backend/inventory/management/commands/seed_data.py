from decimal import Decimal

from django.core.management.base import BaseCommand

from inventory.models import (
    Organization,
    User,
    Category,
    Product,
    Supplier,
    Customer,
    Purchase,
    PurchasedItem,
    Sale,
    SoldItem,
    InventoryMovement,
    AuditLog,
)


class Command(BaseCommand):
    help = "Load sample data so you can experiment."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            name="Ethio Supply House",
            defaults={
                "location": "Merkato, Addis Ababa",
                "description": "A sample wholesale shop for experiments.",
            },
        )

        owner, _ = User.objects.get_or_create(
            username="owner",
            defaults={
                "email": "owner@example.com",
                "first_name": "Dawit",
                "last_name": "Tesfaye",
                "phone": "0911000001",
                "role": User.Role.OWNER,
                "organization": org,
            },
        )
        owner.set_password("password123")
        owner.save()

        cashier, _ = User.objects.get_or_create(
            username="cashier",
            defaults={
                "email": "cashier@example.com",
                "first_name": "Sara",
                "last_name": "Mekonnen",
                "phone": "0911000002",
                "role": User.Role.CASHIER,
                "organization": org,
            },
        )
        cashier.set_password("password123")
        cashier.save()

        categories = {}
        for name in [
            "Grains & Flour",
            "Cooking Oil",
            "Beverages",
            "Medicine",
            "Construction",
        ]:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat

        product_data = [
            ("Buna (roasted coffee)", "Grains & Flour", "350.00", "7290000000011"),
            ("Rice (1kg)", "Grains & Flour", "120.00", "7290000000028"),
            ("Sugar (1kg)", "Grains & Flour", "95.00", "7290000000035"),
            ("Flour (1kg)", "Grains & Flour", "70.00", "7290000000042"),
            ("Local Honey (1kg)", "Grains & Flour", "400.00", None),
            ("Cooking Oil (5L)", "Cooking Oil", "300.00", "7290000000059"),
            ("Bottled Water (1.5L)", "Beverages", "25.00", "7290000000066"),
            ("Soft Drink (500ml)", "Beverages", "35.00", "7290000000073"),
            ("Amoxicillin 500mg", "Medicine", "25.00", "7290000000080"),
            ("Paracetamol 500mg", "Medicine", "15.00", "7290000000097"),
            ("Cement (50kg)", "Construction", "850.00", "7290000000103"),
            ("Rebar 12mm (piece)", "Construction", "950.00", "7290000000110"),
        ]

        products = {}
        for name, cat_name, price, barcode in product_data:
            product, _ = Product.objects.get_or_create(
                name=name,
                organization=org,
                defaults={
                    "category": categories[cat_name],
                    "price": Decimal(price),
                    "barcode": barcode,
                },
            )
            products[name] = product

        supplier_data = [
            ("Addis Wholesale PLC", "Merkato, Addis Ababa", "Grains and oils"),
            ("Blue Nile Distributors", "Bole, Addis Ababa", "Beverages"),
            ("Merkato Foods Import", "Kality, Addis Ababa", "Imported goods"),
            ("National Pharma Supply", "Piassa, Addis Ababa", "Medicine"),
            ("Selam Construction Materials", "Megenagna, Addis Ababa", "Building materials"),
        ]
        suppliers = {}
        for name, location, description in supplier_data:
            supplier, _ = Supplier.objects.get_or_create(
                name=name,
                organization=org,
                defaults={"location": location, "description": description},
            )
            suppliers[name] = supplier

        customer_data = [
            ("Zemen Retail Shop", "0912000001", "zemen@example.com"),
            ("Bole Supermarket", "0912000002", "bole@example.com"),
            ("Alem Grocery Store", "0912000003", "alem@example.com"),
            ("Tikur Anbessa Pharmacy", "0912000004", "pharma@example.com"),
            ("Getnet Hardware", "0912000005", "hardware@example.com"),
        ]
        customers = {}
        for name, phone, email in customer_data:
            customer, _ = Customer.objects.get_or_create(
                name=name,
                organization=org,
                defaults={"phone": phone, "email": email},
            )
            customers[name] = customer

        purchases = [
            (
                "Addis Wholesale PLC",
                "received",
                [
                    ("Rice (1kg)", 100, "110.00"),
                    ("Sugar (1kg)", 200, "85.00"),
                    ("Flour (1kg)", 150, "60.00"),
                    ("Cooking Oil (5L)", 50, "270.00"),
                ],
            ),
            (
                "National Pharma Supply",
                "received",
                [
                    ("Amoxicillin 500mg", 10, "20.00"),
                    ("Paracetamol 500mg", 20, "12.00"),
                ],
            ),
            (
                "Selam Construction Materials",
                "received",
                [
                    ("Cement (50kg)", 30, "800.00"),
                    ("Rebar 12mm (piece)", 20, "900.00"),
                ],
            ),
        ]
        for sup_name, status, items in purchases:
            purchase = Purchase.objects.create(
                supplier=suppliers[sup_name],
                organization=org,
                status=status,
                created_by=owner,
            )
            for product_name, quantity, cost in items:
                item = PurchasedItem.objects.create(
                    purchase=purchase,
                    product=products[product_name],
                    quantity=quantity,
                    cost_at_time=Decimal(cost),
                )
                InventoryMovement.objects.create(
                    organization=org,
                    product=item.product,
                    quantity=quantity,
                    type=InventoryMovement.Type.IN,
                    purchase_item=item,
                    created_by=owner,
                )

        sales = [
            (
                "Zemen Retail Shop",
                "completed",
                [
                    ("Rice (1kg)", 30, "120.00"),
                    ("Sugar (1kg)", 50, "95.00"),
                    ("Cooking Oil (5L)", 10, "300.00"),
                ],
            ),
            (
                "Tikur Anbessa Pharmacy",
                "completed",
                [
                    ("Amoxicillin 500mg", 6, "25.00"),
                    ("Paracetamol 500mg", 8, "15.00"),
                ],
            ),
            (
                "Getnet Hardware",
                "awaiting_payment",
                [
                    ("Cement (50kg)", 5, "850.00"),
                ],
            ),
        ]
        for cust_name, status, items in sales:
            sale = Sale.objects.create(
                organization=org,
                customer=customers[cust_name],
                status=status,
                created_by=cashier,
            )
            for product_name, quantity, price in items:
                item = SoldItem.objects.create(
                    sale=sale,
                    product=products[product_name],
                    quantity=quantity,
                    price_at_time=Decimal(price),
                )
                InventoryMovement.objects.create(
                    organization=org,
                    product=item.product,
                    quantity=quantity,
                    type=InventoryMovement.Type.OUT,
                    sale_item=item,
                    created_by=cashier,
                )

        AuditLog.objects.create(
            organization=org,
            user=owner,
            action="created organization",
            target=f"Organization:{org.id}",
        )
        AuditLog.objects.create(
            organization=org,
            user=owner,
            action="ran seed_data command",
            target="seed_data",
            details="loaded sample purchases and sales",
        )

        self.stdout.write(self.style.SUCCESS("Sample data loaded."))
        self.stdout.write(f"Organization: {org.name}")
        self.stdout.write(f"Owner login: owner / password123")
        self.stdout.write(f"Cashier login: cashier / password123")
