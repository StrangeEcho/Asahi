CREATE TABLE IF NOT EXISTS Guild_Settings(
    guild_id BIGINT NOT NULL,
    prefix VARCHAR(10),
    confession_channel BIGINT
)