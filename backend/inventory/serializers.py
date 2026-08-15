from django.db.models import Sum

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class RegisterUserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'phone', 'role', 'organization_name']
        extra_kwargs = {'password': {'write_only': True}}


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

'''
customers and suppliers serializers
'''
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields  = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'



'''
💰 Sales (5)
'''



class SoldItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SoldItem
        fields = ['id', 'sale', 'product', 'product_name', 'price_at_time', 'quantity']

    def create(self, validated_data):
        product = validated_data.get('product')
        sale = validated_data.get('sale')
        quantity = validated_data.get('quantity')

        # Stock on hand = SUM(IN) - SUM(OUT) from movements. Never stored.
        stock_in = InventoryMovement.objects.filter(
            product=product, type=InventoryMovement.Type.IN
        ).aggregate(total=Sum('quantity'))['total'] or 0

        stock_out = InventoryMovement.objects.filter(
            product=product, type=InventoryMovement.Type.OUT
        ).aggregate(total=Sum('quantity'))['total'] or 0

        if stock_in - stock_out < quantity:
            raise ValidationError(detail='Low stock quantity')

        item = SoldItem.objects.create(**validated_data)

        InventoryMovement.objects.get_or_create(
            organization=sale.organization,
            product=product,
            quantity=quantity,
            type="out",
            created_by=sale.created_by,
            sale_item=item,
        )
        return item


class SaleSerializer(serializers.ModelSerializer):
    items = SoldItemSerializer(many=True, read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'organization', 'customer', 'payment_method', 'status', 'created_by', 'created_at', 'items']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        organization = user.organization

        items = self.initial_data.get('items', [])

        # Check stock for every line BEFORE writing anything so a failed
        # checkout can't leave a half-created sale behind.
        for item in items:
            product = Product.objects.get(id=item['product'])
            quantity = int(item['quantity'])
            stock_in = InventoryMovement.objects.filter(
                product=product, type=InventoryMovement.Type.IN
            ).aggregate(total=Sum('quantity'))['total'] or 0
            stock_out = InventoryMovement.objects.filter(
                product=product, type=InventoryMovement.Type.OUT
            ).aggregate(total=Sum('quantity'))['total'] or 0
            if stock_in - stock_out < quantity:
                raise ValidationError({'detail': f'Not enough stock for {product.name} (have {stock_in - stock_out}, need {quantity})'})

        sale = Sale.objects.create(
            organization=organization,
            created_by=user,
            customer=validated_data.get('customer'),
            payment_method=validated_data.get('payment_method', Sale.PaymentChoice.CASH),
            status=validated_data.get('status', Sale.Status.OPEN),
        )

        for item in items:
            product = Product.objects.get(id=item['product'])
            quantity = int(item['quantity'])
            price_at_time = item.get('price_at_time') or product.price
            sold = SoldItem.objects.create(
                sale=sale, product=product, quantity=quantity, price_at_time=price_at_time
            )
            InventoryMovement.objects.create(
                organization=organization,
                product=product,
                quantity=quantity,
                type=InventoryMovement.Type.OUT,
                created_by=user,
                sale_item=sold,
            )

        return sale

"""
Purchase
"""

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedItem
        field = '__all__'