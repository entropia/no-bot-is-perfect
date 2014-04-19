from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.base import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    (r'^accounts/$', RedirectView.as_view(url='/')),
    (r'^accounts/profile/$', RedirectView.as_view(url = '/')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('nbip.urls')),
)
