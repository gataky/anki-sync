import pandas as pd


class Rev:
    """Revision log entry."""

    order = ["id", "cid", "usn", "ease", "ivl", "lastIvl", "factor", "time", "type"]

    def __init__(self, data: pd.DataFrame):
        data = data.to_dict()
        self.values = []
        for ord in self.order:
            self.values.append(data[ord])

    def write_to_db(self, new_db_conn):
        """Write the revision log entry to the database."""
        new_db_conn.execute(
            "INSERT INTO revlog VALUES(?,?,?,?,?,?,?,?,?);", self.values
        )
