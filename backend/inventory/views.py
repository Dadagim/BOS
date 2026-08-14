from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
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
            return User.objects.get(user=user)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return User.objects.all()
        elif user.role == 'Owner':
            return User.objects.filter(organization=user.organization)
        elif user.is_authenticated:
            return User.objects.get(user=user)

class MeView(APIView):

    def get(self):
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
            return Organization.objects.filter(organization=user.organization)
        else:
            return None




class OrganizationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()





'''
This section contain category and Product details and others
'''

class ProductsList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


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

    def get(self, *args, **kwargs):
        item_id = kwargs.get('pk')

        # get the product from the url bar
        item = Product.objects.get(id=item_id)

        print(item)


        in_move = InventoryMovement.objects.filter(product=item, type='in')
        out_move = InventoryMovement.objects.filter(product=item, type='out')


        total_input = 0
        total_out = 0

        if len(in_move) > 0 or len(out_move) > 0:
            for move in in_move:
                total_input += move.quantity

            for move in out_move:
                total_out += move.quantity

            stock = total_input - total_out

            return Response({"Total Stock": stock, 'sale stock': total_out, "purchase stock": total_input})
        else:
            return Response({"message": "No stock to calculate."})




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
    queryset = Customer.objects.all()



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
        
        print(kwargs.get("sale_id"))
        print(request.data)
        product_id = request.data.get("product_id")

        try:
            sale = Sale.objects.get(id=kwargs.get("sale_id"))
            product = Product.objects.get(id=product_id)
            
            if sale.status == "open":
                added, created = SoldItem.objects.get_or_create(sale=sale, product=product, price_at_time=product.price)

                if created:
                    created.quantity += 1

                return Response(SoldItemSerializer(added).data)
            else:
                return Response({"detail": "You can't add to completed cart."})
        except ObjectDoesNotExist:
            return Response({"detail": "Sale not found"})




class SaleDetail(APIView):

    def get(self, *args, **kwargs):
        user = self.request.user
        sale_id = kwargs.get('pk')
        sale = Sale.objects.get(id=sale_id)


        return Response({'data': SaleSerializer(sale).data, "total": sale.total()})



class SoldItemsView(generics.ListCreateAPIView):
    serializer_class = SoldItemSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return SoldItem.objects.all()
        else:
            return SoldItem.objects.filter(sale__organization = user.organization)


class SoldItemDetail(APIView):
    serializer_class = SoldItemSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Sale.objects.all()
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