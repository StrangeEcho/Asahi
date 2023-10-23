import datetime

from humanize import naturaldelta, precisedelta


def humanize_timedelta(
    delta: datetime.timedelta, *, precise: bool = False
) -> str:
    """ "Humanize" a datetime.timedelta object to be human readable"""
    if precise:
        return precisedelta(delta)
    return naturaldelta(delta)


def box(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text}\n```"


def convert_permission_integer(permission_integer: int) -> list[str]:
    permissions = {
        "create_instant_invite": 1,
        "kick_members": 2,
        "ban_members": 4,
        "administrator": 8,
        "manage_channels": 16,
        "manage_guild": 32,
        "add_reactions": 64,
        "view_audit_log": 128,
        "priority_speaker": 256,
        "stream": 512,
        "view_channel": 1024,
        "send_messages": 2048,
        "send_tts_messages": 4096,
        "manage_messages": 8192,
        "embed_links": 16384,
        "attach_files": 32768,
        "read_message_history": 65536,
        "mention_everyone": 131072,
        "use_external_emojis": 262144,
        "view_guild_insights": 524288,
        "connect": 1048576,
        "speak": 2097152,
        "mute_members": 4194304,
        "deafen_members": 8388608,
        "move_members": 16777216,
        "use_vad": 33554432,
        "change_nickname": 67108864,
        "manage_nicknames": 134217728,
        "manage_roles": 268435456,
        "manage_webhooks": 536870912,
        "manage_emojis_and_stickers": 1073741824,
        "use_application_commands": 2147483648,
        "request_to_speak": 4294967296,
        "manage_threads": 8589934592,
        "create_public_threads": 17179869184,
        "create_private_threads": 34359738368,
        "use_external_stickers": 68719476736,
    }

    readable_permissions = []
    for permission, value in permissions.items():
        if permission_integer & value == value:
            readable_permissions.append(permission)

    return readable_permissions
