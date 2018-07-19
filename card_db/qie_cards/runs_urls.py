from django.conf.urls import url, include
from django.views.static import serve
from django.views.generic import RedirectView

from . import run_views as views
from card_db.settings import MEDIA_ROOT


urlpatterns = [
    #url(r'^catalog$', views.CatalogView.as_view(), name='catalog'),
    url(r'^$', RedirectView.as_view(url='catalog')),
    url(r'^catalog$', views.catalog, name='catalog'),
    url(r'^(?P<run>[0-9]{1,4})/$', views.detail, name='detail'),
    url(r'^(?P<run>[0-9]{1,4})/(?P<card>[a-fA-F0-9]{5,10})/$', views.card_plots, name='card_plots'),
    url(r'^(?P<run>[0-9]{1,4})/(?P<test>.*)/$', views.test_plots, name='test_plots'),
    url(r'^calibration$', views.calibration, name='calibration'),
    #url(r'^summary$', views.summary, name='summary'),
    #url(r'^testers$', views.TestersView.as_view(), name='testers'),
    #url(r'^stats$', views.stats, name='stats'),
    #url(r'^test-details$', views.TestDetailsView.as_view(), name='test-details'),
    #url(r'(?P<card>[a-fA-F0-9]{8,16})/$', views.detail, name='detail-uid'),
    #url(r'^(?P<card>[a-fA-F0-9]{8,16})/calibration$', views.calibration, name='calibration-uid'),
    #url(r'^(?P<card>[a-fA-F0-9]{8,16})/calibration/(?P<group>[0-9]{1,2})/plots$', views.calPlots, name='plotview-uid'),
    #url(r'^(?P<card>[a-fA-F0-9]{8,16})/calibration/(?P<group>[0-9]{1,2})/results$', views.calResults, name='results-uid'),
    #url(r'^(?P<card>[a-fA-F0-9]{8,16})/(?P<test>.*)$', views.testDetail, name='testDetail-uid'),
    #url(r'^(?P<card>[0-9]{3,7})/$', views.detail, name='detail'),
    #url(r'^(?P<card>[0-9]{3,7})/calibration$', views.calibration, name='calibration'),
    #url(r'^(?P<card>[0-9]{3,7})/calibration/(?P<group>[0-9]{1,2})/plots$', views.calPlots, name='plotview'),
    #url(r'^(?P<card>[0-9]{3,7})/calibration/(?P<group>[0-9]{1,2})/results$', views.calResults, name='results'),
    #url(r'^(?P<card>[0-9]{3,7})/(?P<test>.*)$', views.testDetail, name='testDetail'),
    #url(r'^error$', views.error, name='error'),
    #url(r'^media/(?P<path>.*)$', serve, {'document_root':MEDIA_ROOT,'show_indexes':True}),
    #url(r'^plots$', views.PlotView.as_view(), name='plots'),
    #url(r'^field$', views.fieldView, name='fieldView'),
]

