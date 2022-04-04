CREATE TABLE IF NOT EXISTS Guild_Settings(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    prefix VARCHAR(10),
    confession_channel BIGINT
)