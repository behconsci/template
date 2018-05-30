from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import FormView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login

from .forms import LoginForm, RegisterForm
from {{ project_name }}.apps.core.utils import send_email_in_template
from {{ project_name }}.apps.core.models import create_default_hash
from .models import Profile


class Login(FormView):
    def get(self, request, *args, **kwargs):
        return render(request, 'sign.html', {
            'login_form': LoginForm(), 'register_form': RegisterForm()
        })

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST or None)

        if login_form.is_valid():
            data = login_form.cleaned_data
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('profile'))
                else:
                    # user is not active, user should confirm his registration first
                    return render(request, 'sign.html', {
                        'login_form': login_form, 'register_form': RegisterForm(),
                        'login_error': 'Please confirm your registration.'
                    })
            else:
                # bad credentials
                return render(request, 'sign.html', {
                    'login_form': login_form, 'register_form': RegisterForm(),
                    'login_error': 'Wrong credentials'
                })

        # bad form data
        return render(request, 'sign.html', {
            'login_form': login_form, 'register_form': RegisterForm(),
            'login_error': 'Wrong credentials'
        })


class Register(FormView):
    def get(self, request, *args, **kwargs):
        return render(request, 'sign.html', {
            'login_form': LoginForm(), 'register_form': RegisterForm()
        })

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('new_username')
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            country = form.cleaned_data.get('country')

            if password2 != password1:
                return render(request, 'sign.html', {
                    'login_form': LoginForm(),
                    'register_form': form,
                    'reg_error': 'Passwords don\'t match'
                })

            if User.objects.filter(email=email).count():
                return render(request, 'sign.html', {
                    'login_form': LoginForm(),
                    'register_form': form,
                    'reg_error': 'User with this email exists already. Please sign in instead.'
                })

            new_user = User.objects.create(username=username, email=email, is_active=False)
            new_user.set_password(password2)
            new_user.save()

            # send confirmation link
            confirm_hash = create_default_hash()

            new_user.profile.confirm_hash = confirm_hash
            new_user.profile.country = country
            new_user.profile.save()

            confirm_link = 'https://%s%s' % (
                request.META.get('HTTP_HOST'),
                reverse('confirm_register', kwargs={'confirm_hash': confirm_hash})
            )

            send_email_in_template(
                'Your registration in bolstrim.com', email, **{
                    'text': "Thanks for registering on bolstrim.com. Please confirm your registration by clicking on "
                            "the link below.",
                    'link': confirm_link,
                    'link_name': 'Confirm'
                }
            )

            return redirect('%s?please_confirm=1' % reverse('login'))


def confirm_register(request, confirm_hash):
    user_profile = Profile.objects.filter(confirm_hash=confirm_hash).last()

    if not user_profile:
        # either hash is already used or invalid hash
        return redirect('%s?invalid_link=1' % reverse('login'))

    user = user_profile.user

    if user.is_active:
        return redirect('%s?already_confirmed=1' % reverse('profile'))

    user.is_active = True
    user.save(update_fields=['is_active'])

    # login user
    login(request, user)

    return redirect('%s?registration_complete=1' % reverse('profile'))


class ProfileView(LoginRequiredMixin, FormView):
    login_url = '/user/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        return render(request, 'profile.html')
