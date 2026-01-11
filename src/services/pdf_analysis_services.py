from src.aws_client import AwsClient
from src.utils.pdf_tools import get_first_page_as_image
from PIL import ImageDraw
import json
import os


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
        Annotate a PDF file using AWS Textract.
        Args:
            pdf_path (str): The path to the PDF file to be annotated.
        """
        with open(pdf_path, "rb") as pdf_file:
            document_bytes = pdf_file.read()
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
        

