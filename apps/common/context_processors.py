from common.models import Banner


def banners(request):
    if not request.user.is_authenticated or request.user.is_pro:
        return {}

    return {
        "banner_top": Banner.objects.filter(
            active=True, position="DASHBOARD_TOP"
        ).first(),
    }
