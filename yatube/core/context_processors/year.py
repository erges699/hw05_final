from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now = timezone.now().year
    return {
        'year_now': year_now,
    }
