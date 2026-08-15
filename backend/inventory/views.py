from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Sum
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView
from rest_framework import generics, permissions, request

from .models import *
from .models import Sale, User
from .serializers import *
from .permissions import IsOwnerOrReadOnly


class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return User.objects.all()
        elif user.role == 'Owner':
            return User.objects.filter(organization=user.organization)
        else:
            return User.objects.filter(id=user.id)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return User.objects.all()
        elif user.is_authenticated:
            return User.objects.filter(id=user.id)

class MeView(APIView):

    def get(self, *args, **kwargs):
        user = self.request.user

        serializer = UserSerializer(user)
        return Response(serializer.data)


class OrganizationList(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer


    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Organization.objects.all()
        elif user.role == 'Owner':
            return Organization.objects.filter(id=user.organization_id)
        else:
            return Organization.objects.none()




class OrganizationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        org_name = data.pop('organization_name', '') or f"{data.get('first_name', '') or 'My'} Shop"
        role = data.pop('role', User.Role.OWNER)
        password = data.pop('password')

        org = Organization.objects.create(name=org_name)

        user = User.objects.create_user(
            organization=org,
            role=role,
            password=password,
            **data,
        )

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)





'''
This section contain category and Product details and others
'''

class ProductsList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(organization_id=user.organization_id)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(organization_id=user.organization_id)


class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


    # improve this by just fetching the organizations scope categories

    # def get_queryset(self):
    #     user = self.request.user
    #
    #     return Category.objects.filter(organization=user.organization)
    #

class ProductStock(APIView):

    def get(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')

        try:
            item = Product.objects.get(id=item_id, organization_id=request.user.organization_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        in_move = InventoryMovement.objects.filter(product=item, type='in')
        out_move = InventoryMovement.objects.filter(product=item, type='out')

        total_input = sum(move.quantity for move in in_move)
        total_out = sum(move.quantity for move in out_move)

        return Response({"total_stock": total_input - total_out, "sale_stock": total_out, "purchase_stock": total_input})


class StockListView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        products = Product.objects.filter(organization_id=user.organization_id)

        rows = []
        for product in products:
            stock_in = InventoryMovement.objects.filter(
                product=product, type='in'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            stock_out = InventoryMovement.objects.filter(
                product=product, type='out'
            ).aggregate(total=Sum('quantity'))['total'] or 0

            rows.append({
                'product_id': product.id,
                'product_name': product.name,
                'barcode': product.barcode,
                'price': product.price,
                'quantity': stock_in - stock_out,
            })

        return Response(rows)




class ProductScan(APIView):

    def get(self, *args, **kwargs):

        barcode = kwargs.get('barcode')

        try:
            product = Product.objects.get(barcode=barcode)

            serializer = ProductSerializer(product)

            return Response(serializer.data)

        except Product.DoesNotExist:
            return Response({"detail": "Product not found. Learn to scan"}, status=status.HTTP_404_NOT_FOUND)




'''
Below section related to Customers and Suppliers together
'''

class CustomerList(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Customer.objects.filter(organization=user.organization)

class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        return Customer.objects.filter(organization=user.organization)



class SupplierList(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer

    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Supplier.objects.filter(organization=user.organization)


class SupplierDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierSerializer

    # permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return Supplier.objects.filter(organization=user.organization)


'''
💰 Sales (5)
'''

class SalesView(generics.ListCreateAPIView):
    serializer_class = SaleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Sale.objects.all()
        else:
            return Sale.objects.filter(organization=user.organization)


class AddItemToSale(APIView):

    def get(self, *args, **kwargs):
        try:
            sale = Sale.objects.get(id=kwargs.get("sale_id"))

            filtered = Product.objects.filter(organization=sale.organization)

            serializer = ProductSerializer(filtered, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"detail": "Sale not found "}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")

        try:
            sale = Sale.objects.get(id=kwargs.get("sale_id"), organization_id=request.user.organization_id)
            product = Product.objects.get(id=product_id)
            
            if sale.status == "open":
                item, created = SoldItem.objects.get_or_create(
                    sale=sale,
                    product=product,
                    defaults={"quantity": 1, "price_at_time": product.price},
                )
                if not created:
                    item.quantity += 1
                    item.save()

                return Response(SoldItemSerializer(item).data)
            else:
                return Response({"detail": "You can't add to completed cart."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": "Sale or product not found"}, status=status.HTTP_404_NOT_FOUND)




class SaleDetail(APIView):

    def get(self, request, *args, **kwargs):
        sale_id = kwargs.get('pk')
        try:
            sale = Sale.objects.get(id=sale_id, organization_id=request.user.organization_id)
        except Sale.DoesNotExist:
            return Response({"detail": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'data': SaleSerializer(sale).data, "total": sale.total()})



class SoldItemsView(generics.ListCreateAPIView):
    serializer_class = SoldItemSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return SoldItem.objects.all()
        else:
            return SoldItem.objects.filter(sale__organization = user.organization)


class SoldItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SoldItemSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return SoldItem.objects.all()
        else:
            return SoldItem.objects.filter(sale__organization = user.organization)





class PurchaseListView(generics.ListCreateAPIView):
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Purchase.objects.all()

        elif user.is_authenticated:
            return Purchase.objects.filter(organization=user.organization)
        else:
            return None

class PurchaseDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PurchaseSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Purchase.objects.all()

        elif user.is_authenticated:
            return Purchase.objects.filter(organization=user.organization)
        else:
            return None