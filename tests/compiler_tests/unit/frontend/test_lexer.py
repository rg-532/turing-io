"""
TODO:
    - Write other types of tests.
    - Consider wrapping some things in classes.
TODO:
    - Doc some objects + fixtures + tests.
    - Move some things away to conftest / utils.
TODO:
    - Add option in pytest execution to override goldens (or have that by default w/ option to turn off).
"""
import logging
from typing import List, Optional

import pytest
import jsonpickle.errors

from compiler.frontend.lexer import TMLexer
from compiler_tests.utils.metadata import LazyMetadata

from compiler_tests.utils.objects.tokens import LexerToken
from compiler_tests.utils.files import (
    TextFileManager, GoldenFileManager,
    TokenFileSchema, GoldenFileOriginSchema, TokenFileDataSchema
)


_metadata: LazyMetadata = LazyMetadata("lexer/lexer.json")
"""Metadata file from `[root]/tests/data/`"""

@pytest.fixture(scope="module")
def input_reader() -> TextFileManager:
    return TextFileManager(_metadata.input_dir).set_perms("r")

@pytest.fixture(scope="module")
def output_reader() -> GoldenFileManager[TokenFileSchema]:
    return GoldenFileManager(_metadata.output_dir).set_perms("r")

@pytest.fixture(scope="module")
def golden_writer() -> GoldenFileManager[TokenFileSchema]:
    """Specifically for writing golden file outputs."""
    return GoldenFileManager(_metadata.golden_dir).set_perms("w")


@pytest.fixture
def lexer() -> TMLexer:
    return TMLexer()


@pytest.fixture(params=_metadata.input_paths)
def input_relpath(request) -> str:
    return request.param

@pytest.fixture
def input_data(input_reader, input_relpath) -> str:
    """Assumes file ``{input_mgr.dirpath}/{input_relpath}`` exists."""
    return input_reader.read(input_relpath)

@pytest.fixture
def lexer_tokens(lexer, input_data) -> List[LexerToken]:
    """TODO - add error handling.
    Assumes the input data is fully scannable (Raises some error otherwise)."""
    return [LexerToken.from_tok(tok) for tok in lexer.tokenize(input_data)]


@pytest.fixture
def expected_relpath(input_relpath) -> str:
    return f"{input_relpath}.tok"

@pytest.fixture
def raw_expected_schema(
        output_reader, expected_relpath,
        request, lexer_tokens, golden_writer  # For when read fails.
) -> Optional[TokenFileSchema]:
    """Returns the expected output's schema or an exception thrown when reading."""
    cause = None

    try:
        return output_reader.read(expected_relpath)
    except FileNotFoundError as exc:
        cause = exc
    except (Exception, jsonpickle.errors.ClassNotFoundError) as exc:
        cause = exc
    finally:
        if cause is not None:
            reason = f"{cause.__class__.__qualname__}: {str(cause)}"
            golden = TokenFileSchema(
                origin=GoldenFileOriginSchema(
                    creator=request.node.name,
                    reason=f"Fixture {request.fixturename} on {expected_relpath} got {reason}"),
                data=TokenFileDataSchema(tokens=lexer_tokens))
            golden_writer.write(expected_relpath, golden, allow_overwrite=True)
            logging.warning(reason)
            pytest.skip()

@pytest.fixture
def checked_expected_schema(raw_expected_schema) -> TokenFileSchema:
    read_version = raw_expected_schema.schema_version
    current_version = TokenFileSchema.schema_version

    if read_version != current_version:
        logging.warning(f"Expected schema may be outdated (Read {read_version}, Current {current_version})")

    return raw_expected_schema

@pytest.fixture
def expected_tokens(checked_expected_schema) -> Optional[List[LexerToken]]:
    return list(checked_expected_schema.data.tokens)



def test_lexer_valid(lexer_tokens, expected_tokens):
    assert lexer_tokens == expected_tokens



