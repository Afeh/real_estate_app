from django.urls import path
from .views import RegisterView, LoginView, SendOTPView, ResendOTPView, VerifyOTPView, ForgotPasswordView, PasswordResetView
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView
)

urlpatterns = [
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('register', RegisterView.as_view(), name='register'),
	path('login', LoginView.as_view(), name='login'),
	path('send-otp', SendOTPView.as_view(), name='send_otp'),
	path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
	path('resend-otp', ResendOTPView.as_view(), name='resend-otp'),
	path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
	path('password-reset/<uidb64>/<token>', PasswordResetView.as_view(), name='password-reset' )
]
