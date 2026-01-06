from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken import views as drf_auth_views

schema_view = get_schema_view(
   openapi.Info(
      title="Mini Assessment Engine API",
      default_version='v1',
      description="""API for collecting and grading student exams.

**Authentication Guide:**
1. **Session Auth**: Click "Login" top right (for browser use).
2. **Token Auth**: 
    - POST username/password to `/api/token-auth/` to get a key.
    - Click "Authorize" button.
    - Enter value: `Token <YOUR_KEY>` (prefix is important!).
      """,
      contact=openapi.Contact(email="contact@acad.ai"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('/swagger/')

# ... imports ...

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assessments.urls')),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token-auth/', drf_auth_views.obtain_auth_token, name='api_token_auth'),
    
    path('accounts/logout/', custom_logout, name='logout'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
