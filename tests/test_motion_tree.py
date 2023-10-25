from scrivid import dump, errors, HideAdjustment, image_reference, motion_nodes, parse, ShowAdjustment, walk

import pytest


# Alternative name for module to reduce typing
pytest_parametrize = pytest.mark.parametrize


def create_references():
    return [
        image_reference(1, "1"),
        image_reference(2, "2"),
        image_reference(3, "3")
    ]


def has_method(cls, method):
    if (n := getattr(cls, method, None)) and callable(n):
        return True
    else:
        return False


def parse_empty():
    return parse([])


def parse_references():
    return parse(create_references())


def parse_references_with_adjustments():
    references = create_references()
    for index, reference in enumerate(references):
        ShowAdjustment(2 * (index+1)) >> reference
        HideAdjustment(4 * (index+1)) >> reference
    return parse(references)


@pytest_parametrize("indent", [0, 2, 4, 8])
@pytest_parametrize("reference_callable,expected_string_raw", [
    (parse_empty, "MotionTree({\\n}{\\i}body=[{\\n}{\\i}{\\i}Start(), {\\n}{\\i}{\\i}End()])"),
    (parse_references, "MotionTree({\\n}{\\i}body=[{\\n}{\\i}{\\i}Start(), {\\n}{\\i}{\\i}End()])"),
    (parse_references_with_adjustments,
     "MotionTree({\\n}{\\i}body=[{\\n}{\\i}{\\i}Start(), {\\n}{\\i}{\\i}Continue(length=2), {\\n}{\\i}{\\i}ShowImage(in"
     "dex=2), {\\n}{\\i}{\\i}Continue(length=2), {\\n}{\\i}{\\i}HideImage(index=4), {\\n}{\\i}{\\i}ShowImage(index=4), "
     "{\\n}{\\i}{\\i}Continue(length=2), {\\n}{\\i}{\\i}ShowImage(index=6), {\\n}{\\i}{\\i}Continue(length=2), {\\n}{\\"
     "i}{\\i}HideImage(index=8), {\\n}{\\i}{\\i}Continue(length=4), {\\n}{\\i}{\\i}HideImage(index=12), {\\n}{\\i}{\\i}"
     "End()])")
])
def test_dump(indent, reference_callable, expected_string_raw):
    expected = (
        expected_string_raw
        .replace("{\\i}", " " * indent)
        .replace("{\\n}", "\n" if indent else "")
    )
    actual = dump(reference_callable(), indent=indent)
    assert actual == expected


@pytest_parametrize("node_cls,attr", [
    (motion_nodes.Continue, "length"),
    (motion_nodes.HideImage, "index"),
    (motion_nodes.MotionTree, "body"),
    (motion_nodes.ShowImage, "index")
])
def test_nodes_has_attributes(node_cls, attr):
    assert hasattr(node_cls, attr)


@pytest_parametrize("node_cls,method", [
    (motion_nodes.HideImage, "__eq__"),
    (motion_nodes.HideImage, "__ge__"),
    (motion_nodes.HideImage, "__gt__"),
    (motion_nodes.HideImage, "__le__"),
    (motion_nodes.HideImage, "__lt__"),
    (motion_nodes.HideImage, "__ne__"),
    (motion_nodes.MotionTree, "convert_to_string"),
    (motion_nodes.ShowImage, "__eq__"),
    (motion_nodes.ShowImage, "__ge__"),
    (motion_nodes.ShowImage, "__gt__"),
    (motion_nodes.ShowImage, "__le__"),
    (motion_nodes.ShowImage, "__lt__"),
    (motion_nodes.ShowImage, "__ne__"),
])
def test_nodes_has_methods_additional(node_cls, method):
    # This test function accounts for motion_node classes that are not
    # accounted for regarding the matrix strategy in
    # `test_nodes_has_methods_required`.
    assert has_method(node_cls, method)


@pytest_parametrize("node_cls", [
    motion_nodes.Continue, motion_nodes.End, motion_nodes.HideImage, motion_nodes.MotionTree, motion_nodes.ShowImage,
    motion_nodes.Start
])
@pytest_parametrize("method", ["__init__", "__repr__", "__setattr__", "__delattr__", "__getstate__", "__setstate__"])
def test_nodes_has_methods_required(node_cls, method):
    assert has_method(node_cls, method)


@pytest_parametrize("node_cls,args", [
    (motion_nodes.Continue, (0,)),
    (motion_nodes.End, ()),
    (motion_nodes.HideImage, (0,)),
    (motion_nodes.MotionTree, ()),
    (motion_nodes.ShowImage, (0,)),
    (motion_nodes.Start, ())
])
def test_nodes_inheritance(node_cls, args):
    node = node_cls(*args)
    assert isinstance(node, motion_nodes.RootMotionTree)


@pytest_parametrize("parsing_callable", [parse_empty, parse_references, parse_references_with_adjustments])
def test_parse(parsing_callable):
    parsing_callable()  # This should not raise an exception.


def test_parse_duplicate_id():
    references = (
        image_reference(0, ""),
        image_reference(0, "")
    )  # These two reference objects have the same ID field.
    with pytest.raises(errors.DuplicateIDError):
        parse(references)


@pytest_parametrize("parsing_callable,expected_node_order", [
    (parse_empty, [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.End]),
    (parse_references, [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.End]),
    (parse_references_with_adjustments,
     [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.Continue, motion_nodes.ShowImage, motion_nodes.Continue,
      motion_nodes.HideImage, motion_nodes.ShowImage, motion_nodes.Continue, motion_nodes.ShowImage,
      motion_nodes.Continue, motion_nodes.HideImage, motion_nodes.Continue, motion_nodes.HideImage, motion_nodes.End])
])
def test_walk(parsing_callable, expected_node_order):
    motion_tree = parsing_callable()
    for actual, expected_node in zip(walk(motion_tree), expected_node_order):
        actual_node = type(actual)
        assert actual_node is expected_node
