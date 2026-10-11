import unittest
from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_bold(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_italic(self):
        node = TextNode("An _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("An ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delimiter_at_start(self):
        node = TextNode("**Bold** at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("Bold", TextType.BOLD),
                TextNode(" at the start", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delimiter_at_end(self):
        node = TextNode("Ends with **bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("Ends with ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_multiple_delimited_sections(self):
        node = TextNode("`one` and `two` and `three`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("one", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("three", TextType.CODE),
            ],
            new_nodes,
        )

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual([TextNode("Just plain text", TextType.TEXT)], new_nodes)

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual([TextNode("already bold", TextType.BOLD)], new_nodes)

    def test_mixed_node_list(self):
        nodes = [
            TextNode("A `code` bit", TextType.TEXT),
            TextNode("untouched", TextType.ITALIC),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("A ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" bit", TextType.TEXT),
                TextNode("untouched", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_chained_calls(self):
        node = TextNode("A **bold** and `code` mix", TextType.TEXT)
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("A ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" mix", TextType.TEXT),
            ],
            nodes,
        )

    def test_unclosed_delimiter(self):
        node = TextNode("This has an `unclosed delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_empty_node_list(self):
        self.assertListEqual([], split_nodes_delimiter([], "`", TextType.CODE))


if __name__ == "__main__":
    unittest.main()


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_links_ignores_images(self):
        text = "An ![image](https://i.imgur.com/x.png) and a [link](https://boot.dev)"
        self.assertListEqual(
            [("link", "https://boot.dev")], extract_markdown_links(text)
        )

    def test_images_ignores_links(self):
        text = "An ![image](https://i.imgur.com/x.png) and a [link](https://boot.dev)"
        self.assertListEqual(
            [("image", "https://i.imgur.com/x.png")], extract_markdown_images(text)
        )

    def test_no_images(self):
        self.assertListEqual([], extract_markdown_images("Just plain text"))

    def test_no_links(self):
        self.assertListEqual([], extract_markdown_links("Just plain text"))

    def test_empty_alt_text(self):
        self.assertListEqual(
            [("", "https://i.imgur.com/x.png")],
            extract_markdown_images("![](https://i.imgur.com/x.png)"),
        )

    def test_empty_anchor_text(self):
        self.assertListEqual(
            [("", "https://boot.dev")], extract_markdown_links("[](https://boot.dev)")
        )


class TestSplitImagesAndLinks(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode("![image](https://i.imgur.com/x.png)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("image", TextType.IMAGE, "https://i.imgur.com/x.png")],
            split_nodes_image([node]),
        )

    def test_split_image_at_start(self):
        node = TextNode(
            "![image](https://i.imgur.com/x.png) trailing text", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/x.png"),
                TextNode(" trailing text", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_link_at_end(self):
        node = TextNode("Go to [boot dev](https://www.boot.dev)", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("Go to ", TextType.TEXT),
                TextNode("boot dev", TextType.LINK, "https://www.boot.dev"),
            ],
            split_nodes_link([node]),
        )

    def test_split_images_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual(
            [TextNode("Just plain text", TextType.TEXT)], split_nodes_image([node])
        )

    def test_split_links_no_links(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual(
            [TextNode("Just plain text", TextType.TEXT)], split_nodes_link([node])
        )

    def test_split_image_non_text_node(self):
        node = TextNode("already bold", TextType.BOLD)
        self.assertListEqual(
            [TextNode("already bold", TextType.BOLD)], split_nodes_image([node])
        )

    def test_split_links_ignores_images(self):
        node = TextNode(
            "An ![image](https://i.imgur.com/x.png) and a [link](https://boot.dev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("An ![image](https://i.imgur.com/x.png) and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            split_nodes_link([node]),
        )

    def test_split_images_then_links(self):
        node = TextNode(
            "![pic](https://i.imgur.com/x.png) then [link](https://boot.dev)",
            TextType.TEXT,
        )
        nodes = split_nodes_image([node])
        nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("pic", TextType.IMAGE, "https://i.imgur.com/x.png"),
                TextNode(" then ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_split_adjacent_images(self):
        node = TextNode(
            "![one](https://a.png)![two](https://b.png)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("one", TextType.IMAGE, "https://a.png"),
                TextNode("two", TextType.IMAGE, "https://b.png"),
            ],
            split_nodes_image([node]),
        )

    def test_split_multiple_input_nodes(self):
        nodes = [
            TextNode("A ![pic](https://a.png) here", TextType.TEXT),
            TextNode("No images here", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("A ", TextType.TEXT),
                TextNode("pic", TextType.IMAGE, "https://a.png"),
                TextNode(" here", TextType.TEXT),
                TextNode("No images here", TextType.TEXT),
            ],
            split_nodes_image(nodes),
        )

    def test_split_empty_node_list(self):
        self.assertListEqual([], split_nodes_image([]))
        self.assertListEqual([], split_nodes_link([]))


class TestTextToTextNodes(unittest.TestCase):
    def test_all_types(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_plain_text(self):
        self.assertListEqual(
            [TextNode("Just plain text", TextType.TEXT)],
            text_to_textnodes("Just plain text"),
        )

    def test_bold_only(self):
        self.assertListEqual(
            [
                TextNode("A ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            text_to_textnodes("A **bold** word"),
        )

    def test_url_with_underscores(self):
        self.assertListEqual(
            [
                TextNode("See ", TextType.TEXT),
                TextNode("the docs", TextType.LINK, "https://boot.dev/some_long_path"),
            ],
            text_to_textnodes("See [the docs](https://boot.dev/some_long_path)"),
        )

    def test_multiple_same_type(self):
        self.assertListEqual(
            [
                TextNode("one", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.BOLD),
            ],
            text_to_textnodes("**one** and **two**"),
        )

    def test_empty_string(self):
        self.assertListEqual([], text_to_textnodes(""))

    def test_whole_string_is_bold(self):
        self.assertListEqual(
            [TextNode("everything", TextType.BOLD)],
            text_to_textnodes("**everything**"),
        )


if __name__ == "__main__":
    unittest.main()
