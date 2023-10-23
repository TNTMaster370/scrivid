# Changelog
Scrivid uses the [SemVer](https://semver.org) format for versioning. The project is currently in 
development (major version zero), so the API may change at any time without warning.

If Scrivid's public API is being used, there should be no issues with upgrading to the latest 
version. There is as of yet no deprecated functionality, so no policy is in place yet for it. When 
it is, it will be included here.

## 0.1.0

### Changes
- Added the following dependencies:
  - [PIL](https://github.com/python-pillow/Pillow) (Python Imaging Library), also referred to as Pillow;
  - [MoviePy](https://github.com/Zulko/moviepy);
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