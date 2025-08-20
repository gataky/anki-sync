import itertools
import pathlib
from unittest.mock import Mock, patch

import pytest

from anki_sync.core.sql import AnkiDatabase


class Test_AnkiDatabase:

    @patch("anki_sync.core.sql.sqlite3")
    @patch("anki_sync.core.sql.time")
    def test_init_path_exists(self, mock_time, mock_sqlite3: Mock):
        # setup a fake path that will ack as our database file.
        mock_path = Mock(spec=pathlib.Path)
        mock_path.is_file.return_value = True
        mock_path.resolve.return_value = "/var/anki.sql"

        # setup a fake connection, this is what we should get back
        # after calling sqlite3.connect with the path.
        mock_sqlite_conn = Mock()
        mock_sqlite3.connect.return_value = mock_sqlite_conn

        now = 1755707897.780504
        mock_time.time.return_value = now

        # test
        dut = AnkiDatabase(mock_path)

        # asserts
        assert dut.conn == mock_sqlite_conn
        assert dut.path == mock_path
        assert isinstance(dut.id_gen, itertools.count)
        assert next(dut.id_gen) == int(now * 1000)

    def test_init_path_not_exists(self):
        # setup a fake path that does not exist
        mock_path = Mock(spec=pathlib.Path)
        mock_path.is_file.return_value = False

        with pytest.raises(FileNotFoundError) as err:
            AnkiDatabase(mock_path)
