from scrivid import dump, HideAdjustment, image_reference, motion_nodes, parse, ShowAdjustment, walk


# Global variables for characters, for use for long string for testing the
# 'dump' function.
nl = "\n"
sp = " "


def create_references():
    return [
        image_reference("1"),
        image_reference("2"),
        image_reference("3")
    ]


def parse_references():
    return parse(create_references())


def parse_references_with_adjustments():
    references = create_references()
    for index, reference in enumerate(references):
        ShowAdjustment(2 * (index+1)) >> reference
        HideAdjustment(4 * (index+1)) >> reference
    return parse(references)


def test_dump_empty():
    expected = "MotionTree(body=[Start(), End()])"
    string = dump(parse([]))
    assert string == expected


def test_dump_filled():
    expected = "MotionTree(body=[Start(), End()])"
    string = dump(parse_references())  # This set of references does not
    # automatically fill out the motion tree, since there's no adjustments
    # relating to it.
    assert string == expected


def test_dump_filled_adjustments():
    expected = "MotionTree(body=[Start(), Continue(length=2), ShowImage(index=2), Continue(length=2), HideImage(index" \
               "=4), ShowImage(index=4), Continue(length=2), ShowImage(index=6), Continue(length=2), HideImage(index=" \
               "8), Continue(length=4), HideImage(index=12), End()])"
    string = dump(parse_references_with_adjustments())
    assert string == expected


def test_dump_indent_empty():
    expected = f"MotionTree({nl}{4*sp}body=[{nl}{8*sp}Start(), {nl}{8*sp}End()])"
    string = dump(parse([]), indent=4)
    assert string == expected

    expected = f"MotionTree({nl}{8*sp}body=[{nl}{16*sp}Start(), {nl}{16*sp}End()])"
    string = dump(parse([]), indent=8)
    assert string == expected


def test_dump_indent_filled_adjustments():
    expected = f"MotionTree({nl}{4*sp}body=[{nl}{8*sp}Start(), {nl}{8*sp}Continue(length=2), {nl}{8*sp}ShowImage(inde" \
               f"x=2), {nl}{8*sp}Continue(length=2), {nl}{8*sp}HideImage(index=4), {nl}{8*sp}ShowImage(index=4), {nl}" \
               f"{8*sp}Continue(length=2), {nl}{8*sp}ShowImage(index=6), {nl}{8*sp}Continue(length=2), {nl}{8*sp}Hide" \
               f"Image(index=8), {nl}{8*sp}Continue(length=4), {nl}{8*sp}HideImage(index=12), {nl}{8*sp}End()])"
    string = dump(parse_references_with_adjustments(), indent=4)
    assert string == expected

    expected = f"MotionTree({nl}{8*sp}body=[{nl}{16*sp}Start(), {nl}{16*sp}Continue(length=2), {nl}{16*sp}ShowImage(i" \
               f"ndex=2), {nl}{16*sp}Continue(length=2), {nl}{16*sp}HideImage(index=4), {nl}{16*sp}ShowImage(index=4)" \
               f", {nl}{16*sp}Continue(length=2), {nl}{16*sp}ShowImage(index=6), {nl}{16*sp}Continue(length=2), {nl}" \
               f"{16*sp}HideImage(index=8), {nl}{16*sp}Continue(length=4), {nl}{16*sp}HideImage(index=12), {nl}" \
               f"{16*sp}End()])"
    string = dump(parse_references_with_adjustments(), indent=8)
    assert string == expected


def test_parse_empty():
    _ = parse([])  # Should raise no exception.


def test_parse_filled():
    _ = parse_references()  # Should raise no exception.


# `test_parse_filled_adjustments` would be the exact same to `test_parse_filled`, so it is excluded.


def test_walk_empty():
    expected_node_order = [motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.End]
    motion_tree = parse_references()
    for actual, expected_node in zip(walk(motion_tree), expected_node_order):
        actual_node = type(actual)
        assert actual_node is expected_node


# `test_walk_filled` would be the exact same to `test_walk_empty`, so it is excluded.


def test_walk_filled_adjustments():
    expected_node_order = [
        motion_nodes.MotionTree, motion_nodes.Start, motion_nodes.Continue, motion_nodes.ShowImage,
        motion_nodes.Continue, motion_nodes.HideImage, motion_nodes.ShowImage, motion_nodes.Continue,
        motion_nodes.ShowImage, motion_nodes.Continue, motion_nodes.HideImage, motion_nodes.Continue,
        motion_nodes.HideImage, motion_nodes.End
    ]
    motion_tree = parse_references_with_adjustments()
    for actual, expected_node in zip(walk(motion_tree), expected_node_order):
        actual_node = type(actual)
        assert actual_node is expected_node
