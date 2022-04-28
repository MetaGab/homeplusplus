from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from commons.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, login as auth_login
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
    template_name = "index.html"

    return render(request, template_name, locals())

def login(request):
    template_name = "login.html"
    
    if request.POST:
        username = request.POST.get("username", "")
        password = request.POST.get("pass", "")
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            auth_login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = "Login Error"


    return render(request, template_name, locals())

def signup(request):
    template_name = "signup.html"
    
    if request.POST:
        new_user = {}
        error = {}
        for field in request.POST:
            new_user[field] = request.POST[field] 
            if field == "":
                error[field] = "Debe ser llenado"
        try:
            validate_email(new_user["email"])
            if User.objects.filter(email=new_user["email"]).exists():
                error["email"] = "Correo ya fue utilizado en otra cuenta"
        except:
            error["email"] = "Error en formato de email"

        if new_user["pass"] != new_user["pass2"]:
            error["pass2"] = "Repite la contraseña sin cambios"

        if not error:
            user = User.objects.create_user(new_user['name'], new_user['email'], new_user['pass'])
            auth_login(request, user)
            home = Home(user=user, name="Casa de %s" % new_user['name'], lat=0, lon=0)
            home.save()
            return HttpResponseRedirect('/')


    return render(request, template_name, locals())

def signout(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_info(request):
    template_name = "default.html"

    reading = Reading()
    reading.temperature = request.GET.get("temperature", 0)
    reading.humidity = request.GET.get("humidity", 0)
    reading.gas = request.GET.get("gas", 0)
    reading.illumination = request.GET.get("illumination", 0)
    reading.home = Home.objects.get(id=request.GET.get("home"))
    reading.save()

    if int(reading.gas) > 30:
        send_notification_gas(reading)

    return render(request, template_name, locals())

def register_access(request):
    template_name = "default.html"

    access = Access()
    if "card" in request.GET:
        access.person = Person.objects.get(card=request.GET.get("card"))
        access.home = Home.objects.get(id=request.GET.get("home"))
        access.triggered_alarm = request.GET.get("alarm", False)
        access.save()
        msg = "EXITO"

        if access.triggered_alarm:
            send_notification_alarm(access)
    else:
        msg = "FALLO"

    return render(request, template_name, locals())

def status_luz(request):
    home = Home.objects.get(id=request.GET.get("home"))
    html = ">%s" % home.light
    return HttpResponse(html)

def status_alarma(request):
    home = Home.objects.get(id=request.GET.get("home"))
    html = ">%s" % home.alarm
    return HttpResponse(html)

def accesos(request):
    template_name = "accesos.html"
    accesos = Access.objects.filter(home=Home.objects.get(user=request.user))
    return render(request, template_name, locals())

@csrf_exempt
def acciones(request):
    template_name = "elements.html"
    home=Home.objects.get(user=request.user)
    
    if request.POST:
        print(request.POST)
        home.light = True if request.POST.get("focos1", False) == "on" else False
        home.alarm = True if request.POST.get("alarma1", False) == "on" else False
        home.save()
        return HttpResponseRedirect("/acciones")
    return render(request, template_name, locals())

def servicios(request):
    if request.user.is_authenticated:
        template_name = "servicios.html"
        reading = Reading.objects.filter(home=Home.objects.get(user=request.user))
        if reading.exists():
            reading = reading.last()
    else:
        template_name = "serviciossinlogin.html"
    return render(request, template_name, locals())

def contacto(request):
    template_name = "contact.html"
    return render(request, template_name, locals())

@csrf_exempt
def test(request):
    if request.POST:
        print(request.POST)
        post = request.POST
    return render(request,"default.html", locals())



def send_notification_gas(reading):
    send_mail(
            'Alerta de gas',
            'Gas al %s' % (reading.gas),
            "ith.humanware@gmail.com",
            [reading.home.user.email],
            fail_silently=False,
        )

def send_notification_alarm(access):
    pass