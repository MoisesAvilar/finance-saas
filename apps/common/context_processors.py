from common.models import Banner


def banners(request):
    if not request.user.is_authenticated or request.user.is_pro:
        return {}

    return {
        "banners_top_list": Banner.objects.filter(
            active=True, position="DASHBOARD_TOP"
        ).order_by('?')
    }
