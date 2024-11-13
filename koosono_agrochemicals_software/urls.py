from django.contrib import admin
from django.urls import include, path
from koosono_agrochemicals_software import settings
from django.views.static import serve
from django.conf.urls.static import static
from django.urls import re_path
from koosono_agro_app import views, AdminViews
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', include('pwa.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login_page'),
    path('homepage', AdminViews.homepage, name="homepage"),
    path('add-product', AdminViews.add_product, name="add_product"),
    path('add_product_save', AdminViews.add_product_save, name="add_product_save"),
    path('products/<int:product_id>/enter_sale/', AdminViews.enter_sale, name='enter_sale'),
    path('sales-report', AdminViews.sales_report, name='sales_report'),
    path('search-product/', AdminViews.search_product, name='search_product'),
    path('login', views.do_login, name='do_login'),
    path('products/', AdminViews.product_list, name='product_list'),
    path('add-purchase/<int:product_id>/', AdminViews.add_purchase, name='add_purchase'),
    path('do_logout', views.Logout_User, name="do_logout"),
    path('pin-authentication/', AdminViews.pin_authentication_view, name='pin_authentication'),
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name="password_reset_form.html"), name="reset_password"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if not settings.DEBUG: 
     urlpatterns += re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
