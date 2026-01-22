import csv
import io
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Import, ImportItem, SupplierItem, CreditorItem, truncate, to_int, to_float
from .forms import ImportForm


@login_required()
def import_form(request):
    type = request.GET.get('type')
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            msg = "CSV file has been imported successfully!"
            msg_type = "success"
            cur = None
            try:
                # Create import record
                import_ref = Import.objects.create(
                    import_date=timezone.now().date(),
                    import_time=timezone.now().time(),
                    import_by=request.user,
                    import_type=type,
                    import_status='Processing'
                )
                
                # Read the CSV file with different encodings
                csv_file = request.FILES['csv_file']
                file_content = csv_file.read()
                
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                data_set = None
                
                for encoding in encodings:
                    try:
                        data_set = file_content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if data_set is None:
                    raise ValueError("Failed to decode the file. Please ensure the file is in a supported encoding (UTF-8, Latin-1, Windows-1252, or ISO-8859-1).")
                
                io_string = io.StringIO(data_set)
                
                # Skip header row
                next(io_string, None)
                
                # Process each row in the CSV
                for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                    cur = row
                    data = None
                    if type == 'D' and len(row) >= 18:  # Ensure we have enough columns
                        data = ImportItem.objects.create(
                            import_ref=import_ref,
                            barcode=row[0],
                            full_description=truncate(row[1], 250),
                            short_name=truncate(row[2], 50),
                            category=truncate(row[3], 50),
                            uom=truncate(row[4], 20),
                            reorder_point=to_int(row[5]),
                            ceiling_qty=to_int(row[6]),
                            srp=to_float(row[7]),
                            selling_price=to_float(row[8]),
                            wholesale_price=to_float(row[9]),
                            wholesale_qty=to_int(row[10]),
                            tax_type=truncate(row[11], 1),
                            is_prime_commodity=row[12].lower() == 'true',
                            is_consigned=row[13].lower() == 'true',
                            is_buyer_info_required=row[14].lower() == 'true',
                            other_info=truncate(row[15], 250),
                            suppliers=truncate(row[16], 250),
                            warehouse_qty=to_int(row[17]),
                            store_qty=to_int(row[18]) if len(row) > 18 else 0,
                        )
                    elif type == 'S' and len(row) >= 8:  # Ensure we have enough columns
                        data = SupplierItem.objects.create(
                            import_ref=import_ref,
                            supplier_name=row[0],
                            address=truncate(row[1], 250),
                            contact_person=truncate(row[2], 50),
                            contact_info=truncate(row[3], 20),
                            email=truncate(row[4], 250),
                            tax_type=truncate(row[5], 1),
                            tin=truncate(row[6], 20),
                            deducts_vat=row[7].lower() == 'true',
                        )
                    elif type == 'C' and len(row) >= 6:
                        data = CreditorItem.objects.create(
                            import_ref=import_ref,
                            creditor_type=row[0],
                            id_number=row[1],
                            name=row[2],
                            address=truncate(row[3], 250),
                            tin=truncate(row[4], 20),
                            credit_limit=to_float(row[5]),
                        )

                    if data:
                        data.do_import(request.user)
                
                # Update import status to completed
                import_ref.import_status = 'Completed'
                import_ref.save()

                messages.success(request, 'CSV file has been imported successfully!')
                
            except Exception as e:
                # If any error occurs, update the import status to Failed
                if 'import_ref' in locals():
                    import_ref.import_status = 'Failed'
                    import_ref.save()
                
                msg = "Error processing CSV file: " + str(e) + "\n" + str(cur)
                msg_type = "error"
                messages.error(request, msg)

            return render(request, 'import/form.html', {'msg': msg, 'msg_type': msg_type})
    else:
        form = ImportForm()
    
    return render(request, "import/form.html", {'form': form, 'type': request.GET.get('type')})
