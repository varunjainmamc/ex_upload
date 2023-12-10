 def post(self, request):        
        user = request.user.username
        table_name = request.POST['table_name']
        rows = Table_E.objects.filter(h1=user, h3=table_name) # Fetch rows based on username and table_name
        header_row = rows.filter(h2='Y').first() # Extract the header from the row where 'header' column is 'Y'
        header = [getattr(header_row, f'h{i}', '') for i in range(4, 51)]
        num_col = len(header) # Determine the number of columns
        num_row = rows.count()
        num_row_list = [str(i) for i in range(1, num_row+1)]
        # Remove empty columns
        header = [col for col in header if col]
        if request.POST['page_t']:
            feedback = [(header_n, 0) for header_n in header]
            print(feedback)            
            ctx = {'header': header, 'num_col': num_col, 'num_row': num_row,\
                    'table_name': table_name, 'feedback': feedback, 'num_row_list':num_row_list} # You can pass these variables to your template
            return render(request, self.template_input, ctx)
        else:
            feedback ={}
            for j in range(1,num_row+1):
                feedback[j] ={}
                key = header[0]
                key = f'{key}{j}'
                ukv = request.POST.get(key, '')
                print(" 2 HQ")
                print(ukv)
                print(key)
                existing_data = rows.filter(h4__iexact=ukv).first()
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
                        if str(value_form).lower() == str(correct_value).lower():
                            feedback[j][field_name] = [value_form,1]
                            # 1 will used in html to display "correct"
                        else:
                            feedback[j][field_name] = [value_form,correct_value]
                # print("feedback")
                # print(feedback)
            ctx = {'header':header,'feedback': feedback}
            return render(request, self.template_feedback)
