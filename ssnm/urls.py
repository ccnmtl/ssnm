import django.contrib.auth.views
import django.views.static
import djangowind.views
import flashpolicies.views

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from registration.backends.default.views import RegistrationView
from ssnm.main.forms import CreateAccountForm
from ssnm.main.views import (
    get_map, get_map_details, delete_map, show_maps, contact, go_home,
    display,
)

admin.autodiscover()

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
logout_page = url(r'^logout/$', django.contrib.auth.views.logout,
                  {'next_page': redirect_after_logout})
admin_logout_page = url(r'^accounts/logout/$',
                        django.contrib.auth.views.logout,
                        {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))
    logout_page = url(r'^logout/$', djangowind.views.logout,
                      {'next_page': redirect_after_logout})
    admin_logout_page = url(r'^admin/logout/$', djangowind.views.logout,
                            {'next_page': redirect_after_logout})

urlpatterns = [
    logout_page,
    admin_logout_page,
    auth_urls,
    url(r'^crossdomain.xml$', flashpolicies.views.simple,
        {'domains': [settings.STATIC_URL, '*.ccnmtl.columbia.edu']}),
    url(r'^flash/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm), name='registration_register'),
    url(r'^accounts/password_reset/$',
        django.contrib.auth.views.password_reset, name='password_reset'),
    url(r'^accounts/password_reset/done/$',
        django.contrib.auth.views.password_reset_done,
        name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django.contrib.auth.views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$',
        django.contrib.auth.views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^$', show_maps),
    url(r'^help/$', TemplateView.as_view(template_name="help.html"),
        {}, "help-page"),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"),
        {}, "about-page"),
    url(r'^contact/$', contact),
    url(r'^logout/$',  django.contrib.auth.views.logout, {'next_page': '/'}),
    url(r'^thanks/$', TemplateView.as_view(template_name="thanks.html"),
        {}, "thanks-page"),
    url(r'^ecomap/$', get_map),
    url(r'^ecomap/(?P<map_id>\d+)/$', get_map),
    url(r'^ecomap/(?P<map_id>\d+)/display/flashConduit$', display),
    url(r'^details/(?P<map_id>\d+)/$', get_map_details),
    url(r'^ecomap/(?P<map_id>\d+)/delete_map/$', delete_map),
    url(r'^ecomap/(?P<map_id>\d+)/display/back_to_list_button_clicked$',
        go_home),
    url(r'^details/$', get_map_details),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
