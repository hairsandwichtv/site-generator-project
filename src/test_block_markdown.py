import unittest
from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    extract_title,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        self.assertEqual(
            markdown_to_blocks("# Just a heading"), ["# Just a heading"]
        )

    def test_excessive_newlines(self):
        md = """
# Heading



A paragraph



- list item
"""
        self.assertEqual(
            markdown_to_blocks(md), ["# Heading", "A paragraph", "- list item"]
        )

    def test_leading_and_trailing_whitespace(self):
        md = "   # Heading   \n\n   A paragraph   "
        self.assertEqual(markdown_to_blocks(md), ["# Heading", "A paragraph"])

    def test_empty_markdown(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_only_whitespace(self):
        self.assertEqual(markdown_to_blocks("\n\n   \n\n"), [])

    def test_multiline_block_preserved(self):
        md = "- one\n- two\n- three"
        self.assertEqual(markdown_to_blocks(md), ["- one\n- two\n- three"])

    def test_three_block_example(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        self.assertEqual(
            markdown_to_blocks(md),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )


if __name__ == "__main__":
    unittest.main()


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_one(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_heading_six(self):
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_seven_hashes_is_paragraph(self):
        self.assertEqual(block_to_block_type("####### Nope"), BlockType.PARAGRAPH)

    def test_hash_without_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("#NoSpace"), BlockType.PARAGRAPH)

    def test_code_block(self):
        self.assertEqual(
            block_to_block_type("```\nprint('hi')\n```"), BlockType.CODE
        )

    def test_code_block_empty(self):
        self.assertEqual(block_to_block_type("```\n```"), BlockType.CODE)

    def test_unclosed_code_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("```\nprint('hi')"), BlockType.PARAGRAPH
        )

    def test_quote_single_line(self):
        self.assertEqual(block_to_block_type("> a quote"), BlockType.QUOTE)

    def test_quote_multiline(self):
        self.assertEqual(
            block_to_block_type("> line one\n> line two\n> line three"),
            BlockType.QUOTE,
        )

    def test_quote_no_space_after_marker(self):
        self.assertEqual(block_to_block_type(">tight quote"), BlockType.QUOTE)

    def test_quote_partial_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("> line one\nline two"), BlockType.PARAGRAPH
        )

    def test_unordered_list(self):
        self.assertEqual(
            block_to_block_type("- one\n- two\n- three"), BlockType.UNORDERED_LIST
        )

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- only one"), BlockType.UNORDERED_LIST)

    def test_dash_without_space_is_paragraph(self):
        self.assertEqual(block_to_block_type("-nospace"), BlockType.PARAGRAPH)

    def test_unordered_list_partial_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("- one\ntwo"), BlockType.PARAGRAPH
        )

    def test_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. one\n2. two\n3. three"), BlockType.ORDERED_LIST
        )

    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_block_type("1. only one"), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_start_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("2. two\n3. three"), BlockType.PARAGRAPH
        )

    def test_ordered_list_skipped_number_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("1. one\n3. three"), BlockType.PARAGRAPH
        )

    def test_ordered_list_out_of_order_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("1. one\n3. three\n2. two"), BlockType.PARAGRAPH
        )

    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("Just a normal paragraph of text."),
            BlockType.PARAGRAPH,
        )

    def test_paragraph_multiline(self):
        self.assertEqual(
            block_to_block_type("First line\nsecond line"), BlockType.PARAGRAPH
        )


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_headings(self):
        md = """
# Heading one

### Heading three with **bold**

###### Heading six
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><h1>Heading one</h1><h3>Heading three with <b>bold</b></h3><h6>Heading six</h6></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> spanning two lines
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><blockquote>This is a quote spanning two lines</blockquote></div>",
        )

    def test_quote_with_inline(self):
        md = "> A quote with **bold** text"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><blockquote>A quote with <b>bold</b> text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- first item
- second with _italic_
- third
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ul><li>first item</li><li>second with <i>italic</i></li><li>third</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. first item
2. second with **bold**
3. third
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ol><li>first item</li><li>second with <b>bold</b></li><li>third</li></ol></div>",
        )

    def test_paragraph_with_link_and_image(self):
        md = "A [link](https://boot.dev) and an ![img](https://i.imgur.com/x.png)"
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            '<div><p>A <a href="https://boot.dev">link</a> and an <img src="https://i.imgur.com/x.png" alt="img"></img></p></div>',
        )

    def test_mixed_document(self):
        md = """
# Title

A paragraph with `code`.

- item one
- item two

> a quote
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><h1>Title</h1><p>A paragraph with <code>code</code>.</p><ul><li>item one</li><li>item two</li></ul><blockquote>a quote</blockquote></div>",
        )

    def test_empty_markdown(self):
        self.assertEqual(markdown_to_html_node("").to_html(), "<div></div>")

    def test_codeblock(self):
        nl = chr(10)
        fence = chr(96) * 3
        md = (
            nl + fence + nl
            + "This is text that _should_ remain" + nl
            + "the **same** even with inline stuff" + nl
            + fence + nl
        )
        expected = (
            "<div><pre><code>This is text that _should_ remain" + nl
            + "the **same** even with inline stuff" + nl
            + "</code></pre></div>"
        )
        self.assertEqual(markdown_to_html_node(md).to_html(), expected)


class TestExtractTitle(unittest.TestCase):
    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_whitespace(self):
        self.assertEqual(extract_title("#    Hello   "), "Hello")

    def test_title_in_document(self):
        md = "# Tolkien Fan Club\n\nSome paragraph text\n\n## A subheading"
        self.assertEqual(extract_title(md), "Tolkien Fan Club")

    def test_title_not_first_line(self):
        md = "Some intro text\n\n# The Real Title\n\nMore text"
        self.assertEqual(extract_title(md), "The Real Title")

    def test_ignores_h2(self):
        md = "## Not an h1\n\n# This one is"
        self.assertEqual(extract_title(md), "This one is")

    def test_no_title_raises(self):
        with self.assertRaises(ValueError):
            extract_title("## Only an h2\n\nSome text")

    def test_empty_markdown_raises(self):
        with self.assertRaises(ValueError):
            extract_title("")
