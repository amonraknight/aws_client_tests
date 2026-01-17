from src.aws_client import AwsClient
from src.utils.pdf_tools import get_first_page_as_image
from PIL import ImageDraw
import json
import os
import fitz
from io import BytesIO
import io


def ShowBoundingBox(draw, box, width, height, boxColor):

    left = width * box["Left"]
    top = height * box["Top"]
    draw.rectangle(
        [left, top, left + (width * box["Width"]), top + (height * box["Height"])],
        outline=boxColor,
    )


def ShowSelectedElement(draw, box, width, height, boxColor):

    left = width * box["Left"]
    top = height * box["Top"]
    draw.rectangle(
        [left, top, left + (width * box["Width"]), top + (height * box["Height"])],
        fill=boxColor,
    )


class PDFAnalysisServices:
    def __init__(self):
        self.aws_client = AwsClient()

    def anotate_a_pdf(self, pdf_path: str):
        """
        Annotate a PDF file using AWS Textract. Only annotate the first page.
        Args:
            pdf_path (str): The path to the PDF file to be annotated.
        """
        doc = fitz.open(pdf_path)
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=0, to_page=0)
            output = BytesIO()
            new_doc.save(output)
            document_bytes = output.getvalue()
        finally:
            doc.close()
            new_doc.close()
        response = self.aws_client.analyze_doc(document_bytes)

        json_path = os.path.splitext(pdf_path)[0] + ".json"
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, indent=2, ensure_ascii=False)

        image = get_first_page_as_image(pdf_path)

        blocks = response["Blocks"]
        width, height = image.size
        print("Detected Document Text")

        for block in blocks:
            draw = ImageDraw.Draw(image)

            # Draw bounding boxes for different detected response objects
            if block["BlockType"] == "KEY_VALUE_SET":
                if block["EntityTypes"][0] == "KEY":
                    ShowBoundingBox(
                        draw, block["Geometry"]["BoundingBox"], width, height, "red"
                    )
                else:
                    ShowBoundingBox(
                        draw, block["Geometry"]["BoundingBox"], width, height, "green"
                    )
            if block["BlockType"] == "TABLE":
                ShowBoundingBox(
                    draw, block["Geometry"]["BoundingBox"], width, height, "blue"
                )
            if block["BlockType"] == "CELL":
                ShowBoundingBox(
                    draw, block["Geometry"]["BoundingBox"], width, height, "yellow"
                )
            if block["BlockType"] == "SELECTION_ELEMENT":
                if block["SelectionStatus"] == "SELECTED":
                    ShowSelectedElement(
                        draw, block["Geometry"]["BoundingBox"], width, height, "blue"
                    )

        png_path = os.path.splitext(pdf_path)[0] + ".png"
        image.save(png_path)
        image.show()
        

    def anotate_a_pdf_from_s3(self, bucket: str, document: str, save_local_path: str = None):
        """
        Annotate a PDF file from S3 using AWS Textract. Only annotate the first page.
        Args:
            bucket (str): The name of the S3 bucket.
            document (str): The name of the PDF file in the S3 bucket.
        """
        stream = self.aws_client.get_file_from_s3(bucket, document)
        stream = io.BytesIO(stream)
        image_binary = stream.getvalue()
        response = self.aws_client.analyze_doc(document_bytes=image_binary, feature_types=["TABLES", "FORMS"])
        if save_local_path:
            with open(save_local_path, "w", encoding="utf-8") as json_file:
                json.dump(response, json_file, indent=2, ensure_ascii=False)