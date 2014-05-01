from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.base import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}, name="login"),
    url(r'^accounts/$', RedirectView.as_view(url='/')),
    url(r'^accounts/profile/$', RedirectView.as_view(url = '/')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('nbip.urls')),
)
