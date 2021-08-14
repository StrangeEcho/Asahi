import sqlite3

from config import BOT_PREFIX

schema = f"""
  CREATE TABLE IF NOT EXISTS "guildsettings" (
    "guild"  INTEGER NOT NULL,
    "prefix"  TEXT NOT NULL DEFAULT "{BOT_PREFIX}",
    "log_channel" INTEGER NOT NULL,
    "log_enabled" INTEGER NOT NULL 
  )
 """

connection = sqlite3.connect("kurisu.db")
