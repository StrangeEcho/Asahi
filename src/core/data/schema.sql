CREATE TABLE IF NOT EXISTS Guild_Settings(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    prefix VARCHAR(10),
    confession_channel BIGINT
)
;;
CREATE TABLE IF NOT EXISTS Mute_Settings(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    mute_role BIGINT
)