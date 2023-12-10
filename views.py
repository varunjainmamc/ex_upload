from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import pandas as pd
from io import StringIO
from django.views import View
from ex_upload.models import Table_Excel, Table_E
from .forms import PasteDataForm, ExcelUploadForm, ConfirmationForm


def paste_data(request):
    if request.method == 'POST':
        form = PasteDataForm(request.POST)
        if form.is_valid():
            pasted_data = form.cleaned_data['data']
            # Process pasted_data, e.g., convert it to DataFrame
            df = pd.read_csv(StringIO(pasted_data), sep='\t')  # Adjust separator as needed
            # Do something with the DataFrame 'df', e.g., save to database
            # ...

            return render(request, 'ex_upload/paste_success.html', {'df': df})
    else:
        form = PasteDataForm()

    return render(request, 'ex_upload/paste_data.html', {'form': form})


class input_feedbackView(LoginRequiredMixin, View):
    template_feedback = 'ex_upload/feedback.html'
    template_input = 'ex_upload/input.html'
    # success_url = reverse_lazy('table_revision:input_data')

    def get(self, request):

        table_all = Table_E.objects.values_list('h3', flat=True).distinct()
        ctx = {'table_all': table_all}

        return render(request, self.template_input, ctx)

    def post(self, request):        
        user = request.user.username
        table_name = request.POST['table_name']
        rows = Table_E.objects.filter(h1=user, h3=table_name) # Fetch rows based on username and table_name
        header_row = rows.filter(h2='Y').first() # Extract the header from the row where 'header' column is 'Y'
        header = [getattr(header_row, f'h{i}', '') for i in range(4, 51)]
        
        num_row = rows.count()
        num_row_list = [str(i) for i in range(1, num_row+1)]
        # Remove empty columns
        header = [col for col in header if col]
        num_col = len(header) # Determine the number of columns
        if request.POST['page_t']:
            # feedback = [(header_n, 0) for header_n in header]
            feedback = [(f'h{i}',0) for i in range(4, num_col+4)]
            print(feedback)            
            ctx = {'header': header, 'num_col': num_col, 'num_row': num_row,\
                    'table_name': table_name, 'feedback': feedback, 'num_row_list':num_row_list} # You can pass these variables to your template
            return render(request, self.template_input, ctx)
        else:
            feedback ={}
            for j in range(1,num_row+1):
                feedback[j] ={}
                key = header[0]
                key = f'h4{j}'
                ukv = request.POST.get(key, '')
                print(" 2 HQ")                
                print(key)
                print(ukv)
                existing_data = rows.filter(h4__iexact=ukv).first()
                print(existing_data)
                row = {} # row is dic to collect user value of every current iterating row against field name
                if existing_data:                
                    for f_name, f_value in request.POST.items():
                        if f_name.endswith(str(j)):
                            row[f_name] = f_value
                    print("row")
                    print(row)
                    for field_name, value_form in row.items():
                        modified_field_name = field_name[:-1]
                        correct_value = getattr(existing_data, modified_field_name)
                        print('correct_value', correct_value)
                        if str(value_form).lower() == str(correct_value).lower():
                            feedback[j][field_name] = [value_form,1]
                            # 1 will used in html to display "correct"
                        else:
                            feedback[j][field_name] = [value_form,correct_value]
                print("feedback")
                print(feedback)
            ctx = {'header':header,'feedback': feedback, 'table_name': table_name}
            return render(request, self.template_feedback, ctx)


class upload_excel(View):
    def get(self, request):        
        form = ExcelUploadForm()
        return render(request, 'ex_upload/upload_excel.html', {'form': form})

    def post(self, request):           
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            table_name = form.cleaned_data['table_name']
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file, header=None)
            df.insert(0, 'User_Name', request.user.username)
            df.insert(1, 'header', "N")
            df.loc[0, 'header'] = "Y"
            df.insert(2, 'table_name', table_name)
            num_col = 50- len(df.columns)
            if num_col > 0:
                for i in range(num_col):
                    df.insert(50-num_col+i,f'hi{i}','')
            df.columns = [f'h{i}' for i in range(1, 51)]
            # Store the DataFrame in the session

            data_dict = df.to_dict(orient='split')
            request.session['data_dict'] = data_dict

            # Redirect to the confirmation view
            return redirect('confirmation')
            

        return render(request, 'ex_upload/upload_excel.html', {'form': form})   

class ConfirmationView(View):
    template_name = 'confirmation.html'

    def get(self, request):
        # Retrieve the dictionary from the session
        data_dict = request.session.get('data_dict', {})

        # Reconstruct the DataFrame
        df = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
        form = ConfirmationForm()
        # Display the data for confirmation        
        return render(request, 'ex_upload/confirmation.html', {'df': df, 'form': form})


    def post(self, request):
        # Process confirmation form submission and store data in the database
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            # Retrieve the dictionary from the session
            data_dict = request.session.get('data_dict', {})

            # Reconstruct the DataFrame
            df = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
            data_to_insert = df.to_dict(orient='records') # Convert DataFrame to a list of dictionaries
            Table_E.objects.bulk_create([Table_E(**data) for data in data_to_insert]) # Bulk insert into the database
            request.session.pop('df', None) # Clear the session data
            return redirect('input') # Redirect to a success page

        data_dict = request.session.get('data_dict', {})
        df = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
        return render(request, 'ex_upload/confirmation.html', {'df': df, 'form': form})
