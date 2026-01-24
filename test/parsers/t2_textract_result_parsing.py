import unittest
import json
from pydantic import BaseModel

from src.parsers.textract_response_parser import parse_textract_response

class test_textract_response_parser(unittest.TestCase):
    def test_parse_textract_response(self):
        with open("E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\textract_output_sample_1.json", "r", encoding="utf-8") as json_file:
            response = json.load(json_file)
        textract_response: BaseModel = parse_textract_response(response)
        print(textract_response.model_dump_json())

if __name__ == "__main__":
    unittest.main()