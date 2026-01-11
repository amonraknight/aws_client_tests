import unittest
from src.services.pdf_analysis_services import PDFAnalysisServices

class pdf_analysis_services_test(unittest.TestCase):
    def test_anotate_a_pdf(self):
        pdf_path = "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\mineru_input_sample_1.pdf"
        pdf_analysis_services = PDFAnalysisServices()
        pdf_analysis_services.anotate_a_pdf(pdf_path)
        


if __name__ == '__main__':
    unittest.main()