from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .models import (
    Category,
    Customer,
    InventoryMovement,
    Organization,
    Product,
    Purchase,
    PurchasedItem,
    Sale,
    SoldItem,
    Supplier,
    User,
)
from .serializers import SoldItemSerializer


class BaseSetup(TestCase):
    """Shared objects for every test class."""

    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.owner = User.objects.create_user(
            username="owner", password="pass",
            organization=self.org, role=User.Role.OWNER,
        )
        self.category = Category.objects.create(name="Grains")
        self.product = Product.objects.create(
            name="Rice 5kg", category=self.category,
            organization=self.org, price=Decimal("850.00"),
        )
        self.customer = Customer.objects.create(name="Walk-in", organization=self.org)
        self.supplier = Supplier.objects.create(name="Grain Wholesale", organization=self.org)


class SaleTotalTests(BaseSetup):
    """Rule: sale.total() = sum(price_at_time * quantity) over its lines."""

    def test_total_sums_line_items(self):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        SoldItem.objects.create(sale=sale, product=self.product,
                                price_at_time=Decimal("850.00"), quantity=2)
        SoldItem.objects.create(sale=sale, product=self.product,
                                price_at_time=Decimal("100.00"), quantity=3)

        self.assertEqual(sale.total(), Decimal("2000.00"))

    def test_total_is_decimal_not_float(self):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        SoldItem.objects.create(sale=sale, product=self.product,
                                price_at_time=Decimal("99.99"), quantity=2)

        self.assertEqual(sale.total(), Decimal("199.98"))
        self.assertIsInstance(sale.total(), Decimal)

    def test_empty_sale_total_is_zero(self):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        self.assertEqual(sale.total(), 0)


class InventoryMovementTests(BaseSetup):
    """Rule: every sold item writes an OUT movement linked to that item."""

    def setUp(self):
        super().setUp()
        self.purchase = Purchase.objects.create(
            supplier=self.supplier, organization=self.org,
            status=Purchase.Status.DRAFT, created_by=self.owner,
        )
        self.purchased_item = PurchasedItem.objects.create(
            purchase=self.purchase, product=self.product,
            quantity=100, cost_at_time=Decimal("700.00"),
        )
        # Received stock must be recorded as an IN movement
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=100, type=InventoryMovement.Type.IN, created_by=self.owner,
        )

    def _make_sale_item(self, quantity=2):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        serializer = SoldItemSerializer(data={
            "sale": sale.id,
            "product": self.product.id,
            "quantity": quantity,
            "price_at_time": "850.00",
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def test_sold_item_creates_out_movement(self):
        item = self._make_sale_item(quantity=2)

        movement = InventoryMovement.objects.get(
            product=self.product, type=InventoryMovement.Type.OUT
        )
        self.assertEqual(movement.quantity, 2)
        self.assertEqual(movement.sale_item, item)
        self.assertEqual(movement.organization, self.org)

    def test_movement_count_matches_sold_items(self):
        self._make_sale_item(quantity=1)
        self._make_sale_item(quantity=3)

        out_count = InventoryMovement.objects.filter(
            product=self.product, type=InventoryMovement.Type.OUT
        ).count()
        self.assertEqual(out_count, 2)


class NegativeStockTests(BaseSetup):
    """Rule: you can't sell more than you have on hand."""

    def setUp(self):
        super().setUp()
        # Stock on hand comes from movements: 3 IN, 0 OUT -> stock = 3
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=3, type=InventoryMovement.Type.IN, created_by=self.owner,
        )

    def test_selling_more_than_stock_is_blocked(self):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        serializer = SoldItemSerializer(data={
            "sale": sale.id,
            "product": self.product.id,
            "quantity": 10,
            "price_at_time": "850.00",
        })
        serializer.is_valid(raise_exception=True)

        with self.assertRaises(ValidationError):
            serializer.save()

    def test_selling_within_stock_succeeds(self):
        sale = Sale.objects.create(
            organization=self.org, customer=self.customer,
            status=Sale.Status.COMPLETED, created_by=self.owner,
        )
        serializer = SoldItemSerializer(data={
            "sale": sale.id,
            "product": self.product.id,
            "quantity": 2,
            "price_at_time": "850.00",
        })
        serializer.is_valid(raise_exception=True)

        item = serializer.save()
        self.assertEqual(item.quantity, 2)


class PurchaseStatusFlowTests(BaseSetup):
    """Rule: status only moves forward: draft -> ordered -> received."""

    def _purchase(self, status):
        return Purchase.objects.create(
            supplier=self.supplier, organization=self.org,
            status=status, created_by=self.owner,
        )

    def test_draft_goes_to_ordered(self):
        p = self._purchase(Purchase.Status.DRAFT)
        p.change_status(p.status)
        p.save()
        self.assertEqual(p.status, Purchase.Status.ORDERED)

    def test_ordered_goes_to_received(self):
        p = self._purchase(Purchase.Status.ORDERED)
        p.change_status(p.status)
        p.save()
        self.assertEqual(p.status, Purchase.Status.RECEIVED)

    def test_received_stays_received(self):
        p = self._purchase(Purchase.Status.RECEIVED)
        p.change_status(p.status)
        p.save()
        self.assertEqual(p.status, Purchase.Status.RECEIVED)


class StockCalculationTests(BaseSetup):
    """Rule: stock = SUM(IN movements) - SUM(OUT movements). Never stored."""

    def test_stock_is_in_minus_out(self):
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=50, type=InventoryMovement.Type.IN, created_by=self.owner,
        )
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=10, type=InventoryMovement.Type.OUT, created_by=self.owner,
        )

        total_in = sum(
            m.quantity for m in InventoryMovement.objects.filter(
                product=self.product, type=InventoryMovement.Type.IN
            )
        )
        total_out = sum(
            m.quantity for m in InventoryMovement.objects.filter(
                product=self.product, type=InventoryMovement.Type.OUT
            )
        )
        self.assertEqual(total_in - total_out, 40)

    def test_stock_endpoint_returns_correct_number(self):
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=25, type=InventoryMovement.Type.IN, created_by=self.owner,
        )
        InventoryMovement.objects.create(
            organization=self.org, product=self.product,
            quantity=5, type=InventoryMovement.Type.OUT, created_by=self.owner,
        )

        response = self.client.get(f"/api/products/{self.product.id}/stock/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Total Stock"], 20)
