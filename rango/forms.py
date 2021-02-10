from django import forms
from rango.models import Page,Category
from django.contrib.auth.models import User
from rango.models import UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category
        # fields mean included on the form
        fields = ('name',)

class PageForm(forms.ModelForm):
    # text entry for users
    title = forms.CharField(max_length=128,help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Page
        # excluded from form
        exclude = ('category',)

        def clean(self):
            cleaned_data = self.cleaned_data
            url = cleaned_data.get('url')

            if url and not url.startswith('http://'):
                url = f'http://{url}'
                cleaned_data['url'] = url
            return cleaned_data
                

    
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture',)
