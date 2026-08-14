from django.urls import path

from .views import *

urlpatterns = [
#     ----------------------uer and Authentication section
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('users/register/', RegisterView.as_view()),
    path('users/me/', MeView.as_view()),
    path('organization/', OrganizationList.as_view()),
    path('organization/<int:pk>/', OrganizationDetail.as_view()),


#     ----------------------Products and Inventory Section
    path('products/', ProductsList.as_view()),
    path('products/<int:pk>/', ProductDetail.as_view()),
    path('category/', CategoryList.as_view()),
    path('category/<int:pk>/', CategoryList.as_view()),
    path('products/scan/<int:barcode>/', ProductScan.as_view()),


#     ----------------------👥 Customers & Suppliers (5 each — same shape)
    path('customers/', CustomerList.as_view()),
    path('customers/<int:pk>/', CustomerDetail.as_view()),

    path('suppliers/', SupplierList.as_view()),
    path('suppliers/<int:pk>/', SupplierDetail.as_view()),

#     ------------------------💰 Sales (5)
    path('sales/', SalesView.as_view()),
    path('sales/<int:pk>/', SaleDetail.as_view()),
    path('sales/<int:sale_id>/items', AddItemToSale.as_view()),

    path('soldItems/', SoldItemsView.as_view()),
    path('soldItems/<int:pk>/', SoldItemDetail.as_view()),


    path('products/<int:pk>/stock/', ProductStock.as_view()),
    path('purchase/', PurchaseListView.as_view()),
    path('purchase/<int:pk>/', PurchaseDetail.as_view())

]