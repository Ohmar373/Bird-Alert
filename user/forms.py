from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_no = forms.CharField(max_length = 20)
    first_name = forms.CharField(max_length = 20)
    last_name = forms.CharField(max_length = 20)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_no', 'password1', 'password2']


class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(label="Email")