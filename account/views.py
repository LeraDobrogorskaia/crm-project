from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.urls import reverse_lazy

from account.forms import AuthenticationForm


def login_view(request):
    context = {}

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return HttpResponseRedirect(
                getattr(request.GET, 'next', reverse_lazy("sepulki-list")),
            )

        context["errors"] = form.errors

    return render(request, "account/login.html", context=context)


def logout_view(request):
    logout(request)
    return render(request, 'account/logout.html')
