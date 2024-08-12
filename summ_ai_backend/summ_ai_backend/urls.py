from django.contrib import admin
from django.urls import path, include
from translation.views import RegisterView, UserDetailView, TranslationCreateView, TranslationListView, AdminUserListView, AdminTranslationListView, AdminTranslationListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static
from django.conf import settings


# URL patterns define the routing for the Django application.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', UserDetailView.as_view(), name='user-detail'),
    path('api/translate/', TranslationCreateView.as_view(), name='translation-create'),
    path('api/translations/', TranslationListView.as_view(), name='translation-list'),
    path('api/admin/translations/<int:user_id>/', AdminTranslationListView.as_view(), name='admin-translation-list'),
    path('api/admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('', include('translation.urls')),
]

# Static files (CSS, JavaScript, Images) configuration for development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)