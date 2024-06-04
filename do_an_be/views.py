from django.urls import reverse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from oauth2_provider.views.generic import ProtectedResourceView
class MyProtectedView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2 protected resource!')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Đăng nhập thành công, chuyển hướng đến trang chính của ứng dụng
            return redirect('{}?client_id={}&response_type=code'.format(reverse('authorize'), 'v0kTLZZ87VxcN2MGMjJw0xGa9bqTzc1AHzi2OBm5'))
        else:
            # Đăng nhập thất bại, hiển thị thông báo lỗi
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')
