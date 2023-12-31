from django.db import models

fields = {}

for i in range(1, 54):
    fields[f'h{i}'] = models.CharField(max_length=100)
    # fields['timestamp'] = models.DateTimeField(auto_now_add=True)

# Dynamically create the model class with the __module__ attribute
Table_E = type('Table_E', (models.Model,), {'__module__': __name__, **fields})