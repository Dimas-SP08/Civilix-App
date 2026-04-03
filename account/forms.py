from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from . models import User
class RegisterUserForms(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'nama', 'email', 'no_hp', 'password1', 'password2'
        ]

    

class UpdateUserForms(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'nama', 'tmp_lahir','email','tgl_lahir', 'no_hp', 'img_user',
        ]

    