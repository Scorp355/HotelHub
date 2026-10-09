from django import forms

ALLOWED_IMPORT_EXTENSIONS = ('.csv', '.xlsx')

class HotelImportForm(forms.Form):
    
    import_file = forms.FileField(
        label='Файл с отелями (CSV или Excel)',
        help_text=(
            'Колонки: name, city, address, price, rating. '
            'Первая строка — заголовок, она пропускается. '
            'Поддерживаются форматы .csv и .xlsx.'
        ),
    )

    def clean_import_file(self):
        file = self.cleaned_data['import_file']
        name = file.name.lower()
        if not name.endswith(ALLOWED_IMPORT_EXTENSIONS):
            raise forms.ValidationError(
                'Поддерживаются только файлы .csv и .xlsx.'
            )
        return file