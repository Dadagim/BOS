from typing import Any

from django.db.models import Sum, query

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password','first_name', 'last_name', 'phone', 'role']


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



class SaleSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    organization = serializers.PrimaryKeyRelatedField(write_only=True,
                                                      queryset=Organization.objects.all())
    class Meta:
        model = Sale
        fields = '__all__'


# 

class SoldItemSerializer(serializers.ModelSerializer):
    # sale = SaleSerializer(read_only=True)
    # product = ProductSerializer(read_only=True)
    class Meta:
        model = SoldItem
        fields = '__all__'


    def create(self, validated_data: Any):
        product = validated_data.get('product')
        sale = validated_data.get('sale')
        quantity = validated_data.get('quantity')

        product = Product.objects.get(id=product.id)

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

        inventory, created = InventoryMovement.objects.get_or_create(organization=sale.organization,
                                                                         product=product,
                                                                         quantity=quantity,
                                                                         type="out",
                                                                         created_by=sale.created_by,
                                                                         sale_item=item,
                                                                         )
        return item

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