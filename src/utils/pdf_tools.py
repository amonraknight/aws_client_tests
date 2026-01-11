import fitz
from PIL import Image
from io import BytesIO


def get_first_page_as_image(pdf_path: str) -> Image.Image:
    """
    获取 PDF 文件的第一页并将其转换为 PIL Image 对象
    
    Args:
        pdf_path: PDF 文件的路径
        
    Returns:
        PIL.Image.Image: PDF 第一页的图像对象
        
    Raises:
        FileNotFoundError: 如果 PDF 文件不存在
        Exception: 如果读取 PDF 文件失败
    """
    doc = fitz.open(pdf_path)
    try:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        image = Image.open(BytesIO(img_data))
        return image
    finally:
        doc.close()
