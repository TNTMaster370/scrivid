# Changelog
Scrivid uses the [SemVer](https://semver.org) format for versioning. The project is currently in 
development (major version zero), so the API may change at any time without warning.

If Scrivid's public API is being used, there should be no issues with upgrading to the latest 
version. There is as of yet no deprecated functionality, so no policy is in place yet for it. When 
it is, it will be included here.

## 0.3.0

This version is in development.

### New Features
- Added the `abc` module, for all abstract base classes that outline how
  classes used by Scrivid should be structured, and the 'contract' for how it
  will be used. This includes:
  - `Adjustment`, replacing `_file_objects.RootAdjustment`; and
  - `Qualm`, for objects from the `qualms` module (see below).
- Added the `qualms` module, for flags as to possible incorrect behaviour. All
  qualm objects are expected to inherit from `abc.Qualm`, and follow its
  outline.
  - Added `DrawingConfliction`, for when two images on the same layer have an
    overlap between them.
  - Added `OutOfRange`, for when an image is partially or completely out of 
    range of the canvas.
- Added the following exceptions to the `errors` module:
  - `InternalErrorFromFFMPEG`, which is equivalent to `InternalError`, but is
    specific to ffmpeg.
- `Metadata` now has a `_validate` method, which is called internally when the
  metadata needs to be used, to ensure that the data being passed in is
  acceptable.

### Changes
- `errors.InternalError` now wraps the respective error that was raised 
  internally.
- All parts of the `_motion_tree` module, including parts that were unpacked 
  into the general namespace, are now wrapped into a public-facing module
  `motion_tree`. This includes:
  - `scrivid.dump`, now `scrivid.motion_tree.dump`;
  - `scrivid.parse`, now `scrivid.motion_tree.parse`;
  - `scrivid.walk`, now `scrivid.motion_tree.walk`; and
  - `scrivid.motion_nodes.<Nodes>`, unpacked into `scrivid.motion_tree.<Nodes>`.

### Removed
- `_file_objects.RootAdjustment` has been replaced by `abc.Adjustment`.
- Removed the `fps` parameter from the constructor or `Metadata`. Use the
  `frame_rate` parameter instead.


## 0.2.0

### New Features
- Added `MoveAdjustment`, a subclass of `RootAdjustment` that handles movement over time, not exclusive to visibility.
- Added an `ID` required field to `ImageReference`, used for unique identification.
- Relevant to the `Adjustment` hierarchy:
  - Added an `ID` required field, used to point to the relevant Reference object; and
  - Added a hidden method `_enact()`, used internally to get the specific instructions for the change (in the form of a `Properties` object).
- Added an `ID` field to `HideImage` and `ShowImage` of the `_motion_tree.nodes` module to match the `ID` field of the respective adjustment object.
- Relevant to `Properties`:
  - Added a new attribute `visibility`, used to signal whether the Reference is being drawn or not.
  - Added a method `merge()`, to create a new object by merging its own attributes with another `Properties` object.
    - Includes a `mode` parameter, which can be used to specify how it's merged. You can merge via either replacement (overwrites the attribute if there's a confliction) or appending (adds both attributes if compatible and specified). Takes in a `_MergeMode` object, detailed below.
  - Added a class attribute `MERGE_MODE`, which houses an enum class called `_MergeMode`. Specified like this for clarity.
- Added the following exceptions to the `errors` module:
  - `ConflictingAttributesError`, for when multiple attributes conflict with each other.
  - `InternalError`, for when something goes wrong internally.

### Changes
- Changed the first parameter of `compile_video()` to be called `instructions` instead of `references`. Now, it can be a list of both reference object and adjustments, instead of just references.
- Renamed the factory function for `ImageReference`s, from `image_reference()` to `create_image_reference()`.
- Updated `RootAdjustment` to behave as an abstract base class.
- Relevant to `Properties`:
  - Changed the sentinel value that the `Properties` class uses to indicate that an attribute was excluded, to no longer be 'protected' and possible to use externally; and
  - Renamed the factory function from `properties()` to `define_properties()`.
- Changed `VisibilityStatus` from the `_file_objects` module to be accessible externally.
- Replaced the depency [MoviePy](https://github.com/Zulko/moviepy) with pure ffmpeg, through the [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) package.

### Removed
- Relevant to `ImageReference`:
  - Removed the `adjustments` field. Now, relevant adjustments must refer to the Reference object by matching with its `ID` field, instead of being contained inside of the class itself; and,
  - Removed support for the 'bit shift' operators. This was appending to the `adjustment` fields under the hood, and it was also unintuitive.
- Relevant to the `Adjustments` hierarchy:
  - Removed support for the 'bit shift' operators.

### Bug Fixes
- Fixed a bug that prevented members of the `Adjustment` hierarchy from comparing correctly (53182ce84653157557051f745d223f242f3e897a)

## 0.1.0

### New Features
- Added the following dependencies:
  - [PIL](https://github.com/python-pillow/Pillow) (Python Imaging Library), also referred to as Pillow;
  - MoviePy;
  - [attrs](https://github.com/python-attrs/attrs); and,
  - [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers).
- Added the internal '._file_objects' module. This module contains a series of classes and functions that are meant to 
  house the objects that are for the scrivid-generated video.
  - Added `ImageReference`, a wrapper for an image and its properties. Can be created by:
    - a factory function `image_reference()`; or, 
    - by directly instantiating it, `ImageReference()`.
  - Added `Properties`, a class for a `Reference` object's properties. Can be created by:
    - a factory function `properties()`; or, 
    - by directly instantiating it, `Properties()`.
  - Added `FileReference`, a wrapper that handles the reading of a file object.
    - Currently includes a subclass `ImageFileReference` that is meant to be used in `ImageReference`.
  - Added `RootAdjustment`, the root class for the `Adjustment` class hierarchy.
    - Added `HideAdjustment`, to signal hiding an object.
    - Added `ShowAdjustment`, to signal showing an object.
- Added the internal '._motion_tree' module. This module has the structure for a tree-like constructor, similar to an 
  abstract syntax tree. This structure, however, is more like a list of instructions. This is meant to be used 
  internally, but can be access externally.
  - Added three functions to manage the motion_tree:
    - `dump()`, which returns a string representation of the tree. Has a keyword-parameter, 'indent', which allows for 
      the string to be formatted as pretty-printed, with an indentation level equal to 'indent'. Default is zero, which 
      will not pretty-print it;
    - `parse()`, which converts a list of `Reference` objects into a 'motion_tree' object; and,
    - `walk()`, which is a generator that goes through the tree in a recursive manner.
  - And there is also a module object that houses all of the nodes that are used. This is mostly to allow unit tests to 
    import the nodes, but I also suspect that this can be used for debugging.
- Added the internal '._utils'. This is for internal functions that help the code structure. These functions cannot be 
  used externally, since that defeats the purpose of it.
- Added a hierarchy of exceptions, which can be access from a module object 'errors'.
  - All exceptions that are used within *scrivid* inherit from `ScrividException`, which itself inherits from Python's 
    built-in `Exception`.
- Added a class for handling scrivid-generated video metadata: `Metadata()`.
- Added a function that compiles the scrivid-generated video: `compile_video()`.

## 0.0.0
- Created repository.