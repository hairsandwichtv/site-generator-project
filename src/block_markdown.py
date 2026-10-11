import re
from enum import Enum

from htmlnode import ParentNode
from inline_markdown import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    raw_blocks = markdown.split("\n\n")
    blocks = []
    for raw_block in raw_blocks:
        block = raw_block.strip()
        if block == "":
            continue
        blocks.append(block)
    return blocks


def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```") and len(block) >= 6:
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(line.startswith(f"{i + 1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def heading_to_html_node(block):
    level = 0
    while level < len(block) and block[level] == "#":
        level += 1
    text = block[level + 1 :]
    return ParentNode(f"h{level}", text_to_children(text))


def code_to_html_node(block):
    text = block[3:-3]
    if text.startswith("\n"):
        text = text[1:]
    code_child = text_node_to_html_node(TextNode(text, TextType.TEXT))
    return ParentNode("pre", [ParentNode("code", [code_child])])


def quote_to_html_node(block):
    lines = [line.lstrip(">").strip() for line in block.split("\n")]
    return ParentNode("blockquote", text_to_children(" ".join(lines)))


def ulist_to_html_node(block):
    items = [
        ParentNode("li", text_to_children(line[2:])) for line in block.split("\n")
    ]
    return ParentNode("ul", items)


def olist_to_html_node(block):
    items = []
    for i, line in enumerate(block.split("\n")):
        prefix_len = len(f"{i + 1}. ")
        items.append(ParentNode("li", text_to_children(line[prefix_len:])))
    return ParentNode("ol", items)


def paragraph_to_html_node(block):
    text = " ".join(block.split("\n"))
    return ParentNode("p", text_to_children(text))


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return ulist_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return olist_to_html_node(block)
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case _:
            raise ValueError(f"invalid block type: {block_type}")


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = [block_to_html_node(block) for block in blocks]
    return ParentNode("div", children)


def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("no h1 header found in markdown")
