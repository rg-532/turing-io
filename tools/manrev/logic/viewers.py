"""Implements viewer classes and tempfile utilities for viewing schemas of golden files (see :class:`Viewer`).
"""
import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

from tabulate import tabulate

from compiler_tests.utils.files import GoldenFileSchema, TokenFileSchema

type _T_NamedTemporaryFile = tempfile._TemporaryFileWrapper


class SchemaTypeNotSupportedError(ValueError):
    """Raised when a schema's viewing logic has not yet been implemented, based on its type.
    """
    pass


class Viewer[T_Schema: GoldenFileSchema](ABC):
    """Base class which provides logic for viewing some :class:`GoldenFileSchema` contents within a temporary file.

    This class mandates implementation of two abstract methods in its subclasses:
        - :func:`_write_schema` Writes the schema into the temporary file's handle.
        - :func:`_view_core`    Shows the contents of the file (for example, using ``subprocess``).

    This class offers the :func:`view` method which wraps the aforementioned abstract methods and is used to view
    the file.

    :ivar schema:  Schema to write and show.
    """
    def __init__(self, schema: T_Schema) -> None:
        self.schema = schema

    @abstractmethod
    def _write_schema(self, tmp: _T_NamedTemporaryFile) -> None:
        """Writes ``self.schema`` into the temporary file given as a file handler ``tmp``.
        """
        ...

    @abstractmethod
    def _view_core(self, tmp: _T_NamedTemporaryFile) -> None:
        """Core method of showing the temporary file given as a file handler ``tmp``.
        """
        ...

    def view(self, tmp: _T_NamedTemporaryFile) -> None:
        """Template - Writes ``schema`` to ``tmp`` and then views it in read-only mode.

        :param tmp:     File handler given by NamedTemporaryFile.
                        (consider using the ``get_tempfile`` utility).
        """
        self._write_schema(tmp)
        tmp.flush()
        os.chmod(tmp.name, 0o400)
        self._view_core(tmp)

    def __call__(self, tmp: _T_NamedTemporaryFile) -> None:
        self.view(tmp)


class GeditViewer[T_Schema: GoldenFileSchema](Viewer[T_Schema]):
    """Intermediate abstract class of :class:`Viewer` which views files in a new window of **Gedit**. The subprocess
    is executed in a blocking manner, meaning it needs to be exited before the program proceeds.

    This class implements :func:`_view_core`, but still requires implementation of :func:`_write_schema` from its
    subclasses.
    """
    @abstractmethod
    def _write_schema(self, tmp: _T_NamedTemporaryFile) -> None:
        ...

    def _view_core(self, tmp: _T_NamedTemporaryFile) -> None:
        subprocess.run(["gedit", "--standalone", tmp.name])


class TokenFileViewer(GeditViewer[TokenFileSchema]):
    """Viewer class of token files in a new window of **Gedit** (subprocess is blocking).
    """
    def _write_schema(self, tmp: _T_NamedTemporaryFile) -> None:
        table = tabulate({
            "Line": [tok.lineno for tok in self.schema.data.tokens],
            "Col": [tok.colno for tok in self.schema.data.tokens],
            "Type": [tok.typ for tok in self.schema.data.tokens],
            "Value": [repr(tok.value) for tok in self.schema.data.tokens],
        }, headers="keys")

        tmp.write(table)
        tmp.write(f"\n\n\nexit_exc:\n\t{repr(self.schema.data.exit_exc)}")


def get_tempfile(
        fpath: Optional[str] = None,
        mode: str = "w+t",
        **named_tempfile_kwargs
) -> _T_NamedTemporaryFile:
    """Helper method which invokes ``tempfile.NamedTemporaryFile`` but allows for name-prefix generation based on
    the original file path (if not ``None``).

    It takes the base name of the file and replaces '.' with '_'.

    :param fpath:                   File path for prefix. If ``None``, it is ignored.
                                    If both ``fpath`` and ``prefix`` are given, ``prefix`` is ignored.
    :param mode:                    Opening mode.
    :param named_tempfile_kwargs:   Other arguments for ``tempfile.NamedTemporaryFile``
    :return:                        A named temporary file.
    """
    named_tempfile_kwargs.update(dict(mode=mode))

    if fpath is not None:
        named_tempfile_kwargs["prefix"] = os.path.basename(fpath).replace('.', '_') + "_"

    return tempfile.NamedTemporaryFile(**named_tempfile_kwargs)



_viewer_map: dict[type[GoldenFileSchema], type[Viewer]] = {
    TokenFileSchema: TokenFileViewer}
"""Simple map for the factory method below."""

def get_viewer[T_Schema: GoldenFileSchema](schema: T_Schema) -> Viewer[T_Schema]:
    """Factory method which returns an appropriate :class:`Viewer` instance based on the type of the ``schema``
    it received.

    :param schema:  Schema to create and return a viewer for.
    :return:        A viewer of the schema.
    """
    if type(schema) not in _viewer_map:
        raise SchemaTypeNotSupportedError(f"Schema type {type(schema)} not yet supported.")

    return _viewer_map[type(schema)](schema)

