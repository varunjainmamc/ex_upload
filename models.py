from django.db import models

fields = {}

class Table_Excel(models.Model):
    for i in range(1, 51):
        fields[f'h{i}'] = models.CharField(max_length=100)

# Dynamically create the model class with the __module__ attribute
Table_E = type('Table_E', (models.Model,), {'__module__': __name__, **fields})
