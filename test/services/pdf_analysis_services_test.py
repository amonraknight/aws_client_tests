import unittest
from dotenv import load_dotenv
from src.services.pdf_analysis_services import PDFAnalysisServices
import os

class pdf_analysis_services_test(unittest.TestCase):
    @unittest.skip("Skip test_anotate_a_pdf")
    def test_anotate_a_pdf(self):
        pdf_path = "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\mineru_input_sample_1.pdf"
        pdf_analysis_services = PDFAnalysisServices()
        pdf_analysis_services.anotate_a_pdf(pdf_path)

    def test_anotate_a_pdf_from_s3(self):
        bucket = os.getenv("AWS_BUCKET_NAME")
        document = "invoice_sample_1_Contractor Customer Invoice.pdf"
        pdf_analysis_services = PDFAnalysisServices()
        pdf_analysis_services.anotate_a_pdf_from_s3(bucket, document, "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\textract_s3_parse_invoice_sample_1_Contractor Customer Invoice.json")
        


if __name__ == '__main__':
    load_dotenv()
    unittest.main()