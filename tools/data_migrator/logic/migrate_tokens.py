"""TokenFileSchema migration scripts
"""
from compiler_tests.utils.files import TokenFileSchema

from data_migrator.logic.engine.collector import migrates


@migrates(TokenFileSchema, "1.1", "1.2")
def add_exit_exc_and_update_file_type(schema: TokenFileSchema) -> TokenFileSchema:
    schema.file_type = "TokenFileSchema"
    schema.data.exit_exc = None

    return schema

