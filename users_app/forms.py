from django import forms

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from users_app.models import User


class UserAdminForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
                       queryset=Group.objects.exclude(name='supplier'),
                       widget=forms.CheckboxSelectMultiple(
                            attrs={
                                'id': 'groups',
                                'label': _('Role'),
                                'class': 'list-unstyled'
                            }
                       )
               )

    class Meta:
        model = User
        fields = (
            'email',
            'groups'
        )
        widgets = {
            'email': forms.TextInput(
                attrs={
                    'id': 'email',
                    'class': 'form-control',
                    'placeholder': 'example@eventbrite.com',
                }
            )
        }

    def clean_email(self):
        if not self.cleaned_data['email'].endswith('@eventbrite.com'):
            raise forms.ValidationError('Invalid e-mail')
        return self.cleaned_data['email']
