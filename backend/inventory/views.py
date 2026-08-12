from rest_framework.views import APIView
from rest_framework import generics, permissions, request

from .models import *
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

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


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


