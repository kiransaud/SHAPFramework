
import re
from .models import CustomUser
from django import  forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

DOMAIN_REGEX = r'^(?=.{1,253}$)(?!-)([A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,}$'

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields =['name','middle_name','last_name', 'email', 'password','organization', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'class': 'form-input'
            }),
            'middle_name': forms.TextInput(attrs={
                'placeholder': 'Middle Name',
                'class': 'form-input'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'form-input'
            }),
            
            
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-input'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Password',
                'class': 'form-input'
            }),
            
            'organization': forms.TextInput(attrs={
                'placeholder': 'Your Organization',
                'class': 'form-input'
            }),
            'location': forms.Select(attrs={
                'class': 'form-input'
            }),
            
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set username to the email value to satisfy the unique constraint.
        user.username = self.cleaned_data.get('email')
        # Hash the password properly.
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        if commit:
            user.save()
        return user
    
    
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        return name
    
    def clean_last_name(self):
        l_name= self.cleaned_data.get('last_name')
        if not l_name:
            raise forms.ValidationError("Last Name is required.")
        return l_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Email is required.")
        
        email = email.strip().lower() # Normalize email address example lower_case for uniqueness
        if '@' in email:
            try:
                validate_email(email)
                
            except DjangoValidationError:
                raise forms.ValidationError("Enter a valid email address.")
        else:
            if not re.match(DOMAIN_REGEX, email):
                raise forms.ValidationError("Enter a valid domain.")

        # ✅ Check uniqueness
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Passwords is require ')
        elif len(password) < 6:
            raise forms.ValidationError('Password must be at least 6 charachrers long ')
        
        return password
    
    def clean_organization(self):
        organization = self.cleaned_data.get('organization')
        if not organization:
            raise forms.ValidationError('Organization is required.')
        return organization
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location:
            raise forms.ValidationError('please select location.')
        return location
            
            