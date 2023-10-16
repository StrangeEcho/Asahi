CREATE TABLE IF NOT EXISTS GuildSettings (
    guild BIGINT PRIMARY KEY, 
    prefix prefix TEXT
);
CREATE TABLE IF NOT EXISTS Warnings (
    user BIGINT, 
    reason TEXT,
    guild BIGINT, 
    moderator BIGINT
);
CREATE TABLE IF NOT EXISTS AFK (
    user BIGINT, 
    message TEXT,
    toggled BOOLEAN
);
CREATE TABLE IF NOT EXISTS Todo (
    user BIGINT, 
    task TEXT
)