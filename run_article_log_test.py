def time_string_to_seconds(time_str):
    if isinstance(time_str, int):
        return time_str
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()

def calculate_totals(data):
    total_cycles = sum(data['Antal'])
    total_time = sum([str_to_timedelta(time_str).total_seconds() for time_str in data['Total Cykeltid (HH:MM:SS)']])
    return total_cycles, total_time

def calculate_average_time(total_time, total_cycles):
    if total_cycles > 0:
        average_time = timedelta(seconds=total_time / total_cycles)
    else:
        average_time = timedelta(seconds=0)
    return average_time


def save_log(filename, data):
    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Create a new workbook and add a worksheet
    wb = openpyxl.Workbook()
    ws = wb.active

    # Add the image to the worksheet
    img = Image(logo_path)
    img.anchor = 'A1'
    ws.add_image(img)


    # Add column headers for the log data
    column_headers = ["Batchdatum", "Antal", "Antal skippad test", "Total Cykeltid (HH:MM:SS)",
                      "Total Ställtid (HH:MM:SS)", "Total Stycktid (HH:MM:SS)", "Cykeltid (HH:MM:SS)",
                      "Stycktid (HH:MM:SS)", "Styck Ställtid (HH:MM:SS)"]
    
    for col_num, header in enumerate(column_headers, 1):
        col_letter = openpyxl.utils.get_column_letter(col_num)
        ws[f'{col_letter}6'] = header
        ws[f'{col_letter}6'].alignment = Alignment(horizontal="center")
        ws[f'{col_letter}6'].font = openpyxl.styles.Font(bold=True)

    # Add the data rows to the worksheet starting from row 7
    for row_num, row_data in df.iterrows():
        for col_num, (col_name, value) in enumerate(row_data.items(), 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            ws[f'{col_letter}{row_num + 7}'] = value

    # Save the workbook
    wb.save(filename)


def create_new_log_file(filename, data):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    df = pd.DataFrame(data)

    # Extract the relevant part of the filename
    base_filename = os.path.basename(filename)
    article_number = base_filename.split('_')[0]

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, startrow=4, startcol=1)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add the image and set its position and size
        img = OpenpyxlImage(logo_path)
        img.anchor = 'A1'
        img.width = 340  # Set the width to fit into A1:B3
        img.height = 80  # Set the height to fit into A1:B3
        worksheet.add_image(img)

        # Add headers
        headers = ["Artikelnummer", "AVG. Stycktid", "Senaste Stycktid"]
        values = [article_number, "00:00:00", df.iloc[0]['Cykeltid (HH:MM:SS)']]  # Initialize with the first entry's Cykeltid
        for col_num, (header, value) in enumerate(zip(headers, values), 2):
            worksheet.cell(row=1, column=col_num * 2).value = header
            worksheet.cell(row=2, column=col_num * 2).value = value
            worksheet.cell(row=1, column=col_num * 2).font = Font(bold=True)
            worksheet.cell(row=2, column=col_num * 2).alignment = Alignment(horizontal="center")

        worksheet.column_dimensions['A'].width = 5
        worksheet.column_dimensions['B'].width = 25
        worksheet.column_dimensions['C'].width = 25
        worksheet.column_dimensions['D'].width = 25
        worksheet.column_dimensions['E'].width = 25
        worksheet.column_dimensions['F'].width = 25
        worksheet.column_dimensions['G'].width = 25
        worksheet.column_dimensions['H'].width = 25
        worksheet.column_dimensions['I'].width = 25
        worksheet.column_dimensions['J'].width = 25
        worksheet.column_dimensions['K'].width = 25

        # Calculate total cycles and total time
        total_cycles, total_time = calculate_totals(data)

        # Calculate average cycle time
        avg_cycle_time = calculate_average_time(total_time, total_cycles)

        # Add headers for total calculations
        worksheet['G1'] = "Total Tid"
        worksheet['G3'] = "Total Antal"

        # Make headers bold
        worksheet['G1'].font = Font(bold=True)
        worksheet['G3'].font = Font(bold=True)

        # Update calculated values in the worksheet
        worksheet['G4'] = total_cycles
        worksheet['G2'] = seconds_to_hms(total_time)
        worksheet['F2'] = str(avg_cycle_time)

    print(f"Created new log file: {filename}")



def update_log(filename, data, batch_name=None):
    try:
        # Load workbook or create new one if not found
        if os.path.exists(filename):
            wb = openpyxl.load_workbook(filename)
        else:
            wb = openpyxl.Workbook()

        # Ensure Sheet1 exists or create it
        if 'Sheet1' not in wb.sheetnames:
            create_new_log_file(filename, [data])  # Create a new log file with the initial data
            return  # No need to continue since the file is created
        else:
            ws_main = wb['Sheet1']

        # Calculate totals and averages for the main sheet
        total_cycles, total_time = calculate_totals(data)
        avg_cycle_time = calculate_average_time(total_time, total_cycles)
        article_number = os.path.basename(filename).split('_')[0]

        # Write to the main sheet, update totals/averages (assuming they are in row 2)
        ws_main.cell(row=2, column=2, value=article_number)
        ws_main.cell(row=2, column=4, value=str(avg_cycle_time))
        ws_main.cell(row=2, column=6, value=data["Cykeltid (HH:MM:SS)"])
        ws_main.cell(row=2, column=8, value=seconds_to_hms(total_time))
        ws_main.cell(row=2, column=10, value=total_cycles)

        # Name the new batch sheet based on batch date or count
        batch_date = datetime.now().strftime('%y-%m-%d %H:%M')
        sheet_name = batch_name if batch_name else f"Batch_{batch_date.replace(':', '-')}"
        if sheet_name in wb.sheetnames:
            ws_batch = wb[sheet_name]
        else:
            ws_batch = wb.create_sheet(title=sheet_name)

        # Add headers for the batch sheet if it's a new sheet
        if ws_batch.max_row == 1:
            batch_headers = ["Tillvekad", "Antal pins", "Fullt testad", "Serienummer"]
            for col_num, header in enumerate(batch_headers, 1):
                col_letter = openpyxl.utils.get_column_letter(col_num)
                ws_batch[f'{col_letter}1'] = header
                ws_batch[f'{col_letter}1'].font = Font(bold=True)

        # Get the next available row in the batch sheet
        next_row_batch = ws_batch.max_row + 1

        # Write to the batch sheet
        ws_batch.cell(row=next_row_batch, column=1, value=data["Batchdatum"])
        ws_batch.cell(row=next_row_batch, column=2, value=8)  # Assuming 8 pins per cycle; adjust as needed
        ws_batch.cell(row=next_row_batch, column=3, value="Ja" if data["Antal skippad test"] == 0 else "Nej")
        ws_batch.cell(row=next_row_batch, column=4, value=data["Serienummer"])

        # Save the workbook after adding the new data
        wb.save(filename)
        print(f"Log updated with batch data in sheet {sheet_name} and main data in Sheet1.")

    except FileNotFoundError:
        # If file doesn't exist, create a new one
        create_new_log_file(filename, [data])






# Function to finish the batch
def finish_batch():
    global amount_of_cycles_done, total_elapsed_time, downtime, skipped_tests, elapsed_time_previous_cycle, elapsed_time_current_cycle

    batch_date = datetime.now().strftime('%y-%m-%d %H:%M')

    # Accumulate data for the entire batch
    total_cycle_time = timedelta(seconds=0)
    total_work_time = timedelta(seconds=0)
    total_stall_time = timedelta(seconds=0)

    for i in range(amount_of_cycles_done):
        cycle_time = max(timedelta(seconds=0), timedelta(seconds=elapsed_time_previous_cycle))
        work_time = max(timedelta(seconds=0), cycle_time - timedelta(seconds=downtime))
        stall_time = max(timedelta(seconds=0), timedelta(seconds=downtime))

        total_cycle_time += cycle_time
        total_work_time += work_time
        total_stall_time += stall_time

        # Log each cycle individually in the batch sheet
        cycle_data = {
            "Batchdatum": batch_date,
            "Antal": 1,
            "Antal skippad test": skipped_tests,
            "Total Cykeltid (HH:MM:SS)": seconds_to_hms(cycle_time.total_seconds()),
            "Total Ställtid (HH:MM:SS)": seconds_to_hms(stall_time.total_seconds()),
            "Total Stycktid (HH:MM:SS)": seconds_to_hms(work_time.total_seconds()),
            "Cykeltid (HH:MM:SS)": seconds_to_hms(cycle_time.total_seconds()),
            "Stycktid (HH:MM:SS)": seconds_to_hms(work_time.total_seconds()),
            "Styck Ställtid (HH:MM:SS)": seconds_to_hms(stall_time.total_seconds()),
            "Serienummer": i + 1
        }

        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_log_filepath = os.path.join(script_dir, "Artiklar", f"{filename}_log.xlsx")
        smb_log_filepath = "/mnt/nas/Artiklar/{}_log.xlsx".format(filename)

        # Update the batch sheet with individual cycle data
        update_log(local_log_filepath, cycle_data, batch_name=f"Batch_{amount_of_cycles_done}")
        update_log(smb_log_filepath, cycle_data, batch_name=f"Batch_{amount_of_cycles_done}")

    # Now, update the main sheet using the format from create_new_log_file
    main_data = {
        "Batchdatum": batch_date,
        "Antal": amount_of_cycles_done,
        "Antal skippad test": skipped_tests,
        "Total Cykeltid (HH:MM:SS)": seconds_to_hms(total_cycle_time.total_seconds()),
        "Total Ställtid (HH:MM:SS)": seconds_to_hms(total_stall_time.total_seconds()),
        "Total Stycktid (HH:MM:SS)": seconds_to_hms(total_work_time.total_seconds())
    }

    # Update the main sheet with cumulative batch data
    update_log(local_log_filepath, main_data)
    update_log(smb_log_filepath, main_data)

    # Reset batch variables after logging the batch summary
    amount_of_cycles_done = 0
    elapsed_time_current_cycle = 0
    total_elapsed_time = 0
    downtime = 0
    skipped_tests = 0

    # Update the labels
    completed_label.config(text=f"Färdiga: {amount_of_cycles_done}st")
    skipped_label.config(text=f"Antal Avvikande: {skipped_tests}st")