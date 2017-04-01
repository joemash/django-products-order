from django import forms


class ContactUsForm(forms.Form):
    full_name = forms.CharField(max_length=200,label='Name')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='phone',widget=forms.NumberInput)
    message = forms.CharField(label='Message',widget=forms.Textarea)
