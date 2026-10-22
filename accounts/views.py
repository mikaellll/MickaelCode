from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UserSignUpForm, UserLoginForm, UserProfileForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:overview")

    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend="accounts.backends.EmailOrUsernameModelBackend")
            messages.success(request, f"Bienvenue {user.display_name()} ! Votre compte a été créé avec succès.")
            return redirect("dashboard:overview")
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées ci-dessous.")
    else:
        form = UserSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:overview")

    redirect_to = request.GET.get("next", "")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Ravi de vous revoir, {user.display_name()} !")

            if redirect_to and url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(redirect_to)
            return redirect("dashboard:overview")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form, "next": redirect_to})


def logout_view(request):
    if request.method == "POST" or request.method == "GET":
        auth_logout(request)
        messages.info(request, "Vous avez été déconnecté en toute sécurité.")
    return redirect("core:home")


@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Veuillez vérifier les informations renseignées.")
    else:
        form = UserProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})
