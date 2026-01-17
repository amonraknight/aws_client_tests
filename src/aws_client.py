import boto3

from dotenv import load_dotenv


class AwsClient:
    def __init__(self):
        load_dotenv()
        self._textract_client = boto3.client("textract")
        self._s3_client = boto3.client("s3")

    def analyze_doc(self, document_bytes: bytes, feature_types: list[str]=["TABLES", "FORMS"]) -> str:
        response = self._textract_client.analyze_document(
            Document={"Bytes": document_bytes},
            FeatureTypes=feature_types,
        )
        return response

    def get_file_from_s3(self, bucket: str, document: str) -> bytes:
        response = self._s3_client.get_object(Bucket=bucket, Key=document)
        return response['Body'].read()
