from src.parsers.textract_schemas import *
from src.parsers.target_schemas import *


def parse_textract_response(response: dict):
    """
    解析 Textract 响应
    """
    textract_response = TextractResponse(**response)
    return textract_response


def transform_model_to_tree(textract_response: TextractResponse) -> Document:
    """
    将 Textract 模型转换为树结构
    """
    document = Document()
    # 建立一个block字典以方便后续查找
    block_dict: dict[str, Block] = {
        block.Id: block for block in textract_response.Blocks
    }

    page_list = []

    # 遍历所有的page block。
    for each_page_block in textract_response.Blocks:
        if each_page_block.BlockType == "PAGE":
            page_list.append(_transform_from_page_block(each_page_block, block_dict))

    document.Pages = page_list
    return document


def _transform_from_page_block(block: Block, block_dict: dict[str, Block]) -> Page:
    # 将page类型的block转化为Page对象

    if block.BlockType != "PAGE":
        return None
    else:
        page = Page(PageIdx=block.Page if block.Page is not None else 1)

        # 遍历block中的所有孩子。
        item_list = []
        for each_relationship in block.Relationships:
            if each_relationship.Type == "CHILD":
                for each_child in each_relationship.Ids:
                    item = _transform_from_page_item_block(
                        block_dict[each_child], block_dict
                    )
                    if item:
                        item_list.append(item)

        page.Items = item_list
        return page


def _transform_from_page_item_block(
    block: Block, block_dict: dict[str, Block]
) -> GeneralItem:
    # 使用match语法根据BlockType返回不同的GeneralItem类型
    match block.BlockType:
        case "LINE":
            return _transform_line_block(block)

        case "TABLE":
            return _transform_table_block(block, block_dict)
        case "KEY_VALUE_SET":
            if "KEY" in block.EntityTypes:
                return _transform_key_value_set_blocks(block, block_dict)
            else:
                return None
        case _:
            # 忽略其他类型的block
            return None


def _transform_line_block(block: Block) -> IndependentLine:
    # 将line类型的block转化为IndependentLine对象
    line = IndependentLine(
        Text=block.Text if block.Text is not None else "", Geometry=block.Geometry
    )
    return line


def _transform_table_block(
    block: Block, block_dict: dict[str, Block]
) -> StructuredTable:
    # 将table类型的block转化为StructuredTable对象
    table = StructuredTable(Geometry=block.Geometry)

    title_id_list = []
    footer_id_list = []
    cell_id_list = []

    for each_relationship in block.Relationships:
        if each_relationship.Type == "TABLE_TITLE":
            title_id_list.extend(each_relationship.Ids)
        elif each_relationship.Type == "TABLE_FOOTER":
            footer_id_list.extend(each_relationship.Ids)
        elif each_relationship.Type == "CHILD":
            cell_id_list.extend(each_relationship.Ids)

    table.TableTitle = _collect_words_from_blocks(title_id_list, block_dict)
    table.TableFooter = _collect_words_from_blocks(footer_id_list, block_dict)

    # Cells
    table.Content = _allocate_table_cells(cell_id_list, block_dict)

    return table


def _collect_words_from_blocks(
    ids: List[str], block_dict: dict[str, Block]
) -> List[str]:
    # 为table title、footer、cell block收集文字
    words = []
    for each_id in ids:
        word_block: Block = block_dict[each_id]
        if word_block.BlockType == "WORD":
            words.append(word_block.Text)

    return " ".join(words)


def _transform_key_value_set_blocks(
    key_block: Block, block_dict: dict[str, Block]
) -> KeyValueSet:
    # 将key_value_set类型的block转化为KeyValueSet对象
    for each_relation in key_block.Relationships:
        if each_relation.Type == "VALUE":
            value_block_id = each_relation.Ids[0]
        elif each_relation.Type == "CHILD":
            key_children_ids = each_relation.Ids

    key = KeyOfKVSet(Geometry=key_block.Geometry)
    key.Text = _collect_words_from_blocks(key_children_ids, block_dict)

    value_block: Block = block_dict[value_block_id]
    value = ValueOfKVSet(Geometry=value_block.Geometry)

    if value_block.Relationships:
        for each_relation in value_block.Relationships:
            if each_relation.Type == "CHILD":
                value.Text = _collect_words_from_blocks(each_relation.Ids, block_dict)
                break

    key_value_set = KeyValueSet(Key=key, Value=value)

    return key_value_set


def _allocate_table_cells(
    cell_ids: list[str], block_dict: dict[str, Block]
) -> list[list[str]]:
    # 按照cell的height和width分配到对应的行和列

    cell_bocks = [block_dict[each_id] for each_id in cell_ids]

    max_column_idx = 0
    max_row_idx = 0

    for each_cell in cell_bocks:
        max_column_idx = max(max_column_idx, each_cell.RowIndex)
        max_row_idx = max(max_row_idx, each_cell.ColumnIndex)

    # 初始化表格
    rows = [[""] * (max_row_idx) for _ in range(max_column_idx)]

    
    for each_cell in cell_bocks:
        if each_cell.Relationships:
            children_ids = []
            for each_relationship in each_cell.Relationships:
                if each_relationship.Type == "CHILD":
                    children_ids.extend(each_relationship.Ids)
                    break

            rows[each_cell.RowIndex - 1][each_cell.ColumnIndex - 1] = _collect_words_from_blocks(
                children_ids, block_dict
            )

    return rows
