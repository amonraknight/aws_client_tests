import unittest
import json
from pydantic import BaseModel

from src.parsers.textract_response_parser import (
    parse_textract_response,
    transform_model_to_tree,
)


class test_textract_response_parser(unittest.TestCase):

    def test_parse_textract_response(self):
        with open(
            "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\textract_output_sample_invoice_sample_3 Project Customer Invoice.json",
            "r",
            encoding="utf-8",
        ) as json_file:
            response = json.load(json_file)
        # parse
        textract_response: BaseModel = parse_textract_response(response)
        # transform
        document = transform_model_to_tree(textract_response)
        print(document.model_dump_json())


if __name__ == "__main__":
    unittest.main()
