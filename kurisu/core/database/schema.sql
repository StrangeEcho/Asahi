CREATE TABLE IF NOT EXISTS GuildSettings (
    guild BIGINT PRIMARY KEY, 
    prefix prefix TEXT
);

CREATE TABLE IF NOT EXISTS AFK (
    user BIGINT, 
    message TEXT,
    toggled SMALLINT
);
