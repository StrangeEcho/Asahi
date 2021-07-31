import sqlite3

from config import BOT_PREFIX

schema = f"""
  CREATE TABLE IF NOT EXISTS "guildsettings" (
    "guild"  INTEGER NOT NULL,
    "prefix"  TEXT NOT NULL DEFAULT "{BOT_PREFIX}"
  )
 """

connection = sqlite3.connect("kurisu.db")
