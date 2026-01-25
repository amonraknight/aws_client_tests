import unittest
from dotenv import load_dotenv
from src.aws_parser_client_async import AwsParserClientAsync
import os

class aws_parser_client_parser_unit_tests(unittest.TestCase):

    def test_parse_mutiple_files(self):

        files = [
            ["virtual hospital bill 1 JS.pdf", "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\virtual hospital bill 1 JS.json"],
            ["virtual hospital bill 2 AZ.pdf", "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\virtual hospital bill 2 AZ.json"],
            ["virtual hospital bill 3 SQ.pdf", "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\virtual hospital bill 3 SQ.json"]
        ]

        role = os.getenv('AWS_TEXTRACT_ROLE_ARN')
        bucket = os.getenv('AWS_BUCKET_NAME')
        # document = "invoice_sample_1_Contractor Customer Invoice.pdf"
        client = AwsParserClientAsync(role=role, bucket=bucket)
        client.CreateTopicandQueue()
        try:
            for each_file in files:
                client.ProcessDocument(each_file[0], each_file[1])
        finally:
            client.DeleteTopicandQueue()

if __name__ == '__main__':
    load_dotenv()
    unittest.main()
    