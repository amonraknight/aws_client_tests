import unittest
import json
from pydantic import BaseModel

from src.parsers.textract_response_parser import (
    parse_textract_response,
    transform_model_to_tree,
)


class test_textract_response_parser(unittest.TestCase):

    def test_parse_textract_response(self):
        source_json = "E:\\development\\GitRepository\\notes\\markdown_notes\\resources\\virtual hospital bill 1 JS.json"
        with open(
            source_json,
            "r",
            encoding="utf-8",
        ) as json_file:
            response = json.load(json_file)
        # parse
        textract_response: BaseModel = parse_textract_response(response)
        # transform
        document = transform_model_to_tree(textract_response)

        target_json = source_json.replace(".json", "_tree.json")

        with open(
            target_json,
            "w",
            encoding="utf-8",
        ) as json_file:
            json.dump(document.model_dump(), json_file, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    unittest.main()
