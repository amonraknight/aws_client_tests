import unittest
from dotenv import load_dotenv
from src.aws_parser_client_async import AwsParserClientAsync
import os

class aws_parser_client_parser_unit_tests(unittest.TestCase):
    def test_init_loads_dotenv(self):
        
        role = os.getenv('AWS_TEXTRACT_ROLE_ARN')
        bucket = os.getenv('AWS_BUCKET_NAME')
        # document = "cross_page_table_sample_1.pdf"
        document = "invoice_sample_1_Contractor Customer Invoice.pdf"
        client = AwsParserClientAsync(role=role, bucket=bucket, document=document)
        client.CreateTopicandQueue()
        try:
            client.ProcessDocument("E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\textract_s3_parse_invoice_sample_1_Contractor Customer Invoice2.json")
        finally:
            client.DeleteTopicandQueue()

        

if __name__ == '__main__':
    load_dotenv()
    unittest.main()
    