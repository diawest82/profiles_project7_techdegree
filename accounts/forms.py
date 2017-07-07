from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.utils.safestring import mark_safe

from django_countries import widgets, countries
import re
from smartfields import fields

from . import models


class CreateUserForm(UserCreationForm):
    """Creating User Form"""
    verify_email = forms.EmailField(label="Verify your email")

    class Meta:
        model = get_user_model()
        fields = ['first_name',
                  'last_name',
                  'email',
                  'verify_email',
                  'password1',
                  'password2',
                  ]

        def clean(self):
            data = self.cleaned_data
            email = data.get('email')
            verify = data.get('verify')

            if email != verify:
                raise forms.ValidationError(
                    'Emails must match.'
                )
            return data


class UserProfileForm(forms.ModelForm):
    avatar = fields.ImageField(upload_to='avatars/', blank=True)
    bio = forms.CharField(max_length=150,
                          label='Biography',
                          required=False,
                          widget=forms.Textarea(),
                          min_length=10
                          )
    dob = forms.DateTimeField(label='Date of Birth',
                              input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],
                              widget=forms.SelectDateWidget(years=range(1930, 2010))
                              )
    country = forms.ChoiceField(label="Select your Country",
                                widget=widgets.CountrySelectWidget,
                                choices=countries,
                                )
    fav_animal = forms.CharField(label="Favorite Animal",
                                 max_length=50,
                                 required=False,
                                 )
    hobbies = forms.CharField(label='Hobbies',
                              max_length=100,
                              required=False,
                              widget=forms.Textarea(attrs={
                                  'placeholder': "Enter your hobbies"}
                              )
                              )
    location = forms.CharField(label='Location',
                               max_length=100,
                               required=False,
                               )

    class Meta:
        model = models.Profile
        fields = [
            'avatar',
            'bio',
            'dob',
            'location',
            'country',
            'fav_animal',
            'hobbies'
        ]


class UpdateUserForm(forms.ModelForm):
    """Update user profile information"""
    verify_email = forms.EmailField(label="Verify your email address.")

    class Meta:
        model = models.User
        fields = ['first_name',
                  'last_name',
                  'email',
                  'verify_email',

                  ]

        def clean_email(self):
            data = self.cleaned_data
            email = data.get('email')
            verify = data.get('verify')

            if email != verify:
                raise forms.ValidationError(
                    'Emails must match.'
                )
            return data


class ChangePasswordForm(PasswordChangeForm):
    """Changes a user's password"""
    MIN_LENGTH = 14

    new_password1 = forms.CharField(label='Enter a new Password',
                                    required=False,
                                    widget=forms.PasswordInput(attrs={'placeholder': 'New Password'})
                                    )
    new_password2 = forms.CharField(label='Confirm your password',
                                    required=False,
                                    widget=forms.PasswordInput(
                                        attrs={'placeholder': 'Confirm password'}),
                                    )

    class Meta:
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = mark_safe(
            '<ul>\n'
            '<li>Must not be the same as the current password</li>\n'
            '<li>Minimum password length of 14 characters</li>\n'
            '<li>Must use both uppercase and lowercase letters</li>\n'
            '<li>Must include one or more numerical digits</li>\n'
            '<li>Must include at least one special character, such as @, #, or'
            ' $</li>\n'
            "<li>Cannot contain your username or parts of your full name, "
            'such as your first name</li>\n'
            '</ul>'
        )

    def clean(self):
        user = self.request.user
        data = self.cleaned_data
        new_password = data.get('new_password1')
        old_password = data.get('old_password')
        new_password2 = data.get('new_password2')


        # checks new password against old password
        if user.check_password(old_password):
            if new_password == old_password:
                raise forms.ValidationError(
                    "New password cannot match old password"
                )
        else:
            raise forms.ValidationError(
                "Your old password is incorrect"
            )

        # checks for length
        if len(new_password) < self.MIN_LENGTH:
            raise forms.ValidationError(
                "The password must be at least {} characters long".format(self.MIN_LENGTH)
            )

        # checks for an upper and lowercase letter
        if not re.search(r'([a-z])+', new_password) or \
                not re.search(r'([A-Z])+', new_password):
            raise forms.ValidationError(
                "Password must contain a uppercase and lowercase letter"
            )

        # checks for a special character
        if not re.search(r'([@#$])+', new_password):
            raise forms.ValidationError(
                "Password must contain one of the follower @, #, $."
            )


        # Checks for a numerical digit
        if not re.search(r'\d+', new_password):
            raise forms.ValidationError(
                "The password must contain a digit"
            )

        # Checks to make sure passwords match
        if new_password != new_password2:
            raise forms.ValidationError(
                "Passwords must match"
            )

        # Password cannot contain username or parts of the fullname
        user_first = user.first_name.lower()
        user_last = user.last_name.lower()
        user_login = user.email.lower()

        if (user_first in new_password.lower() or user_last in new_password.lower()
                or user_login in new_password.lower()):
            raise forms.ValidationError(
                "Cannot contain your username or parts of your full name, "
                'such as your first name'
            )

        return data
