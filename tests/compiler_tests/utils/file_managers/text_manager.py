from pathlib import Path

from tests.compiler_tests.utils.file_managers.base_manager import FileManager


class TextFileManager(FileManager[str]):
    """Implements simple functionality to read/write text file_managers (into/from strings).
    """
    def _read_core(self, fullpath: Path) -> str:
        return fullpath.read_text()

    def _write_core(self, fullpath: Path, data: str) -> None:
        fullpath.write_text(data)
