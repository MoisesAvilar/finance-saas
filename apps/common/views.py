from django.shortcuts import get_object_or_404, redirect
from .models import Banner


def click_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)

    if banner.active:
        banner.clicks += 1
        banner.save()

    return redirect(banner.link)
