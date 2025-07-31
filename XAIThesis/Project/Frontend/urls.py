from django.urls import path
from .views import (login_view, signup_view, home_view, confirm_email, user_role_view, logout_view,
                    training_sustainability,
                    energy_comparison, guide_view, save_response, start_study, study_complete, complete_session)

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home_view, name="home"),
    path('signup/', signup_view, name='signup'),  # ← THIS name='signup'
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('training',training_sustainability, name= 'training'),
    path('energy/', energy_comparison, name='energy_comparison'),
    path('user_role/', user_role_view, name='user_role'),
    path('user_role/<str:role>/', user_role_view, name='user_role'),
    path('guide',guide_view,name='guide'),
    # Email confirmation link
    path('confirm_email/<str:token>/', confirm_email, name='confirm_email'),
    # Request a password reset (enter email)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html'
         ), 
         name='password_reset'),
    
    # Email sent confirmation
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    # Link from email: enter new password
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    # Password reset complete confirmation
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    path('study',start_study,name='study'),

    path('save_response',save_response,name= 'save_response'),
    path("study_complete/<int:session_id>/", study_complete, name="study_complete"),
    path('complete_session/', complete_session, name='complete_session'),


]

