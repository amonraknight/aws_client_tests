import unittest

from src.parsers.mark_it_down import parse_pdf_with_markitdown


class test_markitdown_parser(unittest.TestCase):
    def test_anotate_a_pdf(self):
        pdf_path = "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\invoice_sample_1_Contractor Customer Invoice.pdf"
        markdown_text = parse_pdf_with_markitdown(pdf_path)
        print(markdown_text)


if __name__ == "__main__":
    unittest.main()
