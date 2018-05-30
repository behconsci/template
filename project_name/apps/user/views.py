from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import FormView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.utils import timezone

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
            new_user.profile.save()

            confirm_link = 'https://%s%s' % (
                request.META.get('HTTP_HOST'),
                reverse('confirm_register', kwargs={'confirm_hash': confirm_hash})
            )

            send_email_in_template(
                'Your registration in {{ project_name }}.com', email, **{
                    'text': "Thanks for registering on {{ project_name }}.com. Please confirm your registration by clicking on "
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


class PasswordForgot(FormView):
    def get(self, request, *args, **kwargs):
        return render(request, 'request_password_reset.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')

        if not email:
            return render(request, 'request_password_reset.html', {
                'error_no_input': 'yes', 'email': email
            })

        if not User.objects.filter(email=email).count():
            return render(request, 'request_password_reset.html', {
                'error_user_not_found': 'yes', 'email': email
            })

        user = User.objects.filter(email=email).last()

        pw_onetime_hash = create_default_hash()
        user.profile.pw_onetime_hash = pw_onetime_hash
        user.profile.save()

        send_email_in_template(
            'your new access',
            email,
            'email/pw_reset.html',
            **{
                'request_domain': request.META.get('HTTP_HOST'),
                'user_name': user.username,
                'pw_reset_url': 'https://%s%s' % (
                    request.META.get('HTTP_HOST'),
                    reverse('password_reset', kwargs={'onetime_hash': pw_onetime_hash})
                ),
            }
        )
        return redirect(reverse('password_forgot_success'))


class PasswordReset(FormView):

    def get(self, request, *args, **kwargs):
        onetime_hash = kwargs.get('onetime_hash')

        user_profile = Profile.objects.filter(pw_onetime_hash=onetime_hash).last()
        if not user_profile:
            error = 'link is invalid'
            return render(request, 'password_reset.html', {
                'error': error, 'link_invalid': 'yes'
            })

        # invalidate the confirm hash
        now = timezone.now()
        user_profile.pw_onetime_hash = '%s-clicked-at-%s' % (
            onetime_hash, '%s_%s_%s_%s_%s' % (now.year, now.month, now.day, now.hour, now.minute)
        )
        user_profile.save()

        return render(request, 'password_reset.html', {
            'user_profile_id': user_profile.id
        })

    def post(self, request, *args, **kwargs):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_profile_id = request.POST.get('user_profile_id')

        if not Profile.objects.filter(id=user_profile_id).last():
            return render(request, 'password_reset.html', {
                'error': 'error while resetting'
            })

        if password1 != password1:
            return render(request, 'password_reset.html', {
                'error': 'passwords dont match'
            })

        user_profile = Profile.objects.get(id=user_profile_id)
        user = user_profile.user
        user.set_password(password2)
        user.save()

        login(request, user)

        return redirect('%s?password_changed=1' % reverse('profile'))