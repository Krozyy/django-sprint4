from django.contrib import admin
from django.urls import path, include
from django.views.generic import CreateView, RedirectView
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
     path('accounts/profile/', RedirectView.as_view(url='/', permanent=False)),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', 
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url='/auth/login/'
        ),
        name='registration')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
