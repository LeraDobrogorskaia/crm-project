from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login
from django.urls import reverse_lazy

from account.forms import AuthenticationForm


def login_view(request):
    context = {}

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return HttpResponseRedirect(reverse_lazy("sepulki-list"))

        context["errors"] = form.errors

    return render(request, "account/login.html", context=context)

