from src.parsers.textract_schemas import Textract_Response

def parse_textract_response(response: dict):
    """
    解析 Textract 响应
    """
    textract_response = Textract_Response(**response)
    return textract_response
