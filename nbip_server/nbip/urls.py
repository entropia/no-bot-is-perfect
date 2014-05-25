from django.conf.urls import patterns, url

from nbip import views, bot_views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^stats/$', views.stats, name='stats'),

    # human interaction
    url(r'^submit/$', views.submit, name='submit'),
    url(r'^explain/$', views.explain, name='explain'),
    url(r'^guess/$', views.new_guess, name='new_guess'),
    url(r'^guess/(\d+)/$', views.guess, name='guess'),
    url(r'^view_guess/(\d+)/$', views.view_guess, name='view_guess'),

    # bot management
    url(r'^new_bot/$', views.new_bot, name='new_bot'),

    # bot interface
    url(r'^bot/get/$', bot_views.get, name='bot_get'),
    url(r'^bot/put/$', bot_views.put, name='bot_pu'),

    # Raw data
    url(r'^highscore_data/$', views.highscore_data, name='highscore_data'),
)
