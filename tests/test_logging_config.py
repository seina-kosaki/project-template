import io
import logging
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from src import logging_config


@pytest.fixture
def log_directory(tmp_path, monkeypatch):
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    original_owned_handlers = logging_config._handlers
    monkeypatch.setattr(logging_config, "_LOG_DIRECTORY", tmp_path / "logs")
    monkeypatch.setattr(logging_config, "_handlers", ())
    try:
        yield tmp_path / "logs"
    finally:
        for handler in logging_config._handlers:
            root.removeHandler(handler)
            handler.close()
        root.handlers[:] = original_handlers
        root.setLevel(original_level)
        logging_config._handlers = original_owned_handlers


def today_file(directory):
    return directory / f"{datetime.now().date().isoformat()}.log"


def test_info_format_utf8_and_stderr(log_directory, capsys):
    logging_config.setup_logging()
    logger = logging.getLogger("logging_config_test")
    logger.debug("hidden debug message")
    logger.info("\u65e5\u672c\u8a9e\u306e\u30ed\u30b0")

    captured = capsys.readouterr()
    content = today_file(log_directory).read_text(encoding="utf-8")
    assert captured.out == ""
    assert captured.err == content
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        r" \[INFO\] logging_config_test: \u65e5\u672c\u8a9e\u306e\u30ed\u30b0\n",
        content,
    )


def test_reinitialization_changes_level_without_duplicates(log_directory, capsys):
    logging_config.setup_logging()
    logging.getLogger("logging_config_test").info("before")
    previous_handlers = logging_config._handlers
    logging_config.setup_logging(level=logging.DEBUG)
    logging_config.setup_logging(level="DEBUG")
    logging.getLogger("logging_config_test").debug("after")

    content = today_file(log_directory).read_text(encoding="utf-8")
    assert content.count(": before\n") == 1
    assert content.count(": after\n") == 1
    assert capsys.readouterr().err == content
    assert previous_handlers[1]._stream is None


def test_unrelated_handlers_are_preserved(log_directory):
    stream = io.StringIO()
    external = logging.StreamHandler(stream)
    logging.getLogger().addHandler(external)
    logging_config.setup_logging()
    logging_config.setup_logging()
    logging.getLogger("logging_config_test").info("external")

    assert external in logging.getLogger().handlers
    assert not stream.closed
    assert stream.getvalue().count("external\n") == 1


def test_restart_appends_and_preserves_old_files(log_directory):
    log_directory.mkdir()
    old_file = log_directory / "2000-01-01.log"
    old_file.write_text("keep this log\n", encoding="utf-8")
    script = (
        "import logging, sys; from pathlib import Path; "
        "from src import logging_config; "
        "logging_config._LOG_DIRECTORY = Path(sys.argv[1]); "
        "logging_config.setup_logging(); "
        "logging.getLogger('restart_test').info(sys.argv[2])"
    )
    project_directory = Path(__file__).resolve().parent.parent
    for message in ("first run", "second run"):
        result = subprocess.run(
            [sys.executable, "-c", script, str(log_directory), message],
            cwd=project_directory,
            capture_output=True,
            text=True,
            check=True,
        )
        assert message in result.stderr

    content = today_file(log_directory).read_text(encoding="utf-8")
    assert content.count(": first run\n") == 1
    assert content.count(": second run\n") == 1
    assert old_file.read_text(encoding="utf-8") == "keep this log\n"


def test_midnight_switches_to_new_file(log_directory, monkeypatch):
    clock = Mock()
    clock.now.return_value = datetime(2026, 11, 4, 23, 59, 59)
    clock.fromtimestamp.side_effect = datetime.fromtimestamp
    monkeypatch.setattr(logging_config, "datetime", clock)
    logging_config.setup_logging()
    handler = logging_config._handlers[1]

    for instant, message in (
        (datetime(2026, 11, 4, 23, 59, 59), "before midnight"),
        (datetime(2026, 11, 5, 0, 0, 0), "after midnight"),
        (datetime(2026, 11, 6, 12, 0, 0), "after idle day"),
    ):
        record = logging.LogRecord("midnight", logging.INFO, "", 0, message, (), None)
        record.created = instant.timestamp()
        handler.handle(record)

    for date, time, message in (
        ("2026-11-04", "23:59:59", "before midnight"),
        ("2026-11-05", "00:00:00", "after midnight"),
        ("2026-11-06", "12:00:00", "after idle day"),
    ):
        assert (log_directory / f"{date}.log").read_text(encoding="utf-8") == (
            f"{date} {time} [INFO] midnight: {message}\n"
        )


def test_default_directory_is_independent_of_cwd(tmp_path):
    source_directory = tmp_path / "project" / "src"
    source_directory.mkdir(parents=True)
    shutil.copyfile(logging_config.__file__, source_directory / "logging_config.py")
    working_directory = tmp_path / "elsewhere"
    working_directory.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import logging, sys; sys.path.insert(0, sys.argv[1]); "
            "from logging_config import setup_logging; setup_logging(); "
            "logging.getLogger('cwd_test').info('correct location')",
            str(source_directory),
        ],
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=True,
    )
    content = today_file(source_directory.parent / "logs").read_text(encoding="utf-8")
    assert content == result.stderr
    assert ": correct location\n" in content
    assert not (working_directory / "logs").exists()


@pytest.mark.parametrize("level", ["INVALID", None, object()])
def test_invalid_level_is_reported_without_reconfiguring(log_directory, level):
    logging_config.setup_logging()
    previous_handlers = logging_config._handlers
    with pytest.raises((TypeError, ValueError)):
        logging_config.setup_logging(level=level)
    assert logging_config._handlers == previous_handlers


def test_directory_creation_failure_propagates(log_directory):
    log_directory.write_text("not a directory", encoding="utf-8")
    with pytest.raises(FileExistsError):
        logging_config.setup_logging()


def test_file_open_failure_propagates(log_directory):
    log_directory.mkdir()
    today_file(log_directory).mkdir()
    with pytest.raises(OSError):
        logging_config.setup_logging()


def test_rollover_failure_propagates(log_directory):
    logging_config.setup_logging()
    handler = logging_config._handlers[1]
    (log_directory / "2030-01-01.log").mkdir()
    record = logging.LogRecord("failure", logging.ERROR, "", 0, "failure", (), None)
    record.created = datetime(2030, 1, 1).timestamp()
    with pytest.raises(OSError):
        handler.handle(record)


@pytest.mark.parametrize("operation", ["write", "flush"])
def test_write_failure_propagates(log_directory, monkeypatch, operation):
    logging_config.setup_logging()
    monkeypatch.setattr(logging, "raiseExceptions", False)
    handler = logging_config._handlers[1]
    stream = Mock(wraps=handler._stream)
    getattr(stream, operation).side_effect = OSError("file output failed")
    monkeypatch.setattr(handler, "_stream", stream)
    with pytest.raises(OSError, match="file output failed"):
        logging.getLogger("logging_config_test").error("failure")
