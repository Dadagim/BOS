from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        CASHIER = "cashier", "Cashier"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to="users/", blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CASHIER)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # organization = models.ForeignKey(Organization, related_name="category", on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="products"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="customers"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="suppliers"
    )
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting payment"

    class PaymentChoice(models.TextChoices):
        TELEBIRR = 'telebirr', 'Telebirr'
        CASH = 'cash', 'cash'
        CREDIT = 'credit', 'Credit'

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="sales"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="sales", null=True, blank=True
    )
    payment_method = models.CharField(max_length=10, choices=PaymentChoice.choices, default=PaymentChoice.CASH)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="sales_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.price_at_time * item.quantity for item in self.items.all())


class SoldItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="sold_items"
    )
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()


class Purchase(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ORDERED = "ordered", "Ordered"
        RECEIVED = "received", "Received"

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="purchases"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="purchases"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="purchases_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def change_status(self, current_Status):
        if current_Status == 'draft':
            self.status = 'ordered'
        elif current_Status == 'ordered':
            self.status = 'received'
        else:
            self.status = current_Status





class PurchasedItem(models.Model):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="purchased_items"
    )
    quantity = models.PositiveIntegerField()
    cost_at_time = models.DecimalField(max_digits=12, decimal_places=2)


class InventoryMovement(models.Model):
    class Type(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="movements"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="movements"
    )
    quantity = models.PositiveIntegerField()
    type = models.CharField(max_length=3, choices=Type.choices)
    sale_item = models.ForeignKey(
        SoldItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )
    purchase_item = models.ForeignKey(
        PurchasedItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="movements_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audit_logs"
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="audit_logs"
    )
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
