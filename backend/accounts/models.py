from django.db import models


class Customerprofile(models.Model):
    user = models.OneToOneField("AuthUser", models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=32)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "accounts_customerprofile"


class Userprofile(models.Model):
    user = models.OneToOneField("AuthUser", models.CASCADE, primary_key=True)
    is_vendor = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "accounts_userprofile"


class AuthUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active_bool(self):
        return bool(self.is_active)

    @property
    def is_staff_bool(self):
        return bool(self.is_staff)

    @property
    def is_superuser_bool(self):
        return bool(self.is_superuser)
