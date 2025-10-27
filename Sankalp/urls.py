"""
URL configuration for Sankalp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from Dashboard import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login_page'),          # for login
    path('api/login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('profile/', views.profile_view , name="profile_view"),
    path('api/baby-status-count/', views.count_baby_status_live, name='baby_status_count_live'),
    path('api/baby_stillborn_count_view/', views.baby_stillborn_count_view, name='baby_stillborn_count_view'),
    path('api/live-born-dag/', views.count_live_born_by_dag, name='live_born_dag'),
    path('api/stillborn-dag/', views.stillborn_dag_count_view, name='stillborn_dag'),
    path('api/count-dead-calls/', views.count_dead_calls, name='count_dead_calls'),
    path('dead_counts/', views.count_dead_calls_dag, name='dead_counts'),
    path("api/connected-calls/", views.count_connected_calls, name="count_connected_calls"),
    path("api/connected-calls-dag/", views.count_connected_calls_dag, name="count_connected_calls_dag"),
    path("api/total-deliveries/", views.count_total_deliveries, name="count_total_deliveries"),
    path("api/total-deliveries-dag/", views.count_total_deliveries_dag, name="count_total_deliveries_dag"),
    path('api/stillbirth-rate/', views.stillbirth_rate_view, name='stillbirth_rate'),
    path("api/stillbirth-rate-dag/", views.stillbirth_rate_dag_view, name="stillbirth_rate_dag"),
    path("api/neonatal-mortality-rate/", views.neonatal_mortality_rate_view, name="neonatal_mortality_rate"),
    path("api/neonatal-mortality-rate-dag/", views.neonatal_mortality_rate_dag_view, name="neonatal_mortality_rate_dag"),
    path("api/sbr-nmr-combined/", views.sbr_nmr_combined_view, name="sbr_nmr_combined"),
    path("api/sbr-nmr-combined-dag/", views.sbr_nmr_combined_dag_view, name="sbr_nmr_combined_dag"),
    #path('refresh-data/', views.refresh_data, name='refresh_data'),


#########performance###########
path('day29-chart/', views.chart_view, name='day29_chart'),


path('api/day29-followup-status/', views.count_day29_followup_combined, name='count_day29_followup_combined'),
path('api/birthweight-availability/', views.count_birthweight_availability, name='count_birthweight_availability'),
path("api/delivery-location-availability/", views.count_delivery_location_availability, name="count_delivery_location_availability"),  # ✅ new
  ########3 death place of death

  path('death-place-availability/', views.count_death_place_availability, name='death_place_availability'),
  path("death-date-availability/", views.count_death_date_availability, name="death_date_availability"),

  path("gender-availability/", views.count_livebirth_gender_availability, name="count_livebirth_gender_availability"),
  path("dead-gender-availability/", views.count_dead_gender_availability, name="count_dead_gender_availability"),


  path("death-cause-availability/", views.count_death_cause_availability, name="death_cause_availability"),


  ######outcome

      path('outcome_dashboard/', views.outcome_dashboard, name='outcome_dashboard'),
        path('count_delivery_location_place/', views.count_delivery_location_place, name='count_delivery_location_place'),

        path('count_birthweight_category/', views.count_birthweight_category, name='count_birthweight_category'),
       path('count_birthweight_category_for_dead_calls/', views.count_birthweight_category_for_dead_calls, name='count_birthweight_category_for_dead_calls'),
     
     path('count_place_of_death_for_dead_calls/', views.count_place_of_death_for_dead_calls, name='count_place_of_death_for_dead_calls'),
    path('count_dead_gender_availabilitys/', views.count_dead_gender_availabilitys, name='count_dead_gender_availabilitys'),

    path('count_livebirth_gender_availabilityes/', views.count_livebirth_gender_availabilityes, name='count_livebirth_gender_availabilityes'),
        path('api/count-total-deliveriess/', views.count_total_deliveriess, name='count_total_deliveriess'),


    path('api/ga_count_total_deliveriess/', views.ga_count_total_deliveriess, name='ga_count_total_deliveriess'),


    ## analytic 

    path("count/place-vs-delivery/", views.count_place_vs_delivery_combined, name="count_place_vs_delivery_combined"),

    path("count/gender-live-vs-dead/", views.count_gender_live_vs_dead, name="count_gender_live_vs_dead"),

    path("count/birthweight-live-vs-dead/", views.count_birthweight_live_vs_dead, name="count_birthweight_live_vs_dead"),












        # for dashboard
]


