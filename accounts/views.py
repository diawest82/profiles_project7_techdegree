from django.contrib import messages
from django.contrib.auth import (
	authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import forms


def sign_in(request):
	"""Sign in"""
	form = AuthenticationForm()
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			if form.user_cache is not None:
				user = form.user_cache
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect(
						reverse('home')  # TODO: go to profile
					)
				else:
					messages.error(
						request,
						"That user account has been disabled."
					)
			else:
				messages.error(
					request,
					"Username or password is incorrect."
				)
	return render(request, 'accounts/sign_in.html', {'form': form})


def sign_up(request):
	"""Registration Form"""
	form = forms.CreateUserForm()
	if request.method == 'POST':
		form = forms.CreateUserForm(data=request.POST)
		if form.is_valid():
			form.save()
			user = authenticate(
				email=form.cleaned_data['email'],
				password=form.cleaned_data['password1']
			)
			login(request, user)
			messages.success(
				request,
				"You're now a user! You've been signed in, too."
			)
			return HttpResponseRedirect(reverse('home'))  # TODO: go to profile
	return render(request, 'accounts/sign_up.html', {'form': form})


@login_required
def sign_out(request):
	"""Log out"""
	logout(request)
	messages.success(request, "You've been signed out. Come back soon!")
	return HttpResponseRedirect(reverse('home'))

@login_required
def user_profile(request):
	"""User Profile View"""
	user = request.user
	return render(request, 'accounts/profile.html', {'user': user})

@login_required
def edit_user_profile(request):
	"""Edit User Profle information"""
	user = request.user
	form1 = forms.UpdateUserForm(instance=user)
	form2 = forms.UserProfileForm(instance=user.profile)

	if request.method == 'POST':
		form1 = forms.UpdateUserForm(instance=user, data=request.POST)
		form2 = forms.UserProfileForm(instance=user.profile,
									  data=request.POST,
									  files=request.FILES
									  )
		if form1.is_valid() and form2.is_valid():
			form1.save()
			form2.save()
			messages.success(request, 'Your profle has been update')
			return HttpResponseRedirect(reverse('accounts:profile'))
	return render(request, 'accounts/edit.html',
				  {'form1': form1,
				   'form2': form2,
				   })

@login_required
def change_password(request):
	"""Changes the password"""
	form = forms.ChangePasswordForm(
		user=request.user,
		request=request
	)
	if request.method == "POST":
		form = forms.ChangePasswordForm(
			user=request.user,
			request=request,
			data=request.POST
		)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			messages.success(request, "Password updataed!")
			return HttpResponseRedirect(reverse('accounts:profile'))
	return render(request, 'accounts/change_password.html', {'form': form})

