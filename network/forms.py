from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User


class ProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['profile_pic', 'bio', 'cover','first_name','last_name','username']  # Include other fields you want to allow users to edit

        widgets = {
            
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control', 'style': 'width: 350px; height: 40px; border: 2px solid #e6ecf0 #ccc; margin-bottom: 1px;'}),

            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style':'width: 350px; height: 60px; border: 2px solid #e6ecf0 #ccc;' 'margin-bottom: 1px;'}),

            'cover': forms.ClearableFileInput(attrs={'class': 'form-control', 'style':'width: 350px; height: 40px; border: 2px solid #e6ecf0 #ccc;' 'margin-bottom: 1px;'}),

            'first_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 350px; height: 30px; border: 2px solid #e6ecf0 #ccc; margin-bottom: 1px;'}),

            'last_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 350px; height: 30px; border: 2px solid #e6ecf0 #ccc; margin-bottom: 1px;'}),

            'username': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 350px; height: 30px; border: 2px solid #e6ecf0 #ccc; margin-bottom: 1px;'}),

            
        }
