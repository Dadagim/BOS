from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Organization)
admin.site.register(Sale)
admin.site.register(SoldItem)
admin.site.register(Purchase)
admin.site.register(PurchasedItem)
admin.site.register(Category)
admin.site.register(InventoryMovement)
admin.site.register(AuditLog)