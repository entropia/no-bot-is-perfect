from django.conf.urls import patterns, url

from nbip import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^submit/$', views.submit, name='submit'),
    url(r'^explain/$', views.explain, name='explain'),
    url(r'^guess/$', views.new_guess, name='new_guess'),
    url(r'^guess/(\d+)/$', views.guess, name='guess'),
)
