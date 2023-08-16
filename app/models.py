from django.db import models


class MergedPDF(models.Model):
    pdf_file = models.FileField(upload_to='merged_pdfs/')
    merged_name = models.CharField(max_length=255, blank=True, null=True)  # Optional field for the merged PDF name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.merged_name or self.pdf_file.name


