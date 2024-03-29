from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404 page_not_found.html',
                  {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'core/500 server_error.html', status=500)


def permission_denied(request, exception):
    return render(request, 'core/403 permission_denied_view.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
