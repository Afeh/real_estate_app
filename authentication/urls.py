from django.urls import path
from .views import RegisterView, LoginView, SendOTPView, ResendOTPView, VerifyOTPView, ForgotPasswordView, PasswordResetView, GetAgentDetail, GetClientDetail, UpdateUserProfile, DeactivateAccountView, ReactivateAccountView, ActivateAccountView, SaveUserLocation, CreateTestimonialView, GetAgentTestimonials, AgentListView
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
	path('verify-otp', VerifyOTPView.as_view(), name='verify_otp'),
	path('resend-otp', ResendOTPView.as_view(), name='resend_otp'),
	path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
	path('password-reset/<uidb64>/<token>', PasswordResetView.as_view(), name='password_reset' ),
	path('client/<client_id>', GetClientDetail.as_view(), name='client_details'),
	path('agent/<agent_id>', GetAgentDetail.as_view(), name='agent_details'),
	path('update/<user_id>', UpdateUserProfile.as_view(), name='update_profile'),
	path('deactivate/<user_id>', DeactivateAccountView.as_view(), name='deactivate_account'),
	path('reactivate', ReactivateAccountView.as_view(), name='reactivate_account'),
	path('activate/<uidb64>/<token>', ActivateAccountView.as_view(), name='activate_account'),
	path('save-location', SaveUserLocation.as_view(), name='save_location'), 
	path('agents-testimonial', CreateTestimonialView.as_view(), name='create_testimonial'),
	path('agents-testimonial/<uuid:agent_id>', GetAgentTestimonials.as_view(), name='get_testimonials'),
	path('agents', AgentListView.as_view(), name='agents')

	
]
