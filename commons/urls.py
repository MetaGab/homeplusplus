from django.contrib import admin
from django.urls import include, path
from commons import views

urlpatterns = [
    path('info', views.register_info, name="register_info"),
    path('access', views.register_access, name="register_access"),
    path('status_luz', views.status_luz, name="status_luz"),
    path('status_alarma', views.status_alarma, name="status_alarma"),
    path('accesos', views.accesos, name="accesos"),
    path('test', views.test, name="test"),
    path('acciones', views.acciones, name="acciones"),
    path('servicios', views.servicios, name='servicios'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('contacto', views.contacto, name='contacto'),
    path('', views.home, name="home")
]
