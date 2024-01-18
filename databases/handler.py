import sqlite3


class Handler:
  def __init__(self, db: str):
    self.db=db

  def execute(self, code: str):
    con = sqlite3.connect(self.db)
    cur = con.cursor()
    res = cur.execute(code)
    con.commit()
    return cur.fetchall()
