import glob
import json
import logging
import os
from pathlib import Path
from shutil import rmtree
from typing import ClassVar

TMP_FILE = "./missing_init_files.json"
NFILES = []

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class ColorFormatter(logging.Formatter):
    """A custom formatter that adds color to log messages based on their severity level.

    This formatter uses ANSI escape codes to colorize log output in the terminal,
    making it easier to distinguish between different log levels.
    """  # noqa: E501
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "  # noqa
        "(%(filename)s:%(lineno)d)"
    )

    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: green + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color based on its severity level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message with appropriate color.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


ch = logging.StreamHandler()
ch.setFormatter(ColorFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[ch],
)


# -----------------------------------------------------------------------------


def create_init_file(dirpath: str, msg: str) -> None:
    """Create an __init__.py in the specified directory and log the action.

    Args:
        dirpath (str): The directory path where the __init__.py file created.
        msg (str): A message to include in the log entry.
    """
    global NFILES  # noqa: PLW0602
    ini_file = f"{dirpath}/__init__.py"
    Path(ini_file).touch()
    NFILES.append(ini_file)
    logging.info(f"{msg}: created '{ini_file}'")    # noqa: G004


def create_parent_init_files(dirpath: str, rootpath: str, msg: str) -> None:
    """Create __init__.py files in all parent directories up to the root.

    Args:
        dirpath (str): The starting directory path.
        rootpath (str): The root directory path to stop at.
        msg (str): A message to include in the log entry.
    """
    parent_path = dirpath
    while parent_path != rootpath:
        parent_path = os.path.dirname(parent_path)
        parent_init = os.path.join(parent_path, "__init__.py")
        if not os.path.exists(parent_init):
            create_init_file(parent_path, msg)
        else:
            break


def add_missing_init_files(*roots: str, msg: str = "") -> None:
    """Scan root directories for Python files without __init__.py.

    This function takes in one or more root directories as arguments and
    scans them for Python files without an `__init__.py` file. It
    generates a JSON file named `missing_init_files.json` containing the
    paths of these files.

    Args:
        *roots: Variable number of root directories to scan.
        msg: An optional message to display during the process.
    """
    for root in roots:
        if not os.path.exists(root):
            continue
        rootpath = os.path.abspath(root)
        for dirpath, _dirs, files in os.walk(rootpath):
            if "__init__.py" in files:
                continue

            if "." in dirpath:
                continue

            if (
                not glob.glob(os.path.join(dirpath, "*.py"))
                and "vendor" not in dirpath
            ):
                continue

            create_init_file(dirpath, msg)
            create_parent_init_files(dirpath, rootpath, msg)

    with open(TMP_FILE, "w", encoding="utf-8") as f:
        json.dump(NFILES, f)


def remove_missing_init_files(msg: str = "") -> None:
    """Remove temporary __init__.py files created by add_missing_init_files().

    This function removes temporary `__init__.py` files created in the
    `add_missing_init_files()` function. It reads the paths of these files from
    a JSON file named `missing_init_files.json`.

    Args:
        msg: An optional message to display during the removal process.
    """
    global NFILES  # noqa: PLW0603
    nfiles = []
    if os.path.exists(TMP_FILE):
        with open(TMP_FILE, encoding="utf-8") as f:
            nfiles = json.load(f)
    else:
        nfiles = NFILES

    for file in nfiles:
        Path(file).unlink()
        logging.info(f"{msg}: removed {file}")     # noqa: G004

    os.remove(TMP_FILE)
    NFILES = []


def remove_pychache_dirs(msg: str = "") -> None:
    """Remove all existing '__pycache__' directories.
    
    This function walks the current directory and removes all existing
    '__pycache__' directories.

    Args:
        msg: An optional message to display during the removal process.

    """
    nremoved = 0

    for dirpath, dirs, _files in os.walk("."):
        if "__pycache__" in dirs:
            pydir = Path(f"{dirpath}/__pycache__")
            rmtree(pydir)
            nremoved += 1
            logging.info(f"{msg}: removed '{pydir}'")     # noqa: G004

    if not nremoved:
        logging.info(f"{msg}: no __pycache__ dirs found")     # noqa: G004


# mkdocs hooks ----------------------------------------------------------------


def on_startup(command: str, dirty: bool) -> None:  # noqa: ARG001, FBT001
    """MkDocs hook called when the server starts.

    This function is called when the MkDocs development server starts up.
    It removes all existing '__pycache__' directories to ensure a clean state.

    Args:
        command (str): The MkDocs command being executed.
        dirty (bool): Whether this is a dirty build.
    """
    remove_pychache_dirs(msg="HOOK    -  on_startup")


def on_pre_build(config: dict) -> None:  # noqa: ARG001
    """This function is called before the MkDocs build process begins.

    It adds temporary `__init__.py` files to directories that do not
    contain one, to make sure mkdocs doesn't ignore them.
    """
    try:
        add_missing_init_files(
            "client",
            "server",
            "services",
            msg="HOOK    -  on_pre_build",
        )
    except BaseException as e:
        logging.error(e)  # noqa: LOG015, TRY400
        remove_missing_init_files(
            msg="HOOK    -  on_post_build: cleaning up on error !"
        )
        raise


def on_post_build(config: dict) -> None:  # noqa: ARG001
    """This function is called after the MkDocs build process ends.
    
    It removes temporary `__init__.py` files that were added in the
    `on_pre_build()` function.
    """
    remove_missing_init_files(msg="HOOK    -  on_post_build")
