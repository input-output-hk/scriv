"""Miscellanous helpers."""

from __future__ import annotations

import collections
import re
from typing import Dict, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def order_dict(
    d: Dict[Optional[K], T], keys: Sequence[Optional[K]]
) -> Dict[Optional[K], T]:
    """
    Produce an OrderedDict of `d`, but with the keys in `keys` order.

    Keys in `d` that don't appear in `keys` will be at the end in an
    undetermined order.
    """
    with_order = collections.OrderedDict()
    to_insert = set(d)
    for k in keys:
        if k not in to_insert:
            continue
        with_order[k] = d[k]
        to_insert.remove(k)

    for k in to_insert:
        with_order[k] = d[k]

    return with_order


def partition_lines(text: str, marker: str) -> Tuple[str, str, str]:
    """
    Split `text` by lines, similar to str.partition.

    The splitting line is the first line containing `marker`.

    """
    lines = text.splitlines(keepends=True)
    marker_pos = [i for i, line in enumerate(lines) if marker in line]
    if not marker_pos:
        return (text, "", "")
    pos = marker_pos[0]
    return (
        "".join(lines[:pos]),
        lines[pos],
        "".join(lines[pos + 1 :]),
    )


VERSION_REGEX = r"""(?ix)   # based on https://peps.python.org/pep-0440/
    \b                      # at a word boundary
    v?                      # maybe a leading "v"
    (\d+!)?                 # maybe a version epoch
    \d+(\.\d+)+             # the meat of the version number: N.N.N
    (?P<pre>
        [-._]?[a-z]+\.?\d*
    )?                      # maybe a pre-release: .beta3
    ([-._][a-z]+\d*)*       # maybe post and dev releases
    (\+\w[\w.]*\w)?         # maybe a local version
    \b
    """


class Version:
    """
    A version string that compares correctly.

    For example, "v1.2.3" and "1.2.3" are considered the same.

    """

    def __init__(self, vtext: str) -> None:
        """Create a smart version from a string version number."""
        self.vtext = vtext

    def __repr__(self):
        return f"<Version {self.vtext!r}>"

    def __str__(self):
        return self.vtext

    def __bool__(self):
        return bool(self.vtext)

    def __eq__(self, other):
        this = self.vtext
        if hasattr(other, "vtext"):
            that = other.vtext
        else:
            that = other
        return this.lstrip("v") == that.lstrip("v")

    def __hash__(self):
        return hash(self.vtext.lstrip("v"))

    @classmethod
    def from_text(cls, text: str) -> Optional[Version]:
        """Find a version number in a text string."""
        m = re.search(VERSION_REGEX, text)
        if m:
            return cls(m[0])
        return None

    def is_prerelease(self) -> bool:  # noqa: D400
        """Is this version number a pre-release?"""
        m = re.fullmatch(VERSION_REGEX, self.vtext)
        assert m  # the version must be a valid version
        return bool(m["pre"])
