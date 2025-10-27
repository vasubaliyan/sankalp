

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# ============================
#  PROJECT 1 MODEL
# ============================
class Project1Record(models.Model):
    record_id = models.CharField(max_length=50, unique=True)
    data_access_group = models.CharField(max_length=255, null=True, blank=True)

    # Baby status
    baby1_status = models.CharField(max_length=255, null=True, blank=True)
    baby2_status = models.CharField(max_length=255, null=True, blank=True)
    baby3_status = models.CharField(max_length=255, null=True, blank=True)

    # baby sttus day29
    d29_baby_current_status_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b3=models.CharField(max_length=255, null=True, blank=True)



    # Call status
    d29_call_status_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    # Birth weight
    baby1_birthweight = models.CharField(max_length=255, null=True, blank=True)
    baby2_birthweight = models.CharField(max_length=255, null=True, blank=True)
    baby3_birthweight = models.CharField(max_length=255, null=True, blank=True)

    # Gestation & delivery
    gestationage = models.CharField(max_length=255, null=True, blank=True)
    estimateddateofdelivery = models.CharField(max_length=255, null=True, blank=True)
    q34_estimated_ga_through_ultrasound = models.CharField(max_length=255, null=True, blank=True)
    q35_if_available_estimated_ga_through_ultrasound = models.CharField(max_length=255, null=True, blank=True)
    reg_b1_delivery_type = models.CharField(max_length=255, null=True, blank=True)
    assistedvaginaldelivery = models.CharField(max_length=255, null=True, blank=True)
    reg_b1_total_baby_delivered = models.CharField(max_length=255, null=True, blank=True)

    # Baby current status
    d29_baby_current_status_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    # baby current status day 29
    d29_call_status_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b3=models.CharField(max_length=255, null=True, blank=True)



    # Cause of death
    q17_cause_of_death_d7_if_known = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_specify_d7 = models.CharField(max_length=255, null=True, blank=True)
    q17_cause_of_death_d7_b2 = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_specify_d7_b2 = models.CharField(max_length=255, null=True, blank=True)
    q17_cause_of_death_d7_b3 = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_d7_b3 = models.CharField(max_length=255, null=True, blank=True)

    # Baby sex
    baby1_sex = models.CharField(max_length=255, null=True, blank=True)
    baby2_sex = models.CharField(max_length=255, null=True, blank=True)
    baby3_sex = models.CharField(max_length=255, null=True, blank=True)

    # Delivery
    reg_b1_delivery_date = models.CharField(max_length=255, null=True, blank=True)
    delivery_date = models.CharField(max_length=255, null=True, blank=True)
    delivery_location = models.CharField(max_length=255, null=True, blank=True)

    # Baby death place
    d29_baby_death_place_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    #date of death#
    d29_baby_death_date_b1= models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_date_b2= models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_date_b3= models.CharField(max_length=255, null=True, blank=True)
    #day_29 place of death

    d29_baby_death_place_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b3=models.CharField(max_length=255, null=True, blank=True)
    q17_cause_of_death_d29_b1_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_10 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_10 = models.CharField(max_length=100, null=True, blank=True)
          
# Similarly for baby 3
    q17_cause_of_death_d29_b3_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_10 = models.CharField(max_length=100, null=True, blank=True)


    #####GA########3

    estimated_date_of_delivery = models.CharField(max_length=100,null=True,blank=True,db_column="estimated_date_of_delivery_p1" ) 
    gestation_age=models.CharField(max_length=100, null=True, blank=True)
    ga_edd=models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        
        return f"{self.record_id}"



# ============================
#  PROJECT 2 MODEL
# ============================
class Project2Record(models.Model):
    record_id = models.CharField(max_length=50, unique=True)
    data_access_group = models.CharField(max_length=255, null=True, blank=True)

    # Baby status
    baby1_status = models.CharField(max_length=255, null=True, blank=True)
    baby2_status = models.CharField(max_length=255, null=True, blank=True)
    baby3_status = models.CharField(max_length=255, null=True, blank=True)

    # Call status
    d29_call_status_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    #call status day_29
    d29_call_status_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_call_status_b3=models.CharField(max_length=255, null=True, blank=True)


    # Birth weight
    baby1_birthweight = models.CharField(max_length=255, null=True, blank=True)
    baby2_birthweight = models.CharField(max_length=255, null=True, blank=True)
    baby3_birthweight = models.CharField(max_length=255, null=True, blank=True)

    # Gestation & delivery
    gestationage = models.CharField(max_length=255, null=True, blank=True)
    estimateddateofdelivery = models.CharField(max_length=255, null=True, blank=True)
    q34_estimated_ga_through_ultrasound = models.CharField(max_length=255, null=True, blank=True)
    q35_if_available_estimated_ga_through_ultrasound = models.CharField(max_length=255, null=True, blank=True)
    reg_b1_delivery_type = models.CharField(max_length=255, null=True, blank=True)
    assistedvaginaldelivery = models.CharField(max_length=255, null=True, blank=True)
    reg_b1_total_baby_delivered = models.CharField(max_length=255, null=True, blank=True)

    # Baby current status
    d29_baby_current_status_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    # Cause of death
    q17_cause_of_death_d7_if_known = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_specify_d7 = models.CharField(max_length=255, null=True, blank=True)
    q17_cause_of_death_d7_b2 = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_specify_d7_b2 = models.CharField(max_length=255, null=True, blank=True)
    q17_cause_of_death_d7_b3 = models.CharField(max_length=255, null=True, blank=True)
    q17a_if_other_d7_b3 = models.CharField(max_length=255, null=True, blank=True)

    # Baby sex
    baby1_sex = models.CharField(max_length=255, null=True, blank=True)
    baby2_sex = models.CharField(max_length=255, null=True, blank=True)
    baby3_sex = models.CharField(max_length=255, null=True, blank=True)

    # Delivery
    reg_b1_delivery_date = models.CharField(max_length=255, null=True, blank=True)
    delivery_date = models.CharField(max_length=255, null=True, blank=True)
    delivery_location = models.CharField(max_length=255, null=True, blank=True)

    # Baby death place
    d29_baby_death_place_b1_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b2_d14_d7 = models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b3_d14_d7 = models.CharField(max_length=255, null=True, blank=True)

    # baby sttus day29
    d29_baby_current_status_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_current_status_b3=models.CharField(max_length=255, null=True, blank=True)

    #date of death#
    d29_baby_death_date_b1= models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_date_b2= models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_date_b3= models.CharField(max_length=255, null=True, blank=True)
    #day_29 place of death

    d29_baby_death_place_b1=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b2=models.CharField(max_length=255, null=True, blank=True)
    d29_baby_death_place_b3=models.CharField(max_length=255, null=True, blank=True)

    q17_cause_of_death_d29_b1_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b1_10 = models.CharField(max_length=100, null=True, blank=True)
    # Similarly for baby 2
    q17_cause_of_death_d29_b2_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b2_10 = models.CharField(max_length=100, null=True, blank=True)  
    # Similarly for baby 3
    q17_cause_of_death_d29_b3_1 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_2 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_3 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_4 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_5 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_6 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_7 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_8 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_9 = models.CharField(max_length=100, null=True, blank=True)
    q17_cause_of_death_d29_b3_10 = models.CharField(max_length=100, null=True, blank=True)




    ######GA#############
    gestation_age=models.CharField(max_length=100, null=True, blank=True)
    estimated_date_of_delivery = models.CharField(max_length=100,null=True,blank=True,db_column="estimated_date_of_delivery_p2" ) 
    q40_ga_ultrasound_20wks_weeks = models.CharField(
        max_length=50, null=True, blank=True, db_column="q40_ga_ultrasound_20wks_weeks"
    )





    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.record_id}"



# ============================
#  FETCH LOG (shared)
# ============================
class ProjectFetchLog(models.Model):
    project_name = models.CharField(max_length=255, unique=True)
    last_fetch_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} last fetched at {self.last_fetch_time}"




from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
