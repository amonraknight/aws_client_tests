from markitdown import MarkItDown


def parse_pdf_with_markitdown(pdf_path: str) -> str:
    """
    使用MarkItDown解析PDF文件并返回Markdown文本。

    :param pdf_path: PDF文件的路径
    :return: 解析后的Markdown文本
    """
    # 初始化MarkItDown解析器
    md = MarkItDown()

    # 解析PDF文件
    result = md.convert(pdf_path)

    return result.text_content
