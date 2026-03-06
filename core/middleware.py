from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to login, register, and admin without redirecting
        exempt_urls = [reverse('login'), reverse('register')]
        
        if not request.user.is_authenticated:
            if request.path not in exempt_urls and not request.path.startswith('/admin/'):
                return redirect('login')

        response = self.get_response(request)
        return response