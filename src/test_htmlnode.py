import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(
            "a",
            "Click me",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(), ' href="https://www.google.com" target="_blank"'
        )

    def test_props_to_html_single(self):
        node = HTMLNode("a", "Click me", None, {"href": "https://www.boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://www.boot.dev"')

    def test_props_to_html_none(self):
        node = HTMLNode("p", "Just a paragraph")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty(self):
        node = HTMLNode("p", "Just a paragraph", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_defaults(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_to_html_raises(self):
        node = HTMLNode("p", "Hello")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode("p", "Hello", None, {"class": "greeting"})
        self.assertEqual(repr(node), "HTMLNode(p, Hello, None, {'class': 'greeting'})")


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just raw text")
        self.assertEqual(node.to_html(), "Just raw text")

    def test_leaf_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_multiple_props(self):
        node = LeafNode("a", "Link", {"href": "https://boot.dev", "target": "_blank"})
        self.assertEqual(
            node.to_html(), '<a href="https://boot.dev" target="_blank">Link</a>'
        )

    def test_leaf_repr(self):
        node = LeafNode("p", "Hello")
        self.assertEqual(repr(node), "LeafNode(p, Hello, None)")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_many_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(), '<div class="container"><span>child</span></div>'
        )

    def test_to_html_deeply_nested(self):
        node = ParentNode(
            "html",
            [
                ParentNode(
                    "body",
                    [
                        ParentNode(
                            "div",
                            [LeafNode("p", "deep")],
                        )
                    ],
                )
            ],
        )
        self.assertEqual(
            node.to_html(), "<html><body><div><p>deep</p></div></body></html>"
        )

    def test_to_html_mixed_children(self):
        node = ParentNode(
            "div",
            [
                LeafNode("h1", "Title"),
                ParentNode("p", [LeafNode("b", "Bold"), LeafNode(None, " and plain")]),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><h1>Title</h1><p><b>Bold</b> and plain</p></div>",
        )

    def test_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("span", "child")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_empty_children(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_parent_repr(self):
        child = LeafNode("span", "child")
        node = ParentNode("div", [child])
        self.assertEqual(repr(node), "ParentNode(div, [LeafNode(span, child, None)], None)")


if __name__ == "__main__":
    unittest.main()
