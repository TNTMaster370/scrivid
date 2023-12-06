from samples import empty, figure_eight, image_drawing

from scrivid import (
    create_image_reference, dump, errors, motion_nodes, parse, walk
)

import textwrap

import pytest


# Alternative name for module to reduce typing
pytest_parametrize = pytest.mark.parametrize


def has_method(cls, method):
    if (n := getattr(cls, method, None)) and callable(n):
        return True
    else:
        return False


@pytest_parametrize("indent", [0, 2, 4, 8])
@pytest_parametrize("sample_module,expected_string_raw", [
    (empty, 
     textwrap.dedent(r"""
        MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}HideImage(id=
        'HIDDEN', time=0), {\b}{\i}{\i}Continue(length=1), {\b}{\i}{\i}MoveImag
        e(id='HIDDEN', time=1, duration=11), {\b}{\i}{\i}InvokePrevious(length=
        11), {\b}{\i}{\i}End()])
     """).replace("\n", "")),
    (figure_eight, 
     textwrap.dedent(r"""
        MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}Continue(leng
        th=6), {\b}{\i}{\i}MoveImage(id='BLOCK', time=6, duration=10), {\b}{\i}
        {\i}InvokePrevious(length=10), {\b}{\i}{\i}MoveImage(id='BLOCK', time=1
        6, duration=5), {\b}{\i}{\i}InvokePrevious(length=5), {\b}{\i}{\i}MoveI
        mage(id='BLOCK', time=21, duration=5), {\b}{\i}{\i}InvokePrevious(lengt
        h=10), {\b}{\i}{\i}MoveImage(id='BLOCK', time=26, duration=10), {\b}{\i
        }{\i}InvokePrevious(length=5), {\b}{\i}{\i}MoveImage(id='BLOCK', time=3
        6, duration=5), {\b}{\i}{\i}InvokePrevious(length=5), {\b}{\i}{\i}MoveI
        mage(id='BLOCK', time=41, duration=5), {\b}{\i}{\i}InvokePrevious(lengt
        h=5), {\b}{\i}{\i}End()])
     """).replace("\n", "")),
    (image_drawing, 
     textwrap.dedent(r"""
        MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}HideImage(id=
        'HIDDEN', time=0), {\b}{\i}{\i}Continue(length=20), {\b}{\i}{\i}ShowIma
        ge(id='HIDDEN', time=20), {\b}{\i}{\i}End()])
     """).replace("\n", ""))
])
def test_dump(indent, sample_module, expected_string_raw):
    expected = (
        expected_string_raw
        .replace(r"{\i}", " " * indent)
        .replace(r"{\b}", "\n" if indent else "")
    )

    instructions, _ = sample_module.data()
    motion_tree = parse(instructions)

    actual = dump(motion_tree, indent=indent)
    assert actual == expected


@pytest_parametrize("node_cls,attr", [
    (motion_nodes.Continue, "length"),
    (motion_nodes.HideImage, "id"),
    (motion_nodes.HideImage, "time"),
    (motion_nodes.InvokePrevious, "length"),
    (motion_nodes.MotionTree, "body"),
    (motion_nodes.MoveImage, "duration"),
    (motion_nodes.MoveImage, "id"),
    (motion_nodes.MoveImage, "time"),
    (motion_nodes.ShowImage, "id"),
    (motion_nodes.ShowImage, "time")
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
    (motion_nodes.MoveImage, "__eq__"),
    (motion_nodes.MoveImage, "__ge__"),
    (motion_nodes.MoveImage, "__gt__"),
    (motion_nodes.MoveImage, "__le__"),
    (motion_nodes.MoveImage, "__lt__"),
    (motion_nodes.MoveImage, "__ne__"),
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
    motion_nodes.Continue, motion_nodes.End, motion_nodes.HideImage,
    motion_nodes.InvokePrevious, motion_nodes.MotionTree,
    motion_nodes.MoveImage, motion_nodes.ShowImage, motion_nodes.Start
])
@pytest_parametrize("method", [
    "__init__", "__repr__", "__setattr__", "__delattr__", "__getstate__",
    "__setstate__"
])
def test_nodes_has_methods_required(node_cls, method):
    assert has_method(node_cls, method)


@pytest_parametrize("node_cls,args", [
    (motion_nodes.Continue, (0,)),
    (motion_nodes.End, ()),
    (motion_nodes.HideImage, (0, 0)),
    (motion_nodes.InvokePrevious, (0,)),
    (motion_nodes.MotionTree, ()),
    (motion_nodes.MoveImage, (0, 0, 0)),
    (motion_nodes.ShowImage, (0, 0)),
    (motion_nodes.Start, ())
])
def test_nodes_inheritance(node_cls, args):
    node = node_cls(*args)
    assert isinstance(node, motion_nodes.RootMotionTree)


@pytest_parametrize("sample_module", [empty, figure_eight, image_drawing])
def test_parse(sample_module):
    instructions, _ = sample_module.data()
    parse(instructions)


def test_parse_duplicate_id():
    references = (
        create_image_reference(0, ""),
        create_image_reference(0, "")
    )  # These two reference objects have the same ID field.
    with pytest.raises(errors.DuplicateIDError):
        parse(references)


@pytest_parametrize("sample_module,expected_node_order", [
    (empty, 
     [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.HideImage,
      motion_nodes.Continue, motion_nodes.MoveImage,
      motion_nodes.InvokePrevious, motion_nodes.End]),
    (figure_eight,
     [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.Continue,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious,
      motion_nodes.MoveImage, motion_nodes.InvokePrevious, motion_nodes.End]),
    (image_drawing, 
     [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.HideImage,
      motion_nodes.Continue, motion_nodes.ShowImage, motion_nodes.End])
])
def test_walk(sample_module, expected_node_order):
    instructions, _ = sample_module.data()
    motion_tree = parse(instructions)
    for actual, expected_node in zip(walk(motion_tree), expected_node_order):
        actual_node = type(actual)
        assert actual_node is expected_node
