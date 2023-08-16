import os
import time
import fitz
from django import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from multiupload.fields import MultiFileField
from .models import MergedPDF


class MergePDFsForm(forms.Form):
    pdf_files = MultiFileField(min_num=1, max_num=settings.DATA_UPLOAD_MAX_NUMBER_FILES)


def merge_pdfs(request):
    if request.method == "POST":
        form = MergePDFsForm(request.POST, request.FILES)

        if form.is_valid():
            pdf_files = form.cleaned_data['pdf_files']
            merged_pdf_name = request.POST.get('merged_pdf_name', 'merged_pdf')  # Get the user-provided name
            start_time = time.time()
            merged_count = len(pdf_files)
            total_page_count = 0

            input_directory = os.path.join(settings.MEDIA_ROOT, "input_files")
            output_directory = os.path.join(settings.MEDIA_ROOT, "output_files")
            os.makedirs(input_directory, exist_ok=True)
            os.makedirs(output_directory, exist_ok=True)

            input_file_paths = []

            try:
                for idx, pdf_file in enumerate(pdf_files):
                    input_file_path = os.path.join(input_directory, f"input_{idx}.pdf")
                    with open(input_file_path, "wb") as f:
                        f.write(pdf_file.read())
                    input_file_paths.append(input_file_path)

                pdf_merger = fitz.open()

                try:
                    for input_file_path in input_file_paths:
                        try:
                            pdf_document = fitz.open(input_file_path)
                            total_pages = pdf_document.page_count
                            total_page_count += total_pages
                            pdf_merger.insert_pdf(pdf_document, from_page=0, to_page=total_pages - 1)
                            pdf_document.close()
                        except Exception as e:
                            print(f"Error processing file: {e}")

                    output_filename = f"{merged_pdf_name}_{int(time.time())}.pdf"
                    output_file_path = os.path.join(output_directory, output_filename)
                    pdf_merger.save(output_file_path, garbage=4, deflate=True)

                    # Save the merged PDF to the database
                    merged_pdf = MergedPDF(pdf_file=output_file_path, merged_name=merged_pdf_name)
                    merged_pdf.save()

                    # end_time = time.time()
                    # merge_time = end_time - start_time

                    # with open(output_file_path, "rb") as f:
                    #     merged_pdf_data = f.read()
                    #
                    # response = HttpResponse(merged_pdf_data, content_type="application/pdf")
                    # response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
                    #
                    # response["X-Merged-Count"] = str(merged_count)
                    # response["X-Total-Page-Count"] = str(total_page_count)
                    # response["X-Merge-Time"] = str(merge_time)

                    # return response


                finally:
                    pdf_merger.close()

            finally:
                # Clean up: Remove the input files
                for input_file_path in input_file_paths:
                    try:
                        os.remove(input_file_path)
                    except Exception as e:
                        print(f"Error removing input file: {e}")

        return redirect("get-pdfs")

    else:
        form = MergePDFsForm()

    return render(request, "upload.html", {"form": form})




def get_pdf(request):
    pdf_objects = MergedPDF.objects.all()
    return render(request, "pdf_list.html", {"pdf_objects": pdf_objects})



def download_merged_pdf(request):
    # Retrieve all MergedPDF objects from the database
    pdf_objects = MergedPDF.objects.all()

    if pdf_objects:
        start_time = time.time()
        total_page_count = 0

        output_directory = os.path.join(settings.MEDIA_ROOT, "output_files")
        os.makedirs(output_directory, exist_ok=True)

        try:
            pdf_merger = fitz.open()

            for pdf_obj in pdf_objects:
                try:
                    pdf_document = fitz.open(pdf_obj.pdf_file.path)
                    total_pages = pdf_document.page_count
                    total_page_count += total_pages
                    pdf_merger.insert_pdf(pdf_document, from_page=0, to_page=total_pages - 1)
                    pdf_document.close()
                except Exception as e:
                    print(f"Error processing file: {e}")

            output_filename = f"merged_all_{int(time.time())}.pdf"
            output_file_path = os.path.join(output_directory, output_filename)
            pdf_merger.save(output_file_path, garbage=4, deflate=True)

            end_time = time.time()
            merge_time = end_time - start_time

            with open(output_file_path, "rb") as f:
                merged_pdf_data = f.read()

            response = HttpResponse(merged_pdf_data, content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename="{output_filename}"'

            response["X-Total-Page-Count"] = str(total_page_count)
            response["X-Merge-Time"] = str(merge_time)

            return response

        finally:
            pdf_merger.close()

    else:
        return HttpResponse("No PDFs found in the database.")


def clearTable(request):
    obj = MergedPDF.objects.all().delete()
    return redirect('merge_pdfs')


