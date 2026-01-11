import boto3

from dotenv import load_dotenv


class AwsClient:
    def __init__(self):
        load_dotenv()
        self._textract_client = boto3.client("textract")

    def analyze_doc(self, document_bytes: bytes, feature_types: list[str]=["TABLES", "FORMS"]) -> str:
        response = self._textract_client.analyze_document(
            Document={"Bytes": document_bytes},
            FeatureTypes=feature_types,
        )
        return response
