# forms.py
from django import forms

class PasteDataForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
    table_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'list': 'table_list', 'placeholder': 'New Name or select from dropdown to update existing table', 'size': '53'}),
    )


class ConfirmationForm(forms.Form):
    confirm = forms.BooleanField(label='Confirm Data', required=True)

    def clean(self):
        cleaned_data = super().clean()
        confirm = cleaned_data.get('confirm')

        if not confirm:
            raise forms.ValidationError('You must confirm the data upload.')

        return cleaned_data
