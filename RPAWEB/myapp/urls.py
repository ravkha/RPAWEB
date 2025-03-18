from django.urls import path
from . import views
from .views import oracle_data_view
from .views import login_view,logout_view,FlowPOSO
from .views import OrderListView


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('oracledb/', oracle_data_view, name='oracledb'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('OrderListView/', OrderListView.as_view(), name='order_list'),
    path('data/', views.load_data_view, name='load_data_view'),
    path('flowposo/', views.FlowPOSO, name='flowposo'),
]
