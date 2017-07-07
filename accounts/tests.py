from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import User, create_user_profile, Profile
# Create your tests here.


user_create_data= {
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'test@gmail.com',
    'password1': 'TestPassword1$',
    'password2': 'TestPassword1$'
}

class TestData():
    @classmethod
    def setUp(cls):
        User = get_user_model()
        cls.user_test = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@gmail.com',
            password='TestPassword1$'
        )


# Testing models

class UserModelTest(TestData, TestCase):
    def UserCreationTest(self):
        user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@gmail.com',
            password='TestPassword1$'
        )

        self.assertIn(user.first_name, 'Test')


