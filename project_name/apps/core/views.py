from django.shortcuts import render, redirect, reverse


def letsencrypt(request):
    return HttpResponse(
        'pFmV21J6LJNm4q3E4H0rY6iUDjSjVJmLlSGCnPs3u0Y.XwnczyaCPkwyyhUn0Hyko_vPtjZBq31fIKmZHsCJqu0',
        content_type='text/plain'
    )


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('profile'))

    return redirect(reverse('login'))

