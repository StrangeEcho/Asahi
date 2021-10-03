schema = """
CREATE TABLE IF NOT EXISTS guildsettings (guild BIGINT PRIMARY KEY, prefix VARCHAR(10))
;;
CREATE TABLE IF NOT EXISTS warnings (user BIGINT, reason VARCHAR(200), guild BIGINT, moderator VARCHAR)
 """
