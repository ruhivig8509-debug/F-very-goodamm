#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ✦ RUHI X ASSISTANT - TELEGRAM BOT ✦                  ║
║        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    ║
║                                                              ║
║   👑 Owner:  愛 | 𝗥𝗨𝗛𝗜 𝗫 𝗤𝗡𝗥〆                              ║
║   ⚡ Engine: python-telegram-bot v20+                        ║
║   🗄️ Database: PostgreSQL (Render)                           ║
║   🌐 Hosting: Render Web Service (Webhook)                   ║
║   📦 Single File Architecture                                ║
║                                                              ║
║   SECTION 1: Core System & Setup                             ║
║   ─────────────────────────────────                          ║
║   • Bot initialization with webhook (Render compatible)      ║
║   • PostgreSQL database (Render DB)                          ║
║   • Owner system                                             ║
║   • Sudo users system                                        ║
║   • Support users system                                     ║
║   • Logger channel                                           ║
║   • Start command with stylish welcome                       ║
║   • Help command with inline buttons                         ║
║   • About command                                            ║
║   • Alive/Ping command                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════
# ◈ IMPORTS
# ═══════════════════════════════════════════════════════════════

import os
import sys
import time
import json
import html
import logging
import asyncio
import traceback
import re
import random
import string
import hashlib
import base64
import io
import math
import datetime
import calendar
import urllib.parse
import textwrap
import functools
import signal
import threading
from uuid import uuid4
from typing import (
    Optional, List, Dict, Tuple, Union,
    Any, Callable, Set, Sequence
)
from datetime import datetime, timedelta, timezone
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
from enum import Enum, auto
from contextlib import asynccontextmanager
from html import escape as html_escape

# ── Telegram imports ──
from telegram import (
    Update, Bot, Chat, User, Message,
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove,
    KeyboardButton, ForceReply,
    ChatPermissions, ChatMember, ChatMemberOwner,
    ChatMemberAdministrator, ChatMemberMember,
    ChatMemberRestricted, ChatMemberBanned, ChatMemberLeft,
    BotCommand, BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats, BotCommandScopeChat,
    InputMediaPhoto, InputMediaVideo, InputMediaDocument,
    InputMediaAnimation, InputMediaAudio,
    CallbackQuery, MessageEntity,
    ChatInviteLink, StickerSet
)
from telegram.ext import (
    Application, ApplicationBuilder,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, ConversationHandler,
    ContextTypes, Defaults,
    filters, InvalidCallbackData
)
from telegram.constants import (
    ParseMode, ChatAction, ChatType,
    ChatMemberStatus, MessageEntityType,
    FileSizeLimit
)
from telegram.error import (
    TelegramError, BadRequest, Forbidden,
    TimedOut, NetworkError, RetryAfter,
    ChatMigrated, InvalidToken
)
from telegram.helpers import escape_markdown, mention_html

# ── Web server for Render webhook ──
from aiohttp import web

# ── PostgreSQL ──
import asyncpg

# ═══════════════════════════════════════════════════════════════
# ◈ LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    format=(
        "╔═[%(asctime)s]═══════════════════╗\n"
        "║ %(levelname)-8s │ %(name)s\n"
        "║ %(message)s\n"
        "╚═══════════════════════════════════╝"
    ),
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.INFO)
logger = logging.getLogger("RuhiBot")

# ═══════════════════════════════════════════════════════════════
# ◈ CONFIGURATION - ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════

# ── Required ──
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "RUHI_X_QNR")

# ── Optional ──
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "0"))
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "")
UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "")

# ── Render specific ──
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
PORT = int(os.environ.get("PORT", "10000"))
# Use stable secret derived from BOT_TOKEN if not explicitly set (uuid4 changes every restart!)
_default_secret = hashlib.md5(BOT_TOKEN.encode()).hexdigest() if BOT_TOKEN else str(uuid4())
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", _default_secret)
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

# ── Bot info ──
BOT_NAME = os.environ.get("BOT_NAME", "Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ")
BOT_VERSION = "3.0.0"
BOT_START_TIME = time.time()

# ── Initial Sudo & Support users (comma-separated IDs) ──
INITIAL_SUDO_USERS = [
    int(x.strip()) for x in
    os.environ.get("SUDO_USERS", "").split(",")
    if x.strip().isdigit()
]
INITIAL_SUPPORT_USERS = [
    int(x.strip()) for x in
    os.environ.get("SUPPORT_USERS", "").split(",")
    if x.strip().isdigit()
]

# ═══════════════════════════════════════════════════════════════
# ◈ STYLISH TEXT UTILITIES
# ═══════════════════════════════════════════════════════════════

class StyleFont:
    """
    ╔═══════════════════════════════════════╗
    ║  Unicode stylish font converter       ║
    ║  Supports multiple font styles        ║
    ╚═══════════════════════════════════════╝
    """

    # ── Bold Serif (Mathematical Bold) ──
    BOLD_UPPER = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
    BOLD_LOWER = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"

    # ── Small Caps ──
    SMALL_CAPS = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"

    # ── Bold Sans ──
    BOLD_SANS_UPPER = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    BOLD_SANS_LOWER = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"

    # ── Italic Sans ──
    ITALIC_SANS_UPPER = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    ITALIC_SANS_LOWER = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"

    # ── Monospace ──
    MONO_UPPER = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    MONO_LOWER = "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"

    # ── Script / Cursive ──
    SCRIPT_UPPER = "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    SCRIPT_LOWER = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏"

    # ── Double-Struck ──
    DOUBLE_UPPER = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
    DOUBLE_LOWER = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"

    # ── Fraktur ──
    FRAKTUR_UPPER = "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
    FRAKTUR_LOWER = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"

    # ── Circled ──
    CIRCLED_UPPER = "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
    CIRCLED_NUMS = "⓪①②③④⑤⑥⑦⑧⑨"

    # ── Stylish numbers ──
    BOLD_NUMS = "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
    SANS_BOLD_NUMS = "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"

    NORMAL_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    NORMAL_LOWER = "abcdefghijklmnopqrstuvwxyz"
    NORMAL_NUMS = "0123456789"

    @classmethod
    def bold(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.BOLD_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.BOLD_LOWER)[idx])
            elif ch in cls.NORMAL_NUMS:
                idx = cls.NORMAL_NUMS.index(ch)
                result.append(list(cls.BOLD_NUMS)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def small_caps(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.SMALL_CAPS)[idx])
            elif ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.SMALL_CAPS)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def bold_sans(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.BOLD_SANS_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.BOLD_SANS_LOWER)[idx])
            elif ch in cls.NORMAL_NUMS:
                idx = cls.NORMAL_NUMS.index(ch)
                result.append(list(cls.SANS_BOLD_NUMS)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def mono(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.MONO_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.MONO_LOWER)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def script(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.SCRIPT_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.SCRIPT_LOWER)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def double_struck(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.DOUBLE_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.DOUBLE_LOWER)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def fraktur(cls, text: str) -> str:
        result = []
        for ch in text:
            if ch in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(ch)
                result.append(list(cls.FRAKTUR_UPPER)[idx])
            elif ch in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(ch)
                result.append(list(cls.FRAKTUR_LOWER)[idx])
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def mixed_bold_smallcaps(cls, text: str) -> str:
        """
        First letter of each word → Bold, rest → small caps
        Like: 𝐇ᴇʟʟᴏ 𝐖ᴏʀʟᴅ
        """
        words = text.split()
        styled_words = []
        for word in words:
            if not word:
                styled_words.append(word)
                continue
            first = word[0]
            rest = word[1:]
            if first in cls.NORMAL_UPPER:
                idx = cls.NORMAL_UPPER.index(first)
                styled_first = list(cls.BOLD_UPPER)[idx]
            elif first in cls.NORMAL_LOWER:
                idx = cls.NORMAL_LOWER.index(first)
                styled_first = list(cls.BOLD_UPPER)[idx]
            else:
                styled_first = first
            styled_rest = cls.small_caps(rest.lower())
            styled_words.append(styled_first + styled_rest)
        return " ".join(styled_words)


# ═══════════════════════════════════════════════════════════════
# ◈ SYMBOLS & DECORATIONS LIBRARY
# ═══════════════════════════════════════════════════════════════

class Symbols:
    """
    ╔═══════════════════════════════════════╗
    ║  God-level symbols & decorations      ║
    ║  Ultra rare Unicode characters        ║
    ╚═══════════════════════════════════════╝
    """

    # ── Stars & Sparkles ──
    STAR = "✦"
    STAR2 = "✧"
    STAR3 = "✯"
    STAR4 = "✰"
    STAR5 = "⭐"
    STAR6 = "🌟"
    SPARKLE = "✨"
    SPARKLE2 = "❇️"
    GLITTER = "✵"
    FOUR_STAR = "✦"
    EIGHT_STAR = "✴️"

    # ── Diamonds & Gems ──
    DIAMOND = "◈"
    DIAMOND2 = "◇"
    DIAMOND3 = "◆"
    DIAMOND4 = "💎"
    DIAMOND5 = "❖"
    GEM = "༗"

    # ── Arrows ──
    ARROW_R = "➤"
    ARROW_R2 = "➜"
    ARROW_R3 = "➥"
    ARROW_R4 = "⟫"
    ARROW_R5 = "»"
    ARROW_L = "⟨"
    ARROW_FANCY = "꒰"
    ARROW_FANCY2 = "꒱"
    ARROW_TRI = "▸"
    ARROW_TRI2 = "▹"

    # ── Bullets & Points ──
    BULLET = "•"
    BULLET2 = "◦"
    BULLET3 = "‣"
    BULLET4 = "⊙"
    BULLET5 = "⊚"
    TINY_DOT = "·"
    RING = "⊛"

    # ── Lines & Borders ──
    LINE = "━"
    LINE2 = "─"
    LINE3 = "═"
    LINE4 = "▬"
    LINE5 = "◽"
    DOTTED = "┄"
    WAVE_LINE = "〰️"
    FULL_LINE = "━━━━━━━━━━━━━━━━━━"

    # ── Box Drawing ──
    BOX_TL = "╔"
    BOX_TR = "╗"
    BOX_BL = "╚"
    BOX_BR = "╝"
    BOX_H = "═"
    BOX_V = "║"
    BOX_VR = "╠"
    BOX_VL = "╣"
    BOX_HU = "╩"
    BOX_HD = "╦"

    # ── Brackets & Enclosures ──
    LBRACKET = "【"
    RBRACKET = "】"
    LBRACKET2 = "『"
    RBRACKET2 = "』"
    LBRACKET3 = "〖"
    RBRACKET3 = "〗"
    LBRACKET4 = "「"
    RBRACKET4 = "」"
    LPAREN = "（"
    RPAREN = "）"
    LANGLE = "〈"
    RANGLE = "〉"
    LCLOUD = "꒰"
    RCLOUD = "꒱"
    LDECO = "❮"
    RDECO = "❯"

    # ── Crowns & Status ──
    CROWN = "👑"
    CROWN2 = "♛"
    CROWN3 = "♚"
    SWORDS = "⚔️"
    SHIELD = "🛡️"
    FIRE = "🔥"
    THUNDER = "⚡"
    SKULL = "💀"

    # ── Hearts ──
    HEART = "❤️"
    HEART2 = "💖"
    HEART3 = "💗"
    HEART4 = "♡"
    HEART5 = "❣️"
    BLACK_HEART = "🖤"
    BLUE_HEART = "💙"
    PURPLE_HEART = "💜"

    # ── Checkmarks & Crosses ──
    CHECK = "✓"
    CHECK2 = "✔️"
    CHECK3 = "☑️"
    CROSS = "✗"
    CROSS2 = "✘"
    CROSS3 = "❌"
    CROSS4 = "✕"

    # ── Warning & Info ──
    WARNING = "⚠️"
    INFO = "ℹ️"
    QUESTION = "❓"
    EXCLAIM = "❗"
    BELL = "🔔"
    MEGAPHONE = "📢"
    PIN = "📌"
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"

    # ── Numbers (Stylish) ──
    NUM_1 = "➊"
    NUM_2 = "➋"
    NUM_3 = "➌"
    NUM_4 = "➍"
    NUM_5 = "➎"
    NUM_6 = "➏"
    NUM_7 = "➐"
    NUM_8 = "➑"
    NUM_9 = "➒"
    NUM_10 = "➓"
    NUMS = ["➊", "➋", "➌", "➍", "➎", "➏", "➐", "➑", "➒", "➓"]

    # ── Misc ──
    GEAR = "⚙️"
    TOOLS = "🛠️"
    ROBOT = "🤖"
    LINK = "🔗"
    GLOBE = "🌐"
    CLOCK = "🕐"
    CALENDAR = "📅"
    FOLDER = "📁"
    CHART = "📊"
    TROPHY = "🏆"
    MEDAL = "🏅"
    ROCKET = "🚀"
    MAGIC = "🪄"
    CRYSTAL = "🔮"
    LOTUS = "🪷"
    CHERRY = "🌸"
    LEAF = "🍃"
    BUTTERFLY = "🦋"
    PEACE = "☮️"
    YIN_YANG = "☯️"
    INFINITY = "♾️"
    RECYCLE = "♻️"
    ATOM = "⚛️"
    LOVE_LETTER = "💌"

    # ── Japanese / Special ──
    AI = "愛"
    SUME = "〆"
    FLOWER = "❀"
    SNOW = "❄️"
    MUSIC = "♪"
    MUSIC2 = "♫"
    DAGGER = "†"
    DOUBLE_DAGGER = "‡"

    @classmethod
    def divider(cls, style: int = 1) -> str:
        dividers = {
            1: "━━━━━━━━━━━━━━━━━━",
            2: "═══════════════════",
            3: "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            4: "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄",
            5: "◈━━━━━━━━━━━━━━━━◈",
            6: "✦━━━━━━━━━━━━━━━━✦",
            7: "❖═══════════════❖",
            8: "⊱━━━━━━━━━━━━━━━⊰",
            9: "꒰━━━━━━━━━━━━━━━꒱",
            10: "✧══════════════✧",
        }
        return dividers.get(style, dividers[1])

    @classmethod
    def header_box(cls, title: str) -> str:
        styled_title = StyleFont.bold_sans(title)
        return (
            f"╔═══[ {styled_title} ]═════╗\n"
        )

    @classmethod
    def footer_box(cls) -> str:
        return "╚════════════════════════╝"

    @classmethod
    def info_line(cls, label: str, value: str) -> str:
        styled_label = StyleFont.mixed_bold_smallcaps(label)
        return f"║ {cls.STAR2} {styled_label}: {value}"

    @classmethod
    def section_title(cls, title: str) -> str:
        styled = StyleFont.bold_sans(title)
        return (
            f"\n{cls.STAR} {styled} {cls.STAR}\n"
            f"{cls.divider(6)}"
        )


# ═══════════════════════════════════════════════════════════════
# ◈ CONSTANTS & ENUMS
# ═══════════════════════════════════════════════════════════════

class UserRole(Enum):
    """User privilege levels"""
    OWNER = auto()
    SUDO = auto()
    SUPPORT = auto()
    ADMIN = auto()
    MEMBER = auto()
    RESTRICTED = auto()
    BANNED = auto()
    LEFT = auto()
    ANONYMOUS = auto()


class LogType(Enum):
    """Types of log entries"""
    BAN = "🔨"
    UNBAN = "🔓"
    KICK = "🦶"
    MUTE = "🔇"
    UNMUTE = "🔊"
    WARN = "⚠️"
    UNWARN = "✅"
    PROMOTE = "⬆️"
    DEMOTE = "⬇️"
    PIN = "📌"
    UNPIN = "📌"
    FLOOD = "🌊"
    FILTER = "🔍"
    NOTE = "📝"
    WELCOME = "👋"
    GOODBYE = "👋"
    ANTIFLOOD = "🌊"
    BLACKLIST = "🚫"
    GBANNED = "🔨"
    UNGBANNED = "🔓"
    SETTINGS = "⚙️"
    FED = "🏛️"
    ERROR = "❌"
    START = "🚀"
    COMMAND = "📋"


# ═══════════════════════════════════════════════════════════════
# ◈ DATABASE MANAGER - PostgreSQL (Render)
# ═══════════════════════════════════════════════════════════════

class DatabaseManager:
    """
    ╔═══════════════════════════════════════╗
    ║  PostgreSQL Database Manager          ║
    ║  Optimized for Render deployment      ║
    ║  Connection pooling & auto-reconnect  ║
    ╚═══════════════════════════════════════╝
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._ready = False
        self._lock: Optional[asyncio.Lock] = None  # Lazy init — must be inside event loop

    def _get_lock(self) -> asyncio.Lock:
        """Lazily create lock inside running event loop"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def connect(self) -> None:
        """Establish connection pool to PostgreSQL"""
        if self._ready and self.pool:
            return

        async with self._get_lock():
            if self._ready and self.pool:
                return

            try:
                db_url = DATABASE_URL
                # Render uses postgresql:// but asyncpg wants postgresql://
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql://", 1)

                self.pool = await asyncpg.create_pool(
                    dsn=db_url,
                    min_size=2,
                    max_size=10,
                    max_inactive_connection_lifetime=300,
                    command_timeout=60,
                    statement_cache_size=0,
                )

                await self._create_tables()
                self._ready = True
                logger.info("✅ Database connected successfully!")

            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                raise

    async def _create_tables(self) -> None:
        """Create all required tables"""
        async with self.pool.acquire() as conn:
            # ── Users table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    language_code TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE,
                    total_messages BIGINT DEFAULT 0,
                    bio TEXT DEFAULT '',
                    afk BOOLEAN DEFAULT FALSE,
                    afk_reason TEXT DEFAULT '',
                    afk_time TIMESTAMP,
                    warns INTEGER DEFAULT 0,
                    is_gbanned BOOLEAN DEFAULT FALSE,
                    gban_reason TEXT DEFAULT '',
                    is_gmuted BOOLEAN DEFAULT FALSE,
                    gmute_reason TEXT DEFAULT '',
                    reputation INTEGER DEFAULT 0,
                    custom_title TEXT DEFAULT '',
                    profile_views BIGINT DEFAULT 0
                );
            """)

            # ── Chats table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id BIGINT PRIMARY KEY,
                    chat_title TEXT,
                    chat_type TEXT,
                    chat_username TEXT,
                    added_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE,
                    member_count INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en',

                    -- Welcome settings
                    welcome_enabled BOOLEAN DEFAULT TRUE,
                    welcome_text TEXT DEFAULT '',
                    welcome_media TEXT DEFAULT '',
                    welcome_media_type TEXT DEFAULT '',
                    welcome_buttons TEXT DEFAULT '[]',
                    welcome_delete_after INTEGER DEFAULT 300,
                    goodbye_enabled BOOLEAN DEFAULT TRUE,
                    goodbye_text TEXT DEFAULT '',
                    clean_welcome BOOLEAN DEFAULT TRUE,
                    last_welcome_msg_id BIGINT DEFAULT 0,

                    -- Anti-flood settings
                    antiflood_enabled BOOLEAN DEFAULT FALSE,
                    antiflood_limit INTEGER DEFAULT 10,
                    antiflood_time INTEGER DEFAULT 45,
                    antiflood_action TEXT DEFAULT 'mute',
                    antiflood_action_duration INTEGER DEFAULT 3600,

                    -- Anti-spam settings
                    antispam_enabled BOOLEAN DEFAULT TRUE,
                    anti_channel_pin BOOLEAN DEFAULT FALSE,
                    anti_linked_channel BOOLEAN DEFAULT FALSE,

                    -- Locks
                    locks TEXT DEFAULT '{}',

                    -- Blacklist
                    blacklist_mode TEXT DEFAULT 'delete',
                    blacklist_action_duration INTEGER DEFAULT 3600,

                    -- Rules
                    rules TEXT DEFAULT '',

                    -- Logging
                    log_channel BIGINT DEFAULT 0,

                    -- Misc settings
                    clean_commands BOOLEAN DEFAULT FALSE,
                    strict_admin BOOLEAN DEFAULT FALSE,
                    report_enabled BOOLEAN DEFAULT TRUE,
                    admin_cache TEXT DEFAULT '[]',
                    admin_cache_time TIMESTAMP DEFAULT NOW(),

                    -- Night mode
                    night_mode BOOLEAN DEFAULT FALSE,
                    night_start TEXT DEFAULT '22:00',
                    night_end TEXT DEFAULT '06:00',

                    -- Slow mode
                    slowmode_enabled BOOLEAN DEFAULT FALSE,
                    slowmode_seconds INTEGER DEFAULT 0,

                    -- Link preview
                    no_link_preview BOOLEAN DEFAULT FALSE,

                    -- Auto-delete
                    auto_delete_enabled BOOLEAN DEFAULT FALSE,
                    auto_delete_seconds INTEGER DEFAULT 0
                );
            """)

            # ── Sudo users table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sudo_users (
                    user_id BIGINT PRIMARY KEY,
                    added_by BIGINT,
                    added_at TIMESTAMP DEFAULT NOW(),
                    reason TEXT DEFAULT ''
                );
            """)

            # ── Support users table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS support_users (
                    user_id BIGINT PRIMARY KEY,
                    added_by BIGINT,
                    added_at TIMESTAMP DEFAULT NOW(),
                    reason TEXT DEFAULT ''
                );
            """)

            # ── Warnings table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    warned_by BIGINT NOT NULL,
                    reason TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Warning settings table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warn_settings (
                    chat_id BIGINT PRIMARY KEY,
                    warn_limit INTEGER DEFAULT 3,
                    warn_action TEXT DEFAULT 'mute',
                    warn_action_duration INTEGER DEFAULT 3600
                );
            """)

            # ── Notes table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    media_type TEXT DEFAULT '',
                    media_id TEXT DEFAULT '',
                    buttons TEXT DEFAULT '[]',
                    is_private BOOLEAN DEFAULT FALSE,
                    created_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, name)
                );
            """)

            # ── Filters table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS filters (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    keyword TEXT NOT NULL,
                    content TEXT NOT NULL,
                    media_type TEXT DEFAULT '',
                    media_id TEXT DEFAULT '',
                    buttons TEXT DEFAULT '[]',
                    created_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, keyword)
                );
            """)

            # ── Blacklist table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    trigger TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    added_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, trigger)
                );
            """)

            # ── Disabled commands table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS disabled_commands (
                    chat_id BIGINT NOT NULL,
                    command TEXT NOT NULL,
                    disabled_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(chat_id, command)
                );
            """)

            # ── Global bans table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS gbans (
                    user_id BIGINT PRIMARY KEY,
                    reason TEXT DEFAULT '',
                    banned_by BIGINT,
                    banned_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Global mutes table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS gmutes (
                    user_id BIGINT PRIMARY KEY,
                    reason TEXT DEFAULT '',
                    muted_by BIGINT,
                    muted_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Federations table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS federations (
                    fed_id TEXT PRIMARY KEY,
                    fed_name TEXT NOT NULL,
                    owner_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    fed_admins TEXT DEFAULT '[]',
                    fed_log BIGINT DEFAULT 0,
                    fed_rules TEXT DEFAULT ''
                );
            """)

            # ── Federation bans table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fed_bans (
                    fed_id TEXT NOT NULL,
                    user_id BIGINT NOT NULL,
                    reason TEXT DEFAULT '',
                    banned_by BIGINT,
                    banned_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(fed_id, user_id)
                );
            """)

            # ── Federation chats table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fed_chats (
                    fed_id TEXT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    joined_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(fed_id, chat_id)
                );
            """)

            # ── Reputation table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reputation (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    rep_count INTEGER DEFAULT 0,
                    last_rep_by BIGINT,
                    last_rep_time TIMESTAMP,
                    PRIMARY KEY(chat_id, user_id)
                );
            """)

            # ── AFK table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS afk (
                    user_id BIGINT PRIMARY KEY,
                    is_afk BOOLEAN DEFAULT FALSE,
                    reason TEXT DEFAULT '',
                    afk_time TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Pins table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS pins (
                    chat_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    pinned_by BIGINT,
                    pinned_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(chat_id, message_id)
                );
            """)

            # ── Bot stats table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id SERIAL PRIMARY KEY,
                    stat_key TEXT UNIQUE NOT NULL,
                    stat_value BIGINT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Approval table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    approved_by BIGINT,
                    approved_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(chat_id, user_id)
                );
            """)

            # ── Custom commands table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS custom_commands (
                    chat_id BIGINT NOT NULL,
                    command TEXT NOT NULL,
                    response TEXT NOT NULL,
                    media_type TEXT DEFAULT '',
                    media_id TEXT DEFAULT '',
                    created_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY(chat_id, command)
                );
            """)

            # ── Reminders table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    reminder_text TEXT NOT NULL,
                    remind_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_done BOOLEAN DEFAULT FALSE
                );
            """)

            # ── Captcha table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS captcha_settings (
                    chat_id BIGINT PRIMARY KEY,
                    enabled BOOLEAN DEFAULT FALSE,
                    captcha_type TEXT DEFAULT 'button',
                    timeout INTEGER DEFAULT 120,
                    kick_on_fail BOOLEAN DEFAULT TRUE,
                    welcome_msg TEXT DEFAULT ''
                );
            """)

            # ── Captcha pending ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS captcha_pending (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    answer TEXT NOT NULL,
                    message_id BIGINT,
                    expires_at TIMESTAMP,
                    PRIMARY KEY(chat_id, user_id)
                );
            """)

            # ── Anti-service table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS anti_service (
                    chat_id BIGINT PRIMARY KEY,
                    delete_join BOOLEAN DEFAULT FALSE,
                    delete_leave BOOLEAN DEFAULT FALSE,
                    delete_pin BOOLEAN DEFAULT FALSE,
                    delete_photo BOOLEAN DEFAULT FALSE
                );
            """)

            # ── Chat permissions log ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS action_log (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    admin_id BIGINT NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Connection table ──
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    user_id BIGINT PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    connected_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # ── Indexes for performance ──
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_warnings_chat_user
                ON warnings(chat_id, user_id);
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_chat
                ON notes(chat_id);
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_filters_chat
                ON filters(chat_id);
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_blacklist_chat
                ON blacklist(chat_id);
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_action_log_chat
                ON action_log(chat_id);
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_reminders_time
                ON reminders(remind_at) WHERE is_done = FALSE;
            """)

            # ── Insert initial stats ──
            await conn.execute("""
                INSERT INTO bot_stats (stat_key, stat_value)
                VALUES ('total_commands', 0)
                ON CONFLICT (stat_key) DO NOTHING;
            """)
            await conn.execute("""
                INSERT INTO bot_stats (stat_key, stat_value)
                VALUES ('total_messages', 0)
                ON CONFLICT (stat_key) DO NOTHING;
            """)
            await conn.execute("""
                INSERT INTO bot_stats (stat_key, stat_value)
                VALUES ('total_callbacks', 0)
                ON CONFLICT (stat_key) DO NOTHING;
            """)

            # ── Insert initial sudo users ──
            for uid in INITIAL_SUDO_USERS:
                await conn.execute("""
                    INSERT INTO sudo_users (user_id, added_by)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO NOTHING;
                """, uid, OWNER_ID)

            # ── Insert initial support users ──
            for uid in INITIAL_SUPPORT_USERS:
                await conn.execute("""
                    INSERT INTO support_users (user_id, added_by)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO NOTHING;
                """, uid, OWNER_ID)

            # ─── Section 2 tables: user_settings, personal_notes, user_global_stats ───
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id             BIGINT PRIMARY KEY,
                    bio                 TEXT DEFAULT '',
                    custom_name         TEXT DEFAULT '',
                    notifications       BOOLEAN DEFAULT TRUE,
                    pm_allowed          BOOLEAN DEFAULT TRUE,
                    read_receipts       BOOLEAN DEFAULT TRUE,
                    auto_afk            BOOLEAN DEFAULT FALSE,
                    auto_afk_time       INTEGER DEFAULT 3600,
                    welcome_dm          BOOLEAN DEFAULT TRUE,
                    language            TEXT DEFAULT 'en',
                    timezone_offset     INTEGER DEFAULT 0,
                    theme               TEXT DEFAULT 'default',
                    profile_private     BOOLEAN DEFAULT FALSE,
                    last_seen_enabled   BOOLEAN DEFAULT TRUE,
                    created_at          TIMESTAMP DEFAULT NOW(),
                    updated_at          TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_global_stats (
                    user_id             BIGINT PRIMARY KEY,
                    total_messages      BIGINT DEFAULT 0,
                    total_commands      BIGINT DEFAULT 0,
                    total_groups        INTEGER DEFAULT 0,
                    first_seen          TIMESTAMP DEFAULT NOW(),
                    last_seen           TIMESTAMP DEFAULT NOW(),
                    xp                  INTEGER DEFAULT 0,
                    level               INTEGER DEFAULT 1
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_notes (
                    id              SERIAL PRIMARY KEY,
                    user_id         BIGINT NOT NULL,
                    note_name       TEXT NOT NULL,
                    note_content    TEXT NOT NULL,
                    media_type      TEXT DEFAULT '',
                    media_id        TEXT DEFAULT '',
                    created_at      TIMESTAMP DEFAULT NOW(),
                    updated_at      TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, note_name)
                );
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_personal_notes_user
                    ON personal_notes(user_id);
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    id          SERIAL PRIMARY KEY,
                    user_id     BIGINT NOT NULL,
                    chat_id     BIGINT NOT NULL,
                    messages    BIGINT DEFAULT 0,
                    commands    BIGINT DEFAULT 0,
                    last_seen   TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, chat_id)
                );
            """)

            # ─── Section 3 tables: welcome_settings, captcha_queue ───
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS welcome_settings (
                    chat_id              BIGINT PRIMARY KEY,
                    welcome_enabled      BOOLEAN DEFAULT TRUE,
                    welcome_text         TEXT DEFAULT '',
                    welcome_media        TEXT DEFAULT '',
                    welcome_media_type   TEXT DEFAULT '',
                    welcome_buttons      TEXT DEFAULT '[]',
                    welcome_delete_after INTEGER DEFAULT 300,
                    goodbye_enabled      BOOLEAN DEFAULT TRUE,
                    goodbye_text         TEXT DEFAULT '',
                    clean_welcome        BOOLEAN DEFAULT TRUE,
                    last_welcome_msg_id  BIGINT DEFAULT 0,
                    captcha_enabled      BOOLEAN DEFAULT FALSE,
                    captcha_type         TEXT DEFAULT 'button',
                    captcha_timeout      INTEGER DEFAULT 120,
                    captcha_action       TEXT DEFAULT 'kick',
                    antiraid_enabled     BOOLEAN DEFAULT FALSE,
                    antiraid_threshold   INTEGER DEFAULT 10,
                    antiraid_time_window INTEGER DEFAULT 60,
                    antiraid_action      TEXT DEFAULT 'restrict',
                    created_at           TIMESTAMP DEFAULT NOW(),
                    updated_at           TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS captcha_queue (
                    id          SERIAL PRIMARY KEY,
                    chat_id     BIGINT NOT NULL,
                    user_id     BIGINT NOT NULL,
                    message_id  BIGINT DEFAULT 0,
                    joined_at   TIMESTAMP DEFAULT NOW(),
                    expires_at  TIMESTAMP,
                    UNIQUE(chat_id, user_id)
                );
            """)

            # ─── Section 5 tables: protection_settings, blacklist, approved ───
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS protection_settings (
                    chat_id                     BIGINT PRIMARY KEY,
                    antiflood_enabled           BOOLEAN DEFAULT FALSE,
                    antiflood_limit             INTEGER DEFAULT 10,
                    antiflood_time_window       INTEGER DEFAULT 45,
                    antiflood_action            TEXT DEFAULT 'mute',
                    antiflood_action_duration   INTEGER DEFAULT 3600,
                    antiflood_del_msg           BOOLEAN DEFAULT TRUE,
                    antispam_enabled            BOOLEAN DEFAULT FALSE,
                    antispam_action             TEXT DEFAULT 'mute',
                    antispam_score_threshold    INTEGER DEFAULT 5,
                    antilink_enabled            BOOLEAN DEFAULT FALSE,
                    antilink_action             TEXT DEFAULT 'delete',
                    antilink_warn               BOOLEAN DEFAULT TRUE,
                    antilink_allow_admins       BOOLEAN DEFAULT TRUE,
                    antilink_allow_tg_links     BOOLEAN DEFAULT FALSE,
                    antibot_enabled             BOOLEAN DEFAULT FALSE,
                    antibot_action              TEXT DEFAULT 'kick',
                    antiforward_enabled         BOOLEAN DEFAULT FALSE,
                    antiforward_action          TEXT DEFAULT 'delete',
                    antiforward_from_channels   BOOLEAN DEFAULT TRUE,
                    antiforward_from_users      BOOLEAN DEFAULT FALSE,
                    antiforward_from_bots       BOOLEAN DEFAULT TRUE,
                    antichannel_enabled         BOOLEAN DEFAULT FALSE,
                    antiarabic_enabled          BOOLEAN DEFAULT FALSE,
                    antiarabic_action           TEXT DEFAULT 'delete',
                    antisticker_enabled         BOOLEAN DEFAULT FALSE,
                    antisticker_limit           INTEGER DEFAULT 5,
                    antisticker_time_window     INTEGER DEFAULT 30,
                    antisticker_action          TEXT DEFAULT 'mute',
                    antigif_enabled             BOOLEAN DEFAULT FALSE,
                    antigif_limit               INTEGER DEFAULT 5,
                    antigif_time_window         INTEGER DEFAULT 30,
                    antigif_action              TEXT DEFAULT 'mute',
                    antinsfw_enabled            BOOLEAN DEFAULT FALSE,
                    antinsfw_action             TEXT DEFAULT 'delete',
                    slowmode_enabled            BOOLEAN DEFAULT FALSE,
                    slowmode_seconds            INTEGER DEFAULT 0,
                    slowmode_custom_enabled     BOOLEAN DEFAULT FALSE,
                    slowmode_custom_seconds     INTEGER DEFAULT 10,
                    total_flood_actions         BIGINT DEFAULT 0,
                    total_spam_actions          BIGINT DEFAULT 0,
                    total_link_deleted          BIGINT DEFAULT 0,
                    total_bot_kicked            BIGINT DEFAULT 0,
                    total_forward_deleted       BIGINT DEFAULT 0,
                    total_channel_banned        BIGINT DEFAULT 0,
                    total_arabic_deleted        BIGINT DEFAULT 0,
                    total_sticker_actions       BIGINT DEFAULT 0,
                    total_gif_actions           BIGINT DEFAULT 0,
                    total_nsfw_actions          BIGINT DEFAULT 0,
                    total_blacklist_actions     BIGINT DEFAULT 0,
                    created_at                  TIMESTAMP DEFAULT NOW(),
                    updated_at                  TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS blacklist_words (
                    id          SERIAL PRIMARY KEY,
                    chat_id     BIGINT NOT NULL,
                    word        TEXT NOT NULL,
                    added_by    BIGINT DEFAULT 0,
                    reason      TEXT DEFAULT '',
                    created_at  TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, word)
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS blacklist_settings (
                    chat_id         BIGINT PRIMARY KEY,
                    action          TEXT DEFAULT 'delete',
                    warn_enabled    BOOLEAN DEFAULT FALSE,
                    created_at      TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS whitelist_urls (
                    id          SERIAL PRIMARY KEY,
                    chat_id     BIGINT NOT NULL,
                    url         TEXT NOT NULL,
                    added_by    BIGINT DEFAULT 0,
                    created_at  TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, url)
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS approved_users (
                    id          SERIAL PRIMARY KEY,
                    chat_id     BIGINT NOT NULL,
                    user_id     BIGINT NOT NULL,
                    approved_by BIGINT DEFAULT 0,
                    created_at  TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, user_id)
                );
            """)

            logger.info("✅ All database tables created successfully!")

    async def close(self) -> None:
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self._ready = False
            logger.info("Database connection closed.")

    async def _ensure_connected(self) -> None:
        """Make sure pool is initialized before any query"""
        if not self.pool or not self._ready:
            logger.warning("⚠️ DB pool not ready, reconnecting...")
            await self.connect()
        if not self.pool:
            raise RuntimeError("Database pool is unavailable. Check DATABASE_URL and DB connection.")

    async def execute(self, query: str, *args) -> str:
        """Execute a query"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        """Fetch multiple rows"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    # ═══════════════════════════════════════════════════════════
    # USER OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def upsert_user(
        self, user_id: int, username: str = "",
        first_name: str = "", last_name: str = "",
        is_bot: bool = False, language_code: str = "en"
    ) -> None:
        """Insert or update user"""
        await self.execute("""
            INSERT INTO users (
                user_id, username, first_name, last_name,
                is_bot, language_code, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                is_bot = EXCLUDED.is_bot,
                language_code = EXCLUDED.language_code,
                updated_at = NOW();
        """, user_id, username or "", first_name or "",
            last_name or "", is_bot, language_code or "en")

    async def get_user(self, user_id: int) -> Optional[asyncpg.Record]:
        """Get user by ID"""
        return await self.fetchrow(
            "SELECT * FROM users WHERE user_id = $1;", user_id
        )

    async def get_all_users(self) -> list:
        """Get all users"""
        return await self.fetch("SELECT * FROM users;")

    async def get_user_count(self) -> int:
        """Get total user count"""
        return await self.fetchval("SELECT COUNT(*) FROM users;")

    async def increment_user_messages(self, user_id: int) -> None:
        """Increment user's message count"""
        await self.execute("""
            UPDATE users SET total_messages = total_messages + 1,
            updated_at = NOW() WHERE user_id = $1;
        """, user_id)

    # ═══════════════════════════════════════════════════════════
    # CHAT OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def upsert_chat(
        self, chat_id: int, chat_title: str = "",
        chat_type: str = "", chat_username: str = ""
    ) -> None:
        """Insert or update chat"""
        await self.execute("""
            INSERT INTO chats (
                chat_id, chat_title, chat_type,
                chat_username, updated_at
            ) VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (chat_id) DO UPDATE SET
                chat_title = EXCLUDED.chat_title,
                chat_type = EXCLUDED.chat_type,
                chat_username = EXCLUDED.chat_username,
                updated_at = NOW();
        """, chat_id, chat_title or "", chat_type or "",
            chat_username or "")

    async def get_chat(self, chat_id: int) -> Optional[asyncpg.Record]:
        """Get chat by ID"""
        return await self.fetchrow(
            "SELECT * FROM chats WHERE chat_id = $1;", chat_id
        )

    async def get_all_chats(self) -> list:
        """Get all chats"""
        return await self.fetch(
            "SELECT * FROM chats WHERE is_active = TRUE;"
        )

    async def get_chat_count(self) -> int:
        """Get total chat count"""
        return await self.fetchval(
            "SELECT COUNT(*) FROM chats WHERE is_active = TRUE;"
        )

    async def deactivate_chat(self, chat_id: int) -> None:
        """Mark chat as inactive"""
        await self.execute("""
            UPDATE chats SET is_active = FALSE, updated_at = NOW()
            WHERE chat_id = $1;
        """, chat_id)

    # ═══════════════════════════════════════════════════════════
    # SUDO OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def add_sudo(self, user_id: int, added_by: int,
                       reason: str = "") -> bool:
        """Add sudo user"""
        try:
            await self.execute("""
                INSERT INTO sudo_users (user_id, added_by, reason)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, user_id, added_by, reason)
            return True
        except Exception:
            return False

    async def remove_sudo(self, user_id: int) -> bool:
        """Remove sudo user"""
        result = await self.execute(
            "DELETE FROM sudo_users WHERE user_id = $1;", user_id
        )
        return result == "DELETE 1"

    async def get_sudos(self) -> List[int]:
        """Get all sudo user IDs"""
        rows = await self.fetch("SELECT user_id FROM sudo_users;")
        return [row["user_id"] for row in rows]

    async def is_sudo(self, user_id: int) -> bool:
        """Check if user is sudo"""
        result = await self.fetchval(
            "SELECT user_id FROM sudo_users WHERE user_id = $1;",
            user_id
        )
        return result is not None

    # ═══════════════════════════════════════════════════════════
    # SUPPORT OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def add_support(self, user_id: int, added_by: int,
                          reason: str = "") -> bool:
        """Add support user"""
        try:
            await self.execute("""
                INSERT INTO support_users (user_id, added_by, reason)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, user_id, added_by, reason)
            return True
        except Exception:
            return False

    async def remove_support(self, user_id: int) -> bool:
        """Remove support user"""
        result = await self.execute(
            "DELETE FROM support_users WHERE user_id = $1;", user_id
        )
        return result == "DELETE 1"

    async def get_supports(self) -> List[int]:
        """Get all support user IDs"""
        rows = await self.fetch("SELECT user_id FROM support_users;")
        return [row["user_id"] for row in rows]

    async def is_support(self, user_id: int) -> bool:
        """Check if user is support"""
        result = await self.fetchval(
            "SELECT user_id FROM support_users WHERE user_id = $1;",
            user_id
        )
        return result is not None

    # ═══════════════════════════════════════════════════════════
    # STATS OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def increment_stat(self, stat_key: str,
                             increment: int = 1) -> None:
        """Increment a stat counter"""
        await self.execute("""
            INSERT INTO bot_stats (stat_key, stat_value, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (stat_key) DO UPDATE SET
                stat_value = bot_stats.stat_value + $2,
                updated_at = NOW();
        """, stat_key, increment)

    async def get_stat(self, stat_key: str) -> int:
        """Get a stat value"""
        val = await self.fetchval(
            "SELECT stat_value FROM bot_stats WHERE stat_key = $1;",
            stat_key
        )
        return val or 0

    async def get_all_stats(self) -> Dict[str, int]:
        """Get all stats"""
        rows = await self.fetch("SELECT stat_key, stat_value FROM bot_stats;")
        return {row["stat_key"]: row["stat_value"] for row in rows}

    # ═══════════════════════════════════════════════════════════
    # CHAT SETTINGS OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def update_chat_setting(
        self, chat_id: int, setting: str, value: Any
    ) -> None:
        """Update a specific chat setting"""
        # Validate setting name to prevent SQL injection
        valid_settings = [
            'welcome_enabled', 'welcome_text', 'welcome_media',
            'welcome_media_type', 'welcome_buttons',
            'welcome_delete_after', 'goodbye_enabled', 'goodbye_text',
            'clean_welcome', 'last_welcome_msg_id',
            'antiflood_enabled', 'antiflood_limit', 'antiflood_time',
            'antiflood_action', 'antiflood_action_duration',
            'antispam_enabled', 'anti_channel_pin',
            'anti_linked_channel', 'locks',
            'blacklist_mode', 'blacklist_action_duration',
            'rules', 'log_channel', 'clean_commands',
            'strict_admin', 'report_enabled',
            'admin_cache', 'admin_cache_time',
            'night_mode', 'night_start', 'night_end',
            'slowmode_enabled', 'slowmode_seconds',
            'no_link_preview', 'auto_delete_enabled',
            'auto_delete_seconds'
        ]
        if setting not in valid_settings:
            raise ValueError(f"Invalid setting: {setting}")

        await self.execute(f"""
            UPDATE chats SET {setting} = $1, updated_at = NOW()
            WHERE chat_id = $2;
        """, value, chat_id)

    async def get_chat_setting(
        self, chat_id: int, setting: str
    ) -> Any:
        """Get a specific chat setting"""
        row = await self.fetchrow(
            "SELECT * FROM chats WHERE chat_id = $1;", chat_id
        )
        if row and setting in dict(row):
            return row[setting]
        return None


# ═══════════════════════════════════════════════════════════════
# ◈ GLOBAL DATABASE INSTANCE
# ═══════════════════════════════════════════════════════════════

db = DatabaseManager()


# ═══════════════════════════════════════════════════════════════
# ◈ CACHE MANAGER
# ═══════════════════════════════════════════════════════════════

class CacheManager:
    """
    ╔═══════════════════════════════════════╗
    ║  In-memory cache for fast access      ║
    ║  Reduces database queries             ║
    ╚═══════════════════════════════════════╝
    """

    def __init__(self):
        self._sudo_users: Set[int] = set()
        self._support_users: Set[int] = set()
        self._gbanned_users: Set[int] = set()
        self._gmuted_users: Set[int] = set()
        self._admin_cache: Dict[int, Dict[int, ChatMember]] = {}
        self._admin_cache_time: Dict[int, float] = {}
        self._chat_settings: Dict[int, dict] = {}
        self._flood_counter: Dict[str, List[float]] = defaultdict(list)
        self._command_cooldown: Dict[str, float] = {}
        self._disabled_commands: Dict[int, Set[str]] = defaultdict(set)
        self.ADMIN_CACHE_TTL = 600  # 10 minutes

    async def load_from_db(self) -> None:
        """Load cache from database"""
        try:
            # Load sudo users
            sudos = await db.get_sudos()
            self._sudo_users = set(sudos)
            self._sudo_users.add(OWNER_ID)

            # Load support users
            supports = await db.get_supports()
            self._support_users = set(supports)

            # Load gbanned users
            rows = await db.fetch(
                "SELECT user_id FROM gbans;"
            )
            self._gbanned_users = {r["user_id"] for r in rows}

            # Load gmuted users
            rows = await db.fetch(
                "SELECT user_id FROM gmutes;"
            )
            self._gmuted_users = {r["user_id"] for r in rows}

            # Load disabled commands per chat
            rows = await db.fetch(
                "SELECT chat_id, command FROM disabled_commands;"
            )
            for row in rows:
                self._disabled_commands[row["chat_id"]].add(
                    row["command"]
                )

            logger.info(
                f"✅ Cache loaded: {len(self._sudo_users)} sudos, "
                f"{len(self._support_users)} supports, "
                f"{len(self._gbanned_users)} gbanned"
            )
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")

    def is_owner(self, user_id: int) -> bool:
        return user_id == OWNER_ID

    def is_sudo(self, user_id: int) -> bool:
        return user_id in self._sudo_users or user_id == OWNER_ID

    def is_support(self, user_id: int) -> bool:
        return (
            user_id in self._support_users
            or self.is_sudo(user_id)
        )

    def is_gbanned(self, user_id: int) -> bool:
        return user_id in self._gbanned_users

    def is_gmuted(self, user_id: int) -> bool:
        return user_id in self._gmuted_users

    def add_sudo(self, user_id: int) -> None:
        self._sudo_users.add(user_id)

    def remove_sudo(self, user_id: int) -> None:
        self._sudo_users.discard(user_id)

    def add_support(self, user_id: int) -> None:
        self._support_users.add(user_id)

    def remove_support(self, user_id: int) -> None:
        self._support_users.discard(user_id)

    def add_gban(self, user_id: int) -> None:
        self._gbanned_users.add(user_id)

    def remove_gban(self, user_id: int) -> None:
        self._gbanned_users.discard(user_id)

    def add_gmute(self, user_id: int) -> None:
        self._gmuted_users.add(user_id)

    def remove_gmute(self, user_id: int) -> None:
        self._gmuted_users.discard(user_id)

    async def get_admin_cache(
        self, chat_id: int, bot: Bot
    ) -> Dict[int, ChatMember]:
        """Get cached admins or refresh if stale"""
        now = time.time()
        if (
            chat_id in self._admin_cache
            and chat_id in self._admin_cache_time
            and now - self._admin_cache_time[chat_id] < self.ADMIN_CACHE_TTL
        ):
            return self._admin_cache[chat_id]

        try:
            admins = await bot.get_chat_administrators(chat_id)
            admin_dict = {}
            for admin in admins:
                admin_dict[admin.user.id] = admin
            self._admin_cache[chat_id] = admin_dict
            self._admin_cache_time[chat_id] = now
            return admin_dict
        except Exception as e:
            logger.error(
                f"Failed to get admins for {chat_id}: {e}"
            )
            return self._admin_cache.get(chat_id, {})

    def invalidate_admin_cache(self, chat_id: int) -> None:
        """Force refresh admin cache for a chat"""
        self._admin_cache.pop(chat_id, None)
        self._admin_cache_time.pop(chat_id, None)

    def check_flood(
        self, chat_id: int, user_id: int,
        limit: int = 10, window: int = 45
    ) -> bool:
        """Check if user is flooding. Returns True if flooding."""
        key = f"{chat_id}:{user_id}"
        now = time.time()
        self._flood_counter[key] = [
            t for t in self._flood_counter[key]
            if now - t < window
        ]
        self._flood_counter[key].append(now)
        return len(self._flood_counter[key]) > limit

    def reset_flood(self, chat_id: int, user_id: int) -> None:
        """Reset flood counter for user"""
        key = f"{chat_id}:{user_id}"
        self._flood_counter.pop(key, None)

    def check_cooldown(
        self, key: str, cooldown: float = 3.0
    ) -> bool:
        """Check command cooldown. Returns True if on cooldown."""
        now = time.time()
        if key in self._command_cooldown:
            if now - self._command_cooldown[key] < cooldown:
                return True
        self._command_cooldown[key] = now
        return False

    def is_command_disabled(
        self, chat_id: int, command: str
    ) -> bool:
        """Check if command is disabled in chat"""
        return command in self._disabled_commands.get(chat_id, set())

    def disable_command(self, chat_id: int, command: str) -> None:
        self._disabled_commands[chat_id].add(command)

    def enable_command(self, chat_id: int, command: str) -> None:
        self._disabled_commands[chat_id].discard(command)


# ═══════════════════════════════════════════════════════════════
# ◈ GLOBAL CACHE INSTANCE
# ═══════════════════════════════════════════════════════════════

cache = CacheManager()


# ═══════════════════════════════════════════════════════════════
# ◈ PERMISSION CHECKER UTILITIES
# ═══════════════════════════════════════════════════════════════

class Permissions:
    """
    ╔═══════════════════════════════════════╗
    ║  Advanced permission checking system  ║
    ║  Handles all role verification        ║
    ╚═══════════════════════════════════════╝
    """

    @staticmethod
    async def get_user_role(
        chat_id: int, user_id: int, bot: Bot
    ) -> UserRole:
        """Determine user's role in chat"""
        if cache.is_owner(user_id):
            return UserRole.OWNER
        if cache.is_sudo(user_id):
            return UserRole.SUDO
        if cache.is_support(user_id):
            return UserRole.SUPPORT

        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if isinstance(member, ChatMemberOwner):
                return UserRole.OWNER
            elif isinstance(member, ChatMemberAdministrator):
                return UserRole.ADMIN
            elif isinstance(member, ChatMemberMember):
                return UserRole.MEMBER
            elif isinstance(member, ChatMemberRestricted):
                return UserRole.RESTRICTED
            elif isinstance(member, ChatMemberBanned):
                return UserRole.BANNED
            elif isinstance(member, ChatMemberLeft):
                return UserRole.LEFT
            else:
                return UserRole.MEMBER
        except Exception:
            return UserRole.MEMBER

    @staticmethod
    async def is_user_admin(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user is admin in chat"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        return user_id in admins

    @staticmethod
    async def is_user_owner(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user is the chat owner"""
        if cache.is_owner(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            return isinstance(admins[user_id], ChatMemberOwner)
        return False

    @staticmethod
    async def is_bot_admin(chat_id: int, bot: Bot) -> bool:
        """Check if the bot is admin in chat"""
        try:
            bot_member = await bot.get_chat_member(chat_id, bot.id)
            return isinstance(
                bot_member,
                (ChatMemberAdministrator, ChatMemberOwner)
            )
        except Exception:
            return False

    @staticmethod
    async def has_ban_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has ban permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_restrict_members
        return False

    @staticmethod
    async def has_delete_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has delete permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_delete_messages
        return False

    @staticmethod
    async def has_pin_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has pin permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_pin_messages
        return False

    @staticmethod
    async def has_invite_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has invite users permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_invite_users
        return False

    @staticmethod
    async def has_promote_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has promote permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_promote_members
        return False

    @staticmethod
    async def has_manage_chat_permission(
        chat_id: int, user_id: int, bot: Bot
    ) -> bool:
        """Check if user has manage chat permission"""
        if cache.is_owner(user_id) or cache.is_sudo(user_id):
            return True

        admins = await cache.get_admin_cache(chat_id, bot)
        if user_id in admins:
            admin = admins[user_id]
            if isinstance(admin, ChatMemberOwner):
                return True
            if isinstance(admin, ChatMemberAdministrator):
                return admin.can_manage_chat
        return False

    @staticmethod
    async def can_restrict_user(
        chat_id: int, admin_id: int, target_id: int, bot: Bot
    ) -> Tuple[bool, str]:
        """
        Full check: can admin restrict target?
        Returns (can_restrict, error_message)
        """
        # Owner can't be restricted
        if cache.is_owner(target_id):
            return (
                False,
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Cannot restrict the bot owner')}!"
            )

        # Sudo can't be restricted by non-owner
        if cache.is_sudo(target_id) and not cache.is_owner(admin_id):
            return (
                False,
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Cannot restrict a sudo user')}!"
            )

        # Support can't be restricted by non-sudo
        if (
            cache.is_support(target_id)
            and not cache.is_sudo(admin_id)
        ):
            return (
                False,
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Cannot restrict a support user')}!"
            )

        # Check if bot is admin
        if not await Permissions.is_bot_admin(chat_id, bot):
            return (
                False,
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('I am not an admin in this chat')}!\n"
                f"{Symbols.BULLET} {StyleFont.small_caps('please make me admin with ban rights')}."
            )

        # Check if admin has ban permission
        if not await Permissions.has_ban_permission(
            chat_id, admin_id, bot
        ):
            return (
                False,
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('You dont have ban rights')}!"
            )

        # Check target is not admin
        admins = await cache.get_admin_cache(chat_id, bot)
        if target_id in admins:
            target_admin = admins[target_id]
            if isinstance(target_admin, ChatMemberOwner):
                return (
                    False,
                    f"{Symbols.CROSS3} "
                    f"{StyleFont.mixed_bold_smallcaps('Cannot restrict the group owner')}!"
                )
            if isinstance(target_admin, ChatMemberAdministrator):
                # Check if admin was promoted by bot
                if not cache.is_sudo(admin_id) and not cache.is_owner(admin_id):
                    return (
                        False,
                        f"{Symbols.CROSS3} "
                        f"{StyleFont.mixed_bold_smallcaps('Cannot restrict another admin')}!"
                    )

        # Check bot's own ban rights
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        if isinstance(bot_member, ChatMemberAdministrator):
            if not bot_member.can_restrict_members:
                return (
                    False,
                    f"{Symbols.CROSS3} "
                    f"{StyleFont.mixed_bold_smallcaps('I dont have restrict rights')}!\n"
                    f"{Symbols.BULLET} {StyleFont.small_caps('give me ban users permission')}."
                )

        return (True, "")


# ═══════════════════════════════════════════════════════════════
# ◈ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_user_mention(user: User) -> str:
    """Get HTML mention for user"""
    name = html_escape(user.first_name or "User")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def get_user_full_name(user: User) -> str:
    """Get full name of user"""
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    return name.strip() or "Unknown"


def format_time_delta(seconds: Union[int, float]) -> str:
    """Format seconds into human-readable time"""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} {StyleFont.small_caps('seconds')}"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        result = f"{mins} {StyleFont.small_caps('minutes')}"
        if secs:
            result += f" {secs} {StyleFont.small_caps('seconds')}"
        return result
    elif seconds < 86400:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        result = f"{hours} {StyleFont.small_caps('hours')}"
        if mins:
            result += f" {mins} {StyleFont.small_caps('minutes')}"
        return result
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        result = f"{days} {StyleFont.small_caps('days')}"
        if hours:
            result += f" {hours} {StyleFont.small_caps('hours')}"
        return result


def format_number(num: int) -> str:
    """Format number with commas and style"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)


def parse_time_arg(arg: str) -> Optional[int]:
    """
    Parse time argument like 1h, 30m, 2d, 1w
    Returns seconds or None
    """
    if not arg:
        return None

    match = re.match(r'^(\d+)([smhdw])$', arg.lower().strip())
    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
    }

    return amount * multipliers.get(unit, 0)


async def extract_user_and_reason(
    message: Message, bot: Bot
) -> Tuple[Optional[int], Optional[str], Optional[User]]:
    """
    Extract target user ID and reason from message.
    Supports:
    - Reply to message
    - @username
    - user_id
    - /cmd @user reason
    - /cmd user_id reason
    """
    user_id = None
    reason = None
    user_obj = None

    # If replying to a message
    if message.reply_to_message:
        user_obj = message.reply_to_message.from_user
        if user_obj:
            user_id = user_obj.id
        # Check for reason in the command text
        args = message.text.split(None, 1)
        if len(args) > 1:
            reason = args[1].strip()
        return user_id, reason, user_obj

    # Extract from command arguments
    args = message.text.split(None)
    if len(args) < 2:
        return None, None, None

    target = args[1]

    # If @username
    if target.startswith("@"):
        username = target[1:]
        try:
            chat = await bot.get_chat(f"@{username}")
            user_id = chat.id
            user_obj = None  # We don't have full User object
        except Exception:
            return None, None, None
    else:
        # If user_id
        try:
            user_id = int(target)
        except ValueError:
            return None, None, None

    # Extract reason
    if len(args) > 2:
        reason = " ".join(args[2:]).strip()

    # Try to get user object
    if user_id and not user_obj:
        try:
            chat = await bot.get_chat(user_id)
            # Create a minimal user-like info
            user_obj = chat
        except Exception:
            pass

    return user_id, reason, user_obj


def get_readable_time(seconds: int) -> str:
    """Get human readable time from seconds"""
    periods = [
        ('ᴡ', 604800), ('ᴅ', 86400),
        ('ʜ', 3600), ('ᴍ', 60), ('s', 1)
    ]
    result = []
    for suffix, period in periods:
        if seconds >= period:
            count = seconds // period
            seconds %= period
            result.append(f"{count}{suffix}")
    return " ".join(result) if result else "0s"


# ═══════════════════════════════════════════════════════════════
# ◈ LOGGER - SEND LOGS TO CHANNEL
# ═══════════════════════════════════════════════════════════════

class BotLogger:
    """
    ╔═══════════════════════════════════════╗
    ║  Stylish log messages to channel      ║
    ╚═══════════════════════════════════════╝
    """

    @staticmethod
    async def log(
        bot: Bot,
        log_type: LogType,
        chat: Optional[Chat] = None,
        admin: Optional[User] = None,
        user: Optional[User] = None,
        reason: str = "",
        extra: str = "",
    ) -> None:
        """Send a styled log message to log channel"""
        if not LOG_CHANNEL_ID:
            return

        try:
            emoji = log_type.value
            action = log_type.name.replace("_", " ").title()
            styled_action = StyleFont.bold_sans(action)

            text = (
                f"{Symbols.STAR} {styled_action} {emoji}\n"
                f"{Symbols.divider(6)}\n"
            )

            if chat:
                chat_name = html_escape(chat.title or "PM")
                text += (
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
                    f"{chat_name}\n"
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Chat Id')}: "
                    f"<code>{chat.id}</code>\n"
                )

            if admin:
                admin_mention = get_user_mention(admin)
                text += (
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
                    f"{admin_mention}\n"
                )

            if user:
                user_mention = get_user_mention(user)
                text += (
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: "
                    f"{user_mention}\n"
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
                    f"<code>{user.id}</code>\n"
                )

            if reason:
                text += (
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                    f"{html_escape(reason)}\n"
                )

            if extra:
                text += (
                    f"{Symbols.BOX_V} {Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Extra')}: "
                    f"{extra}\n"
                )

            text += (
                f"{Symbols.divider(6)}\n"
                f"{Symbols.CLOCK} "
                f"{StyleFont.small_caps(datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))}\n"
                f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
            )

            await bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Failed to send log: {e}")


bot_logger = BotLogger()


# ═══════════════════════════════════════════════════════════════
# ◈ DECORATORS
# ═══════════════════════════════════════════════════════════════

def owner_only(func: Callable) -> Callable:
    """Decorator: Only bot owner can use"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        if not user or not cache.is_owner(user.id):
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('This command is owner only')}!\n"
                f"{Symbols.CROWN} {StyleFont.small_caps('only the bot owner can use this')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def sudo_only(func: Callable) -> Callable:
    """Decorator: Only sudo users can use"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        if not user or not cache.is_sudo(user.id):
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('This command is sudo only')}!\n"
                f"{Symbols.SWORDS} {StyleFont.small_caps('only sudo users can use this')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def support_only(func: Callable) -> Callable:
    """Decorator: Only support users can use"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        if not user or not cache.is_support(user.id):
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('This command is support only')}!\n"
                f"{Symbols.SHIELD} "
                f"{StyleFont.small_caps('only support users can use this')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def admin_only(func: Callable) -> Callable:
    """Decorator: Only admins can use"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user
        chat = update.effective_chat
        message = update.effective_message

        if not user or not chat:
            return

        # Allow in private chat
        if chat.type == ChatType.PRIVATE:
            return await func(update, context)

        # Check admin
        is_admin = await Permissions.is_user_admin(
            chat.id, user.id, context.bot
        )
        if not is_admin:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Admin rights required')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('you need to be an admin to use this')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def group_only(func: Callable) -> Callable:
    """Decorator: Only works in groups"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        chat = update.effective_chat
        if not chat or chat.type == ChatType.PRIVATE:
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('This command only works in groups')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('add me to a group and try again')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def private_only(func: Callable) -> Callable:
    """Decorator: Only works in private chat"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        chat = update.effective_chat
        if not chat or chat.type != ChatType.PRIVATE:
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('This command only works in PM')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('send me a private message')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def bot_admin_required(func: Callable) -> Callable:
    """Decorator: Bot must be admin"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        chat = update.effective_chat
        if not chat or chat.type == ChatType.PRIVATE:
            return await func(update, context)

        is_admin = await Permissions.is_bot_admin(
            chat.id, context.bot
        )
        if not is_admin:
            await update.effective_message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('I need admin rights')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('promote me as admin with proper permissions')}.",
                parse_mode=ParseMode.HTML,
            )
            return
        return await func(update, context)
    return wrapper


def cooldown(seconds: float = 3.0):
    """Decorator: Add cooldown to command"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
        ):
            user = update.effective_user
            if not user:
                return
            # Skip cooldown for owner/sudo
            if cache.is_sudo(user.id):
                return await func(update, context)

            key = f"{func.__name__}:{user.id}"
            if cache.check_cooldown(key, seconds):
                return  # Silently ignore
            return await func(update, context)
        return wrapper
    return decorator


def track_command(func: Callable) -> Callable:
    """Decorator: Track command usage in stats"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        try:
            await db.increment_stat("total_commands")
        except Exception:
            pass
        return await func(update, context)
    return wrapper


def check_disabled(func: Callable) -> Callable:
    """Decorator: Check if command is disabled in chat"""
    @functools.wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        chat = update.effective_chat
        user = update.effective_user
        if not chat or not user:
            return await func(update, context)

        if chat.type == ChatType.PRIVATE:
            return await func(update, context)

        # Admins bypass disabled commands
        if cache.is_sudo(user.id):
            return await func(update, context)

        cmd_name = func.__name__.replace("cmd_", "")
        if cache.is_command_disabled(chat.id, cmd_name):
            return  # Silently ignore
        return await func(update, context)
    return wrapper


# ═══════════════════════════════════════════════════════════════
# ◈ TRACK USER & CHAT ON EVERY MESSAGE
# ═══════════════════════════════════════════════════════════════

async def track_user_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Track every user and chat that interacts with the bot"""
    try:
        user = update.effective_user
        chat = update.effective_chat

        if user and not user.is_bot:
            await db.upsert_user(
                user_id=user.id,
                username=user.username or "",
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                is_bot=user.is_bot,
                language_code=user.language_code or "en",
            )
            await db.increment_user_messages(user.id)

        if chat and chat.type != ChatType.PRIVATE:
            await db.upsert_chat(
                chat_id=chat.id,
                chat_title=chat.title or "",
                chat_type=chat.type,
                chat_username=chat.username or "",
            )

        await db.increment_stat("total_messages")
    except Exception as e:
        logger.debug(f"Track error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈ HELP MENU DATA - ALL SECTIONS
# ═══════════════════════════════════════════════════════════════

HELP_SECTIONS = OrderedDict({
    "admin": {
        "title": "𝐀ᴅᴍɪɴ 𝐂ᴏɴᴛʀᴏʟ",
        "emoji": "👑",
        "description": (
            "Full admin management commands including "
            "ban, kick, mute, promote, demote and more."
        ),
        "commands": [
            ("/ban", "Ban a user from the group"),
            ("/unban", "Unban a user"),
            ("/tban", "Temporarily ban a user"),
            ("/kick", "Kick a user"),
            ("/mute", "Mute a user"),
            ("/unmute", "Unmute a user"),
            ("/tmute", "Temporarily mute"),
            ("/promote", "Promote user to admin"),
            ("/demote", "Demote an admin"),
            ("/title", "Set custom admin title"),
            ("/adminlist", "List all admins"),
            ("/invitelink", "Get group invite link"),
            ("/admincache", "Refresh admin cache"),
        ],
    },
    "welcome": {
        "title": "𝐖ᴇʟᴄᴏᴍᴇ 𝐒ʏsᴛᴇᴍ",
        "emoji": "👋",
        "description": (
            "Customize welcome and goodbye messages "
            "with media, buttons and variables."
        ),
        "commands": [
            ("/welcome", "Toggle welcome on/off"),
            ("/setwelcome", "Set welcome message"),
            ("/resetwelcome", "Reset to default"),
            ("/goodbye", "Toggle goodbye on/off"),
            ("/setgoodbye", "Set goodbye message"),
            ("/resetgoodbye", "Reset to default"),
            ("/cleanwelcome", "Delete old welcome msgs"),
        ],
    },
    "antiflood": {
        "title": "𝐀ɴᴛɪ-𝐅ʟᴏᴏᴅ",
        "emoji": "🌊",
        "description": (
            "Protect your group from message flooding."
        ),
        "commands": [
            ("/antiflood", "Toggle antiflood"),
            ("/setflood", "Set flood limit"),
            ("/setfloodaction", "Set action on flood"),
            ("/floodmode", "View current settings"),
        ],
    },
    "notes": {
        "title": "𝐍ᴏᴛᴇs",
        "emoji": "📝",
        "description": (
            "Save and retrieve notes using hashtags "
            "or the /get command."
        ),
        "commands": [
            ("/save", "Save a note"),
            ("/get", "Get a note"),
            ("/notes", "List all notes"),
            ("/clear", "Delete a note"),
            ("/clearall", "Delete all notes"),
            ("#notename", "Quick get note"),
        ],
    },
    "filters": {
        "title": "𝐅ɪʟᴛᴇʀs",
        "emoji": "🔍",
        "description": (
            "Auto-reply with custom messages "
            "when keywords are triggered."
        ),
        "commands": [
            ("/filter", "Add a filter"),
            ("/filters", "List all filters"),
            ("/stop", "Remove a filter"),
            ("/stopall", "Remove all filters"),
        ],
    },
    "warns": {
        "title": "𝐖ᴀʀɴɪɴɢs",
        "emoji": "⚠️",
        "description": (
            "Warning system with configurable limits "
            "and actions."
        ),
        "commands": [
            ("/warn", "Warn a user"),
            ("/unwarn", "Remove last warn"),
            ("/warns", "Check user warnings"),
            ("/resetwarns", "Reset user warns"),
            ("/warnlimit", "Set warn limit"),
            ("/warnaction", "Set warn action"),
            ("/warnlist", "List warned users"),
        ],
    },
    "blacklist": {
        "title": "𝐁ʟᴀᴄᴋʟɪsᴛ",
        "emoji": "🚫",
        "description": (
            "Blacklist words/phrases that will be "
            "auto-deleted."
        ),
        "commands": [
            ("/blacklist", "List blacklisted words"),
            ("/addblacklist", "Add to blacklist"),
            ("/rmblacklist", "Remove from blacklist"),
            ("/blaction", "Set blacklist action"),
        ],
    },
    "locks": {
        "title": "𝐋ᴏᴄᴋs",
        "emoji": "🔒",
        "description": (
            "Lock different types of content "
            "in your group."
        ),
        "commands": [
            ("/lock", "Lock a type"),
            ("/unlock", "Unlock a type"),
            ("/locks", "View current locks"),
            ("/locktypes", "List lockable types"),
        ],
    },
    "rules": {
        "title": "𝐑ᴜʟᴇs",
        "emoji": "📋",
        "description": "Set and view group rules.",
        "commands": [
            ("/rules", "View rules"),
            ("/setrules", "Set rules"),
            ("/clearrules", "Clear rules"),
        ],
    },
    "gban": {
        "title": "𝐆ʟᴏʙᴀʟ 𝐁ᴀɴs",
        "emoji": "🔨",
        "description": (
            "Globally ban users across all groups "
            "where bot is admin."
        ),
        "commands": [
            ("/gban", "Globally ban a user"),
            ("/ungban", "Remove global ban"),
            ("/gbanlist", "List gbanned users"),
            ("/gmute", "Globally mute a user"),
            ("/ungmute", "Remove global mute"),
        ],
    },
    "purge": {
        "title": "𝐏ᴜʀɢᴇ",
        "emoji": "🧹",
        "description": "Mass delete messages.",
        "commands": [
            ("/purge", "Purge from reply to end"),
            ("/spurge", "Silent purge"),
            ("/del", "Delete replied message"),
            ("/purgefrom", "Purge from message"),
            ("/purgeto", "Purge to message"),
        ],
    },
    "pin": {
        "title": "𝐏ɪɴs",
        "emoji": "📌",
        "description": "Pin and unpin messages.",
        "commands": [
            ("/pin", "Pin a message"),
            ("/unpin", "Unpin a message"),
            ("/unpinall", "Unpin all messages"),
            ("/pinned", "Get pinned message"),
            ("/permapin", "Pin text permanently"),
        ],
    },
    "reports": {
        "title": "𝐑ᴇᴘᴏʀᴛs",
        "emoji": "📢",
        "description": "Report bad users to admins.",
        "commands": [
            ("/report", "Report a user"),
            ("/reports", "Toggle reports on/off"),
        ],
    },
    "afk": {
        "title": "𝐀𝐅𝐊",
        "emoji": "💤",
        "description": "Away From Keyboard system.",
        "commands": [
            ("/afk", "Set AFK status"),
            ("/afk [reason]", "Set AFK with reason"),
        ],
    },
    "misc": {
        "title": "𝐌ɪsᴄ",
        "emoji": "🎯",
        "description": "Miscellaneous utility commands.",
        "commands": [
            ("/id", "Get user/chat ID"),
            ("/info", "Get user info"),
            ("/ping", "Check bot latency"),
            ("/alive", "Check if bot is running"),
            ("/stats", "Bot statistics"),
        ],
    },
    "sudo": {
        "title": "𝐒ᴜᴅᴏ & 𝐎ᴡɴᴇʀ",
        "emoji": "⚡",
        "description": (
            "Owner and sudo user management commands."
        ),
        "commands": [
            ("/addsudo", "Add sudo user"),
            ("/rmsudo", "Remove sudo user"),
            ("/sudolist", "List sudo users"),
            ("/addsupport", "Add support user"),
            ("/rmsupport", "Remove support user"),
            ("/supportlist", "List support users"),
            ("/broadcast", "Broadcast message"),
            ("/chatlist", "List all chats"),
            ("/leave", "Leave a chat"),
            ("/logs", "Get bot logs"),
        ],
    },
    "disable": {
        "title": "𝐃ɪsᴀʙʟᴇ 𝐂ᴍᴅs",
        "emoji": "🚫",
        "description": (
            "Disable/enable specific commands in chat."
        ),
        "commands": [
            ("/disable", "Disable a command"),
            ("/enable", "Enable a command"),
            ("/disabled", "List disabled commands"),
            ("/enableall", "Enable all commands"),
        ],
    },
    "connection": {
        "title": "𝐂ᴏɴɴᴇᴄᴛɪᴏɴ",
        "emoji": "🔗",
        "description": (
            "Connect to a group from PM to manage it."
        ),
        "commands": [
            ("/connect", "Connect to a group"),
            ("/disconnect", "Disconnect"),
            ("/connection", "View connection"),
        ],
    },
    "approve": {
        "title": "𝐀ᴘᴘʀᴏᴠᴀʟs",
        "emoji": "✅",
        "description": (
            "Approve users to bypass locks and antiflood."
        ),
        "commands": [
            ("/approve", "Approve a user"),
            ("/unapprove", "Unapprove a user"),
            ("/approved", "List approved users"),
        ],
    },
    "federation": {
        "title": "𝐅ᴇᴅᴇʀᴀᴛɪᴏɴs",
        "emoji": "🏛️",
        "description": (
            "Create federations and share banlists."
        ),
        "commands": [
            ("/newfed", "Create new federation"),
            ("/delfed", "Delete federation"),
            ("/fedinfo", "Federation info"),
            ("/joinfed", "Join federation"),
            ("/leavefed", "Leave federation"),
            ("/fban", "Federation ban"),
            ("/unfban", "Federation unban"),
            ("/fedadmins", "Fed admin list"),
            ("/fedpromote", "Promote fed admin"),
            ("/feddemote", "Demote fed admin"),
            ("/fbanlist", "List fed bans"),
        ],
    },
    "stickers": {
        "title": "𝐒ᴛɪᴄᴋᴇʀs",
        "emoji": "🎨",
        "description": "Sticker utilities.",
        "commands": [
            ("/stickerid", "Get sticker ID"),
            ("/getsticker", "Get sticker as PNG"),
            ("/kang", "Kang a sticker"),
        ],
    },
    "fun": {
        "title": "𝐅ᴜɴ",
        "emoji": "🎮",
        "description": "Fun commands and games.",
        "commands": [
            ("/roll", "Roll a dice"),
            ("/flip", "Flip a coin"),
            ("/truth", "Truth question"),
            ("/dare", "Dare challenge"),
            ("/quote", "Random quote"),
            ("/joke", "Random joke"),
            ("/8ball", "Magic 8 ball"),
            ("/decide", "Yes or no"),
        ],
    },
    "extra": {
        "title": "𝐄xᴛʀᴀ 𝐅ᴇᴀᴛᴜʀᴇs",
        "emoji": "🌟",
        "description": "Extra bonus features.",
        "commands": [
            ("/repo", "Source code"),
            ("/donate", "Support development"),
            ("/covid", "COVID-19 stats"),
            ("/weather", "Weather info"),
            ("/translate", "Translate text"),
            ("/tts", "Text to speech"),
            ("/carbon", "Code screenshot"),
            ("/paste", "Paste text online"),
        ],
    },
})

# Total commands count
TOTAL_COMMANDS = sum(
    len(section["commands"]) for section in HELP_SECTIONS.values()
)


# ═══════════════════════════════════════════════════════════════
# ◈ INLINE KEYBOARD BUILDERS
# ═══════════════════════════════════════════════════════════════

class KeyboardBuilder:
    """
    ╔═══════════════════════════════════════╗
    ║  Build stylish inline keyboards       ║
    ╚═══════════════════════════════════════╝
    """

    @staticmethod
    def start_keyboard(bot_username: str) -> InlineKeyboardMarkup:
        """Main start menu keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❓ {StyleFont.bold_sans('Help')}",
                    callback_data="help_main"
                ),
                InlineKeyboardButton(
                    f"ℹ️ {StyleFont.bold_sans('About')}",
                    callback_data="about"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"👑 {StyleFont.bold_sans('Owner')}",
                    url=f"tg://user?id={OWNER_ID}"
                ),
                InlineKeyboardButton(
                    f"📊 {StyleFont.bold_sans('Stats')}",
                    callback_data="stats"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"➕ {StyleFont.bold_sans('Add Me To Group')}",
                    url=(
                        f"https://t.me/{bot_username}"
                        f"?startgroup=true"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📢 {StyleFont.bold_sans('Updates')}",
                    url=f"https://t.me/{UPDATES_CHANNEL}"
                ) if UPDATES_CHANNEL else
                InlineKeyboardButton(
                    f"📢 {StyleFont.bold_sans('Updates')}",
                    callback_data="no_channel"
                ),
                InlineKeyboardButton(
                    f"💬 {StyleFont.bold_sans('Support')}",
                    url=f"https://t.me/{SUPPORT_CHAT}"
                ) if SUPPORT_CHAT else
                InlineKeyboardButton(
                    f"💬 {StyleFont.bold_sans('Support')}",
                    callback_data="no_support"
                ),
            ],
        ])

    @staticmethod
    def help_main_keyboard() -> InlineKeyboardMarkup:
        """Help menu with section buttons"""
        buttons = []
        row = []
        for key, section in HELP_SECTIONS.items():
            btn_text = f"{section['emoji']} {section['title']}"
            row.append(
                InlineKeyboardButton(
                    btn_text,
                    callback_data=f"help_{key}"
                )
            )
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        # Navigation row
        buttons.append([
            InlineKeyboardButton(
                f"🏠 {StyleFont.bold_sans('Home')}",
                callback_data="start_back"
            ),
            InlineKeyboardButton(
                f"🔄 {StyleFont.bold_sans('Close')}",
                callback_data="close"
            ),
        ])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def help_section_keyboard(
        section_key: str
    ) -> InlineKeyboardMarkup:
        """Back button for help section"""
        keys = list(HELP_SECTIONS.keys())
        idx = keys.index(section_key)
        prev_key = keys[idx - 1] if idx > 0 else keys[-1]
        next_key = keys[idx + 1] if idx < len(keys) - 1 else keys[0]

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"◀️ {StyleFont.bold_sans('Prev')}",
                    callback_data=f"help_{prev_key}"
                ),
                InlineKeyboardButton(
                    f"🏠 {StyleFont.bold_sans('Back')}",
                    callback_data="help_main"
                ),
                InlineKeyboardButton(
                    f"{StyleFont.bold_sans('Next')} ▶️",
                    callback_data=f"help_{next_key}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def close_keyboard() -> InlineKeyboardMarkup:
        """Simple close button"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def back_to_help_keyboard() -> InlineKeyboardMarkup:
        """Back to help menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"◀️ {StyleFont.bold_sans('Back')}",
                    callback_data="help_main"
                ),
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def confirm_keyboard(
        action: str, target: str = ""
    ) -> InlineKeyboardMarkup:
        """Confirmation keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"✅ {StyleFont.bold_sans('Yes')}",
                    callback_data=f"confirm_{action}_{target}"
                ),
                InlineKeyboardButton(
                    f"❌ {StyleFont.bold_sans('No')}",
                    callback_data="close"
                ),
            ],
        ])


# ═══════════════════════════════════════════════════════════════
# ◈ MESSAGE TEMPLATES
# ═══════════════════════════════════════════════════════════════

class Templates:
    """
    ╔═══════════════════════════════════════╗
    ║  Pre-built stylish message templates  ║
    ╚═══════════════════════════════════════╝
    """

    @staticmethod
    def start_message(user: User, bot_username: str) -> str:
        """Generate start message"""
        user_mention = get_user_mention(user)
        user_name = get_user_full_name(user)

        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Welcome')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.HEADER_LINE if hasattr(Symbols, 'HEADER_LINE') else ''}"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Your Info')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"@{user.username or StyleFont.small_caps('none')}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.ROBOT} {StyleFont.mixed_bold_smallcaps('I am')} "
            f"<b>{BOT_NAME}</b>\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('a powerful group management bot')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('with')} <b>{TOTAL_COMMANDS}+</b> "
            f"{StyleFont.small_caps('commands')}\n"
            f"\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.bold_sans('Available Features')}:\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('admin management')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('welcome & goodbye')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('anti-flood & anti-spam')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('notes & filters')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('warnings & blacklist')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('federations & global bans')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('and much more...')}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def start_group_message(
        user: User, chat: Chat
    ) -> str:
        """Generate start message for groups"""
        user_mention = get_user_mention(user)

        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Welcome')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Your Info')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"@{user.username or StyleFont.small_caps('none')}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Group Id')}: "
            f"<code>{chat.id}</code>\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.WARNING} {StyleFont.bold_sans('RULES')}:-\n"
            f"{Symbols.NUM_1} 🚫 "
            f"{StyleFont.mixed_bold_smallcaps('No links')}\n"
            f"{Symbols.NUM_2} {Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('No abuse')}\n"
            f"{Symbols.NUM_3} {Symbols.WARNING} "
            f"{StyleFont.mixed_bold_smallcaps('No promo')}\n"
            f"{Symbols.NUM_4} 🔞 "
            f"{StyleFont.mixed_bold_smallcaps('No nsfw')}\n"
            f"{Symbols.NUM_5} ⛔ "
            f"{StyleFont.mixed_bold_smallcaps('No banned emojis')}\n"
            f"\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.bold_sans('Available Commands')}:\n"
            f"{Symbols.BULLET} /id\n"
            f"{Symbols.BULLET} /info\n"
            f"{Symbols.BULLET} /rules\n"
            f"{Symbols.BULLET} /help – "
            f"{Symbols.STAR2}"
            f"{StyleFont.mixed_bold_smallcaps('Useful Bot Cmds')}\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def help_main_message() -> str:
        """Generate main help message"""
        section_list = ""
        for i, (key, section) in enumerate(HELP_SECTIONS.items()):
            num = Symbols.NUMS[i] if i < 10 else f"{i+1}."
            section_list += (
                f"{num} {section['emoji']} "
                f"{section['title']}\n"
            )

        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Help Menu')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.ROBOT} {StyleFont.bold_sans('Bot Commands')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('total commands')}: "
            f"<b>{TOTAL_COMMANDS}+</b>\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('total sections')}: "
            f"<b>{len(HELP_SECTIONS)}</b>\n"
            f"\n"
            f"{Symbols.ARROW_R} "
            f"{StyleFont.small_caps('click any button below to view commands')}\n"
            f"\n"
            f"{section_list}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def help_section_message(section_key: str) -> str:
        """Generate help section message"""
        section = HELP_SECTIONS[section_key]
        title = section["title"]
        emoji = section["emoji"]
        desc = section["description"]
        commands = section["commands"]

        cmd_list = ""
        for cmd, description in commands:
            cmd_list += (
                f"  {Symbols.ARROW_TRI} <code>{cmd}</code>\n"
                f"     {Symbols.TINY_DOT} "
                f"{StyleFont.small_caps(description)}\n"
            )

        return (
            f"{emoji} {title} {emoji}\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.INFO} "
            f"{StyleFont.small_caps(desc)}\n"
            f"\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.bold_sans('Commands')}:\n"
            f"{cmd_list}\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('total')}: "
            f"<b>{len(commands)}</b> "
            f"{StyleFont.small_caps('commands')}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def about_message(bot_user: User) -> str:
        """Generate about message"""
        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('About')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Bot Info')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Name')}: "
            f"{BOT_NAME}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"@{bot_user.username}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Bot Id')}: "
            f"<code>{bot_user.id}</code>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Version')}: "
            f"v{BOT_VERSION}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Language')}: "
            f"Python 3.11+\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Library')}: "
            f"python-telegram-bot v20+\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Database')}: "
            f"PostgreSQL\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Hosting')}: "
            f"Render\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.ROCKET} "
            f"{StyleFont.bold_sans('Features')}:\n"
            f"{Symbols.BULLET} {TOTAL_COMMANDS}+ "
            f"{StyleFont.small_caps('commands')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('advanced group management')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('anti-flood & anti-spam')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('welcome system with media')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('notes, filters & blacklist')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('federation system')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('global ban & mute')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('and much more...')}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def alive_message(uptime_str: str, ping_ms: float) -> str:
        """Generate alive/ping message"""
        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Bot Status')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Status')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Status')}: "
            f"{StyleFont.bold_sans('ONLINE')}\n"
            f"{Symbols.BOX_V} {Symbols.CLOCK} "
            f"{StyleFont.mixed_bold_smallcaps('Uptime')}: "
            f"{uptime_str}\n"
            f"{Symbols.BOX_V} {Symbols.THUNDER} "
            f"{StyleFont.mixed_bold_smallcaps('Ping')}: "
            f"<code>{ping_ms:.2f}ms</code>\n"
            f"{Symbols.BOX_V} {Symbols.GEAR} "
            f"{StyleFont.mixed_bold_smallcaps('Version')}: "
            f"v{BOT_VERSION}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.FIRE} "
            f"{StyleFont.small_caps('all systems operational')}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def stats_message(stats: dict) -> str:
        """Generate stats message"""
        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Bot Statistics')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Stats')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Users')}: "
            f"<b>{format_number(stats.get('users', 0))}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Chats')}: "
            f"<b>{format_number(stats.get('chats', 0))}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Messages')}: "
            f"<b>{format_number(stats.get('total_messages', 0))}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Commands')}: "
            f"<b>{format_number(stats.get('total_commands', 0))}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Callbacks')}: "
            f"<b>{format_number(stats.get('total_callbacks', 0))}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Sudo Users')}: "
            f"<b>{stats.get('sudos', 0)}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Support Users')}: "
            f"<b>{stats.get('supports', 0)}</b>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Gbanned Users')}: "
            f"<b>{stats.get('gbanned', 0)}</b>\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def user_info_message(
        user: User,
        db_user: Optional[dict] = None,
        chat: Optional[Chat] = None,
        member: Optional[ChatMember] = None,
        is_owner: bool = False,
        is_sudo: bool = False,
        is_support: bool = False,
        is_gbanned: bool = False,
    ) -> str:
        """Generate user info message"""
        user_mention = get_user_mention(user)
        full_name = get_user_full_name(user)

        # Role
        role_parts = []
        if is_owner:
            role_parts.append(f"{Symbols.CROWN} Owner")
        if is_sudo:
            role_parts.append(f"{Symbols.SWORDS} Sudo")
        if is_support:
            role_parts.append(f"{Symbols.SHIELD} Support")
        role_str = ", ".join(role_parts) if role_parts else StyleFont.small_caps("member")

        # Chat member status
        status_str = StyleFont.small_caps("unknown")
        if member:
            if isinstance(member, ChatMemberOwner):
                status_str = f"{Symbols.CROWN} {StyleFont.small_caps('owner')}"
            elif isinstance(member, ChatMemberAdministrator):
                title = member.custom_title or ""
                status_str = (
                    f"⚡ {StyleFont.small_caps('admin')}"
                    f"{f' ({title})' if title else ''}"
                )
            elif isinstance(member, ChatMemberMember):
                status_str = f"{Symbols.BULLET} {StyleFont.small_caps('member')}"
            elif isinstance(member, ChatMemberRestricted):
                status_str = f"🔇 {StyleFont.small_caps('restricted')}"
            elif isinstance(member, ChatMemberBanned):
                status_str = f"🔨 {StyleFont.small_caps('banned')}"

        text = (
            f"✦ {StyleFont.mixed_bold_smallcaps('User Info')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Profile')} ]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Name')}: "
            f"{html_escape(full_name)}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"@{user.username or StyleFont.small_caps('none')}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Mention')}: "
            f"{user_mention}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Is Bot')}: "
            f"{'✅' if user.is_bot else '❌'}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Role')}: "
            f"{role_str}\n"
        )

        if chat and chat.type != ChatType.PRIVATE:
            text += (
                f"{Symbols.BOX_V} {Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Chat Status')}: "
                f"{status_str}\n"
            )

        if is_gbanned:
            text += (
                f"{Symbols.BOX_V} {Symbols.WARNING} "
                f"{StyleFont.mixed_bold_smallcaps('Gbanned')}: ✅\n"
            )

        if db_user:
            msgs = db_user.get("total_messages", 0)
            text += (
                f"{Symbols.BOX_V} {Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Messages')}: "
                f"<b>{format_number(msgs)}</b>\n"
            )
            rep = db_user.get("reputation", 0)
            text += (
                f"{Symbols.BOX_V} {Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Reputation')}: "
                f"<b>{rep}</b> ⭐\n"
            )

        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 20}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text


# ═══════════════════════════════════════════════════════════════
# ◈ SECTION 1 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
# /start COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
async def cmd_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /start - Bot start command with stylish welcome
    Works in both private chat and groups
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    # Track user
    await track_user_chat(update, context)

    bot_me = await context.bot.get_me()
    bot_username = bot_me.username

    if chat.type == ChatType.PRIVATE:
        # Private chat - full start menu
        text = Templates.start_message(user, bot_username)
        keyboard = KeyboardBuilder.start_keyboard(bot_username)

        await message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

        # Log to channel
        await bot_logger.log(
            bot=context.bot,
            log_type=LogType.START,
            user=user,
            extra=f"Started bot in PM",
        )
    else:
        # Group chat - brief message
        text = Templates.start_group_message(user, chat)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❓ {StyleFont.bold_sans('Help')}",
                    url=f"https://t.me/{bot_username}?start=help"
                ),
            ],
        ])

        await message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )


# ───────────────────────────────────────────────────────────────
# /help COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
@check_disabled
async def cmd_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /help - Show help menu with inline buttons
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    bot_me = await context.bot.get_me()

    if chat and chat.type != ChatType.PRIVATE:
        # In group - send button to PM
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❓ {StyleFont.bold_sans('Help')}",
                    url=f"https://t.me/{bot_me.username}?start=help"
                ),
            ],
        ])
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('Click the button below for help')}",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        return

    # In PM - show full help
    # Check if specific section requested
    if context.args and context.args[0] in HELP_SECTIONS:
        section_key = context.args[0]
        text = Templates.help_section_message(section_key)
        keyboard = KeyboardBuilder.help_section_keyboard(section_key)
    else:
        text = Templates.help_main_message()
        keyboard = KeyboardBuilder.help_main_keyboard()

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ───────────────────────────────────────────────────────────────
# /about COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /about - Show bot information
    """
    message = update.effective_message
    if not message:
        return

    bot_me = await context.bot.get_me()
    text = Templates.about_message(bot_me)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.back_to_help_keyboard(),
        disable_web_page_preview=True,
    )


# ───────────────────────────────────────────────────────────────
# /alive & /ping COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_alive(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /alive or /ping - Check if bot is running and latency
    """
    message = update.effective_message
    if not message:
        return

    # Calculate ping
    start = time.time()
    msg = await message.reply_text(
        f"{Symbols.CLOCK} "
        f"{StyleFont.small_caps('checking...')}"
    )
    end = time.time()
    ping_ms = (end - start) * 1000

    # Calculate uptime
    uptime_seconds = int(time.time() - BOT_START_TIME)
    uptime_str = get_readable_time(uptime_seconds)

    text = Templates.alive_message(uptime_str, ping_ms)

    await msg.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


@track_command
@cooldown(3.0)
@check_disabled
async def cmd_ping(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /ping - Quick ping check
    """
    message = update.effective_message
    if not message:
        return

    start = time.time()
    msg = await message.reply_text("🏓")
    end = time.time()
    ping_ms = (end - start) * 1000

    await msg.edit_text(
        f"🏓 {StyleFont.bold_sans('Pong')}!\n"
        f"{Symbols.THUNDER} "
        f"{StyleFont.small_caps('latency')}: "
        f"<code>{ping_ms:.2f}ms</code>",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
# /id COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
@check_disabled
async def cmd_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /id - Get user/chat ID
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    text = (
        f"✦ {StyleFont.mixed_bold_smallcaps('Id Info')} ✦\n"
        f"{Symbols.divider(6)}\n\n"
    )

    # If reply to message
    if message.reply_to_message:
        reply_user = message.reply_to_message.from_user
        if reply_user:
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('User')}: "
                f"{get_user_mention(reply_user)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
                f"<code>{reply_user.id}</code>\n\n"
            )
        # If forwarded
        if message.reply_to_message.forward_from:
            fwd = message.reply_to_message.forward_from
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Original User')}: "
                f"{get_user_mention(fwd)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Original Id')}: "
                f"<code>{fwd.id}</code>\n\n"
            )
        if message.reply_to_message.forward_from_chat:
            fwd_chat = message.reply_to_message.forward_from_chat
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Forwarded From')}: "
                f"{html_escape(fwd_chat.title or '')}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Channel Id')}: "
                f"<code>{fwd_chat.id}</code>\n\n"
            )
    else:
        text += (
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Your Id')}: "
            f"<code>{user.id}</code>\n\n"
        )

    if chat and chat.type != ChatType.PRIVATE:
        text += (
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
            f"{html_escape(chat.title or '')}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat Id')}: "
            f"<code>{chat.id}</code>\n"
        )

    text += (
        f"\n{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
# /info COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /info - Get detailed user information
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    target_user = None
    member = None

    # If reply
    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
    elif context.args:
        # Try to parse user_id or username
        target = context.args[0]
        try:
            if target.startswith("@"):
                chat_obj = await context.bot.get_chat(target)
                target_user = chat_obj
            else:
                uid = int(target)
                chat_obj = await context.bot.get_chat(uid)
                target_user = chat_obj
        except Exception:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('User not found')}!",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        target_user = user

    if not target_user:
        target_user = user

    # Get member status in current chat
    if chat and chat.type != ChatType.PRIVATE:
        try:
            member = await context.bot.get_chat_member(
                chat.id, target_user.id
            )
        except Exception:
            pass

    # Get DB user
    try:
        db_user = await db.get_user(target_user.id)
        db_user_dict = dict(db_user) if db_user else None
    except Exception:
        db_user_dict = None

    text = Templates.user_info_message(
        user=target_user,
        db_user=db_user_dict,
        chat=chat,
        member=member,
        is_owner=cache.is_owner(target_user.id),
        is_sudo=cache.is_sudo(target_user.id),
        is_support=cache.is_support(target_user.id),
        is_gbanned=cache.is_gbanned(target_user.id),
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
# /stats COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
async def cmd_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /stats - Show bot statistics
    """
    message = update.effective_message
    if not message:
        return

    # Gather stats
    user_count = await db.get_user_count()
    chat_count = await db.get_chat_count()
    db_stats = await db.get_all_stats()
    sudo_count = len(await db.get_sudos())
    support_count = len(await db.get_supports())
    gban_count = await db.fetchval(
        "SELECT COUNT(*) FROM gbans;"
    )

    stats = {
        "users": user_count,
        "chats": chat_count,
        "total_messages": db_stats.get("total_messages", 0),
        "total_commands": db_stats.get("total_commands", 0),
        "total_callbacks": db_stats.get("total_callbacks", 0),
        "sudos": sudo_count,
        "supports": support_count,
        "gbanned": gban_count or 0,
    }

    text = Templates.stats_message(stats)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
# SUDO USER MANAGEMENT COMMANDS
# ───────────────────────────────────────────────────────────────

@track_command
@owner_only
async def cmd_addsudo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /addsudo - Add a sudo user (Owner only)
    """
    message = update.effective_message
    if not message:
        return

    user_id, reason, user_obj = await extract_user_and_reason(
        message, context.bot
    )

    if not user_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a user')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('reply to user or provide id/username')}",
            parse_mode=ParseMode.HTML,
        )
        return

    if cache.is_owner(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Owner is always sudo')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if cache.is_sudo(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('User is already sudo')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.add_sudo(user_id, update.effective_user.id, reason or "")
    cache.add_sudo(user_id)

    # Try to get user name
    try:
        target = await context.bot.get_chat(user_id)
        user_name = target.first_name or str(user_id)
    except Exception:
        user_name = str(user_id)

    text = (
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Sudo User Added')}\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={user_id}'>"
        f"{html_escape(user_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
        f"<code>{user_id}</code>\n"
    )
    if reason:
        text += (
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
            f"{html_escape(reason)}\n"
        )
    text += (
        f"{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await bot_logger.log(
        bot=context.bot,
        log_type=LogType.SETTINGS,
        admin=update.effective_user,
        extra=f"Added sudo: {user_id}",
    )


@track_command
@owner_only
async def cmd_rmsudo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /rmsudo - Remove a sudo user (Owner only)
    """
    message = update.effective_message
    if not message:
        return

    user_id, _, user_obj = await extract_user_and_reason(
        message, context.bot
    )

    if not user_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if not cache.is_sudo(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('User is not sudo')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if cache.is_owner(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Cannot remove owner from sudo')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.remove_sudo(user_id)
    cache.remove_sudo(user_id)

    try:
        target = await context.bot.get_chat(user_id)
        user_name = target.first_name or str(user_id)
    except Exception:
        user_name = str(user_id)

    text = (
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Sudo User Removed')}\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={user_id}'>"
        f"{html_escape(user_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
        f"<code>{user_id}</code>\n"
        f"{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


@track_command
@sudo_only
async def cmd_sudolist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /sudolist - List all sudo users
    """
    message = update.effective_message
    if not message:
        return

    sudo_ids = await db.get_sudos()
    sudo_ids = list(set(sudo_ids + [OWNER_ID]))

    text = (
        f"✦ {StyleFont.mixed_bold_smallcaps('Sudo Users')} ✦\n"
        f"{Symbols.divider(6)}\n\n"
    )

    for i, uid in enumerate(sudo_ids, 1):
        try:
            user_chat = await context.bot.get_chat(uid)
            name = user_chat.first_name or str(uid)
            if uid == OWNER_ID:
                prefix = f"{Symbols.CROWN}"
            else:
                prefix = f"{Symbols.SWORDS}"
            text += (
                f"{prefix} {i}. "
                f"<a href='tg://user?id={uid}'>"
                f"{html_escape(name)}</a> "
                f"[<code>{uid}</code>]\n"
            )
        except Exception:
            text += (
                f"{Symbols.BULLET} {i}. "
                f"<code>{uid}</code> "
                f"({StyleFont.small_caps('unknown')})\n"
            )

    text += (
        f"\n{Symbols.divider(6)}\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('total')}: "
        f"<b>{len(sudo_ids)}</b>\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


# ───────────────────────────────────────────────────────────────
# SUPPORT USER MANAGEMENT COMMANDS
# ───────────────────────────────────────────────────────────────

@track_command
@sudo_only
async def cmd_addsupport(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /addsupport - Add a support user (Sudo only)
    """
    message = update.effective_message
    if not message:
        return

    user_id, reason, user_obj = await extract_user_and_reason(
        message, context.bot
    )

    if not user_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if cache.is_support(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('User is already support')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.add_support(
        user_id, update.effective_user.id, reason or ""
    )
    cache.add_support(user_id)

    try:
        target = await context.bot.get_chat(user_id)
        user_name = target.first_name or str(user_id)
    except Exception:
        user_name = str(user_id)

    text = (
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Support User Added')}\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={user_id}'>"
        f"{html_escape(user_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
        f"<code>{user_id}</code>\n"
        f"{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


@track_command
@sudo_only
async def cmd_rmsupport(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /rmsupport - Remove a support user (Sudo only)
    """
    message = update.effective_message
    if not message:
        return

    user_id, _, _ = await extract_user_and_reason(
        message, context.bot
    )

    if not user_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if not cache.is_support(user_id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('User is not support')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.remove_support(user_id)
    cache.remove_support(user_id)

    try:
        target = await context.bot.get_chat(user_id)
        user_name = target.first_name or str(user_id)
    except Exception:
        user_name = str(user_id)

    text = (
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Support User Removed')}\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={user_id}'>"
        f"{html_escape(user_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
        f"<code>{user_id}</code>\n"
        f"{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


@track_command
@sudo_only
async def cmd_supportlist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /supportlist - List all support users
    """
    message = update.effective_message
    if not message:
        return

    support_ids = await db.get_supports()

    if not support_ids:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No support users added yet')}",
            parse_mode=ParseMode.HTML,
        )
        return

    text = (
        f"✦ {StyleFont.mixed_bold_smallcaps('Support Users')} ✦\n"
        f"{Symbols.divider(6)}\n\n"
    )

    for i, uid in enumerate(support_ids, 1):
        try:
            user_chat = await context.bot.get_chat(uid)
            name = user_chat.first_name or str(uid)
            text += (
                f"{Symbols.SHIELD} {i}. "
                f"<a href='tg://user?id={uid}'>"
                f"{html_escape(name)}</a> "
                f"[<code>{uid}</code>]\n"
            )
        except Exception:
            text += (
                f"{Symbols.BULLET} {i}. "
                f"<code>{uid}</code>\n"
            )

    text += (
        f"\n{Symbols.divider(6)}\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('total')}: "
        f"<b>{len(support_ids)}</b>\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(text, parse_mode=ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
# ◈ CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════════════

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle all callback queries"""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    try:
        await db.increment_stat("total_callbacks")
    except Exception:
        pass

    data = query.data
    user = query.from_user
    message = query.message

    if not data or not user or not message:
        return

    # ── Start back ──
    if data == "start_back":
        bot_me = await context.bot.get_me()
        text = Templates.start_message(user, bot_me.username)
        keyboard = KeyboardBuilder.start_keyboard(bot_me.username)
        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except BadRequest:
            pass

    # ── Help main ──
    elif data == "help_main":
        text = Templates.help_main_message()
        keyboard = KeyboardBuilder.help_main_keyboard()
        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except BadRequest:
            pass

    # ── Help sections ──
    elif data.startswith("help_"):
        section_key = data.replace("help_", "", 1)
        if section_key in HELP_SECTIONS:
            text = Templates.help_section_message(section_key)
            keyboard = KeyboardBuilder.help_section_keyboard(
                section_key
            )
            try:
                await message.edit_text(
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )
            except BadRequest:
                pass

    # ── About ──
    elif data == "about":
        bot_me = await context.bot.get_me()
        text = Templates.about_message(bot_me)
        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=KeyboardBuilder.back_to_help_keyboard(),
                disable_web_page_preview=True,
            )
        except BadRequest:
            pass

    # ── Stats ──
    elif data == "stats":
        user_count = await db.get_user_count()
        chat_count = await db.get_chat_count()
        db_stats = await db.get_all_stats()
        sudo_count = len(await db.get_sudos())
        support_count = len(await db.get_supports())
        gban_count = await db.fetchval(
            "SELECT COUNT(*) FROM gbans;"
        )

        stats = {
            "users": user_count,
            "chats": chat_count,
            "total_messages": db_stats.get("total_messages", 0),
            "total_commands": db_stats.get("total_commands", 0),
            "total_callbacks": db_stats.get("total_callbacks", 0),
            "sudos": sudo_count,
            "supports": support_count,
            "gbanned": gban_count or 0,
        }

        text = Templates.stats_message(stats)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Refresh')}",
                    callback_data="stats"
                ),
                InlineKeyboardButton(
                    f"🏠 {StyleFont.bold_sans('Home')}",
                    callback_data="start_back"
                ),
            ],
        ])
        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except BadRequest:
            pass

    # ── Close ──
    elif data == "close":
        try:
            await message.delete()
        except BadRequest:
            try:
                await message.edit_text(
                    f"{Symbols.CHECK2} "
                    f"{StyleFont.small_caps('closed')}."
                )
            except Exception:
                pass

    # ── No channel ──
    elif data == "no_channel":
        await query.answer(
            "No updates channel configured!", show_alert=True
        )

    # ── No support ──
    elif data == "no_support":
        await query.answer(
            "No support chat configured!", show_alert=True
        )


# ═══════════════════════════════════════════════════════════════
# ◈ ERROR HANDLER
# ═══════════════════════════════════════════════════════════════

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle errors"""
    logger.error(
        f"Exception while handling an update: "
        f"{context.error}",
        exc_info=context.error,
    )

    # Log to channel
    if LOG_CHANNEL_ID:
        try:
            error_text = (
                f"❌ {StyleFont.bold_sans('Error Occurred')}\n"
                f"{Symbols.divider(6)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Error')}: "
                f"<code>{html_escape(str(context.error)[:1000])}</code>\n"
            )

            if isinstance(update, Update) and update.effective_chat:
                error_text += (
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
                    f"<code>{update.effective_chat.id}</code>\n"
                )

            error_text += (
                f"{Symbols.divider(6)}\n"
                f"{Symbols.CLOCK} "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=error_text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# ◈ WEBHOOK & WEB SERVER (RENDER COMPATIBLE)
# ═══════════════════════════════════════════════════════════════

class WebServer:
    """
    ╔═══════════════════════════════════════╗
    ║  aiohttp web server for webhook       ║
    ║  Render Web Service compatible        ║
    ╚═══════════════════════════════════════╝
    """

    def __init__(self, application: Application):
        self.application = application
        self.app = web.Application()
        self.app.router.add_get("/", self.health_check)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_post(WEBHOOK_PATH, self.webhook_handler)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint for Render"""
        uptime = int(time.time() - BOT_START_TIME)
        return web.json_response({
            "status": "alive",
            "bot": BOT_NAME,
            "version": BOT_VERSION,
            "uptime_seconds": uptime,
            "uptime_readable": get_readable_time(uptime),
        })

    async def webhook_handler(
        self, request: web.Request
    ) -> web.Response:
        """Handle incoming webhook updates"""
        try:
            # Verify secret token
            secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret != WEBHOOK_SECRET:
                return web.Response(status=403, text="Forbidden")

            data = await request.json()
            update = Update.de_json(data, self.application.bot)
            await self.application.update_queue.put(update)
            return web.Response(status=200, text="OK")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.Response(status=500, text="Error")


# ═══════════════════════════════════════════════════════════════
# ◈ BOT INITIALIZATION & STARTUP
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#
#   ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#   ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
#   ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║
#   ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║
#   ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#   ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#
#          ██████╗     ██╗   ██╗███████╗███████╗██████╗
#          ╚════██╗    ██║   ██║██╔════╝██╔════╝██╔══██╗
#           █████╔╝    ██║   ██║███████╗█████╗  ██████╔╝
#          ██╔═══╝     ██║   ██║╚════██║██╔══╝  ██╔══██╗
#          ███████╗    ╚██████╔╝███████║███████╗██║  ██║
#          ╚══════╝     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝
#
#   ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗
#   ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝
#   ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗
#   ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝
#   ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗
#   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#
#   SECTION 2 : USER MANAGEMENT SYSTEM
#   ──────────────────────────────────────
#   ✦ User registration in DB
#   ✦ User info command (/me, /whois)
#   ✦ User ID command (/myid)
#   ✦ Get user profile photos (/pp, /profilepic)
#   ✦ Who is reply (/who)
#   ✦ User stats (/mystats, /userstats)
#   ✦ User settings (/settings, /setbio, /setname)
#   ✦ User warnings system (/warn, /warns, /resetwarns...)
#   ✦ User notes - personal (/pnote, /pnotes, /pclear)
#   ✦ User AFK system (/afk, auto-detect, mention alert)
#
#   Powered By: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — ADDITIONAL DATABASE TABLES ◈◈◈
# ═══════════════════════════════════════════════════════════════

SECTION2_TABLES_SQL = """

-- ══════════════════════════════════════════
-- Personal Notes table (user private notes)
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS personal_notes (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    note_name       TEXT NOT NULL,
    note_content    TEXT NOT NULL,
    media_type      TEXT DEFAULT '',
    media_id        TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, note_name)
);

CREATE INDEX IF NOT EXISTS idx_personal_notes_user
    ON personal_notes(user_id);

-- ══════════════════════════════════════════
-- User settings table
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_settings (
    user_id             BIGINT PRIMARY KEY,
    bio                 TEXT DEFAULT '',
    custom_name         TEXT DEFAULT '',
    notifications       BOOLEAN DEFAULT TRUE,
    pm_allowed          BOOLEAN DEFAULT TRUE,
    read_receipts       BOOLEAN DEFAULT TRUE,
    auto_afk            BOOLEAN DEFAULT FALSE,
    auto_afk_time       INTEGER DEFAULT 3600,
    welcome_dm          BOOLEAN DEFAULT TRUE,
    language            TEXT DEFAULT 'en',
    timezone_offset     INTEGER DEFAULT 0,
    theme               TEXT DEFAULT 'default',
    profile_private     BOOLEAN DEFAULT FALSE,
    last_seen_enabled   BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ══════════════════════════════════════════
-- User stats tracking table
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_stats (
    user_id                 BIGINT NOT NULL,
    chat_id                 BIGINT NOT NULL,
    total_messages          BIGINT DEFAULT 0,
    total_stickers          BIGINT DEFAULT 0,
    total_photos            BIGINT DEFAULT 0,
    total_videos            BIGINT DEFAULT 0,
    total_documents         BIGINT DEFAULT 0,
    total_voices            BIGINT DEFAULT 0,
    total_video_notes       BIGINT DEFAULT 0,
    total_animations        BIGINT DEFAULT 0,
    total_audio             BIGINT DEFAULT 0,
    total_contacts          BIGINT DEFAULT 0,
    total_locations         BIGINT DEFAULT 0,
    total_polls             BIGINT DEFAULT 0,
    total_text              BIGINT DEFAULT 0,
    total_commands          BIGINT DEFAULT 0,
    total_forwards          BIGINT DEFAULT 0,
    total_edits             BIGINT DEFAULT 0,
    total_replies           BIGINT DEFAULT 0,
    total_words             BIGINT DEFAULT 0,
    total_characters        BIGINT DEFAULT 0,
    first_message_at        TIMESTAMP DEFAULT NOW(),
    last_message_at         TIMESTAMP DEFAULT NOW(),
    active_days             INTEGER DEFAULT 1,
    last_active_date        DATE DEFAULT CURRENT_DATE,
    streak_days             INTEGER DEFAULT 0,
    max_streak              INTEGER DEFAULT 0,
    PRIMARY KEY(user_id, chat_id)
);

CREATE INDEX IF NOT EXISTS idx_user_stats_user
    ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_chat
    ON user_stats(chat_id);

-- ══════════════════════════════════════════
-- Global user stats (across all chats)
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_global_stats (
    user_id                 BIGINT PRIMARY KEY,
    total_messages          BIGINT DEFAULT 0,
    total_chats_active      INTEGER DEFAULT 0,
    total_commands_used     BIGINT DEFAULT 0,
    total_words             BIGINT DEFAULT 0,
    total_characters        BIGINT DEFAULT 0,
    total_stickers          BIGINT DEFAULT 0,
    total_photos            BIGINT DEFAULT 0,
    total_videos            BIGINT DEFAULT 0,
    total_documents         BIGINT DEFAULT 0,
    total_voices            BIGINT DEFAULT 0,
    total_animations        BIGINT DEFAULT 0,
    total_audio             BIGINT DEFAULT 0,
    total_text              BIGINT DEFAULT 0,
    total_forwards          BIGINT DEFAULT 0,
    first_seen              TIMESTAMP DEFAULT NOW(),
    last_seen               TIMESTAMP DEFAULT NOW(),
    total_active_days       INTEGER DEFAULT 1,
    last_active_date        DATE DEFAULT CURRENT_DATE,
    xp_points               BIGINT DEFAULT 0,
    level                   INTEGER DEFAULT 1,
    rank_title              TEXT DEFAULT 'Newbie',
    badges                  TEXT DEFAULT '[]'
);

-- ══════════════════════════════════════════
-- AFK history table
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS afk_history (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    reason          TEXT DEFAULT '',
    afk_start       TIMESTAMP DEFAULT NOW(),
    afk_end         TIMESTAMP,
    duration_secs   INTEGER DEFAULT 0,
    mentions_missed INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_afk_history_user
    ON afk_history(user_id);

-- ══════════════════════════════════════════
-- Warning details table (per-chat)
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS warn_details (
    id              SERIAL PRIMARY KEY,
    chat_id         BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    warned_by       BIGINT NOT NULL,
    reason          TEXT DEFAULT '',
    warn_number     INTEGER DEFAULT 1,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    expires_at      TIMESTAMP,
    removed_by      BIGINT,
    removed_at      TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warn_details_chat_user
    ON warn_details(chat_id, user_id);
CREATE INDEX IF NOT EXISTS idx_warn_details_active
    ON warn_details(chat_id, user_id) WHERE is_active = TRUE;

-- ══════════════════════════════════════════
-- User profile cache table
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_profile_cache (
    user_id             BIGINT PRIMARY KEY,
    first_name          TEXT DEFAULT '',
    last_name           TEXT DEFAULT '',
    username            TEXT DEFAULT '',
    bio_text            TEXT DEFAULT '',
    profile_photo_id    TEXT DEFAULT '',
    photo_count         INTEGER DEFAULT 0,
    dc_id               INTEGER DEFAULT 0,
    is_premium          BOOLEAN DEFAULT FALSE,
    is_verified         BOOLEAN DEFAULT FALSE,
    is_scam             BOOLEAN DEFAULT FALSE,
    is_fake             BOOLEAN DEFAULT FALSE,
    common_chats        INTEGER DEFAULT 0,
    last_fetched        TIMESTAMP DEFAULT NOW()
);

"""


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ DATABASE OPERATIONS — SECTION 2 ◈◈◈
# ═══════════════════════════════════════════════════════════════

class UserDB:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   𝐔sᴇʀ 𝐃ᴀᴛᴀʙᴀsᴇ 𝐎ᴘᴇʀᴀᴛɪᴏɴs                        ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       ║
    ║   All user-related database queries                   ║
    ║   Registration, Info, Stats, AFK,                     ║
    ║   Warnings, Personal Notes, Settings                  ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """

    # ───────────────────────────────────────────────────────
    # TABLE CREATION
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def create_tables() -> None:
        """Create all Section 2 tables"""
        try:
            # Split into individual statements to avoid transaction issues
            for stmt in SECTION2_TABLES_SQL.split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    try:
                        await db.execute(stmt)
                    except Exception as se:
                        logger.debug(f"Section 2 stmt skip: {se}")
            logger.info("✅ Section 2 tables created successfully!")
        except Exception as e:
            logger.error(f"❌ Section 2 table creation failed: {e}")

    # ───────────────────────────────────────────────────────
    # USER REGISTRATION & PROFILE
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def register_user(user: User) -> bool:
        """
        Register or update a user in the database.
        Called on every interaction.
        Returns True if new user, False if existing.
        """
        try:
            existing = await db.fetchrow(
                "SELECT user_id FROM users WHERE user_id = $1;",
                user.id
            )

            await db.execute("""
                INSERT INTO users (
                    user_id, username, first_name,
                    last_name, is_bot, language_code,
                    is_active, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, TRUE, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    is_bot = EXCLUDED.is_bot,
                    language_code = EXCLUDED.language_code,
                    is_active = TRUE,
                    updated_at = NOW();
            """,
                user.id,
                user.username or "",
                user.first_name or "",
                user.last_name or "",
                user.is_bot,
                user.language_code or "en"
            )

            # Ensure user_settings row exists
            await db.execute("""
                INSERT INTO user_settings (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING;
            """, user.id)

            # Ensure user_global_stats row exists
            await db.execute("""
                INSERT INTO user_global_stats (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING;
            """, user.id)

            return existing is None  # True = new user

        except Exception as e:
            logger.error(f"User registration error: {e}")
            return False

    @staticmethod
    async def get_full_user(
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive user data from all tables.
        Merges users + user_settings + user_global_stats.
        """
        try:
            user_row = await db.fetchrow(
                "SELECT * FROM users WHERE user_id = $1;",
                user_id
            )
            if not user_row:
                return None

            settings_row = await db.fetchrow(
                "SELECT * FROM user_settings WHERE user_id = $1;",
                user_id
            )

            stats_row = await db.fetchrow(
                "SELECT * FROM user_global_stats WHERE user_id = $1;",
                user_id
            )

            profile_row = await db.fetchrow(
                "SELECT * FROM user_profile_cache WHERE user_id = $1;",
                user_id
            )

            # Active warns count
            warn_count = await db.fetchval("""
                SELECT COUNT(*) FROM warn_details
                WHERE user_id = $1 AND is_active = TRUE;
            """, user_id)

            # Personal notes count
            pnotes_count = await db.fetchval("""
                SELECT COUNT(*) FROM personal_notes
                WHERE user_id = $1;
            """, user_id)

            # AFK status
            afk_row = await db.fetchrow(
                "SELECT * FROM afk WHERE user_id = $1;",
                user_id
            )

            result = dict(user_row)
            if settings_row:
                result["settings"] = dict(settings_row)
            else:
                result["settings"] = {}
            if stats_row:
                result["global_stats"] = dict(stats_row)
            else:
                result["global_stats"] = {}
            if profile_row:
                result["profile_cache"] = dict(profile_row)
            else:
                result["profile_cache"] = {}

            result["active_warns"] = warn_count or 0
            result["personal_notes_count"] = pnotes_count or 0
            result["afk_data"] = dict(afk_row) if afk_row else None

            return result

        except Exception as e:
            logger.error(f"Get full user error: {e}")
            return None

    @staticmethod
    async def update_profile_cache(
        user_id: int,
        first_name: str = "",
        last_name: str = "",
        username: str = "",
        bio_text: str = "",
        profile_photo_id: str = "",
        photo_count: int = 0,
        dc_id: int = 0,
        is_premium: bool = False,
        is_verified: bool = False,
        is_scam: bool = False,
        is_fake: bool = False,
        common_chats: int = 0,
    ) -> None:
        """Cache user profile information"""
        try:
            await db.execute("""
                INSERT INTO user_profile_cache (
                    user_id, first_name, last_name, username,
                    bio_text, profile_photo_id, photo_count,
                    dc_id, is_premium, is_verified,
                    is_scam, is_fake, common_chats,
                    last_fetched
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7,
                    $8, $9, $10, $11, $12, $13, NOW()
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    username = EXCLUDED.username,
                    bio_text = EXCLUDED.bio_text,
                    profile_photo_id = EXCLUDED.profile_photo_id,
                    photo_count = EXCLUDED.photo_count,
                    dc_id = EXCLUDED.dc_id,
                    is_premium = EXCLUDED.is_premium,
                    is_verified = EXCLUDED.is_verified,
                    is_scam = EXCLUDED.is_scam,
                    is_fake = EXCLUDED.is_fake,
                    common_chats = EXCLUDED.common_chats,
                    last_fetched = NOW();
            """,
                user_id, first_name, last_name, username,
                bio_text, profile_photo_id, photo_count,
                dc_id, is_premium, is_verified,
                is_scam, is_fake, common_chats
            )
        except Exception as e:
            logger.error(f"Profile cache update error: {e}")

    @staticmethod
    async def get_all_users_paginated(
        page: int = 1,
        per_page: int = 20,
        order_by: str = "total_messages",
        order_dir: str = "DESC"
    ) -> Tuple[list, int]:
        """
        Get paginated list of users.
        Returns (users_list, total_count).
        """
        try:
            total = await db.fetchval(
                "SELECT COUNT(*) FROM users WHERE is_bot = FALSE;"
            )

            valid_orders = {
                "total_messages": "total_messages",
                "created_at": "created_at",
                "updated_at": "updated_at",
                "reputation": "reputation",
                "user_id": "user_id",
            }
            order_col = valid_orders.get(order_by, "total_messages")
            direction = "DESC" if order_dir.upper() == "DESC" else "ASC"

            offset = (page - 1) * per_page

            rows = await db.fetch(f"""
                SELECT * FROM users
                WHERE is_bot = FALSE
                ORDER BY {order_col} {direction}
                LIMIT $1 OFFSET $2;
            """, per_page, offset)

            return [dict(r) for r in rows], total or 0

        except Exception as e:
            logger.error(f"Paginated users error: {e}")
            return [], 0

    @staticmethod
    async def search_users(query: str) -> list:
        """Search users by name or username"""
        try:
            pattern = f"%{query}%"
            rows = await db.fetch("""
                SELECT * FROM users
                WHERE (
                    LOWER(first_name) LIKE LOWER($1) OR
                    LOWER(last_name) LIKE LOWER($1) OR
                    LOWER(username) LIKE LOWER($1)
                ) AND is_bot = FALSE
                ORDER BY total_messages DESC
                LIMIT 25;
            """, pattern)
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Search users error: {e}")
            return []

    @staticmethod
    async def increment_profile_views(user_id: int) -> None:
        """Increment profile view counter"""
        try:
            await db.execute("""
                UPDATE users
                SET profile_views = profile_views + 1
                WHERE user_id = $1;
            """, user_id)
        except Exception as e:
            logger.debug(f"Profile views increment error: {e}")

    # ───────────────────────────────────────────────────────
    # USER SETTINGS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def get_settings(
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get user settings"""
        try:
            row = await db.fetchrow(
                "SELECT * FROM user_settings WHERE user_id = $1;",
                user_id
            )
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get settings error: {e}")
            return None

    @staticmethod
    async def update_setting(
        user_id: int,
        setting: str,
        value: Any
    ) -> bool:
        """Update a specific user setting"""
        valid_settings = [
            'bio', 'custom_name', 'notifications',
            'pm_allowed', 'read_receipts', 'auto_afk',
            'auto_afk_time', 'welcome_dm', 'language',
            'timezone_offset', 'theme', 'profile_private',
            'last_seen_enabled'
        ]

        if setting not in valid_settings:
            return False

        try:
            await db.execute(f"""
                INSERT INTO user_settings (user_id, {setting}, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    {setting} = EXCLUDED.{setting},
                    updated_at = NOW();
            """, user_id, value)
            return True
        except Exception as e:
            logger.error(f"Update setting error: {e}")
            return False

    @staticmethod
    async def set_bio(user_id: int, bio: str) -> bool:
        """Set user bio"""
        try:
            await db.execute("""
                UPDATE users SET bio = $1 WHERE user_id = $2;
            """, bio[:500], user_id)
            await db.execute("""
                INSERT INTO user_settings (user_id, bio, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    bio = EXCLUDED.bio,
                    updated_at = NOW();
            """, user_id, bio[:500])
            return True
        except Exception as e:
            logger.error(f"Set bio error: {e}")
            return False

    @staticmethod
    async def get_bio(user_id: int) -> str:
        """Get user bio"""
        try:
            bio = await db.fetchval(
                "SELECT bio FROM user_settings WHERE user_id = $1;",
                user_id
            )
            if not bio:
                bio = await db.fetchval(
                    "SELECT bio FROM users WHERE user_id = $1;",
                    user_id
                )
            return bio or ""
        except Exception:
            return ""

    # ───────────────────────────────────────────────────────
    # USER STATS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def track_message_stats(
        user_id: int,
        chat_id: int,
        message: Message
    ) -> None:
        """
        Track detailed message statistics per user per chat.
        Called on every message.
        """
        try:
            # Determine message type columns to increment
            increments = {"total_messages": 1}

            if message.text:
                increments["total_text"] = 1
                word_count = len(message.text.split())
                char_count = len(message.text)
                increments["total_words"] = word_count
                increments["total_characters"] = char_count
            if message.sticker:
                increments["total_stickers"] = 1
            if message.photo:
                increments["total_photos"] = 1
            if message.video:
                increments["total_videos"] = 1
            if message.document:
                increments["total_documents"] = 1
            if message.voice:
                increments["total_voices"] = 1
            if message.video_note:
                increments["total_video_notes"] = 1
            if message.animation:
                increments["total_animations"] = 1
            if message.audio:
                increments["total_audio"] = 1
            if message.contact:
                increments["total_contacts"] = 1
            if message.location:
                increments["total_locations"] = 1
            if message.poll:
                increments["total_polls"] = 1
            if message.forward_date:
                increments["total_forwards"] = 1
            if message.reply_to_message:
                increments["total_replies"] = 1
            if message.text and message.text.startswith("/"):
                increments["total_commands"] = 1

            # Build per-chat stats update
            set_parts = []
            for col, val in increments.items():
                set_parts.append(f"{col} = user_stats.{col} + {val}")
            set_parts.append("last_message_at = NOW()")

            # Handle active days & streak
            set_clause = ", ".join(set_parts)

            await db.execute(f"""
                INSERT INTO user_stats (
                    user_id, chat_id, {", ".join(increments.keys())},
                    first_message_at, last_message_at,
                    active_days, last_active_date, streak_days, max_streak
                ) VALUES (
                    $1, $2, {", ".join(str(v) for v in increments.values())},
                    NOW(), NOW(), 1, CURRENT_DATE, 1, 1
                )
                ON CONFLICT (user_id, chat_id) DO UPDATE SET
                    {set_clause},
                    active_days = CASE
                        WHEN user_stats.last_active_date < CURRENT_DATE
                        THEN user_stats.active_days + 1
                        ELSE user_stats.active_days
                    END,
                    streak_days = CASE
                        WHEN user_stats.last_active_date = CURRENT_DATE - INTERVAL '1 day'
                        THEN user_stats.streak_days + 1
                        WHEN user_stats.last_active_date = CURRENT_DATE
                        THEN user_stats.streak_days
                        ELSE 1
                    END,
                    max_streak = CASE
                        WHEN user_stats.last_active_date = CURRENT_DATE - INTERVAL '1 day'
                             AND user_stats.streak_days + 1 > user_stats.max_streak
                        THEN user_stats.streak_days + 1
                        ELSE user_stats.max_streak
                    END,
                    last_active_date = CURRENT_DATE;
            """, user_id, chat_id)

            # Update global stats
            g_set_parts = []
            for col in ["total_messages", "total_words", "total_characters",
                         "total_stickers", "total_photos", "total_videos",
                         "total_documents", "total_voices",
                         "total_animations", "total_audio",
                         "total_text", "total_forwards"]:
                if col in increments:
                    g_set_parts.append(
                        f"{col} = user_global_stats.{col} + {increments[col]}"
                    )
            g_set_parts.append("last_seen = NOW()")

            if increments.get("total_commands"):
                g_set_parts.append(
                    "total_commands_used = user_global_stats.total_commands_used + 1"
                )

            g_set_clause = ", ".join(g_set_parts)

            await db.execute(f"""
                INSERT INTO user_global_stats (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO UPDATE SET
                    {g_set_clause},
                    total_active_days = CASE
                        WHEN user_global_stats.last_active_date < CURRENT_DATE
                        THEN user_global_stats.total_active_days + 1
                        ELSE user_global_stats.total_active_days
                    END,
                    last_active_date = CURRENT_DATE,
                    xp_points = user_global_stats.xp_points + $2,
                    level = GREATEST(1, FLOOR(
                        SQRT((user_global_stats.xp_points + $2) / 100.0)
                    )::INTEGER);
            """, user_id, random.randint(1, 5))

        except Exception as e:
            logger.debug(f"Stats tracking error: {e}")

    @staticmethod
    async def get_user_chat_stats(
        user_id: int,
        chat_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get per-chat stats for a user"""
        try:
            row = await db.fetchrow("""
                SELECT * FROM user_stats
                WHERE user_id = $1 AND chat_id = $2;
            """, user_id, chat_id)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get chat stats error: {e}")
            return None

    @staticmethod
    async def get_user_global_stats(
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get global stats for a user"""
        try:
            row = await db.fetchrow("""
                SELECT * FROM user_global_stats
                WHERE user_id = $1;
            """, user_id)
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get global stats error: {e}")
            return None

    @staticmethod
    async def get_chat_top_users(
        chat_id: int,
        limit: int = 10
    ) -> list:
        """Get top users by messages in a chat"""
        try:
            rows = await db.fetch("""
                SELECT us.*, u.first_name, u.username
                FROM user_stats us
                JOIN users u ON us.user_id = u.user_id
                WHERE us.chat_id = $1
                ORDER BY us.total_messages DESC
                LIMIT $2;
            """, chat_id, limit)
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Top users error: {e}")
            return []

    @staticmethod
    async def get_global_top_users(limit: int = 10) -> list:
        """Get top users globally"""
        try:
            rows = await db.fetch("""
                SELECT ugs.*, u.first_name, u.username
                FROM user_global_stats ugs
                JOIN users u ON ugs.user_id = u.user_id
                ORDER BY ugs.total_messages DESC
                LIMIT $1;
            """, limit)
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Global top users error: {e}")
            return []

    @staticmethod
    def get_rank_title(level: int) -> str:
        """Get rank title based on level"""
        ranks = {
            (1, 5): "🌱 Nᴇᴡʙɪᴇ",
            (6, 10): "🌿 Bᴇɢɪɴɴᴇʀ",
            (11, 20): "🍀 Aᴄᴛɪᴠᴇ",
            (21, 35): "⭐ Rᴇɢᴜʟᴀʀ",
            (36, 50): "🌟 Vᴇᴛᴇʀᴀɴ",
            (51, 70): "💫 Exᴘᴇʀᴛ",
            (71, 90): "🔥 Mᴀsᴛᴇʀ",
            (91, 120): "💎 Eʟɪᴛᴇ",
            (121, 160): "👑 Lᴇɢᴇɴᴅ",
            (161, 200): "🏆 Mʏᴛʜɪᴄᴀʟ",
            (201, 999): "⚡ Gᴏᴅ Lᴇᴠᴇʟ",
        }
        for (low, high), title in ranks.items():
            if low <= level <= high:
                return title
        return "🌱 Nᴇᴡʙɪᴇ"

    @staticmethod
    def get_xp_for_level(level: int) -> int:
        """Calculate XP needed for a level"""
        return (level ** 2) * 100

    @staticmethod
    def make_progress_bar(
        current: int,
        total: int,
        length: int = 10
    ) -> str:
        """Create a visual progress bar"""
        if total == 0:
            percent = 0
        else:
            percent = min(current / total, 1.0)
        filled = int(length * percent)
        empty = length - filled
        bar = "█" * filled + "░" * empty
        pct = int(percent * 100)
        return f"[{bar}] {pct}%"

    # ───────────────────────────────────────────────────────
    # AFK SYSTEM
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def set_afk(
        user_id: int,
        reason: str = ""
    ) -> None:
        """Set user as AFK"""
        try:
            await db.execute("""
                INSERT INTO afk (user_id, is_afk, reason, afk_time)
                VALUES ($1, TRUE, $2, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    is_afk = TRUE,
                    reason = EXCLUDED.reason,
                    afk_time = NOW();
            """, user_id, reason[:500])

            # Update users table too
            await db.execute("""
                UPDATE users SET
                    afk = TRUE,
                    afk_reason = $1,
                    afk_time = NOW()
                WHERE user_id = $2;
            """, reason[:500], user_id)

        except Exception as e:
            logger.error(f"Set AFK error: {e}")

    @staticmethod
    async def remove_afk(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove AFK status and return AFK info
        (reason, duration, etc.)
        """
        try:
            afk_row = await db.fetchrow(
                "SELECT * FROM afk WHERE user_id = $1 AND is_afk = TRUE;",
                user_id
            )

            if not afk_row:
                return None

            afk_data = dict(afk_row)

            # Calculate duration
            afk_time = afk_data.get("afk_time")
            if afk_time:
                now = datetime.now(timezone.utc)
                if afk_time.tzinfo is None:
                    afk_time = afk_time.replace(tzinfo=timezone.utc)
                duration = int((now - afk_time).total_seconds())
            else:
                duration = 0

            # Save to history
            await db.execute("""
                INSERT INTO afk_history (
                    user_id, reason, afk_start,
                    afk_end, duration_secs
                ) VALUES ($1, $2, $3, NOW(), $4);
            """,
                user_id,
                afk_data.get("reason", ""),
                afk_data.get("afk_time"),
                duration
            )

            # Clear AFK
            await db.execute("""
                UPDATE afk SET is_afk = FALSE WHERE user_id = $1;
            """, user_id)

            await db.execute("""
                UPDATE users SET
                    afk = FALSE,
                    afk_reason = '',
                    afk_time = NULL
                WHERE user_id = $1;
            """, user_id)

            afk_data["duration"] = duration
            return afk_data

        except Exception as e:
            logger.error(f"Remove AFK error: {e}")
            return None

    @staticmethod
    async def is_afk(user_id: int) -> Tuple[bool, str, Optional[datetime]]:
        """Check if user is AFK. Returns (is_afk, reason, afk_time)"""
        try:
            row = await db.fetchrow(
                "SELECT is_afk, reason, afk_time FROM afk WHERE user_id = $1;",
                user_id
            )
            if row and row["is_afk"]:
                return True, row["reason"] or "", row["afk_time"]
            return False, "", None
        except Exception:
            return False, "", None

    @staticmethod
    async def get_afk_history(
        user_id: int,
        limit: int = 10
    ) -> list:
        """Get AFK history for a user"""
        try:
            rows = await db.fetch("""
                SELECT * FROM afk_history
                WHERE user_id = $1
                ORDER BY afk_start DESC
                LIMIT $2;
            """, user_id, limit)
            return [dict(r) for r in rows]
        except Exception:
            return []

    # ───────────────────────────────────────────────────────
    # WARNINGS SYSTEM
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def add_warn(
        chat_id: int,
        user_id: int,
        warned_by: int,
        reason: str = ""
    ) -> Tuple[int, int]:
        """
        Add a warning to user in chat.
        Returns (current_warns, warn_limit).
        """
        try:
            # Get current active warn count
            current = await db.fetchval("""
                SELECT COUNT(*) FROM warn_details
                WHERE chat_id = $1 AND user_id = $2 AND is_active = TRUE;
            """, chat_id, user_id) or 0

            warn_number = current + 1

            # Insert warning
            await db.execute("""
                INSERT INTO warn_details (
                    chat_id, user_id, warned_by,
                    reason, warn_number
                ) VALUES ($1, $2, $3, $4, $5);
            """, chat_id, user_id, warned_by, reason[:500], warn_number)

            # Also insert into legacy warnings table
            await db.execute("""
                INSERT INTO warnings (
                    chat_id, user_id, warned_by, reason
                ) VALUES ($1, $2, $3, $4);
            """, chat_id, user_id, warned_by, reason[:500])

            # Update user warns count in users table
            await db.execute("""
                UPDATE users SET warns = $1
                WHERE user_id = $2;
            """, warn_number, user_id)

            # Get warn limit
            limit_row = await db.fetchrow(
                "SELECT warn_limit FROM warn_settings WHERE chat_id = $1;",
                chat_id
            )
            warn_limit = limit_row["warn_limit"] if limit_row else 3

            return warn_number, warn_limit

        except Exception as e:
            logger.error(f"Add warn error: {e}")
            return 0, 3

    @staticmethod
    async def remove_warn(
        chat_id: int,
        user_id: int,
        removed_by: int
    ) -> bool:
        """Remove the last active warning"""
        try:
            last_warn = await db.fetchrow("""
                SELECT id FROM warn_details
                WHERE chat_id = $1 AND user_id = $2 AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1;
            """, chat_id, user_id)

            if not last_warn:
                return False

            await db.execute("""
                UPDATE warn_details SET
                    is_active = FALSE,
                    removed_by = $1,
                    removed_at = NOW()
                WHERE id = $2;
            """, removed_by, last_warn["id"])

            # Update user warns count
            new_count = await db.fetchval("""
                SELECT COUNT(*) FROM warn_details
                WHERE chat_id = $1 AND user_id = $2 AND is_active = TRUE;
            """, chat_id, user_id) or 0

            await db.execute("""
                UPDATE users SET warns = $1
                WHERE user_id = $2;
            """, new_count, user_id)

            return True

        except Exception as e:
            logger.error(f"Remove warn error: {e}")
            return False

    @staticmethod
    async def get_warns(
        chat_id: int,
        user_id: int
    ) -> Tuple[int, list]:
        """Get active warnings for user in chat"""
        try:
            rows = await db.fetch("""
                SELECT * FROM warn_details
                WHERE chat_id = $1 AND user_id = $2 AND is_active = TRUE
                ORDER BY created_at ASC;
            """, chat_id, user_id)
            return len(rows), [dict(r) for r in rows]
        except Exception:
            return 0, []

    @staticmethod
    async def reset_warns(
        chat_id: int,
        user_id: int,
        removed_by: int
    ) -> int:
        """Reset all warnings for user in chat. Returns count removed."""
        try:
            count = await db.fetchval("""
                SELECT COUNT(*) FROM warn_details
                WHERE chat_id = $1 AND user_id = $2 AND is_active = TRUE;
            """, chat_id, user_id) or 0

            await db.execute("""
                UPDATE warn_details SET
                    is_active = FALSE,
                    removed_by = $1,
                    removed_at = NOW()
                WHERE chat_id = $2 AND user_id = $3 AND is_active = TRUE;
            """, removed_by, chat_id, user_id)

            await db.execute("""
                UPDATE users SET warns = 0
                WHERE user_id = $1;
            """, user_id)

            return count

        except Exception as e:
            logger.error(f"Reset warns error: {e}")
            return 0

    @staticmethod
    async def get_warn_settings(
        chat_id: int
    ) -> Tuple[int, str, int]:
        """Get warning settings for chat. Returns (limit, action, duration)"""
        try:
            row = await db.fetchrow(
                "SELECT * FROM warn_settings WHERE chat_id = $1;",
                chat_id
            )
            if row:
                return (
                    row["warn_limit"],
                    row["warn_action"],
                    row["warn_action_duration"]
                )
            return 3, "mute", 3600
        except Exception:
            return 3, "mute", 3600

    @staticmethod
    async def set_warn_limit(
        chat_id: int,
        limit: int
    ) -> None:
        """Set warning limit for chat"""
        try:
            await db.execute("""
                INSERT INTO warn_settings (chat_id, warn_limit)
                VALUES ($1, $2)
                ON CONFLICT (chat_id) DO UPDATE SET
                    warn_limit = EXCLUDED.warn_limit;
            """, chat_id, max(1, min(limit, 100)))
        except Exception as e:
            logger.error(f"Set warn limit error: {e}")

    @staticmethod
    async def set_warn_action(
        chat_id: int,
        action: str,
        duration: int = 3600
    ) -> None:
        """Set warning action for chat"""
        valid_actions = ["ban", "kick", "mute", "tban", "tmute"]
        if action not in valid_actions:
            action = "mute"
        try:
            await db.execute("""
                INSERT INTO warn_settings (
                    chat_id, warn_action, warn_action_duration
                ) VALUES ($1, $2, $3)
                ON CONFLICT (chat_id) DO UPDATE SET
                    warn_action = EXCLUDED.warn_action,
                    warn_action_duration = EXCLUDED.warn_action_duration;
            """, chat_id, action, duration)
        except Exception as e:
            logger.error(f"Set warn action error: {e}")

    @staticmethod
    async def get_warned_users(
        chat_id: int
    ) -> list:
        """Get all warned users in a chat"""
        try:
            rows = await db.fetch("""
                SELECT wd.user_id,
                       COUNT(*) as warn_count,
                       u.first_name,
                       u.username
                FROM warn_details wd
                JOIN users u ON wd.user_id = u.user_id
                WHERE wd.chat_id = $1 AND wd.is_active = TRUE
                GROUP BY wd.user_id, u.first_name, u.username
                ORDER BY warn_count DESC;
            """, chat_id)
            return [dict(r) for r in rows]
        except Exception:
            return []

    # ───────────────────────────────────────────────────────
    # PERSONAL NOTES
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def save_personal_note(
        user_id: int,
        note_name: str,
        content: str,
        media_type: str = "",
        media_id: str = ""
    ) -> bool:
        """Save a personal note for user"""
        try:
            await db.execute("""
                INSERT INTO personal_notes (
                    user_id, note_name, note_content,
                    media_type, media_id, updated_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (user_id, note_name) DO UPDATE SET
                    note_content = EXCLUDED.note_content,
                    media_type = EXCLUDED.media_type,
                    media_id = EXCLUDED.media_id,
                    updated_at = NOW();
            """, user_id, note_name.lower().strip(),
                content, media_type, media_id)
            return True
        except Exception as e:
            logger.error(f"Save personal note error: {e}")
            return False

    @staticmethod
    async def get_personal_note(
        user_id: int,
        note_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get a personal note"""
        try:
            row = await db.fetchrow("""
                SELECT * FROM personal_notes
                WHERE user_id = $1 AND note_name = $2;
            """, user_id, note_name.lower().strip())
            return dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    async def get_all_personal_notes(
        user_id: int
    ) -> list:
        """Get all personal notes for user"""
        try:
            rows = await db.fetch("""
                SELECT note_name, created_at, updated_at
                FROM personal_notes
                WHERE user_id = $1
                ORDER BY updated_at DESC;
            """, user_id)
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    async def delete_personal_note(
        user_id: int,
        note_name: str
    ) -> bool:
        """Delete a personal note"""
        try:
            result = await db.execute("""
                DELETE FROM personal_notes
                WHERE user_id = $1 AND note_name = $2;
            """, user_id, note_name.lower().strip())
            return result == "DELETE 1"
        except Exception:
            return False

    @staticmethod
    async def clear_all_personal_notes(
        user_id: int
    ) -> int:
        """Delete all personal notes for user"""
        try:
            count = await db.fetchval("""
                SELECT COUNT(*) FROM personal_notes
                WHERE user_id = $1;
            """, user_id)
            await db.execute(
                "DELETE FROM personal_notes WHERE user_id = $1;",
                user_id
            )
            return count or 0
        except Exception:
            return 0

    @staticmethod
    async def count_personal_notes(user_id: int) -> int:
        """Count personal notes"""
        try:
            return await db.fetchval(
                "SELECT COUNT(*) FROM personal_notes WHERE user_id = $1;",
                user_id
            ) or 0
        except Exception:
            return 0


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ AFK CACHE (In-Memory for Fast Access) ◈◈◈
# ═══════════════════════════════════════════════════════════════

class AFKCache:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   In-memory AFK cache for instant lookups            ║
    ║   Syncs with database periodically                   ║
    ╚═══════════════════════════════════════════════════════╝
    """

    def __init__(self):
        self._afk_users: Dict[int, Tuple[str, datetime]] = {}
        # {user_id: (reason, afk_time)}

    async def load_from_db(self) -> None:
        """Load AFK users from database"""
        try:
            rows = await db.fetch(
                "SELECT user_id, reason, afk_time FROM afk WHERE is_afk = TRUE;"
            )
            for row in rows:
                self._afk_users[row["user_id"]] = (
                    row["reason"] or "",
                    row["afk_time"]
                )
            logger.info(
                f"✅ AFK cache loaded: {len(self._afk_users)} users"
            )
        except Exception as e:
            logger.error(f"AFK cache load error: {e}")

    def is_afk(self, user_id: int) -> bool:
        return user_id in self._afk_users

    def get_afk_info(
        self, user_id: int
    ) -> Optional[Tuple[str, datetime]]:
        return self._afk_users.get(user_id)

    def set_afk(
        self, user_id: int, reason: str = ""
    ) -> None:
        self._afk_users[user_id] = (reason, datetime.now(timezone.utc))

    def remove_afk(self, user_id: int) -> bool:
        if user_id in self._afk_users:
            del self._afk_users[user_id]
            return True
        return False

    def get_all_afk(self) -> Dict[int, Tuple[str, datetime]]:
        return self._afk_users.copy()

    def count(self) -> int:
        return len(self._afk_users)


# Global AFK cache
afk_cache = AFKCache()


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — MESSAGE TEMPLATES ◈◈◈
# ═══════════════════════════════════════════════════════════════

class UserTemplates:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Stylish message templates for User Management      ║
    ║   God-level formatting & symbols                     ║
    ╚═══════════════════════════════════════════════════════╝
    """

    # ───────────────────────────────────────────────────────
    # USER INFO / ME
    # ───────────────────────────────────────────────────────

    @staticmethod
    def detailed_user_info(
        user: User,
        full_data: Optional[Dict[str, Any]] = None,
        chat: Optional[Chat] = None,
        member: Optional[ChatMember] = None,
        photos_count: int = 0,
        common_chats: int = 0,
    ) -> str:
        """Ultra-detailed user info card"""

        user_mention = get_user_mention(user)
        full_name = get_user_full_name(user)

        # ── Role badges ──
        badges = []
        if cache.is_owner(user.id):
            badges.append("👑 𝐎ᴡɴᴇʀ")
        if cache.is_sudo(user.id) and not cache.is_owner(user.id):
            badges.append("⚔️ 𝐒ᴜᴅᴏ")
        if cache.is_support(user.id) and not cache.is_sudo(user.id):
            badges.append("🛡️ 𝐒ᴜᴘᴘᴏʀᴛ")
        if cache.is_gbanned(user.id):
            badges.append("🔨 𝐆ʙᴀɴɴᴇᴅ")
        if cache.is_gmuted(user.id):
            badges.append("🔇 𝐆ᴍᴜᴛᴇᴅ")

        badge_str = " │ ".join(badges) if badges else ""

        # ── Chat member status ──
        status_str = ""
        status_emoji = ""
        custom_title = ""
        if member:
            if isinstance(member, ChatMemberOwner):
                status_str = StyleFont.small_caps("creator/owner")
                status_emoji = "👑"
                custom_title = member.custom_title or ""
            elif isinstance(member, ChatMemberAdministrator):
                status_str = StyleFont.small_caps("administrator")
                status_emoji = "⚡"
                custom_title = member.custom_title or ""
            elif isinstance(member, ChatMemberMember):
                status_str = StyleFont.small_caps("member")
                status_emoji = "👤"
            elif isinstance(member, ChatMemberRestricted):
                status_str = StyleFont.small_caps("restricted")
                status_emoji = "🔇"
            elif isinstance(member, ChatMemberBanned):
                status_str = StyleFont.small_caps("banned")
                status_emoji = "🔨"
            elif isinstance(member, ChatMemberLeft):
                status_str = StyleFont.small_caps("left/not member")
                status_emoji = "🚪"

        # ── Global stats ──
        g_stats = full_data.get("global_stats", {}) if full_data else {}
        total_msgs = g_stats.get("total_messages", 0)
        xp = g_stats.get("xp_points", 0)
        level = g_stats.get("level", 1)
        active_days = g_stats.get("total_active_days", 0)
        rank = UserDB.get_rank_title(level)
        next_level_xp = UserDB.get_xp_for_level(level + 1)
        progress = UserDB.make_progress_bar(xp, next_level_xp, 12)

        # ── User settings ──
        settings = full_data.get("settings", {}) if full_data else {}
        bio = settings.get("bio", "") or (
            full_data.get("bio", "") if full_data else ""
        )

        # ── AFK info ──
        afk_data = full_data.get("afk_data") if full_data else None
        afk_str = ""
        if afk_data and afk_data.get("is_afk"):
            afk_reason = afk_data.get("reason", "")
            afk_str = f"✅ ({afk_reason})" if afk_reason else "✅"

        # ── Warns ──
        warns_count = full_data.get("active_warns", 0) if full_data else 0
        pnotes_count = full_data.get("personal_notes_count", 0) if full_data else 0

        # ── Reputation ──
        reputation = full_data.get("reputation", 0) if full_data else 0

        # ── Profile views ──
        profile_views = full_data.get("profile_views", 0) if full_data else 0

        # ── Build message ──
        text = (
            f"✦ {StyleFont.mixed_bold_smallcaps('User Information')} ✦\n"
            f"{Symbols.divider(5)}\n"
        )

        if badge_str:
            text += f"  {badge_str}\n"

        text += (
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Identity')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Full Name')}: "
            f"{html_escape(full_name)}\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"{'@' + user.username if user.username else StyleFont.small_caps('none')}\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Mention')}: "
            f"{user_mention}\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Is Bot')}: "
            f"{'✅ ʏᴇs' if user.is_bot else '❌ ɴᴏ'}\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Dc Id')}: "
            f"<code>{getattr(user, 'dc_id', 'N/A')}</code>\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Language')}: "
            f"<code>{user.language_code or 'N/A'}</code>\n"
            #
            f"{Symbols.BOX_V} {Symbols.DIAMOND} "
            f"{StyleFont.mixed_bold_smallcaps('Profile Photos')}: "
            f"<b>{photos_count}</b>\n"
        )

        if bio:
            text += (
                f"{Symbols.BOX_V} {Symbols.DIAMOND} "
                f"{StyleFont.mixed_bold_smallcaps('Bio')}: "
                f"<i>{html_escape(bio[:200])}</i>\n"
            )

        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
        )

        # ── Chat status section ──
        if chat and chat.type != ChatType.PRIVATE and status_str:
            text += (
                f"\n"
                f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
                f"{StyleFont.bold_sans('Chat Status')} "
                f"]{Symbols.BOX_H * 4}{Symbols.BOX_TR}\n"
                #
                f"{Symbols.BOX_V} {status_emoji} "
                f"{StyleFont.mixed_bold_smallcaps('Status')}: "
                f"{status_str}\n"
            )
            if custom_title:
                text += (
                    f"{Symbols.BOX_V} 🏷️ "
                    f"{StyleFont.mixed_bold_smallcaps('Title')}: "
                    f"<i>{html_escape(custom_title)}</i>\n"
                )
            text += (
                f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            )

        # ── Stats section ──
        text += (
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Statistics')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} 💬 "
            f"{StyleFont.mixed_bold_smallcaps('Messages')}: "
            f"<b>{format_number(total_msgs)}</b>\n"
            #
            f"{Symbols.BOX_V} ⭐ "
            f"{StyleFont.mixed_bold_smallcaps('Reputation')}: "
            f"<b>{reputation}</b>\n"
            #
            f"{Symbols.BOX_V} 📅 "
            f"{StyleFont.mixed_bold_smallcaps('Active Days')}: "
            f"<b>{active_days}</b>\n"
            #
            f"{Symbols.BOX_V} 👁️ "
            f"{StyleFont.mixed_bold_smallcaps('Profile Views')}: "
            f"<b>{format_number(profile_views)}</b>\n"
            #
            f"{Symbols.BOX_V} ⚠️ "
            f"{StyleFont.mixed_bold_smallcaps('Active Warns')}: "
            f"<b>{warns_count}</b>\n"
            #
            f"{Symbols.BOX_V} 📝 "
            f"{StyleFont.mixed_bold_smallcaps('Personal Notes')}: "
            f"<b>{pnotes_count}</b>\n"
            #
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
        )

        # ── Level section ──
        text += (
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Level & XP')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} 🎖️ "
            f"{StyleFont.mixed_bold_smallcaps('Rank')}: "
            f"{rank}\n"
            #
            f"{Symbols.BOX_V} ✨ "
            f"{StyleFont.mixed_bold_smallcaps('Level')}: "
            f"<b>{level}</b>\n"
            #
            f"{Symbols.BOX_V} 💎 "
            f"{StyleFont.mixed_bold_smallcaps('Xp')}: "
            f"<b>{format_number(xp)}</b> / "
            f"<b>{format_number(next_level_xp)}</b>\n"
            #
            f"{Symbols.BOX_V} 📊 "
            f"{StyleFont.mixed_bold_smallcaps('Progress')}: "
            f"<code>{progress}</code>\n"
            #
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
        )

        # ── AFK section ──
        if afk_str:
            text += (
                f"\n"
                f"💤 {StyleFont.mixed_bold_smallcaps('Afk Status')}: "
                f"{afk_str}\n"
            )

        # ── Footer ──
        text += (
            f"\n{Symbols.divider(5)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    # ───────────────────────────────────────────────────────
    # USER STATS
    # ───────────────────────────────────────────────────────

    @staticmethod
    def user_stats_message(
        user: User,
        chat_stats: Optional[Dict[str, Any]],
        global_stats: Optional[Dict[str, Any]],
        chat: Optional[Chat] = None,
    ) -> str:
        """Detailed stats card for a user"""

        user_mention = get_user_mention(user)
        gs = global_stats or {}
        cs = chat_stats or {}

        # Level info
        level = gs.get("level", 1)
        xp = gs.get("xp_points", 0)
        rank = UserDB.get_rank_title(level)
        next_xp = UserDB.get_xp_for_level(level + 1)
        progress = UserDB.make_progress_bar(xp, next_xp, 14)

        text = (
            f"✦ {StyleFont.mixed_bold_smallcaps('User Statistics')} ✦\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Rank')}: "
            f"{rank}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Level')}: "
            f"<b>{level}</b> │ "
            f"{StyleFont.mixed_bold_smallcaps('Xp')}: "
            f"<b>{format_number(xp)}</b>\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Progress')}: "
            f"<code>{progress}</code>\n"
            f"\n"
        )

        # ── Global stats ──
        text += (
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Global Stats')} "
            f"]{Symbols.BOX_H * 4}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} 💬 "
            f"{StyleFont.mixed_bold_smallcaps('Total Messages')}: "
            f"<b>{format_number(gs.get('total_messages', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 📝 "
            f"{StyleFont.mixed_bold_smallcaps('Text Messages')}: "
            f"<b>{format_number(gs.get('total_text', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🖼️ "
            f"{StyleFont.mixed_bold_smallcaps('Photos')}: "
            f"<b>{format_number(gs.get('total_photos', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🎬 "
            f"{StyleFont.mixed_bold_smallcaps('Videos')}: "
            f"<b>{format_number(gs.get('total_videos', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🎭 "
            f"{StyleFont.mixed_bold_smallcaps('Stickers')}: "
            f"<b>{format_number(gs.get('total_stickers', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 📁 "
            f"{StyleFont.mixed_bold_smallcaps('Documents')}: "
            f"<b>{format_number(gs.get('total_documents', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🎵 "
            f"{StyleFont.mixed_bold_smallcaps('Audio')}: "
            f"<b>{format_number(gs.get('total_audio', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🎤 "
            f"{StyleFont.mixed_bold_smallcaps('Voices')}: "
            f"<b>{format_number(gs.get('total_voices', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🎞️ "
            f"{StyleFont.mixed_bold_smallcaps('Gifs')}: "
            f"<b>{format_number(gs.get('total_animations', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} ↩️ "
            f"{StyleFont.mixed_bold_smallcaps('Forwards')}: "
            f"<b>{format_number(gs.get('total_forwards', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 📊 "
            f"{StyleFont.mixed_bold_smallcaps('Words Typed')}: "
            f"<b>{format_number(gs.get('total_words', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 🔤 "
            f"{StyleFont.mixed_bold_smallcaps('Characters')}: "
            f"<b>{format_number(gs.get('total_characters', 0))}</b>\n"
            #
            f"{Symbols.BOX_V} 📅 "
            f"{StyleFont.mixed_bold_smallcaps('Active Days')}: "
            f"<b>{gs.get('total_active_days', 0)}</b>\n"
            #
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Commands Used')}: "
            f"<b>{format_number(gs.get('total_commands_used', 0))}</b>\n"
            #
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
        )

        # ── Chat-specific stats ──
        if cs and chat and chat.type != ChatType.PRIVATE:
            chat_name = html_escape(chat.title or "This Chat")
            text += (
                f"\n"
                f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
                f"{StyleFont.bold_sans('In')} {chat_name} "
                f"]{Symbols.BOX_H * 2}{Symbols.BOX_TR}\n"
                #
                f"{Symbols.BOX_V} 💬 "
                f"{StyleFont.mixed_bold_smallcaps('Messages')}: "
                f"<b>{format_number(cs.get('total_messages', 0))}</b>\n"
                #
                f"{Symbols.BOX_V} 📝 "
                f"{StyleFont.mixed_bold_smallcaps('Text')}: "
                f"<b>{format_number(cs.get('total_text', 0))}</b>\n"
                #
                f"{Symbols.BOX_V} 🖼️ "
                f"{StyleFont.mixed_bold_smallcaps('Media')}: "
                f"<b>{format_number(cs.get('total_photos', 0) + cs.get('total_videos', 0) + cs.get('total_stickers', 0))}</b>\n"
                #
                f"{Symbols.BOX_V} 🔥 "
                f"{StyleFont.mixed_bold_smallcaps('Streak')}: "
                f"<b>{cs.get('streak_days', 0)}</b> "
                f"{StyleFont.small_caps('days')}\n"
                #
                f"{Symbols.BOX_V} 🏆 "
                f"{StyleFont.mixed_bold_smallcaps('Max Streak')}: "
                f"<b>{cs.get('max_streak', 0)}</b> "
                f"{StyleFont.small_caps('days')}\n"
                #
                f"{Symbols.BOX_V} 📅 "
                f"{StyleFont.mixed_bold_smallcaps('Active Days')}: "
                f"<b>{cs.get('active_days', 0)}</b>\n"
                #
                f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            )

        # ── First & last seen ──
        first_seen = gs.get("first_seen")
        last_seen = gs.get("last_seen")
        if first_seen:
            text += (
                f"\n{Symbols.CLOCK} "
                f"{StyleFont.mixed_bold_smallcaps('First Seen')}: "
                f"<code>{first_seen.strftime('%d %b %Y, %H:%M')}</code>\n"
            )
        if last_seen:
            text += (
                f"{Symbols.CLOCK} "
                f"{StyleFont.mixed_bold_smallcaps('Last Active')}: "
                f"<code>{last_seen.strftime('%d %b %Y, %H:%M')}</code>\n"
            )

        text += (
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    # ───────────────────────────────────────────────────────
    # AFK TEMPLATES
    # ───────────────────────────────────────────────────────

    @staticmethod
    def afk_set_message(user: User, reason: str = "") -> str:
        """AFK set notification"""
        user_mention = get_user_mention(user)
        text = (
            f"💤 {StyleFont.mixed_bold_smallcaps('Afk Mode Activated')}\n"
            f"{Symbols.divider(8)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
        )
        if reason:
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:200])}</i>\n"
            )
        text += (
            f"\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('i will notify when you are mentioned')}\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def afk_return_message(
        user: User,
        duration: int = 0,
        mentions_missed: int = 0
    ) -> str:
        """AFK return notification"""
        user_mention = get_user_mention(user)
        dur_str = get_readable_time(duration) if duration else "0s"

        text = (
            f"🌅 {StyleFont.mixed_bold_smallcaps('Welcome Back')}!\n"
            f"{Symbols.divider(8)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Was Afk For')}: "
            f"<b>{dur_str}</b>\n"
        )
        if mentions_missed > 0:
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Missed Mentions')}: "
                f"<b>{mentions_missed}</b>\n"
            )
        text += (
            f"\n{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def afk_mention_alert(
        afk_user: User,
        reason: str = "",
        afk_since: Optional[datetime] = None
    ) -> str:
        """Alert when someone mentions an AFK user"""
        user_mention = get_user_mention(afk_user)

        duration_str = ""
        if afk_since:
            now = datetime.now(timezone.utc)
            if afk_since.tzinfo is None:
                afk_since = afk_since.replace(tzinfo=timezone.utc)
            dur = int((now - afk_since).total_seconds())
            duration_str = get_readable_time(dur)

        text = (
            f"💤 {user_mention} "
            f"{StyleFont.small_caps('is currently afk')}\n"
        )
        if reason:
            text += (
                f"{Symbols.ARROW_TRI} "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:200])}</i>\n"
            )
        if duration_str:
            text += (
                f"{Symbols.ARROW_TRI} "
                f"{StyleFont.mixed_bold_smallcaps('Since')}: "
                f"<b>{duration_str}</b> {StyleFont.small_caps('ago')}\n"
            )

        return text

    # ───────────────────────────────────────────────────────
    # WARNING TEMPLATES
    # ───────────────────────────────────────────────────────

    @staticmethod
    def warn_message(
        user: User,
        admin: User,
        warn_num: int,
        warn_limit: int,
        reason: str = "",
        chat: Optional[Chat] = None,
    ) -> str:
        """Warning issued notification"""
        user_mention = get_user_mention(user)
        admin_mention = get_user_mention(admin)
        warn_bar = UserDB.make_progress_bar(warn_num, warn_limit, 10)

        text = (
            f"⚠️ {StyleFont.mixed_bold_smallcaps('Warning Issued')} ⚠️\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Warn Info')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            #
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            #
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Warned By')}: "
            f"{admin_mention}\n"
            #
            f"{Symbols.BOX_V} ⚠️ "
            f"{StyleFont.mixed_bold_smallcaps('Warns')}: "
            f"<b>{warn_num}</b> / <b>{warn_limit}</b>\n"
            #
            f"{Symbols.BOX_V} 📊 "
            f"{StyleFont.mixed_bold_smallcaps('Status')}: "
            f"<code>{warn_bar}</code>\n"
        )

        if reason:
            text += (
                f"{Symbols.BOX_V} 📋 "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:200])}</i>\n"
            )

        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
        )

        if warn_num >= warn_limit:
            text += (
                f"\n{Symbols.CROSS3} "
                f"{StyleFont.bold_sans('WARN LIMIT REACHED')}!\n"
                f"{Symbols.ARROW_TRI} "
                f"{StyleFont.small_caps('action will be taken automatically')}\n"
            )

        text += (
            f"\n{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    @staticmethod
    def warns_list_message(
        user: User,
        warn_count: int,
        warns: list,
        warn_limit: int,
        chat: Optional[Chat] = None,
    ) -> str:
        """List of warnings for a user"""
        user_mention = get_user_mention(user)
        warn_bar = UserDB.make_progress_bar(warn_count, warn_limit, 10)

        text = (
            f"⚠️ {StyleFont.mixed_bold_smallcaps('Warnings')} ⚠️\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Warns')}: "
            f"<b>{warn_count}</b> / <b>{warn_limit}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Status')}: "
            f"<code>{warn_bar}</code>\n"
            f"\n"
        )

        if warns:
            text += (
                f"{StyleFont.bold_sans('Warning Details')}:\n"
                f"{Symbols.divider(9)}\n"
            )
            for i, w in enumerate(warns, 1):
                reason = w.get("reason", "No reason")
                created = w.get("created_at", "")
                date_str = ""
                if created:
                    date_str = created.strftime("%d/%m/%Y %H:%M")
                text += (
                    f" {Symbols.NUMS[i-1] if i <= 10 else f'{i}.'} "
                    f"{StyleFont.small_caps(reason or 'no reason')}\n"
                    f"    {Symbols.TINY_DOT} "
                    f"{StyleFont.small_caps(date_str)}\n"
                )
        else:
            text += (
                f"{Symbols.CHECK2} "
                f"{StyleFont.small_caps('no active warnings')}\n"
            )

        text += (
            f"\n{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    # ───────────────────────────────────────────────────────
    # PERSONAL NOTES TEMPLATES
    # ───────────────────────────────────────────────────────

    @staticmethod
    def personal_notes_list(
        user: User,
        notes: list,
    ) -> str:
        """List of personal notes"""
        user_mention = get_user_mention(user)

        text = (
            f"📝 {StyleFont.mixed_bold_smallcaps('Personal Notes')} 📝\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Notes')}: "
            f"<b>{len(notes)}</b>\n"
            f"\n"
        )

        if notes:
            for i, note in enumerate(notes, 1):
                name = note.get("note_name", "unknown")
                updated = note.get("updated_at", "")
                date_str = ""
                if updated:
                    date_str = f" ({updated.strftime('%d/%m')})"
                text += (
                    f" {Symbols.ARROW_TRI} "
                    f"<code>{name}</code>{date_str}\n"
                )
        else:
            text += (
                f"{Symbols.INFO} "
                f"{StyleFont.small_caps('no personal notes saved')}\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('use /pnote <name> <content> to save')}\n"
            )

        text += (
            f"\n{Symbols.divider(6)}\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.small_caps('use /pget <name> to retrieve')}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    # ───────────────────────────────────────────────────────
    # USER SETTINGS TEMPLATE
    # ───────────────────────────────────────────────────────

    @staticmethod
    def user_settings_message(
        user: User,
        settings: Dict[str, Any],
    ) -> str:
        """User settings display"""
        user_mention = get_user_mention(user)

        def bool_icon(val: bool) -> str:
            return "✅" if val else "❌"

        text = (
            f"⚙️ {StyleFont.mixed_bold_smallcaps('User Settings')} ⚙️\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Settings')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            #
            f"{Symbols.BOX_V} 📝 "
            f"{StyleFont.mixed_bold_smallcaps('Bio')}: "
            f"<i>{html_escape(settings.get('bio', '') or 'Not set')}</i>\n"
            #
            f"{Symbols.BOX_V} 🏷️ "
            f"{StyleFont.mixed_bold_smallcaps('Custom Name')}: "
            f"{html_escape(settings.get('custom_name', '') or 'Not set')}\n"
            #
            f"{Symbols.BOX_V} 🔔 "
            f"{StyleFont.mixed_bold_smallcaps('Notifications')}: "
            f"{bool_icon(settings.get('notifications', True))}\n"
            #
            f"{Symbols.BOX_V} 💌 "
            f"{StyleFont.mixed_bold_smallcaps('Pm Allowed')}: "
            f"{bool_icon(settings.get('pm_allowed', True))}\n"
            #
            f"{Symbols.BOX_V} 👁️ "
            f"{StyleFont.mixed_bold_smallcaps('Read Receipts')}: "
            f"{bool_icon(settings.get('read_receipts', True))}\n"
            #
            f"{Symbols.BOX_V} 💤 "
            f"{StyleFont.mixed_bold_smallcaps('Auto Afk')}: "
            f"{bool_icon(settings.get('auto_afk', False))}\n"
            #
            f"{Symbols.BOX_V} 👋 "
            f"{StyleFont.mixed_bold_smallcaps('Welcome Dm')}: "
            f"{bool_icon(settings.get('welcome_dm', True))}\n"
            #
            f"{Symbols.BOX_V} 🌐 "
            f"{StyleFont.mixed_bold_smallcaps('Language')}: "
            f"<code>{settings.get('language', 'en')}</code>\n"
            #
            f"{Symbols.BOX_V} 🔒 "
            f"{StyleFont.mixed_bold_smallcaps('Profile Private')}: "
            f"{bool_icon(settings.get('profile_private', False))}\n"
            #
            f"{Symbols.BOX_V} 👀 "
            f"{StyleFont.mixed_bold_smallcaps('Last Seen')}: "
            f"{bool_icon(settings.get('last_seen_enabled', True))}\n"
            #
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.small_caps('use buttons below to change settings')}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text

    # ───────────────────────────────────────────────────────
    # TOP USERS TEMPLATE
    # ───────────────────────────────────────────────────────

    @staticmethod
    def top_users_message(
        top_users: list,
        chat: Optional[Chat] = None,
        is_global: bool = False,
    ) -> str:
        """Top users leaderboard"""
        title = "Global Leaderboard" if is_global else "Chat Leaderboard"
        chat_name = ""
        if chat and not is_global:
            chat_name = html_escape(chat.title or "This Chat")

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        text = (
            f"🏆 {StyleFont.mixed_bold_smallcaps(title)} 🏆\n"
            f"{Symbols.divider(6)}\n"
        )

        if chat_name and not is_global:
            text += (
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
                f"{chat_name}\n"
            )

        text += f"\n"

        if not top_users:
            text += (
                f"{Symbols.INFO} "
                f"{StyleFont.small_caps('no data available yet')}\n"
            )
        else:
            for i, u in enumerate(top_users):
                medal = medals[i] if i < len(medals) else f"{i+1}."
                name = html_escape(u.get("first_name", "Unknown"))
                msgs = format_number(u.get("total_messages", 0))
                username = u.get("username", "")
                uid = u.get("user_id", 0)

                text += (
                    f" {medal} "
                    f"<a href='tg://user?id={uid}'>{name}</a>"
                    f" — <b>{msgs}</b> "
                    f"{StyleFont.small_caps('msgs')}\n"
                )

        text += (
            f"\n{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        return text


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — KEYBOARD BUILDERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class UserKeyboards:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Inline keyboards for user management commands      ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    def info_keyboard(
        user_id: int,
        show_stats: bool = True,
    ) -> InlineKeyboardMarkup:
        """User info action keyboard"""
        buttons = []
        if show_stats:
            buttons.append([
                InlineKeyboardButton(
                    f"📊 {StyleFont.bold_sans('Stats')}",
                    callback_data=f"ustats_{user_id}"
                ),
                InlineKeyboardButton(
                    f"🖼️ {StyleFont.bold_sans('Photo')}",
                    callback_data=f"uphoto_{user_id}"
                ),
            ])
        buttons.append([
            InlineKeyboardButton(
                f"⚠️ {StyleFont.bold_sans('Warns')}",
                callback_data=f"uwarns_{user_id}"
            ),
            InlineKeyboardButton(
                f"🔄 {StyleFont.bold_sans('Refresh')}",
                callback_data=f"uinfo_{user_id}"
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                f"🔄 {StyleFont.bold_sans('Close')}",
                callback_data="close"
            ),
        ])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def stats_keyboard(
        user_id: int,
        chat_id: int = 0,
    ) -> InlineKeyboardMarkup:
        """Stats navigation keyboard"""
        buttons = [
            [
                InlineKeyboardButton(
                    f"🌍 {StyleFont.bold_sans('Global')}",
                    callback_data=f"gstats_{user_id}"
                ),
                InlineKeyboardButton(
                    f"💬 {StyleFont.bold_sans('Chat')}",
                    callback_data=f"cstats_{user_id}_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🏆 {StyleFont.bold_sans('Top Users')}",
                    callback_data=f"topusers_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"◀️ {StyleFont.bold_sans('Back')}",
                    callback_data=f"uinfo_{user_id}"
                ),
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
        """User settings toggle keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔔 {StyleFont.bold_sans('Notifications')}",
                    callback_data=f"uset_notifications_{user_id}"
                ),
                InlineKeyboardButton(
                    f"💌 {StyleFont.bold_sans('PM')}",
                    callback_data=f"uset_pm_allowed_{user_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"💤 {StyleFont.bold_sans('Auto AFK')}",
                    callback_data=f"uset_auto_afk_{user_id}"
                ),
                InlineKeyboardButton(
                    f"🔒 {StyleFont.bold_sans('Private')}",
                    callback_data=f"uset_profile_private_{user_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"👀 {StyleFont.bold_sans('Last Seen')}",
                    callback_data=f"uset_last_seen_enabled_{user_id}"
                ),
                InlineKeyboardButton(
                    f"👋 {StyleFont.bold_sans('Welcome DM')}",
                    callback_data=f"uset_welcome_dm_{user_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📝 {StyleFont.bold_sans('Set Bio')}",
                    callback_data=f"uset_bio_prompt_{user_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def warn_action_keyboard(
        chat_id: int,
        user_id: int,
    ) -> InlineKeyboardMarkup:
        """Warn action buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❌ {StyleFont.bold_sans('Remove Warn')}",
                    callback_data=f"unwarn_{chat_id}_{user_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def personal_note_keyboard(
        note_name: str,
    ) -> InlineKeyboardMarkup:
        """Personal note actions"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❌ {StyleFont.bold_sans('Delete')}",
                    callback_data=f"pdel_{note_name}"
                ),
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def afk_keyboard() -> InlineKeyboardMarkup:
        """AFK info keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — COMMAND HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
#  /me — SELF INFO COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_me(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /me — View your own detailed profile information.
    Shows identity, stats, level, XP, rank, and more.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    # Register / update user
    await UserDB.register_user(user)

    # Increment profile views
    await UserDB.increment_profile_views(user.id)

    # Get full data
    full_data = await UserDB.get_full_user(user.id)

    # Get profile photos count
    photos_count = 0
    try:
        photos = await context.bot.get_user_profile_photos(
            user.id, limit=1
        )
        photos_count = photos.total_count
    except Exception:
        pass

    # Get member status
    member = None
    if chat and chat.type != ChatType.PRIVATE:
        try:
            member = await context.bot.get_chat_member(
                chat.id, user.id
            )
        except Exception:
            pass

    text = UserTemplates.detailed_user_info(
        user=user,
        full_data=full_data,
        chat=chat,
        member=member,
        photos_count=photos_count,
    )

    keyboard = UserKeyboards.info_keyboard(user.id)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ───────────────────────────────────────────────────────────────
#  /whois — DETAILED USER INFO (reply / @username / user_id)
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_whois(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /whois — Get detailed information about any user.
    Usage: /whois (reply) or /whois @username or /whois user_id
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    # Determine target user
    target_user = None
    target_id = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args:
        target_str = context.args[0]
        try:
            if target_str.startswith("@"):
                chat_info = await context.bot.get_chat(target_str)
                target_id = chat_info.id
                # We need to construct user-like object
                target_user = chat_info
            else:
                target_id = int(target_str)
                chat_info = await context.bot.get_chat(target_id)
                target_user = chat_info
        except (ValueError, BadRequest, Forbidden):
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('User not found')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('check the id or username and try again')}.",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        target_user = user
        target_id = user.id

    if not target_user or not target_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Please specify a user')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('reply to a message or provide @username / user_id')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Register target user if possible
    if hasattr(target_user, 'is_bot'):
        await UserDB.register_user(target_user)

    # Increment profile views
    await UserDB.increment_profile_views(target_id)

    # Full data
    full_data = await UserDB.get_full_user(target_id)

    # Photos count
    photos_count = 0
    try:
        photos = await context.bot.get_user_profile_photos(
            target_id, limit=1
        )
        photos_count = photos.total_count
    except Exception:
        pass

    # Member status
    member = None
    if chat and chat.type != ChatType.PRIVATE:
        try:
            member = await context.bot.get_chat_member(
                chat.id, target_id
            )
        except Exception:
            pass

    text = UserTemplates.detailed_user_info(
        user=target_user,
        full_data=full_data,
        chat=chat,
        member=member,
        photos_count=photos_count,
    )

    keyboard = UserKeyboards.info_keyboard(target_id)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ───────────────────────────────────────────────────────────────
#  /who — QUICK WHO IS (reply only)
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
@check_disabled
async def cmd_who(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /who — Quick who is this (reply to message).
    Shows a brief profile of the replied user.
    """
    message = update.effective_message
    if not message:
        return

    if not message.reply_to_message:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Reply to a message to use this')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    target = message.reply_to_message.from_user
    if not target:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Cannot identify user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_chat_action(ChatAction.TYPING)

    user_mention = get_user_mention(target)
    full_name = get_user_full_name(target)

    # Quick info
    is_owner = cache.is_owner(target.id)
    is_sudo = cache.is_sudo(target.id)
    is_support = cache.is_support(target.id)

    role = StyleFont.small_caps("member")
    if is_owner:
        role = f"👑 {StyleFont.small_caps('owner')}"
    elif is_sudo:
        role = f"⚔️ {StyleFont.small_caps('sudo')}"
    elif is_support:
        role = f"🛡️ {StyleFont.small_caps('support')}"

    # AFK check
    afk_str = ""
    if afk_cache.is_afk(target.id):
        info = afk_cache.get_afk_info(target.id)
        if info:
            afk_str = f"\n💤 {StyleFont.small_caps('currently afk')}"
            if info[0]:
                afk_str += f": <i>{html_escape(info[0][:100])}</i>"

    text = (
        f"✦ {StyleFont.mixed_bold_smallcaps('Who Is This')} ✦\n"
        f"{Symbols.divider(8)}\n"
        f"\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Name')}: "
        f"{html_escape(full_name)}\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Id')}: "
        f"<code>{target.id}</code>\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Username')}: "
        f"{'@' + target.username if target.username else StyleFont.small_caps('none')}\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Mention')}: "
        f"{user_mention}\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Role')}: "
        f"{role}\n"
        f"{Symbols.DIAMOND} "
        f"{StyleFont.mixed_bold_smallcaps('Bot')}: "
        f"{'✅' if target.is_bot else '❌'}"
        f"{afk_str}\n"
        f"\n{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=UserKeyboards.info_keyboard(target.id),
    )


# ───────────────────────────────────────────────────────────────
#  /myid — QUICK ID COMMAND
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
@check_disabled
async def cmd_myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /myid — Quick get your own ID.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    text = (
        f"🆔 {StyleFont.mixed_bold_smallcaps('Your Id')}\n"
        f"{Symbols.divider(8)}\n"
        f"\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
        f"<code>{user.id}</code>\n"
    )

    if chat and chat.type != ChatType.PRIVATE:
        text += (
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat Id')}: "
            f"<code>{chat.id}</code>\n"
        )

    if message.reply_to_message and message.reply_to_message.from_user:
        reply_user = message.reply_to_message.from_user
        text += (
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Replied User Id')}: "
            f"<code>{reply_user.id}</code>\n"
        )

    text += (
        f"\n{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /pp, /profilepic — GET USER PROFILE PHOTOS
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
@check_disabled
async def cmd_profilepic(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pp or /profilepic — Get profile photo(s) of a user.
    Reply to user or provide @username / user_id.
    Optional: /pp @user 3 (get up to 3 photos)
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    # Determine target
    target_id = user.id
    target_name = get_user_full_name(user)
    count = 1  # default: send 1 photo

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        target_name = get_user_full_name(target_user)
        if context.args:
            try:
                count = min(int(context.args[0]), 10)
            except ValueError:
                count = 1
    elif context.args:
        target_str = context.args[0]
        try:
            if target_str.startswith("@"):
                chat_info = await context.bot.get_chat(target_str)
                target_id = chat_info.id
                target_name = chat_info.first_name or target_str
            elif target_str.isdigit():
                target_id = int(target_str)
                chat_info = await context.bot.get_chat(target_id)
                target_name = chat_info.first_name or str(target_id)
            else:
                try:
                    count = min(int(target_str), 10)
                except ValueError:
                    pass
        except (BadRequest, Forbidden):
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('User not found')}!",
                parse_mode=ParseMode.HTML,
            )
            return

        if len(context.args) > 1:
            try:
                count = min(int(context.args[1]), 10)
            except ValueError:
                count = 1

    count = max(1, count)

    await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

    try:
        photos = await context.bot.get_user_profile_photos(
            target_id, limit=count
        )
    except (BadRequest, Forbidden):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Cannot access profile photos')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if photos.total_count == 0:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No profile photos found')} "
            f"{StyleFont.small_caps('for')} "
            f"<a href='tg://user?id={target_id}'>"
            f"{html_escape(target_name)}</a>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Send photos
    if len(photos.photos) == 1:
        # Single photo
        photo = photos.photos[0][-1]  # Highest resolution
        caption = (
            f"🖼️ {StyleFont.mixed_bold_smallcaps('Profile Photo')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={target_id}'>"
            f"{html_escape(target_name)}</a>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Photos')}: "
            f"<b>{photos.total_count}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Photo Id')}: "
            f"<code>{photo.file_id[:20]}...</code>\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        await message.reply_photo(
            photo=photo.file_id,
            caption=caption,
            parse_mode=ParseMode.HTML,
        )
    else:
        # Multiple photos — send as media group
        media_group = []
        for i, photo_sizes in enumerate(photos.photos):
            photo = photo_sizes[-1]  # Highest res
            if i == 0:
                caption = (
                    f"🖼️ {StyleFont.mixed_bold_smallcaps('Profile Photos')}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: "
                    f"{html_escape(target_name)}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Showing')}: "
                    f"{len(photos.photos)} / {photos.total_count}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )
            else:
                caption = f"📸 Photo {i+1}"

            media_group.append(
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
            )

        try:
            await message.reply_media_group(media=media_group)
        except BadRequest:
            # Fallback: send one by one
            for media in media_group:
                await message.reply_photo(
                    photo=media.media,
                    caption=media.caption,
                    parse_mode=ParseMode.HTML,
                )


# ───────────────────────────────────────────────────────────────
#  /mystats, /userstats — USER STATISTICS
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_mystats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /mystats — View your own message statistics.
    Shows global & chat-specific stats.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    # Global stats
    global_stats = await UserDB.get_user_global_stats(user.id)

    # Chat stats (if in group)
    chat_stats = None
    if chat and chat.type != ChatType.PRIVATE:
        chat_stats = await UserDB.get_user_chat_stats(
            user.id, chat.id
        )

    text = UserTemplates.user_stats_message(
        user=user,
        chat_stats=chat_stats,
        global_stats=global_stats,
        chat=chat,
    )

    keyboard = UserKeyboards.stats_keyboard(
        user.id,
        chat.id if chat else 0
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


@track_command
@cooldown(3.0)
@check_disabled
async def cmd_userstats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /userstats — View another user's statistics.
    Usage: /userstats (reply) or /userstats @user
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not message:
        return

    # Determine target
    target_user = None
    target_id = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args:
        try:
            target_str = context.args[0]
            if target_str.startswith("@"):
                info = await context.bot.get_chat(target_str)
            else:
                info = await context.bot.get_chat(int(target_str))
            target_user = info
            target_id = info.id
        except Exception:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('User not found')}!",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        target_user = user
        target_id = user.id

    if not target_id:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    global_stats = await UserDB.get_user_global_stats(target_id)

    chat_stats = None
    if chat and chat.type != ChatType.PRIVATE:
        chat_stats = await UserDB.get_user_chat_stats(
            target_id, chat.id
        )

    text = UserTemplates.user_stats_message(
        user=target_user,
        chat_stats=chat_stats,
        global_stats=global_stats,
        chat=chat,
    )

    keyboard = UserKeyboards.stats_keyboard(
        target_id,
        chat.id if chat else 0
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# ───────────────────────────────────────────────────────────────
#  /topusers — LEADERBOARD
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
@check_disabled
async def cmd_topusers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /topusers — Show top 10 most active users.
    In group: shows chat leaderboard.
    In PM: shows global leaderboard.
    """
    chat = update.effective_chat
    message = update.effective_message

    if not message:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    if chat and chat.type != ChatType.PRIVATE:
        # Chat leaderboard
        top = await UserDB.get_chat_top_users(chat.id, 10)
        text = UserTemplates.top_users_message(
            top, chat=chat, is_global=False
        )
    else:
        # Global leaderboard
        top = await UserDB.get_global_top_users(10)
        text = UserTemplates.top_users_message(
            top, is_global=True
        )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
#  /settings — USER SETTINGS
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /settings — View and manage your personal settings.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    settings = await UserDB.get_settings(user.id)
    if not settings:
        # Create default settings
        await UserDB.update_setting(user.id, "bio", "")
        settings = await UserDB.get_settings(user.id)
        if not settings:
            settings = {}

    text = UserTemplates.user_settings_message(user, settings)
    keyboard = UserKeyboards.settings_keyboard(user.id)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# ───────────────────────────────────────────────────────────────
#  /setbio — SET USER BIO
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
@check_disabled
async def cmd_setbio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /setbio <text> — Set your profile bio.
    Max 500 characters.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide bio text')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('usage')}: <code>/setbio Your bio here</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    bio = " ".join(context.args)
    if len(bio) > 500:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Bio too long')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('max 500 characters, yours')}: "
            f"<b>{len(bio)}</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    success = await UserDB.set_bio(user.id, bio)

    if success:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Bio Updated')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('New Bio')}: "
            f"<i>{html_escape(bio[:200])}</i>\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed to update bio')}!",
            parse_mode=ParseMode.HTML,
        )


# ───────────────────────────────────────────────────────────────
#  /clearbio — CLEAR USER BIO
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_clearbio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /clearbio — Clear your profile bio.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    await UserDB.set_bio(user.id, "")

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Bio Cleared')}!\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WARNING SYSTEM COMMANDS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
#  /warn — WARN A USER
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_warn(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /warn — Issue a warning to a user.
    Usage: /warn (reply) [reason] or /warn @user [reason]
    When warn limit reached, action is taken automatically.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    # Extract target & reason
    target_id, reason, target_obj = await extract_user_and_reason(
        message, context.bot
    )

    if not target_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify a user to warn')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('reply to a message or provide user id')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Permission checks
    can_restrict, error_msg = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can_restrict:
        await message.reply_text(error_msg, parse_mode=ParseMode.HTML)
        return

    # Don't warn self
    if target_id == user.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You cannot warn yourself')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    # Don't warn the bot
    if target_id == context.bot.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('I am not going to warn myself')}! 😤",
            parse_mode=ParseMode.HTML,
        )
        return

    # Get target user info
    try:
        target_chat = await context.bot.get_chat(target_id)
        target_user_name = target_chat.first_name or str(target_id)
    except Exception:
        target_user_name = str(target_id)

    # Add warning
    warn_num, warn_limit = await UserDB.add_warn(
        chat.id, target_id, user.id, reason or ""
    )

    # Create a mock user object for template
    class MockUser:
        def __init__(self, uid, fname, uname=None):
            self.id = uid
            self.first_name = fname
            self.last_name = ""
            self.username = uname
            self.is_bot = False
    
    target_mock = MockUser(target_id, target_user_name)

    text = UserTemplates.warn_message(
        user=target_mock,
        admin=user,
        warn_num=warn_num,
        warn_limit=warn_limit,
        reason=reason or "",
        chat=chat,
    )

    keyboard = UserKeyboards.warn_action_keyboard(chat.id, target_id)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )

    # If warn limit reached, take action
    if warn_num >= warn_limit:
        _, action, duration = await UserDB.get_warn_settings(chat.id)
        await _execute_warn_action(
            context.bot, chat, target_id,
            target_user_name, action, duration, warn_num
        )

    # Log
    await bot_logger.log(
        bot=context.bot,
        log_type=LogType.WARN,
        chat=chat,
        admin=user,
        user=target_mock,
        reason=reason or "No reason",
        extra=f"Warn {warn_num}/{warn_limit}",
    )


async def _execute_warn_action(
    bot: Bot,
    chat: Chat,
    user_id: int,
    user_name: str,
    action: str,
    duration: int,
    warn_count: int,
) -> None:
    """Execute the action when warn limit is reached"""
    try:
        action_text = ""

        if action == "ban":
            await bot.ban_chat_member(chat.id, user_id)
            action_text = f"🔨 {StyleFont.mixed_bold_smallcaps('Banned')}"

        elif action == "kick":
            await bot.ban_chat_member(chat.id, user_id)
            await bot.unban_chat_member(chat.id, user_id)
            action_text = f"🦶 {StyleFont.mixed_bold_smallcaps('Kicked')}"

        elif action == "mute":
            await bot.restrict_chat_member(
                chat.id, user_id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            action_text = f"🔇 {StyleFont.mixed_bold_smallcaps('Muted permanently')}"

        elif action == "tban":
            until = datetime.now(timezone.utc) + timedelta(seconds=duration)
            await bot.ban_chat_member(
                chat.id, user_id,
                until_date=until
            )
            dur_str = get_readable_time(duration)
            action_text = (
                f"🔨 {StyleFont.mixed_bold_smallcaps('Temporarily banned')} "
                f"({dur_str})"
            )

        elif action == "tmute":
            until = datetime.now(timezone.utc) + timedelta(seconds=duration)
            await bot.restrict_chat_member(
                chat.id, user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until,
            )
            dur_str = get_readable_time(duration)
            action_text = (
                f"🔇 {StyleFont.mixed_bold_smallcaps('Temporarily muted')} "
                f"({dur_str})"
            )

        if action_text:
            # Reset warns after action
            await UserDB.reset_warns(chat.id, user_id, 0)

            await bot.send_message(
                chat.id,
                f"{Symbols.WARNING} "
                f"{StyleFont.bold_sans('Warn Limit Action')}\n"
                f"{Symbols.divider(8)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('User')}: "
                f"<a href='tg://user?id={user_id}'>"
                f"{html_escape(user_name)}</a>\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                f"{action_text}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Warns Reached')}: "
                f"<b>{warn_count}</b>\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Warns Reset')}: ✅\n"
                f"{Symbols.divider(8)}\n"
                f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
                parse_mode=ParseMode.HTML,
            )

    except Exception as e:
        logger.error(f"Warn action error: {e}")


# ───────────────────────────────────────────────────────────────
#  /unwarn — REMOVE LAST WARNING
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(2.0)
async def cmd_unwarn(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /unwarn — Remove the last warning from a user.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, _, _ = await extract_user_and_reason(
        message, context.bot
    )

    if not target_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    removed = await UserDB.remove_warn(chat.id, target_id, user.id)

    if removed:
        warn_count, _ = await UserDB.get_warns(chat.id, target_id)
        warn_limit, _, _ = await UserDB.get_warn_settings(chat.id)

        try:
            target = await context.bot.get_chat(target_id)
            name = target.first_name or str(target_id)
        except Exception:
            name = str(target_id)

        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Warning Removed')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={target_id}'>"
            f"{html_escape(name)}</a>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Current Warns')}: "
            f"<b>{warn_count}</b> / <b>{warn_limit}</b>\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )

        await bot_logger.log(
            bot=context.bot,
            log_type=LogType.UNWARN,
            chat=chat,
            admin=user,
            extra=f"Unwarned user {target_id}",
        )
    else:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No active warnings to remove')}!",
            parse_mode=ParseMode.HTML,
        )


# ───────────────────────────────────────────────────────────────
#  /warns — CHECK WARNINGS
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
@check_disabled
async def cmd_warns(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /warns — Check warnings for a user.
    Usage: /warns (reply) or /warns @user
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if chat.type == ChatType.PRIVATE:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('This only works in groups')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    # Determine target
    target_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_str = context.args[0]
            if target_str.startswith("@"):
                info = await context.bot.get_chat(target_str)
                target_id = info.id
            else:
                target_id = int(target_str)
        except Exception:
            pass
    else:
        target_id = user.id

    if not target_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    warn_count, warns = await UserDB.get_warns(chat.id, target_id)
    warn_limit, _, _ = await UserDB.get_warn_settings(chat.id)

    try:
        target_chat = await context.bot.get_chat(target_id)
    except Exception:
        class MockUser:
            def __init__(self, uid):
                self.id = uid
                self.first_name = str(uid)
                self.last_name = ""
                self.username = None
                self.is_bot = False
        target_chat = MockUser(target_id)

    text = UserTemplates.warns_list_message(
        user=target_chat,
        warn_count=warn_count,
        warns=warns,
        warn_limit=warn_limit,
        chat=chat,
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
#  /resetwarns — RESET ALL WARNINGS
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_resetwarns(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /resetwarns — Reset all warnings for a user.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, _, _ = await extract_user_and_reason(
        message, context.bot
    )

    if not target_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify a user')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    count = await UserDB.reset_warns(chat.id, target_id, user.id)

    try:
        target = await context.bot.get_chat(target_id)
        name = target.first_name or str(target_id)
    except Exception:
        name = str(target_id)

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Warnings Reset')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={target_id}'>"
        f"{html_escape(name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Warns Removed')}: "
        f"<b>{count}</b>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )

    await bot_logger.log(
        bot=context.bot,
        log_type=LogType.UNWARN,
        chat=chat,
        admin=user,
        extra=f"Reset {count} warns for {target_id}",
    )


# ───────────────────────────────────────────────────────────────
#  /warnlimit — SET WARN LIMIT
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_warnlimit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /warnlimit <number> — Set the warning limit.
    """
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    if not context.args:
        limit, action, duration = await UserDB.get_warn_settings(chat.id)
        await message.reply_text(
            f"{Symbols.GEAR} "
            f"{StyleFont.mixed_bold_smallcaps('Warn Settings')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Warn Limit')}: "
            f"<b>{limit}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"<b>{action}</b>\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('use /warnlimit <number> to change')}",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        new_limit = int(context.args[0])
        if new_limit < 1 or new_limit > 100:
            raise ValueError
    except ValueError:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Invalid number')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('must be between 1 and 100')}",
            parse_mode=ParseMode.HTML,
        )
        return

    await UserDB.set_warn_limit(chat.id, new_limit)

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Warn Limit Updated')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('New Limit')}: "
        f"<b>{new_limit}</b>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /warnaction — SET WARN ACTION
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_warnaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /warnaction <action> — Set warn limit action.
    Actions: ban, kick, mute, tban, tmute
    Optional duration: /warnaction tban 1h
    """
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    if not context.args:
        _, action, duration = await UserDB.get_warn_settings(chat.id)
        dur_str = get_readable_time(duration) if duration else "N/A"
        await message.reply_text(
            f"{Symbols.GEAR} "
            f"{StyleFont.mixed_bold_smallcaps('Current Warn Action')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"<b>{action}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Duration')}: "
            f"<b>{dur_str}</b>\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('available: ban, kick, mute, tban, tmute')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('example: /warnaction tban 2h')}",
            parse_mode=ParseMode.HTML,
        )
        return

    action = context.args[0].lower()
    valid_actions = ["ban", "kick", "mute", "tban", "tmute"]

    if action not in valid_actions:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Invalid action')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('choose from')}: "
            f"<code>{'</code>, <code>'.join(valid_actions)}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    duration = 3600  # default 1 hour
    if len(context.args) > 1 and action in ("tban", "tmute"):
        parsed = parse_time_arg(context.args[1])
        if parsed:
            duration = parsed

    await UserDB.set_warn_action(chat.id, action, duration)

    dur_str = get_readable_time(duration)
    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Warn Action Updated')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Action')}: "
        f"<b>{action}</b>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Duration')}: "
        f"<b>{dur_str}</b>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /warnlist — LIST ALL WARNED USERS
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(5.0)
async def cmd_warnlist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /warnlist — List all users with active warnings.
    """
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    warned = await UserDB.get_warned_users(chat.id)

    if not warned:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('No warned users in this chat')}! 🎉",
            parse_mode=ParseMode.HTML,
        )
        return

    warn_limit, _, _ = await UserDB.get_warn_settings(chat.id)

    text = (
        f"⚠️ {StyleFont.mixed_bold_smallcaps('Warned Users')} ⚠️\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
        f"{html_escape(chat.title or '')}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Warn Limit')}: "
        f"<b>{warn_limit}</b>\n"
        f"\n"
    )

    for i, w in enumerate(warned, 1):
        name = html_escape(w.get("first_name", "Unknown"))
        uid = w.get("user_id", 0)
        count = w.get("warn_count", 0)
        bar = UserDB.make_progress_bar(count, warn_limit, 8)

        text += (
            f" {Symbols.NUMS[i-1] if i <= 10 else f'{i}.'} "
            f"<a href='tg://user?id={uid}'>{name}</a>\n"
            f"    {Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('warns')}: "
            f"<b>{count}</b>/<b>{warn_limit}</b> "
            f"<code>{bar}</code>\n"
        )

    text += (
        f"\n{Symbols.divider(6)}\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('total warned')}: "
        f"<b>{len(warned)}</b>\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ PERSONAL NOTES COMMANDS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
#  /pnote, /psave — SAVE PERSONAL NOTE
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
async def cmd_pnote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pnote <name> <content> — Save a personal note.
    Also supports media: reply to media with /pnote <name>
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Usage')}:\n"
            f"{Symbols.BULLET} <code>/pnote name content</code>\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('reply to media with')} "
            f"<code>/pnote name</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    note_name = context.args[0].lower().strip()

    # Check for valid name
    if len(note_name) > 50:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Note name too long')}! "
            f"{StyleFont.small_caps('max 50 characters')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    content = ""
    media_type = ""
    media_id = ""

    if len(context.args) > 1:
        content = " ".join(context.args[1:])

    # Check for reply with media
    reply = message.reply_to_message
    if reply:
        if not content and reply.text:
            content = reply.text
        elif not content and reply.caption:
            content = reply.caption or ""

        if reply.photo:
            media_type = "photo"
            media_id = reply.photo[-1].file_id
        elif reply.video:
            media_type = "video"
            media_id = reply.video.file_id
        elif reply.document:
            media_type = "document"
            media_id = reply.document.file_id
        elif reply.audio:
            media_type = "audio"
            media_id = reply.audio.file_id
        elif reply.voice:
            media_type = "voice"
            media_id = reply.voice.file_id
        elif reply.sticker:
            media_type = "sticker"
            media_id = reply.sticker.file_id
        elif reply.animation:
            media_type = "animation"
            media_id = reply.animation.file_id
        elif reply.video_note:
            media_type = "video_note"
            media_id = reply.video_note.file_id

    if not content and not media_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide note content')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('text after name, or reply to media')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Check limit
    note_count = await UserDB.count_personal_notes(user.id)
    if note_count >= 50:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Note limit reached')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('max 50 personal notes. delete some first')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    success = await UserDB.save_personal_note(
        user.id, note_name, content or "",
        media_type, media_id
    )

    if success:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Personal Note Saved')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Name')}: "
            f"<code>{html_escape(note_name)}</code>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Type')}: "
            f"{media_type or 'text'}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('retrieve with')}: "
            f"<code>/pget {note_name}</code>\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed to save note')}!",
            parse_mode=ParseMode.HTML,
        )


# ───────────────────────────────────────────────────────────────
#  /pget — GET PERSONAL NOTE
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
async def cmd_pget(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pget <name> — Retrieve a personal note.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify note name')}!\n"
            f"{Symbols.BULLET} <code>/pget notename</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    note_name = context.args[0].lower().strip()
    note = await UserDB.get_personal_note(user.id, note_name)

    if not note:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Note not found')}: "
            f"<code>{html_escape(note_name)}</code>\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('use /pnotes to see all notes')}.",
            parse_mode=ParseMode.HTML,
        )
        return

    content = note.get("note_content", "")
    media_type = note.get("media_type", "")
    media_id = note.get("media_id", "")

    caption = (
        f"📝 {StyleFont.mixed_bold_smallcaps('Personal Note')}: "
        f"<code>{html_escape(note_name)}</code>\n"
        f"{Symbols.divider(9)}\n"
    )
    if content:
        caption += f"{content}\n"
    caption += (
        f"{Symbols.divider(9)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )

    keyboard = UserKeyboards.personal_note_keyboard(note_name)

    # Send based on media type
    try:
        if media_type == "photo" and media_id:
            await message.reply_photo(
                photo=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "video" and media_id:
            await message.reply_video(
                video=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "document" and media_id:
            await message.reply_document(
                document=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "audio" and media_id:
            await message.reply_audio(
                audio=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "voice" and media_id:
            await message.reply_voice(
                voice=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "sticker" and media_id:
            await message.reply_sticker(sticker=media_id)
            if content:
                await message.reply_text(
                    caption, parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
        elif media_type == "animation" and media_id:
            await message.reply_animation(
                animation=media_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif media_type == "video_note" and media_id:
            await message.reply_video_note(video_note=media_id)
            if content:
                await message.reply_text(
                    caption, parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
        else:
            await message.reply_text(
                caption, parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
    except Exception as e:
        await message.reply_text(
            caption, parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )


# ───────────────────────────────────────────────────────────────
#  /pnotes — LIST ALL PERSONAL NOTES
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(3.0)
async def cmd_pnotes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pnotes — List all your personal notes.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    notes = await UserDB.get_all_personal_notes(user.id)
    text = UserTemplates.personal_notes_list(user, notes)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
#  /pclear — DELETE A PERSONAL NOTE
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(2.0)
async def cmd_pclear(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pclear <name> — Delete a personal note.
    /pclear all — Delete ALL personal notes.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify note name')}!\n"
            f"{Symbols.BULLET} <code>/pclear notename</code>\n"
            f"{Symbols.BULLET} <code>/pclear all</code> "
            f"{StyleFont.small_caps('to delete all')}",
            parse_mode=ParseMode.HTML,
        )
        return

    target = context.args[0].lower().strip()

    if target == "all":
        count = await UserDB.clear_all_personal_notes(user.id)
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('All Notes Cleared')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Deleted')}: "
            f"<b>{count}</b> {StyleFont.small_caps('notes')}\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
    else:
        deleted = await UserDB.delete_personal_note(user.id, target)
        if deleted:
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Note Deleted')}: "
                f"<code>{html_escape(target)}</code>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Note not found')}: "
                f"<code>{html_escape(target)}</code>",
                parse_mode=ParseMode.HTML,
            )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ AFK SYSTEM COMMANDS & HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
#  /afk — SET AFK STATUS
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
async def cmd_afk(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /afk [reason] — Set your AFK status.
    Others will be notified when they mention you.
    """
    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    reason = ""
    if context.args:
        reason = " ".join(context.args)

    # Check if replying to media for AFK reason
    if message.reply_to_message and not reason:
        if message.reply_to_message.text:
            reason = message.reply_to_message.text[:200]

    # Set AFK in DB and cache
    await UserDB.set_afk(user.id, reason)
    afk_cache.set_afk(user.id, reason)

    text = UserTemplates.afk_set_message(user, reason)

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=UserKeyboards.afk_keyboard(),
    )


# ───────────────────────────────────────────────────────────────
#  AFK MESSAGE HANDLER (auto-detect return & mention alerts)
# ───────────────────────────────────────────────────────────────

async def afk_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles AFK system:
    1. If AFK user sends a message → remove AFK & notify
    2. If someone mentions/replies to an AFK user → alert
    3. If message contains @username of AFK user → alert
    """
    message = update.effective_message
    user = update.effective_user

    if not message or not user or user.is_bot:
        return

    chat = update.effective_chat
    if not chat:
        return

    # ── 1. Check if sender is AFK → auto-return ──
    if afk_cache.is_afk(user.id):
        afk_data = await UserDB.remove_afk(user.id)
        was_afk = afk_cache.remove_afk(user.id)

        if was_afk and afk_data:
            duration = afk_data.get("duration", 0)
            text = UserTemplates.afk_return_message(
                user=user,
                duration=duration,
            )
            try:
                sent = await message.reply_text(
                    text=text,
                    parse_mode=ParseMode.HTML,
                )
                # Auto-delete after 15 seconds
                asyncio.create_task(
                    _auto_delete_message(sent, 15)
                )
            except Exception:
                pass

    # ── 2. Check if replied-to user is AFK ──
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if afk_cache.is_afk(replied_user.id):
            info = afk_cache.get_afk_info(replied_user.id)
            reason = info[0] if info else ""
            afk_since = info[1] if info else None

            alert_text = UserTemplates.afk_mention_alert(
                afk_user=replied_user,
                reason=reason,
                afk_since=afk_since,
            )
            try:
                sent = await message.reply_text(
                    text=alert_text,
                    parse_mode=ParseMode.HTML,
                )
                asyncio.create_task(
                    _auto_delete_message(sent, 10)
                )
            except Exception:
                pass

    # ── 3. Check text mentions ──
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.MENTION:
                # @username mention
                username = message.text[
                    entity.offset + 1:entity.offset + entity.length
                ]
                # Look up user in cache/db
                try:
                    mentioned_chat = await context.bot.get_chat(
                        f"@{username}"
                    )
                    if afk_cache.is_afk(mentioned_chat.id):
                        info = afk_cache.get_afk_info(mentioned_chat.id)
                        reason = info[0] if info else ""
                        afk_since = info[1] if info else None

                        alert_text = UserTemplates.afk_mention_alert(
                            afk_user=mentioned_chat,
                            reason=reason,
                            afk_since=afk_since,
                        )
                        try:
                            sent = await message.reply_text(
                                text=alert_text,
                                parse_mode=ParseMode.HTML,
                            )
                            asyncio.create_task(
                                _auto_delete_message(sent, 10)
                            )
                        except Exception:
                            pass
                except Exception:
                    pass

            elif entity.type == MessageEntityType.TEXT_MENTION:
                # User mention without username
                if entity.user and afk_cache.is_afk(entity.user.id):
                    info = afk_cache.get_afk_info(entity.user.id)
                    reason = info[0] if info else ""
                    afk_since = info[1] if info else None

                    alert_text = UserTemplates.afk_mention_alert(
                        afk_user=entity.user,
                        reason=reason,
                        afk_since=afk_since,
                    )
                    try:
                        sent = await message.reply_text(
                            text=alert_text,
                            parse_mode=ParseMode.HTML,
                        )
                        asyncio.create_task(
                            _auto_delete_message(sent, 10)
                        )
                    except Exception:
                        pass


async def _auto_delete_message(
    message: Message, delay: int
) -> None:
    """Auto-delete a message after delay seconds"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ MESSAGE TRACKING HANDLER (Stats + Registration) ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section2_message_tracker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Track every message for:
    - User registration
    - Message stats per chat & global
    - Active day tracking
    - XP & level system
    """
    message = update.effective_message
    user = update.effective_user

    if not message or not user or user.is_bot:
        return

    chat = update.effective_chat
    if not chat:
        return

    try:
        # Register user
        is_new = await UserDB.register_user(user)

        # Track stats
        if chat.type != ChatType.PRIVATE:
            await UserDB.track_message_stats(
                user.id, chat.id, message
            )
        else:
            # Track global stats only for PM
            await db.execute("""
                INSERT INTO user_global_stats (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO UPDATE SET
                    total_messages = user_global_stats.total_messages + 1,
                    last_seen = NOW(),
                    total_active_days = CASE
                        WHEN user_global_stats.last_active_date < CURRENT_DATE
                        THEN user_global_stats.total_active_days + 1
                        ELSE user_global_stats.total_active_days
                    END,
                    last_active_date = CURRENT_DATE,
                    xp_points = user_global_stats.xp_points + $2;
            """, user.id, random.randint(1, 3))

    except Exception as e:
        logger.debug(f"S2 tracking error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — CALLBACK QUERY HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section2_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle Section 2 callback queries"""
    query = update.callback_query
    if not query:
        return

    data = query.data
    user = query.from_user
    message = query.message

    if not data or not user or not message:
        return

    # ── User Info Refresh ──
    if data.startswith("uinfo_"):
        await query.answer("🔄 Refreshing...")
        target_id = int(data.split("_")[1])

        full_data = await UserDB.get_full_user(target_id)

        try:
            target = await context.bot.get_chat(target_id)
        except Exception:
            await query.answer("User not found!", show_alert=True)
            return

        photos_count = 0
        try:
            photos = await context.bot.get_user_profile_photos(
                target_id, limit=1
            )
            photos_count = photos.total_count
        except Exception:
            pass

        chat = update.effective_chat
        member = None
        if chat and chat.type != ChatType.PRIVATE:
            try:
                member = await context.bot.get_chat_member(
                    chat.id, target_id
                )
            except Exception:
                pass

        text = UserTemplates.detailed_user_info(
            user=target,
            full_data=full_data,
            chat=chat,
            member=member,
            photos_count=photos_count,
        )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=UserKeyboards.info_keyboard(target_id),
            )
        except BadRequest:
            pass

    # ── User Stats ──
    elif data.startswith("ustats_"):
        await query.answer()
        target_id = int(data.split("_")[1])

        try:
            target = await context.bot.get_chat(target_id)
        except Exception:
            await query.answer("User not found!", show_alert=True)
            return

        global_stats = await UserDB.get_user_global_stats(target_id)

        chat = update.effective_chat
        chat_stats = None
        if chat and chat.type != ChatType.PRIVATE:
            chat_stats = await UserDB.get_user_chat_stats(
                target_id, chat.id
            )

        text = UserTemplates.user_stats_message(
            user=target,
            chat_stats=chat_stats,
            global_stats=global_stats,
            chat=chat,
        )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=UserKeyboards.stats_keyboard(
                    target_id,
                    chat.id if chat else 0
                ),
            )
        except BadRequest:
            pass

    # ── User Profile Photo ──
    elif data.startswith("uphoto_"):
        target_id = int(data.split("_")[1])

        try:
            photos = await context.bot.get_user_profile_photos(
                target_id, limit=1
            )
        except Exception:
            await query.answer(
                "Cannot access profile photos!",
                show_alert=True
            )
            return

        if photos.total_count == 0:
            await query.answer(
                "No profile photos found!",
                show_alert=True
            )
            return

        photo = photos.photos[0][-1]
        try:
            target = await context.bot.get_chat(target_id)
            name = target.first_name or str(target_id)
        except Exception:
            name = str(target_id)

        await query.answer()
        await message.reply_photo(
            photo=photo.file_id,
            caption=(
                f"🖼️ {StyleFont.mixed_bold_smallcaps('Profile Photo')}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('User')}: "
                f"{html_escape(name)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Total')}: "
                f"{photos.total_count}"
            ),
            parse_mode=ParseMode.HTML,
        )

    # ── User Warns ──
    elif data.startswith("uwarns_"):
        await query.answer()
        target_id = int(data.split("_")[1])
        chat = update.effective_chat

        if not chat or chat.type == ChatType.PRIVATE:
            await query.answer(
                "Warnings only available in groups!",
                show_alert=True
            )
            return

        warn_count, warns = await UserDB.get_warns(chat.id, target_id)
        warn_limit, _, _ = await UserDB.get_warn_settings(chat.id)

        try:
            target = await context.bot.get_chat(target_id)
        except Exception:
            class MockUser:
                def __init__(self, uid):
                    self.id = uid
                    self.first_name = str(uid)
                    self.last_name = ""
                    self.username = None
                    self.is_bot = False
            target = MockUser(target_id)

        text = UserTemplates.warns_list_message(
            user=target,
            warn_count=warn_count,
            warns=warns,
            warn_limit=warn_limit,
            chat=chat,
        )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"◀️ {StyleFont.bold_sans('Back')}",
                            callback_data=f"uinfo_{target_id}"
                        ),
                        InlineKeyboardButton(
                            f"🔄 {StyleFont.bold_sans('Close')}",
                            callback_data="close"
                        ),
                    ],
                ]),
            )
        except BadRequest:
            pass

    # ── Global Stats ──
    elif data.startswith("gstats_"):
        await query.answer()
        target_id = int(data.split("_")[1])

        try:
            target = await context.bot.get_chat(target_id)
        except Exception:
            await query.answer("User not found!", show_alert=True)
            return

        global_stats = await UserDB.get_user_global_stats(target_id)

        text = UserTemplates.user_stats_message(
            user=target,
            chat_stats=None,
            global_stats=global_stats,
        )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=UserKeyboards.stats_keyboard(target_id, 0),
            )
        except BadRequest:
            pass

    # ── Chat Stats ──
    elif data.startswith("cstats_"):
        await query.answer()
        parts = data.split("_")
        target_id = int(parts[1])
        chat_id = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else 0

        if not chat_id:
            await query.answer(
                "No chat context available!",
                show_alert=True
            )
            return

        try:
            target = await context.bot.get_chat(target_id)
        except Exception:
            await query.answer("User not found!", show_alert=True)
            return

        chat_stats = await UserDB.get_user_chat_stats(target_id, chat_id)
        global_stats = await UserDB.get_user_global_stats(target_id)

        try:
            chat_obj = await context.bot.get_chat(chat_id)
        except Exception:
            chat_obj = None

        text = UserTemplates.user_stats_message(
            user=target,
            chat_stats=chat_stats,
            global_stats=global_stats,
            chat=chat_obj,
        )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=UserKeyboards.stats_keyboard(
                    target_id, chat_id
                ),
            )
        except BadRequest:
            pass

    # ── Top Users ──
    elif data.startswith("topusers_"):
        await query.answer()
        chat_id = int(data.split("_")[1])

        if chat_id:
            top = await UserDB.get_chat_top_users(chat_id, 10)
            try:
                chat_obj = await context.bot.get_chat(chat_id)
            except Exception:
                chat_obj = None
            text = UserTemplates.top_users_message(
                top, chat=chat_obj, is_global=False
            )
        else:
            top = await UserDB.get_global_top_users(10)
            text = UserTemplates.top_users_message(
                top, is_global=True
            )

        try:
            await message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=KeyboardBuilder.close_keyboard(),
            )
        except BadRequest:
            pass

    # ── Unwarn via callback ──
    elif data.startswith("unwarn_"):
        parts = data.split("_")
        chat_id = int(parts[1])
        target_id = int(parts[2])

        # Check if caller is admin
        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer(
                "Only admins can remove warnings!",
                show_alert=True
            )
            return

        removed = await UserDB.remove_warn(chat_id, target_id, user.id)

        if removed:
            warn_count, _ = await UserDB.get_warns(chat_id, target_id)
            warn_limit, _, _ = await UserDB.get_warn_settings(chat_id)

            await query.answer(
                f"✅ Warning removed! ({warn_count}/{warn_limit})"
            )

            try:
                target = await context.bot.get_chat(target_id)
                name = target.first_name or str(target_id)
            except Exception:
                name = str(target_id)

            try:
                await message.edit_text(
                    f"{Symbols.CHECK2} "
                    f"{StyleFont.mixed_bold_smallcaps('Warning Removed')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: "
                    f"<a href='tg://user?id={target_id}'>"
                    f"{html_escape(name)}</a>\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Warns')}: "
                    f"<b>{warn_count}</b> / <b>{warn_limit}</b>\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Removed By')}: "
                    f"{get_user_mention(user)}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
                    parse_mode=ParseMode.HTML,
                )
            except BadRequest:
                pass
        else:
            await query.answer(
                "No active warnings to remove!",
                show_alert=True
            )

    # ── Personal Note Delete via callback ──
    elif data.startswith("pdel_"):
        note_name = data.replace("pdel_", "", 1)
        deleted = await UserDB.delete_personal_note(user.id, note_name)

        if deleted:
            await query.answer(f"✅ Note '{note_name}' deleted!")
            try:
                await message.edit_text(
                    f"{Symbols.CHECK2} "
                    f"{StyleFont.mixed_bold_smallcaps('Note Deleted')}: "
                    f"<code>{html_escape(note_name)}</code>",
                    parse_mode=ParseMode.HTML,
                )
            except BadRequest:
                pass
        else:
            await query.answer("Note not found!", show_alert=True)

    # ── User Settings Toggle ──
    elif data.startswith("uset_") and not data.startswith("uset_bio_prompt"):
        parts = data.split("_")
        # uset_settingname_userid
        if len(parts) >= 3:
            setting = "_".join(parts[1:-1])
            target_id = int(parts[-1])

            if target_id != user.id:
                await query.answer(
                    "You can only change your own settings!",
                    show_alert=True
                )
                return

            # Get current value
            current = await UserDB.get_settings(user.id)
            if not current:
                current = {}

            # Toggle boolean settings
            bool_settings = [
                'notifications', 'pm_allowed', 'read_receipts',
                'auto_afk', 'welcome_dm', 'profile_private',
                'last_seen_enabled'
            ]

            if setting in bool_settings:
                current_val = current.get(setting, True)
                new_val = not current_val
                await UserDB.update_setting(user.id, setting, new_val)

                status = "✅ ON" if new_val else "❌ OFF"
                await query.answer(
                    f"{setting.replace('_', ' ').title()}: {status}"
                )

                # Refresh settings display
                updated = await UserDB.get_settings(user.id)
                if updated:
                    text = UserTemplates.user_settings_message(
                        user, updated
                    )
                    try:
                        await message.edit_text(
                            text=text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=UserKeyboards.settings_keyboard(
                                user.id
                            ),
                        )
                    except BadRequest:
                        pass

    elif data.startswith("uset_bio_prompt_"):
        target_id = int(data.split("_")[-1])
        if target_id != user.id:
            await query.answer(
                "You can only change your own bio!",
                show_alert=True
            )
            return

        await query.answer()
        try:
            await message.reply_text(
                f"{Symbols.GEAR} "
                f"{StyleFont.mixed_bold_smallcaps('Set Bio')}\n"
                f"{Symbols.divider(8)}\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('send your new bio text now')}\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('or use')}: "
                f"<code>/setbio Your bio here</code>",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — POST INIT (Table creation + cache load) ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section2_post_init(application: Application) -> None:
    """Section 2 post-initialization"""
    # Create Section 2 tables
    await UserDB.create_tables()

    # Load AFK cache
    await afk_cache.load_from_db()

    logger.info("✅ Section 2 (User Management) initialized!")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 2 — REGISTER ALL HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

def register_section2_handlers(application: Application) -> None:
    """Register all Section 2 command handlers"""

    # ── User Info Commands ──
    application.add_handler(
        CommandHandler("me", cmd_me)
    )
    application.add_handler(
        CommandHandler("whois", cmd_whois)
    )
    application.add_handler(
        CommandHandler("who", cmd_who)
    )
    application.add_handler(
        CommandHandler("myid", cmd_myid)
    )
    application.add_handler(
        CommandHandler(["pp", "profilepic"], cmd_profilepic)
    )

    # ── Stats Commands ──
    application.add_handler(
        CommandHandler("mystats", cmd_mystats)
    )
    application.add_handler(
        CommandHandler("userstats", cmd_userstats)
    )
    application.add_handler(
        CommandHandler("topusers", cmd_topusers)
    )

    # ── Settings Commands ──
    application.add_handler(
        CommandHandler("settings", cmd_settings)
    )
    application.add_handler(
        CommandHandler("setbio", cmd_setbio)
    )
    application.add_handler(
        CommandHandler("clearbio", cmd_clearbio)
    )

    # ── Warning Commands ──
    application.add_handler(
        CommandHandler("warn", cmd_warn)
    )
    application.add_handler(
        CommandHandler("unwarn", cmd_unwarn)
    )
    application.add_handler(
        CommandHandler("warns", cmd_warns)
    )
    application.add_handler(
        CommandHandler("resetwarns", cmd_resetwarns)
    )
    application.add_handler(
        CommandHandler("warnlimit", cmd_warnlimit)
    )
    application.add_handler(
        CommandHandler("warnaction", cmd_warnaction)
    )
    application.add_handler(
        CommandHandler("warnlist", cmd_warnlist)
    )

    # ── Personal Notes Commands ──
    application.add_handler(
        CommandHandler(["pnote", "psave"], cmd_pnote)
    )
    application.add_handler(
        CommandHandler("pget", cmd_pget)
    )
    application.add_handler(
        CommandHandler("pnotes", cmd_pnotes)
    )
    application.add_handler(
        CommandHandler("pclear", cmd_pclear)
    )

    # ── AFK Command ──
    application.add_handler(
        CommandHandler("afk", cmd_afk)
    )

    # ── Section 2 Callback Handler ──
    application.add_handler(
        CallbackQueryHandler(
            section2_callback_handler,
            pattern=r"^(uinfo_|ustats_|uphoto_|uwarns_|gstats_|"
                    r"cstats_|topusers_|unwarn_|pdel_|uset_)"
        )
    )

    # ── AFK Message Handler (high priority group) ──
    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND & ~filters.StatusUpdate.ALL,
            afk_message_handler
        ),
        group=5,  # Run before other handlers
    )

    # ── Message Tracker (lowest priority) ──
    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            section2_message_tracker
        ),
        group=98,  # Just before section 1 tracker
    )

    logger.info(
        "✅ Section 2 handlers registered: "
        "User Management System "
        f"({len([
            'me', 'whois', 'who', 'myid', 'pp',
            'mystats', 'userstats', 'topusers',
            'settings', 'setbio', 'clearbio',
            'warn', 'unwarn', 'warns', 'resetwarns',
            'warnlimit', 'warnaction', 'warnlist',
            'pnote', 'pget', 'pnotes', 'pclear',
            'afk',
        ])} commands)"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ INTEGRATION INSTRUCTIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════
#
# Add these 2 lines in your existing code:
#
# 1. In post_init() function, ADD:
#        await section2_post_init(application)
#
# 2. In register_handlers() function, ADD:
#        register_section2_handlers(application)
#
# That's it! Section 2 is fully integrated.
#
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#
#   ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#   ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
#   ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║
#   ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║
#   ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#   ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#
#       ██████╗      ██╗    ██╗███████╗██╗      ██████╗
#       ╚════██╗     ██║    ██║██╔════╝██║     ██╔════╝
#        █████╔╝     ██║ █╗ ██║█████╗  ██║     ██║
#        ╚═══██╗     ██║███╗██║██╔══╝  ██║     ██║
#       ██████╔╝     ╚███╔███╔╝███████╗███████╗╚██████╗
#       ╚═════╝       ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝
#
#    ██████╗  ██████╗  ██████╗ ██████╗ ██████╗ ██╗   ██╗███████╗
#   ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝
#   ██║  ███╗██║   ██║██║   ██║██║  ██║██████╔╝ ╚████╔╝ █████╗
#   ██║   ██║██║   ██║██║   ██║██║  ██║██╔══██╗  ╚██╔╝  ██╔══╝
#   ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║   ███████╗
#    ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝
#
# ═══════════════════════════════════════════════════════════════
#
#   SECTION 3 : WELCOME / GOODBYE SYSTEM
#   ──────────────────────────────────────────
#   ✦ Welcome new members (ultra stylish)
#   ✦ Goodbye messages (stylish departure)
#   ✦ Custom welcome message (set/reset)
#   ✦ Welcome format (text / photo / gif / video)
#   ✦ Welcome buttons (inline URL/custom)
#   ✦ Clean welcome (auto-delete old welcome)
#   ✦ Welcome mute (mute new users temp)
#   ✦ CAPTCHA verification system (button/math/text)
#   ✦ Anti-raid welcome system
#   ✦ Welcome channel redirect
#   ✦ Welcome security settings
#
#   Powered By: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — DATABASE TABLES ◈◈◈
# ═══════════════════════════════════════════════════════════════

SECTION3_TABLES_SQL = """

-- ══════════════════════════════════════════
-- Welcome / Goodbye settings (extended)
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS welcome_settings (
    chat_id                 BIGINT PRIMARY KEY,

    -- Welcome toggle & content
    welcome_enabled         BOOLEAN DEFAULT TRUE,
    welcome_text            TEXT DEFAULT '',
    welcome_media_id        TEXT DEFAULT '',
    welcome_media_type      TEXT DEFAULT '',
    welcome_buttons         TEXT DEFAULT '[]',
    welcome_parse_mode      TEXT DEFAULT 'HTML',

    -- Goodbye toggle & content
    goodbye_enabled         BOOLEAN DEFAULT TRUE,
    goodbye_text            TEXT DEFAULT '',
    goodbye_media_id        TEXT DEFAULT '',
    goodbye_media_type      TEXT DEFAULT '',
    goodbye_buttons         TEXT DEFAULT '[]',

    -- Clean welcome
    clean_welcome           BOOLEAN DEFAULT TRUE,
    last_welcome_msg_id     BIGINT DEFAULT 0,
    clean_goodbye           BOOLEAN DEFAULT FALSE,
    last_goodbye_msg_id     BIGINT DEFAULT 0,
    clean_service           BOOLEAN DEFAULT TRUE,

    -- Welcome mute
    welcome_mute            BOOLEAN DEFAULT FALSE,
    welcome_mute_duration   INTEGER DEFAULT 600,
    welcome_mute_text       TEXT DEFAULT '',

    -- CAPTCHA
    captcha_enabled         BOOLEAN DEFAULT FALSE,
    captcha_type            TEXT DEFAULT 'button',
    captcha_timeout         INTEGER DEFAULT 120,
    captcha_kick_on_fail    BOOLEAN DEFAULT TRUE,
    captcha_text            TEXT DEFAULT '',
    captcha_max_attempts    INTEGER DEFAULT 3,

    -- Anti-raid
    antiraid_enabled        BOOLEAN DEFAULT FALSE,
    antiraid_limit          INTEGER DEFAULT 10,
    antiraid_time           INTEGER DEFAULT 60,
    antiraid_action         TEXT DEFAULT 'mute',
    antiraid_active         BOOLEAN DEFAULT FALSE,
    antiraid_activated_at   TIMESTAMP,

    -- Welcome channel redirect
    welcome_channel         BIGINT DEFAULT 0,
    rules_channel           BIGINT DEFAULT 0,

    -- Security
    welcome_security        BOOLEAN DEFAULT FALSE,
    security_timeout        INTEGER DEFAULT 120,
    security_mute_on_fail   BOOLEAN DEFAULT TRUE,

    -- Stats
    total_welcomed          BIGINT DEFAULT 0,
    total_goodbyed          BIGINT DEFAULT 0,
    total_captcha_passed    BIGINT DEFAULT 0,
    total_captcha_failed    BIGINT DEFAULT 0,
    total_raids_blocked     BIGINT DEFAULT 0,

    -- Metadata
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

-- ══════════════════════════════════════════
-- Pending CAPTCHA verifications
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS captcha_queue (
    id                  SERIAL PRIMARY KEY,
    chat_id             BIGINT NOT NULL,
    user_id             BIGINT NOT NULL,
    captcha_type        TEXT NOT NULL DEFAULT 'button',
    answer              TEXT NOT NULL DEFAULT '',
    attempts            INTEGER DEFAULT 0,
    max_attempts        INTEGER DEFAULT 3,
    message_id          BIGINT DEFAULT 0,
    created_at          TIMESTAMP DEFAULT NOW(),
    expires_at          TIMESTAMP NOT NULL,
    is_resolved         BOOLEAN DEFAULT FALSE,
    resolved_at         TIMESTAMP,
    result              TEXT DEFAULT '',
    UNIQUE(chat_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_captcha_queue_pending
    ON captcha_queue(chat_id, user_id)
    WHERE is_resolved = FALSE;

CREATE INDEX IF NOT EXISTS idx_captcha_queue_expires
    ON captcha_queue(expires_at)
    WHERE is_resolved = FALSE;

-- ══════════════════════════════════════════
-- Anti-raid log
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS raid_log (
    id                  SERIAL PRIMARY KEY,
    chat_id             BIGINT NOT NULL,
    joins_in_window     INTEGER DEFAULT 0,
    window_seconds      INTEGER DEFAULT 60,
    action_taken        TEXT DEFAULT '',
    activated_at        TIMESTAMP DEFAULT NOW(),
    deactivated_at      TIMESTAMP,
    users_affected      INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_raid_log_chat
    ON raid_log(chat_id);

-- ══════════════════════════════════════════
-- Welcome join log (for anti-raid detection)
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS join_log (
    id                  SERIAL PRIMARY KEY,
    chat_id             BIGINT NOT NULL,
    user_id             BIGINT NOT NULL,
    joined_at           TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_join_log_chat_time
    ON join_log(chat_id, joined_at);

"""


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WELCOME FORMAT VARIABLES ◈◈◈
# ═══════════════════════════════════════════════════════════════

WELCOME_VARIABLES_HELP = """
✦ {StyleFont.mixed_bold_smallcaps('Welcome Variables')} ✦
{Symbols.divider(6)}

{Symbols.GEAR} {StyleFont.bold_sans('Available Variables')}:
{Symbols.divider(9)}

{Symbols.ARROW_TRI} <code>{{first}}</code> — {StyleFont.small_caps('users first name')}
{Symbols.ARROW_TRI} <code>{{last}}</code> — {StyleFont.small_caps('users last name')}
{Symbols.ARROW_TRI} <code>{{fullname}}</code> — {StyleFont.small_caps('full name')}
{Symbols.ARROW_TRI} <code>{{username}}</code> — {StyleFont.small_caps('username with @')}
{Symbols.ARROW_TRI} <code>{{mention}}</code> — {StyleFont.small_caps('clickable mention')}
{Symbols.ARROW_TRI} <code>{{id}}</code> — {StyleFont.small_caps('user id')}
{Symbols.ARROW_TRI} <code>{{chatname}}</code> — {StyleFont.small_caps('group name')}
{Symbols.ARROW_TRI} <code>{{chatid}}</code> — {StyleFont.small_caps('group id')}
{Symbols.ARROW_TRI} <code>{{count}}</code> — {StyleFont.small_caps('member count')}
{Symbols.ARROW_TRI} <code>{{date}}</code> — {StyleFont.small_caps('current date')}
{Symbols.ARROW_TRI} <code>{{time}}</code> — {StyleFont.small_caps('current time')}
{Symbols.ARROW_TRI} <code>{{rules}}</code> — {StyleFont.small_caps('group rules link')}
{Symbols.ARROW_TRI} <code>{{preview}}</code> — {StyleFont.small_caps('chat preview link')}

{Symbols.GEAR} {StyleFont.bold_sans('Button Format')}:
{Symbols.divider(9)}
{Symbols.ARROW_TRI} <code>[Button Text](buttonurl://link.com)</code>
{Symbols.ARROW_TRI} <code>[Row 2 Btn](buttonurl://link.com:same)</code>
  {Symbols.TINY_DOT} {StyleFont.small_caps('add :same to put buttons on same row')}

{Symbols.GEAR} {StyleFont.bold_sans('Example')}:
{Symbols.divider(9)}
<code>/setwelcome Hey {{mention}}! Welcome to {{chatname}}!
We now have {{count}} members!
[Rules](buttonurl://t.me/rules)
[Channel](buttonurl://t.me/updates:same)</code>

{Symbols.divider(6)}
{StyleFont.mixed_bold_smallcaps('Powered By')}: {Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}
"""


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ CAPTCHA CONSTANTS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class CaptchaType:
    """CAPTCHA types available"""
    BUTTON = "button"       # Simple button click
    MATH = "math"           # Math question (2+3=?)
    TEXT = "text"           # Type a word
    EMOJI = "emoji"         # Select correct emoji
    CUSTOM = "custom"       # Custom question

    ALL = [BUTTON, MATH, TEXT, EMOJI, CUSTOM]

    @staticmethod
    def generate_math() -> Tuple[str, str]:
        """Generate a math captcha question & answer"""
        ops = [
            ("+", lambda a, b: a + b),
            ("-", lambda a, b: a - b),
            ("×", lambda a, b: a * b),
        ]
        a = random.randint(1, 20)
        b = random.randint(1, 15)
        op_symbol, op_func = random.choice(ops)

        # Ensure no negative results
        if op_symbol == "-" and a < b:
            a, b = b, a

        answer = op_func(a, b)
        question = f"{a} {op_symbol} {b} = ?"
        return question, str(answer)

    @staticmethod
    def generate_text() -> Tuple[str, str]:
        """Generate a random text captcha"""
        words = [
            "apple", "brave", "cloud", "dream", "eagle",
            "flame", "grace", "heart", "ivory", "jewel",
            "kite", "light", "magic", "noble", "ocean",
            "peace", "queen", "river", "solar", "tiger",
            "ultra", "vivid", "water", "xenon", "youth",
            "zebra", "storm", "blaze", "frost", "spark",
        ]
        word = random.choice(words)
        return word, word

    @staticmethod
    def generate_emoji() -> Tuple[str, str, List[str]]:
        """
        Generate emoji captcha.
        Returns (target_emoji, correct_answer, all_options)
        """
        emojis = [
            "🍎", "🍊", "🍋", "🍇", "🍓",
            "🌸", "🌻", "🌹", "🌺", "🌷",
            "🐱", "🐶", "🐼", "🦁", "🐨",
            "⭐", "🌙", "☀️", "🌈", "❄️",
            "🎸", "🎹", "🎺", "🥁", "🎻",
            "🚗", "✈️", "🚀", "🛸", "⛵",
        ]
        target = random.choice(emojis)
        wrong = random.sample(
            [e for e in emojis if e != target], 4
        )
        options = wrong + [target]
        random.shuffle(options)
        return target, target, options

    @staticmethod
    def generate_button() -> Tuple[str, str]:
        """Simple button captcha"""
        return "button", "verified"


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WELCOME DATABASE OPERATIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class WelcomeDB:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   𝐖ᴇʟᴄᴏᴍᴇ / 𝐆ᴏᴏᴅʙʏᴇ 𝐃ᴀᴛᴀʙᴀsᴇ 𝐎ᴘᴇʀᴀᴛɪᴏɴs          ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              ║
    ║   Complete DB operations for welcome system           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    async def create_tables() -> None:
        """Create Section 3 tables"""
        try:
            for stmt in SECTION3_TABLES_SQL.split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    try:
                        await db.execute(stmt)
                    except Exception as se:
                        logger.debug(f"Section 3 stmt skip: {se}")
            logger.info("✅ Section 3 tables created!")
        except Exception as e:
            logger.error(f"❌ Section 3 tables error: {e}")

    # ───────────────────────────────────────────────────────
    # WELCOME SETTINGS CRUD
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def get_welcome_settings(
        chat_id: int
    ) -> Dict[str, Any]:
        """Get all welcome settings for a chat"""
        try:
            row = await db.fetchrow(
                "SELECT * FROM welcome_settings WHERE chat_id = $1;",
                chat_id
            )
            if row:
                return dict(row)

            # Create default settings
            await db.execute("""
                INSERT INTO welcome_settings (chat_id)
                VALUES ($1)
                ON CONFLICT (chat_id) DO NOTHING;
            """, chat_id)

            row = await db.fetchrow(
                "SELECT * FROM welcome_settings WHERE chat_id = $1;",
                chat_id
            )
            return dict(row) if row else {}

        except Exception as e:
            logger.error(f"Get welcome settings error: {e}")
            return {}

    @staticmethod
    async def update_welcome_setting(
        chat_id: int,
        setting: str,
        value: Any
    ) -> bool:
        """Update a single welcome setting"""
        valid = [
            'welcome_enabled', 'welcome_text', 'welcome_media_id',
            'welcome_media_type', 'welcome_buttons', 'welcome_parse_mode',
            'goodbye_enabled', 'goodbye_text', 'goodbye_media_id',
            'goodbye_media_type', 'goodbye_buttons',
            'clean_welcome', 'last_welcome_msg_id',
            'clean_goodbye', 'last_goodbye_msg_id', 'clean_service',
            'welcome_mute', 'welcome_mute_duration', 'welcome_mute_text',
            'captcha_enabled', 'captcha_type', 'captcha_timeout',
            'captcha_kick_on_fail', 'captcha_text', 'captcha_max_attempts',
            'antiraid_enabled', 'antiraid_limit', 'antiraid_time',
            'antiraid_action', 'antiraid_active', 'antiraid_activated_at',
            'welcome_channel', 'rules_channel',
            'welcome_security', 'security_timeout',
            'security_mute_on_fail',
            'total_welcomed', 'total_goodbyed',
            'total_captcha_passed', 'total_captcha_failed',
            'total_raids_blocked',
        ]
        if setting not in valid:
            return False

        try:
            await db.execute(f"""
                INSERT INTO welcome_settings (chat_id, {setting}, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO UPDATE SET
                    {setting} = EXCLUDED.{setting},
                    updated_at = NOW();
            """, chat_id, value)
            return True
        except Exception as e:
            logger.error(f"Update welcome setting error: {e}")
            return False

    @staticmethod
    async def set_welcome(
        chat_id: int,
        text: str,
        media_id: str = "",
        media_type: str = "",
        buttons: str = "[]",
    ) -> bool:
        """Set custom welcome message"""
        try:
            await db.execute("""
                INSERT INTO welcome_settings (
                    chat_id, welcome_text, welcome_media_id,
                    welcome_media_type, welcome_buttons,
                    welcome_enabled, updated_at
                ) VALUES ($1, $2, $3, $4, $5, TRUE, NOW())
                ON CONFLICT (chat_id) DO UPDATE SET
                    welcome_text = EXCLUDED.welcome_text,
                    welcome_media_id = EXCLUDED.welcome_media_id,
                    welcome_media_type = EXCLUDED.welcome_media_type,
                    welcome_buttons = EXCLUDED.welcome_buttons,
                    welcome_enabled = TRUE,
                    updated_at = NOW();
            """, chat_id, text, media_id, media_type, buttons)
            return True
        except Exception as e:
            logger.error(f"Set welcome error: {e}")
            return False

    @staticmethod
    async def reset_welcome(chat_id: int) -> bool:
        """Reset welcome to default"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    welcome_text = '',
                    welcome_media_id = '',
                    welcome_media_type = '',
                    welcome_buttons = '[]',
                    updated_at = NOW()
                WHERE chat_id = $1;
            """, chat_id)
            return True
        except Exception as e:
            logger.error(f"Reset welcome error: {e}")
            return False

    @staticmethod
    async def set_goodbye(
        chat_id: int,
        text: str,
        media_id: str = "",
        media_type: str = "",
        buttons: str = "[]",
    ) -> bool:
        """Set custom goodbye message"""
        try:
            await db.execute("""
                INSERT INTO welcome_settings (
                    chat_id, goodbye_text, goodbye_media_id,
                    goodbye_media_type, goodbye_buttons,
                    goodbye_enabled, updated_at
                ) VALUES ($1, $2, $3, $4, $5, TRUE, NOW())
                ON CONFLICT (chat_id) DO UPDATE SET
                    goodbye_text = EXCLUDED.goodbye_text,
                    goodbye_media_id = EXCLUDED.goodbye_media_id,
                    goodbye_media_type = EXCLUDED.goodbye_media_type,
                    goodbye_buttons = EXCLUDED.goodbye_buttons,
                    goodbye_enabled = TRUE,
                    updated_at = NOW();
            """, chat_id, text, media_id, media_type, buttons)
            return True
        except Exception as e:
            logger.error(f"Set goodbye error: {e}")
            return False

    @staticmethod
    async def reset_goodbye(chat_id: int) -> bool:
        """Reset goodbye to default"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    goodbye_text = '',
                    goodbye_media_id = '',
                    goodbye_media_type = '',
                    goodbye_buttons = '[]',
                    updated_at = NOW()
                WHERE chat_id = $1;
            """, chat_id)
            return True
        except Exception as e:
            logger.error(f"Reset goodbye error: {e}")
            return False

    @staticmethod
    async def increment_welcome_count(chat_id: int) -> None:
        """Increment welcome count"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    total_welcomed = total_welcomed + 1
                WHERE chat_id = $1;
            """, chat_id)
        except Exception:
            pass

    @staticmethod
    async def increment_goodbye_count(chat_id: int) -> None:
        """Increment goodbye count"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    total_goodbyed = total_goodbyed + 1
                WHERE chat_id = $1;
            """, chat_id)
        except Exception:
            pass

    # ───────────────────────────────────────────────────────
    # CAPTCHA OPERATIONS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def add_captcha(
        chat_id: int,
        user_id: int,
        captcha_type: str,
        answer: str,
        message_id: int,
        timeout: int,
        max_attempts: int = 3,
    ) -> bool:
        """Add user to captcha queue"""
        try:
            expires = datetime.now(timezone.utc) + timedelta(
                seconds=timeout
            )
            await db.execute("""
                INSERT INTO captcha_queue (
                    chat_id, user_id, captcha_type,
                    answer, message_id, expires_at,
                    max_attempts
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (chat_id, user_id) DO UPDATE SET
                    captcha_type = EXCLUDED.captcha_type,
                    answer = EXCLUDED.answer,
                    attempts = 0,
                    message_id = EXCLUDED.message_id,
                    expires_at = EXCLUDED.expires_at,
                    max_attempts = EXCLUDED.max_attempts,
                    is_resolved = FALSE,
                    result = '',
                    created_at = NOW();
            """, chat_id, user_id, captcha_type,
                answer, message_id, expires, max_attempts)
            return True
        except Exception as e:
            logger.error(f"Add captcha error: {e}")
            return False

    @staticmethod
    async def get_captcha(
        chat_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get pending captcha for user"""
        try:
            row = await db.fetchrow("""
                SELECT * FROM captcha_queue
                WHERE chat_id = $1 AND user_id = $2
                    AND is_resolved = FALSE;
            """, chat_id, user_id)
            return dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    async def resolve_captcha(
        chat_id: int,
        user_id: int,
        result: str
    ) -> bool:
        """Mark captcha as resolved"""
        try:
            await db.execute("""
                UPDATE captcha_queue SET
                    is_resolved = TRUE,
                    resolved_at = NOW(),
                    result = $3
                WHERE chat_id = $1 AND user_id = $2;
            """, chat_id, user_id, result)

            # Update stats
            if result == "passed":
                await db.execute("""
                    UPDATE welcome_settings SET
                        total_captcha_passed = total_captcha_passed + 1
                    WHERE chat_id = $1;
                """, chat_id)
            else:
                await db.execute("""
                    UPDATE welcome_settings SET
                        total_captcha_failed = total_captcha_failed + 1
                    WHERE chat_id = $1;
                """, chat_id)

            return True
        except Exception as e:
            logger.error(f"Resolve captcha error: {e}")
            return False

    @staticmethod
    async def increment_captcha_attempts(
        chat_id: int,
        user_id: int
    ) -> int:
        """Increment captcha attempts. Returns new count."""
        try:
            new_count = await db.fetchval("""
                UPDATE captcha_queue SET
                    attempts = attempts + 1
                WHERE chat_id = $1 AND user_id = $2
                    AND is_resolved = FALSE
                RETURNING attempts;
            """, chat_id, user_id)
            return new_count or 0
        except Exception:
            return 0

    @staticmethod
    async def get_expired_captchas() -> list:
        """Get all expired unresolved captchas"""
        try:
            rows = await db.fetch("""
                SELECT * FROM captcha_queue
                WHERE is_resolved = FALSE
                    AND expires_at < NOW();
            """)
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    async def cleanup_old_captchas() -> int:
        """Remove old resolved captchas"""
        try:
            result = await db.execute("""
                DELETE FROM captcha_queue
                WHERE is_resolved = TRUE
                    AND resolved_at < NOW() - INTERVAL '24 hours';
            """)
            count = int(result.split()[-1]) if result else 0
            return count
        except Exception:
            return 0

    # ───────────────────────────────────────────────────────
    # ANTI-RAID OPERATIONS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def log_join(chat_id: int, user_id: int) -> None:
        """Log a user join event"""
        try:
            await db.execute("""
                INSERT INTO join_log (chat_id, user_id)
                VALUES ($1, $2);
            """, chat_id, user_id)
        except Exception:
            pass

    @staticmethod
    async def get_recent_joins(
        chat_id: int,
        seconds: int = 60
    ) -> int:
        """Get count of recent joins within window"""
        try:
            count = await db.fetchval("""
                SELECT COUNT(*) FROM join_log
                WHERE chat_id = $1
                    AND joined_at > NOW() - INTERVAL '1 second' * $2;
            """, chat_id, seconds)
            return count or 0
        except Exception:
            return 0

    @staticmethod
    async def activate_raid_mode(
        chat_id: int,
        joins: int,
        window: int,
        action: str
    ) -> None:
        """Activate anti-raid mode"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    antiraid_active = TRUE,
                    antiraid_activated_at = NOW(),
                    total_raids_blocked = total_raids_blocked + 1
                WHERE chat_id = $1;
            """, chat_id)

            await db.execute("""
                INSERT INTO raid_log (
                    chat_id, joins_in_window,
                    window_seconds, action_taken
                ) VALUES ($1, $2, $3, $4);
            """, chat_id, joins, window, action)
        except Exception as e:
            logger.error(f"Activate raid mode error: {e}")

    @staticmethod
    async def deactivate_raid_mode(chat_id: int) -> None:
        """Deactivate anti-raid mode"""
        try:
            await db.execute("""
                UPDATE welcome_settings SET
                    antiraid_active = FALSE
                WHERE chat_id = $1;
            """, chat_id)

            await db.execute("""
                UPDATE raid_log SET
                    deactivated_at = NOW()
                WHERE chat_id = $1
                    AND deactivated_at IS NULL;
            """, chat_id)
        except Exception as e:
            logger.error(f"Deactivate raid mode error: {e}")

    @staticmethod
    async def cleanup_join_log() -> None:
        """Clean old join log entries"""
        try:
            await db.execute("""
                DELETE FROM join_log
                WHERE joined_at < NOW() - INTERVAL '1 hour';
            """)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WELCOME TEXT FORMATTER ◈◈◈
# ═══════════════════════════════════════════════════════════════

class WelcomeFormatter:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Format welcome text with variables & buttons       ║
    ║   Parse button markdown from text                    ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    def format_welcome_text(
        text: str,
        user: User,
        chat: Chat,
        member_count: int = 0,
    ) -> str:
        """Replace variables in welcome text"""
        if not text:
            return text

        first = html_escape(user.first_name or "")
        last = html_escape(user.last_name or "")
        fullname = html_escape(get_user_full_name(user))
        username = f"@{user.username}" if user.username else first
        mention = get_user_mention(user)
        chat_name = html_escape(chat.title or "")

        now = datetime.now()

        replacements = {
            "{first}": first,
            "{last}": last,
            "{fullname}": fullname,
            "{username}": username,
            "{mention}": mention,
            "{id}": str(user.id),
            "{chatname}": chat_name,
            "{chatid}": str(chat.id),
            "{count}": str(member_count),
            "{date}": now.strftime("%d/%m/%Y"),
            "{time}": now.strftime("%H:%M:%S"),
            "{rules}": f"@{chat.username}/rules" if chat.username else "rules",
            "{preview}": f"t.me/{chat.username}" if chat.username else "",
        }

        for var, value in replacements.items():
            text = text.replace(var, value)

        return text

    @staticmethod
    def parse_buttons(text: str) -> Tuple[str, List[List[InlineKeyboardButton]]]:
        """
        Parse button markdown from text.
        Format: [Button Text](buttonurl://link.com)
        Same row: [Button Text](buttonurl://link.com:same)

        Returns: (cleaned_text, button_rows)
        """
        button_pattern = re.compile(
            r'\[([^\]]+)\]\(buttonurl://([^\)]+)\)'
        )

        buttons: List[List[InlineKeyboardButton]] = []
        current_row: List[InlineKeyboardButton] = []

        # Find all buttons
        matches = button_pattern.findall(text)

        for btn_text, btn_url in matches:
            same_row = False
            if btn_url.endswith(":same"):
                btn_url = btn_url[:-5]
                same_row = True

            # Clean URL
            btn_url = btn_url.strip()
            if not btn_url.startswith(("http://", "https://", "tg://")):
                btn_url = "https://" + btn_url

            btn = InlineKeyboardButton(
                text=btn_text.strip(),
                url=btn_url
            )

            if same_row and current_row:
                current_row.append(btn)
            else:
                if current_row:
                    buttons.append(current_row)
                current_row = [btn]

        if current_row:
            buttons.append(current_row)

        # Remove button markdown from text
        cleaned = button_pattern.sub("", text).strip()
        # Clean empty lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned, buttons

    @staticmethod
    def get_default_welcome(
        user: User,
        chat: Chat,
        member_count: int = 0,
    ) -> str:
        """Generate the default stylish welcome message"""
        user_mention = get_user_mention(user)
        full_name = html_escape(get_user_full_name(user))
        chat_name = html_escape(chat.title or "")

        return (
            f"✦ {StyleFont.mixed_bold_smallcaps('Welcome')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Your Info')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User Id')}: "
            f"<code>{user.id}</code>\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Username')}: "
            f"{'@' + user.username if user.username else StyleFont.small_caps('none')}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Group')}: "
            f"{chat_name}\n"
            f"{Symbols.BOX_V} {Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Members')}: "
            f"<b>{member_count}</b>\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.WARNING} {StyleFont.bold_sans('RULES')}:-\n"
            f"{Symbols.NUM_1} 🚫 "
            f"{StyleFont.mixed_bold_smallcaps('No links')}\n"
            f"{Symbols.NUM_2} {Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('No abuse')}\n"
            f"{Symbols.NUM_3} {Symbols.WARNING} "
            f"{StyleFont.mixed_bold_smallcaps('No promo')}\n"
            f"{Symbols.NUM_4} 🔞 "
            f"{StyleFont.mixed_bold_smallcaps('No nsfw')}\n"
            f"{Symbols.NUM_5} ⛔ "
            f"{StyleFont.mixed_bold_smallcaps('No banned emojis')}\n"
            f"\n"
            f"{Symbols.GEAR} "
            f"{StyleFont.bold_sans('Available Commands')}:\n"
            f"{Symbols.BULLET} /id {Symbols.BULLET} /info "
            f"{Symbols.BULLET} /rules {Symbols.BULLET} /help\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def get_default_goodbye(
        user: User,
        chat: Chat,
    ) -> str:
        """Generate the default stylish goodbye message"""
        user_mention = get_user_mention(user)
        full_name = html_escape(get_user_full_name(user))
        chat_name = html_escape(chat.title or "")

        return (
            f"👋 {StyleFont.mixed_bold_smallcaps('Goodbye')} 👋\n"
            f"{Symbols.divider(8)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"{user_mention}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Left')}: "
            f"{chat_name}\n"
            f"\n"
            f"{Symbols.BUTTERFLY} "
            f"{StyleFont.small_caps('we will miss you')}... 💔\n"
            f"\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ ANTI-RAID MANAGER ◈◈◈
# ═══════════════════════════════════════════════════════════════

class AntiRaidManager:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Anti-raid detection and response system            ║
    ║   Tracks join rate & auto-activates protection       ║
    ╚═══════════════════════════════════════════════════════╝
    """

    def __init__(self):
        self._join_timestamps: Dict[int, List[float]] = defaultdict(list)
        self._raid_active: Set[int] = set()
        self._raid_cooldown: Dict[int, float] = {}

    async def check_raid(
        self,
        chat_id: int,
        settings: Dict[str, Any],
        bot: Bot,
    ) -> bool:
        """
        Check if a raid is happening.
        Returns True if raid detected.
        """
        if not settings.get("antiraid_enabled", False):
            return False

        # Already active?
        if chat_id in self._raid_active:
            return True

        # Cooldown check (don't re-trigger within 5 mins)
        if chat_id in self._raid_cooldown:
            if time.time() - self._raid_cooldown[chat_id] < 300:
                return False

        limit = settings.get("antiraid_limit", 10)
        window = settings.get("antiraid_time", 60)

        now = time.time()

        # Clean old entries
        self._join_timestamps[chat_id] = [
            t for t in self._join_timestamps[chat_id]
            if now - t < window
        ]

        # Add current join
        self._join_timestamps[chat_id].append(now)

        joins = len(self._join_timestamps[chat_id])

        if joins >= limit:
            # RAID DETECTED!
            self._raid_active.add(chat_id)
            self._raid_cooldown[chat_id] = now

            action = settings.get("antiraid_action", "mute")

            # Activate in DB
            await WelcomeDB.activate_raid_mode(
                chat_id, joins, window, action
            )

            # Send alert
            try:
                await bot.send_message(
                    chat_id,
                    (
                        f"🚨 {StyleFont.bold_sans('RAID DETECTED')} 🚨\n"
                        f"{Symbols.divider(6)}\n"
                        f"\n"
                        f"{Symbols.WARNING} "
                        f"{StyleFont.mixed_bold_smallcaps('Anti-Raid Mode Activated')}!\n"
                        f"\n"
                        f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
                        f"{StyleFont.bold_sans('Raid Info')} "
                        f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
                        f"{Symbols.BOX_V} {Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Joins Detected')}: "
                        f"<b>{joins}</b>\n"
                        f"{Symbols.BOX_V} {Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Time Window')}: "
                        f"<b>{window}s</b>\n"
                        f"{Symbols.BOX_V} {Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                        f"<b>{action}</b>\n"
                        f"{Symbols.BOX_V} {Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Status')}: "
                        f"🔴 {StyleFont.small_caps('all new joins will be')} "
                        f"<b>{action}d</b>\n"
                        f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
                        f"\n"
                        f"{Symbols.BULLET} "
                        f"{StyleFont.small_caps('use /antiraid off to deactivate')}\n"
                        f"\n"
                        f"{Symbols.divider(6)}\n"
                        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.error(f"Raid alert error: {e}")

            # Auto-deactivate after 5 minutes
            asyncio.create_task(
                self._auto_deactivate_raid(chat_id, bot, 300)
            )

            return True

        return False

    async def _auto_deactivate_raid(
        self, chat_id: int, bot: Bot, delay: int
    ) -> None:
        """Auto-deactivate raid mode after delay"""
        await asyncio.sleep(delay)
        await self.deactivate_raid(chat_id, bot)

    async def deactivate_raid(
        self, chat_id: int, bot: Bot
    ) -> None:
        """Deactivate raid mode"""
        self._raid_active.discard(chat_id)
        self._join_timestamps[chat_id] = []
        await WelcomeDB.deactivate_raid_mode(chat_id)

        try:
            await bot.send_message(
                chat_id,
                (
                    f"✅ {StyleFont.mixed_bold_smallcaps('Anti-Raid Mode Deactivated')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{Symbols.BULLET} "
                    f"{StyleFont.small_caps('normal welcome behavior resumed')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass

    def is_raid_active(self, chat_id: int) -> bool:
        return chat_id in self._raid_active

    def record_join(self, chat_id: int) -> None:
        self._join_timestamps[chat_id].append(time.time())


# Global anti-raid manager
antiraid = AntiRaidManager()


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ CAPTCHA MANAGER ◈◈◈
# ═══════════════════════════════════════════════════════════════

class CaptchaManager:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   CAPTCHA verification management                    ║
    ║   button / math / text / emoji types                 ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    async def send_captcha(
        bot: Bot,
        chat: Chat,
        user: User,
        settings: Dict[str, Any],
    ) -> Optional[int]:
        """
        Send CAPTCHA challenge to new user.
        Returns message_id of the captcha message.
        """
        captcha_type = settings.get("captcha_type", "button")
        timeout = settings.get("captcha_timeout", 120)
        max_attempts = settings.get("captcha_max_attempts", 3)
        custom_text = settings.get("captcha_text", "")

        user_mention = get_user_mention(user)
        timeout_str = get_readable_time(timeout)

        msg_id = None

        try:
            if captcha_type == CaptchaType.BUTTON:
                # ── Simple Button CAPTCHA ──
                answer = "verified"

                text = (
                    f"🔐 {StyleFont.mixed_bold_smallcaps('Captcha Verification')} 🔐\n"
                    f"{Symbols.divider(6)}\n"
                    f"\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
                    f"\n"
                    f"{Symbols.WARNING} "
                    f"{StyleFont.small_caps('please click the button below to verify you are human')}\n"
                    f"\n"
                    f"{Symbols.CLOCK} "
                    f"{StyleFont.mixed_bold_smallcaps('Time Limit')}: "
                    f"<b>{timeout_str}</b>\n"
                    f"\n"
                    f"{Symbols.divider(6)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )

                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"✅ {StyleFont.bold_sans('I Am Human')}",
                            callback_data=f"captcha_verify_{chat.id}_{user.id}"
                        ),
                    ],
                ])

                msg = await bot.send_message(
                    chat.id, text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
                msg_id = msg.message_id

            elif captcha_type == CaptchaType.MATH:
                # ── Math CAPTCHA ──
                question, answer = CaptchaType.generate_math()

                # Generate wrong options
                correct = int(answer)
                wrongs = set()
                while len(wrongs) < 3:
                    wrong = correct + random.randint(-10, 10)
                    if wrong != correct and wrong >= 0:
                        wrongs.add(wrong)
                options = list(wrongs) + [correct]
                random.shuffle(options)

                text = (
                    f"🧮 {StyleFont.mixed_bold_smallcaps('Math Captcha')} 🧮\n"
                    f"{Symbols.divider(6)}\n"
                    f"\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
                    f"\n"
                    f"{Symbols.DIAMOND} "
                    f"{StyleFont.bold_sans('Solve')}: "
                    f"<code>{question}</code>\n"
                    f"\n"
                    f"{Symbols.CLOCK} "
                    f"{StyleFont.mixed_bold_smallcaps('Time')}: "
                    f"<b>{timeout_str}</b> │ "
                    f"{StyleFont.mixed_bold_smallcaps('Attempts')}: "
                    f"<b>{max_attempts}</b>\n"
                    f"\n"
                    f"{Symbols.divider(6)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )

                buttons = []
                row = []
                for opt in options:
                    row.append(
                        InlineKeyboardButton(
                            str(opt),
                            callback_data=(
                                f"captcha_math_{chat.id}_{user.id}_{opt}"
                            )
                        )
                    )
                    if len(row) == 2:
                        buttons.append(row)
                        row = []
                if row:
                    buttons.append(row)

                keyboard = InlineKeyboardMarkup(buttons)

                msg = await bot.send_message(
                    chat.id, text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
                msg_id = msg.message_id

            elif captcha_type == CaptchaType.EMOJI:
                # ── Emoji CAPTCHA ──
                target, answer, options = CaptchaType.generate_emoji()

                text = (
                    f"🎯 {StyleFont.mixed_bold_smallcaps('Emoji Captcha')} 🎯\n"
                    f"{Symbols.divider(6)}\n"
                    f"\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
                    f"\n"
                    f"{Symbols.DIAMOND} "
                    f"{StyleFont.bold_sans('Select')}: {target}\n"
                    f"{Symbols.BULLET} "
                    f"{StyleFont.small_caps('click the matching emoji below')}\n"
                    f"\n"
                    f"{Symbols.CLOCK} "
                    f"{StyleFont.mixed_bold_smallcaps('Time')}: "
                    f"<b>{timeout_str}</b>\n"
                    f"\n"
                    f"{Symbols.divider(6)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )

                buttons = []
                row = []
                for emoji in options:
                    row.append(
                        InlineKeyboardButton(
                            emoji,
                            callback_data=(
                                f"captcha_emoji_{chat.id}_{user.id}"
                                f"_{emoji}"
                            )
                        )
                    )
                    if len(row) == 3:
                        buttons.append(row)
                        row = []
                if row:
                    buttons.append(row)

                keyboard = InlineKeyboardMarkup(buttons)

                msg = await bot.send_message(
                    chat.id, text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
                msg_id = msg.message_id

            elif captcha_type == CaptchaType.TEXT:
                # ── Text CAPTCHA ──
                word, answer = CaptchaType.generate_text()

                styled_word = " ".join(list(word.upper()))

                text = (
                    f"🔤 {StyleFont.mixed_bold_smallcaps('Text Captcha')} 🔤\n"
                    f"{Symbols.divider(6)}\n"
                    f"\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: {user_mention}\n"
                    f"\n"
                    f"{Symbols.DIAMOND} "
                    f"{StyleFont.bold_sans('Type this word')}: "
                    f"<code>{styled_word}</code>\n"
                    f"\n"
                    f"{Symbols.BULLET} "
                    f"{StyleFont.small_caps('type the word in chat to verify')}\n"
                    f"\n"
                    f"{Symbols.CLOCK} "
                    f"{StyleFont.mixed_bold_smallcaps('Time')}: "
                    f"<b>{timeout_str}</b> │ "
                    f"{StyleFont.mixed_bold_smallcaps('Attempts')}: "
                    f"<b>{max_attempts}</b>\n"
                    f"\n"
                    f"{Symbols.divider(6)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )

                msg = await bot.send_message(
                    chat.id, text,
                    parse_mode=ParseMode.HTML,
                )
                msg_id = msg.message_id

            else:
                # Fallback to button
                return await CaptchaManager.send_captcha(
                    bot, chat, user,
                    {**settings, "captcha_type": "button"}
                )

            # Store in DB
            if msg_id:
                await WelcomeDB.add_captcha(
                    chat.id, user.id,
                    captcha_type, answer,
                    msg_id, timeout, max_attempts
                )

            return msg_id

        except Exception as e:
            logger.error(f"Send captcha error: {e}")
            return None

    @staticmethod
    async def handle_captcha_pass(
        bot: Bot,
        chat_id: int,
        user_id: int,
        captcha_data: Dict[str, Any],
    ) -> None:
        """Handle successful CAPTCHA verification"""
        try:
            # Resolve captcha
            await WelcomeDB.resolve_captcha(
                chat_id, user_id, "passed"
            )

            # Unmute user if was muted
            try:
                await bot.restrict_chat_member(
                    chat_id, user_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_send_polls=True,
                        can_invite_users=True,
                        can_send_photos=True,
                        can_send_videos=True,
                        can_send_video_notes=True,
                        can_send_voice_notes=True,
                        can_send_documents=True,
                        can_send_audios=True,
                    ),
                )
            except Exception:
                pass

            # Delete captcha message
            msg_id = captcha_data.get("message_id", 0)
            if msg_id:
                try:
                    await bot.delete_message(chat_id, msg_id)
                except Exception:
                    pass

            # Send success
            try:
                name = ""
                try:
                    u = await bot.get_chat(user_id)
                    name = u.first_name or str(user_id)
                except Exception:
                    name = str(user_id)

                sent = await bot.send_message(
                    chat_id,
                    (
                        f"✅ {StyleFont.mixed_bold_smallcaps('Verification Passed')}\n"
                        f"{Symbols.divider(8)}\n"
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('User')}: "
                        f"<a href='tg://user?id={user_id}'>"
                        f"{html_escape(name)}</a>\n"
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Status')}: "
                        f"🟢 {StyleFont.small_caps('verified')}\n"
                        f"{Symbols.divider(8)}\n"
                        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                    ),
                    parse_mode=ParseMode.HTML,
                )
                # Auto-delete success message
                asyncio.create_task(
                    _auto_delete_message(sent, 30)
                )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"CAPTCHA pass error: {e}")

    @staticmethod
    async def handle_captcha_fail(
        bot: Bot,
        chat_id: int,
        user_id: int,
        captcha_data: Dict[str, Any],
        kick: bool = True,
    ) -> None:
        """Handle failed CAPTCHA (timeout or max attempts)"""
        try:
            await WelcomeDB.resolve_captcha(
                chat_id, user_id, "failed"
            )

            # Delete captcha message
            msg_id = captcha_data.get("message_id", 0)
            if msg_id:
                try:
                    await bot.delete_message(chat_id, msg_id)
                except Exception:
                    pass

            if kick:
                try:
                    # Kick (ban + unban)
                    await bot.ban_chat_member(chat_id, user_id)
                    await asyncio.sleep(1)
                    await bot.unban_chat_member(chat_id, user_id)
                except Exception:
                    pass

            try:
                name = ""
                try:
                    u = await bot.get_chat(user_id)
                    name = u.first_name or str(user_id)
                except Exception:
                    name = str(user_id)

                sent = await bot.send_message(
                    chat_id,
                    (
                        f"❌ {StyleFont.mixed_bold_smallcaps('Verification Failed')}\n"
                        f"{Symbols.divider(8)}\n"
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('User')}: "
                        f"<a href='tg://user?id={user_id}'>"
                        f"{html_escape(name)}</a>\n"
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                        f"{'🦶 Kicked' if kick else '🔇 Muted'}\n"
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                        f"{StyleFont.small_caps('captcha timeout/failed')}\n"
                        f"{Symbols.divider(8)}\n"
                        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                    ),
                    parse_mode=ParseMode.HTML,
                )
                asyncio.create_task(
                    _auto_delete_message(sent, 60)
                )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"CAPTCHA fail error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — KEYBOARD BUILDERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class WelcomeKeyboards:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Inline keyboards for welcome system                ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    def welcome_settings_keyboard(
        chat_id: int,
        settings: Dict[str, Any]
    ) -> InlineKeyboardMarkup:
        """Welcome settings panel"""
        w_on = settings.get("welcome_enabled", True)
        g_on = settings.get("goodbye_enabled", True)
        cl_on = settings.get("clean_welcome", True)
        wm_on = settings.get("welcome_mute", False)
        cap_on = settings.get("captcha_enabled", False)
        ar_on = settings.get("antiraid_enabled", False)
        cs_on = settings.get("clean_service", True)

        def tog(val: bool) -> str:
            return "✅" if val else "❌"

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"{tog(w_on)} {StyleFont.bold_sans('Welcome')}",
                    callback_data=f"wtog_welcome_enabled_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"{tog(g_on)} {StyleFont.bold_sans('Goodbye')}",
                    callback_data=f"wtog_goodbye_enabled_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{tog(cl_on)} {StyleFont.bold_sans('Clean Welc')}",
                    callback_data=f"wtog_clean_welcome_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"{tog(cs_on)} {StyleFont.bold_sans('Clean Svc')}",
                    callback_data=f"wtog_clean_service_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{tog(wm_on)} {StyleFont.bold_sans('Welc Mute')}",
                    callback_data=f"wtog_welcome_mute_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"{tog(cap_on)} {StyleFont.bold_sans('CAPTCHA')}",
                    callback_data=f"wtog_captcha_enabled_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{tog(ar_on)} {StyleFont.bold_sans('Anti-Raid')}",
                    callback_data=f"wtog_antiraid_enabled_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"⚙️ {StyleFont.bold_sans('CAPTCHA Cfg')}",
                    callback_data=f"wcaptcha_cfg_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📊 {StyleFont.bold_sans('Stats')}",
                    callback_data=f"wstats_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"❓ {StyleFont.bold_sans('Format Help')}",
                    callback_data=f"wformat_help_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def captcha_config_keyboard(
        chat_id: int,
        settings: Dict[str, Any]
    ) -> InlineKeyboardMarkup:
        """CAPTCHA config panel"""
        current = settings.get("captcha_type", "button")

        def sel(t: str) -> str:
            return "🔘" if current == t else "⚪"

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"{sel('button')} {StyleFont.bold_sans('Button')}",
                    callback_data=f"wcaptcha_type_{chat_id}_button"
                ),
                InlineKeyboardButton(
                    f"{sel('math')} {StyleFont.bold_sans('Math')}",
                    callback_data=f"wcaptcha_type_{chat_id}_math"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"{sel('emoji')} {StyleFont.bold_sans('Emoji')}",
                    callback_data=f"wcaptcha_type_{chat_id}_emoji"
                ),
                InlineKeyboardButton(
                    f"{sel('text')} {StyleFont.bold_sans('Text')}",
                    callback_data=f"wcaptcha_type_{chat_id}_text"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"⏱️ {StyleFont.bold_sans('Timeout')}: "
                    f"{settings.get('captcha_timeout', 120)}s",
                    callback_data=f"wcaptcha_timeout_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"◀️ {StyleFont.bold_sans('Back')}",
                    callback_data=f"wsettings_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])

    @staticmethod
    def welcome_preview_keyboard(
        chat_id: int
    ) -> InlineKeyboardMarkup:
        """Preview welcome/goodbye keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"👋 {StyleFont.bold_sans('Preview Welcome')}",
                    callback_data=f"wpreview_welcome_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"👋 {StyleFont.bold_sans('Preview Goodbye')}",
                    callback_data=f"wpreview_goodbye_{chat_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"◀️ {StyleFont.bold_sans('Back')}",
                    callback_data=f"wsettings_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"🔄 {StyleFont.bold_sans('Close')}",
                    callback_data="close"
                ),
            ],
        ])


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WELCOME SETTINGS TEMPLATE ◈◈◈
# ═══════════════════════════════════════════════════════════════

class WelcomeTemplates:

    @staticmethod
    def settings_message(
        chat: Chat,
        settings: Dict[str, Any],
    ) -> str:
        """Welcome settings panel message"""
        def s(val: bool) -> str:
            return "✅ ᴏɴ" if val else "❌ ᴏғғ"

        cap_type = settings.get("captcha_type", "button")
        cap_timeout = settings.get("captcha_timeout", 120)
        mute_dur = settings.get("welcome_mute_duration", 600)
        ar_limit = settings.get("antiraid_limit", 10)
        ar_time = settings.get("antiraid_time", 60)
        ar_active = settings.get("antiraid_active", False)

        return (
            f"⚙️ {StyleFont.mixed_bold_smallcaps('Welcome Settings')} ⚙️\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
            f"{html_escape(chat.title or '')}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Welcome/Goodbye')} "
            f"]{Symbols.BOX_H * 3}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👋 "
            f"{StyleFont.mixed_bold_smallcaps('Welcome')}: "
            f"{s(settings.get('welcome_enabled', True))}\n"
            f"{Symbols.BOX_V} 👋 "
            f"{StyleFont.mixed_bold_smallcaps('Goodbye')}: "
            f"{s(settings.get('goodbye_enabled', True))}\n"
            f"{Symbols.BOX_V} 🧹 "
            f"{StyleFont.mixed_bold_smallcaps('Clean Welcome')}: "
            f"{s(settings.get('clean_welcome', True))}\n"
            f"{Symbols.BOX_V} 🧹 "
            f"{StyleFont.mixed_bold_smallcaps('Clean Service')}: "
            f"{s(settings.get('clean_service', True))}\n"
            f"{Symbols.BOX_V} 📝 "
            f"{StyleFont.mixed_bold_smallcaps('Custom Welcome')}: "
            f"{'✅' if settings.get('welcome_text') else '❌ Default'}\n"
            f"{Symbols.BOX_V} 📝 "
            f"{StyleFont.mixed_bold_smallcaps('Custom Goodbye')}: "
            f"{'✅' if settings.get('goodbye_text') else '❌ Default'}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Security')} "
            f"]{Symbols.BOX_H * 6}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 🔇 "
            f"{StyleFont.mixed_bold_smallcaps('Welcome Mute')}: "
            f"{s(settings.get('welcome_mute', False))}"
            f" ({get_readable_time(mute_dur)})\n"
            f"{Symbols.BOX_V} 🔐 "
            f"{StyleFont.mixed_bold_smallcaps('Captcha')}: "
            f"{s(settings.get('captcha_enabled', False))}"
            f" ({cap_type})\n"
            f"{Symbols.BOX_V} ⏱️ "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Timeout')}: "
            f"{get_readable_time(cap_timeout)}\n"
            f"{Symbols.BOX_V} 🚨 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Raid')}: "
            f"{s(settings.get('antiraid_enabled', False))}"
            f" ({ar_limit}/{ar_time}s)\n"
            f"{Symbols.BOX_V} 🔴 "
            f"{StyleFont.mixed_bold_smallcaps('Raid Active')}: "
            f"{'🔴 YES' if ar_active else '🟢 NO'}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Stats')} "
            f"]{Symbols.BOX_H * 7}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👋 "
            f"{StyleFont.mixed_bold_smallcaps('Welcomed')}: "
            f"<b>{format_number(settings.get('total_welcomed', 0))}</b>\n"
            f"{Symbols.BOX_V} 👋 "
            f"{StyleFont.mixed_bold_smallcaps('Goodbyed')}: "
            f"<b>{format_number(settings.get('total_goodbyed', 0))}</b>\n"
            f"{Symbols.BOX_V} ✅ "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Passed')}: "
            f"<b>{settings.get('total_captcha_passed', 0)}</b>\n"
            f"{Symbols.BOX_V} ❌ "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Failed')}: "
            f"<b>{settings.get('total_captcha_failed', 0)}</b>\n"
            f"{Symbols.BOX_V} 🚨 "
            f"{StyleFont.mixed_bold_smallcaps('Raids Blocked')}: "
            f"<b>{settings.get('total_raids_blocked', 0)}</b>\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ CAPTCHA TIMEOUT CHECKER (Background Task) ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def captcha_timeout_checker(app: Application) -> None:
    """Background task to check expired CAPTCHAs"""
    while True:
        try:
            expired = await WelcomeDB.get_expired_captchas()

            for cap in expired:
                chat_id = cap["chat_id"]
                user_id = cap["user_id"]

                settings = await WelcomeDB.get_welcome_settings(chat_id)
                kick = settings.get("captcha_kick_on_fail", True)

                await CaptchaManager.handle_captcha_fail(
                    app.bot, chat_id, user_id, cap, kick
                )

            # Cleanup old entries
            await WelcomeDB.cleanup_old_captchas()
            await WelcomeDB.cleanup_join_log()

        except Exception as e:
            logger.debug(f"Captcha checker error: {e}")

        await asyncio.sleep(15)


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — MAIN EVENT HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
#  MEMBER JOIN HANDLER (Welcome + CAPTCHA + AntiRaid)
# ───────────────────────────────────────────────────────────────

async def handle_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle new chat members:
    1. Anti-raid check
    2. Gban check
    3. Clean service message
    4. Welcome mute (if enabled)
    5. CAPTCHA (if enabled)
    6. Send welcome message
    7. Track in DB
    """
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat or not message.new_chat_members:
        return

    # Get welcome settings
    settings = await WelcomeDB.get_welcome_settings(chat.id)

    for new_user in message.new_chat_members:
        if new_user.is_bot:
            if new_user.id == context.bot.id:
                # Bot was added to group
                await _handle_bot_added(chat, context)
            continue

        try:
            # ── Register user ──
            if hasattr(UserDB, 'register_user'):
                await UserDB.register_user(new_user)

            # ── Log join for anti-raid ──
            await WelcomeDB.log_join(chat.id, new_user.id)
            antiraid.record_join(chat.id)

            # ── 1. Anti-Raid Check ──
            is_raid = await antiraid.check_raid(
                chat.id, settings, context.bot
            )
            if is_raid:
                action = settings.get("antiraid_action", "mute")
                try:
                    if action == "ban":
                        await context.bot.ban_chat_member(
                            chat.id, new_user.id
                        )
                    elif action == "kick":
                        await context.bot.ban_chat_member(
                            chat.id, new_user.id
                        )
                        await context.bot.unban_chat_member(
                            chat.id, new_user.id
                        )
                    else:
                        await context.bot.restrict_chat_member(
                            chat.id, new_user.id,
                            permissions=ChatPermissions(
                                can_send_messages=False
                            ),
                        )
                except Exception:
                    pass
                continue  # Skip welcome during raid

            # ── 2. Gban Check ──
            if cache.is_gbanned(new_user.id):
                try:
                    await context.bot.ban_chat_member(
                        chat.id, new_user.id
                    )
                    sent = await context.bot.send_message(
                        chat.id,
                        (
                            f"🔨 {StyleFont.mixed_bold_smallcaps('Gbanned User Detected')}\n"
                            f"{Symbols.divider(8)}\n"
                            f"{Symbols.STAR2} "
                            f"{StyleFont.mixed_bold_smallcaps('User')}: "
                            f"{get_user_mention(new_user)}\n"
                            f"{Symbols.STAR2} "
                            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                            f"🔨 {StyleFont.small_caps('banned')}\n"
                            f"{Symbols.divider(8)}\n"
                            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                    asyncio.create_task(
                        _auto_delete_message(sent, 30)
                    )
                except Exception:
                    pass
                continue

            # ── 3. Clean service message ──
            if settings.get("clean_service", True):
                try:
                    await message.delete()
                except Exception:
                    pass

            # ── 4. Welcome mute ──
            if settings.get("welcome_mute", False):
                mute_dur = settings.get("welcome_mute_duration", 600)
                try:
                    until = datetime.now(timezone.utc) + timedelta(
                        seconds=mute_dur
                    )
                    await context.bot.restrict_chat_member(
                        chat.id, new_user.id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                        until_date=until,
                    )
                except Exception:
                    pass

            # ── 5. CAPTCHA ──
            if settings.get("captcha_enabled", False):
                # Mute until verified
                try:
                    await context.bot.restrict_chat_member(
                        chat.id, new_user.id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                    )
                except Exception:
                    pass

                await CaptchaManager.send_captcha(
                    context.bot, chat, new_user, settings
                )
                # Welcome will be sent after CAPTCHA pass
                await WelcomeDB.increment_welcome_count(chat.id)
                continue

            # ── 6. Check if welcome is enabled ──
            if not settings.get("welcome_enabled", True):
                continue

            # ── 7. Clean old welcome ──
            if settings.get("clean_welcome", True):
                old_msg_id = settings.get("last_welcome_msg_id", 0)
                if old_msg_id:
                    try:
                        await context.bot.delete_message(
                            chat.id, old_msg_id
                        )
                    except Exception:
                        pass

            # ── 8. Get member count ──
            member_count = 0
            try:
                member_count = await context.bot.get_chat_member_count(
                    chat.id
                )
            except Exception:
                pass

            # ── 9. Build welcome message ──
            custom_text = settings.get("welcome_text", "")
            media_id = settings.get("welcome_media_id", "")
            media_type = settings.get("welcome_media_type", "")
            buttons_raw = settings.get("welcome_buttons", "[]")

            if custom_text:
                # Custom welcome
                formatted = WelcomeFormatter.format_welcome_text(
                    custom_text, new_user, chat, member_count
                )
                cleaned_text, parsed_buttons = WelcomeFormatter.parse_buttons(
                    formatted
                )

                # Try stored buttons first
                try:
                    stored_buttons = json.loads(buttons_raw)
                    if stored_buttons:
                        btn_rows = []
                        for row in stored_buttons:
                            btn_row = []
                            for b in row:
                                btn_row.append(
                                    InlineKeyboardButton(
                                        text=b["text"],
                                        url=b.get("url", "")
                                    )
                                )
                            btn_rows.append(btn_row)
                        if btn_rows:
                            parsed_buttons = btn_rows
                except Exception:
                    pass

                keyboard = InlineKeyboardMarkup(parsed_buttons) if parsed_buttons else None

            else:
                # Default welcome
                cleaned_text = WelcomeFormatter.get_default_welcome(
                    new_user, chat, member_count
                )
                media_id = ""
                media_type = ""
                keyboard = None

            # ── 10. Welcome channel redirect ──
            welcome_channel = settings.get("welcome_channel", 0)
            if welcome_channel:
                keyboard_rows = []
                if keyboard:
                    keyboard_rows = keyboard.inline_keyboard
                keyboard_rows.append([
                    InlineKeyboardButton(
                        f"📢 {StyleFont.bold_sans('Read Rules')}",
                        url=f"https://t.me/c/{str(welcome_channel)[4:]}"
                        if str(welcome_channel).startswith("-100")
                        else f"https://t.me/{welcome_channel}"
                    ),
                ])
                keyboard = InlineKeyboardMarkup(keyboard_rows)

            # ── 11. Send welcome ──
            sent_msg = None
            try:
                if media_type == "photo" and media_id:
                    sent_msg = await context.bot.send_photo(
                        chat.id,
                        photo=media_id,
                        caption=cleaned_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                elif media_type == "video" and media_id:
                    sent_msg = await context.bot.send_video(
                        chat.id,
                        video=media_id,
                        caption=cleaned_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                elif media_type == "animation" and media_id:
                    sent_msg = await context.bot.send_animation(
                        chat.id,
                        animation=media_id,
                        caption=cleaned_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                elif media_type == "document" and media_id:
                    sent_msg = await context.bot.send_document(
                        chat.id,
                        document=media_id,
                        caption=cleaned_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                elif media_type == "sticker" and media_id:
                    await context.bot.send_sticker(
                        chat.id, sticker=media_id
                    )
                    if cleaned_text:
                        sent_msg = await context.bot.send_message(
                            chat.id, cleaned_text,
                            parse_mode=ParseMode.HTML,
                            reply_markup=keyboard,
                        )
                else:
                    sent_msg = await context.bot.send_message(
                        chat.id,
                        cleaned_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                    )
            except BadRequest as e:
                # Fallback: send without parse mode
                logger.error(f"Welcome send error: {e}")
                try:
                    sent_msg = await context.bot.send_message(
                        chat.id,
                        f"Welcome {get_user_mention(new_user)}! 👋",
                        parse_mode=ParseMode.HTML,
                    )
                except Exception:
                    pass

            # ── 12. Store last welcome msg ID ──
            if sent_msg:
                await WelcomeDB.update_welcome_setting(
                    chat.id,
                    "last_welcome_msg_id",
                    sent_msg.message_id
                )

            # ── 13. Increment counter ──
            await WelcomeDB.increment_welcome_count(chat.id)

            # ── 14. Log ──
            await bot_logger.log(
                bot=context.bot,
                log_type=LogType.WELCOME,
                chat=chat,
                user=new_user,
                extra="New member joined",
            )

        except Exception as e:
            logger.error(f"Welcome handler error: {e}")


async def _handle_bot_added(
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle when the bot itself is added to a group"""
    try:
        # Register chat
        await db.upsert_chat(
            chat.id,
            chat.title or "",
            chat.type,
            chat.username or "",
        )

        # Create default welcome settings
        await WelcomeDB.get_welcome_settings(chat.id)

        # Send introduction
        text = (
            f"✦ {StyleFont.mixed_bold_smallcaps('Thank You For Adding Me')} ✦\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.ROBOT} {StyleFont.bold_sans(BOT_NAME)}\n"
            f"\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('i am a powerful group management bot')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('with')} <b>{TOTAL_COMMANDS}+</b> "
            f"{StyleFont.small_caps('commands')}\n"
            f"\n"
            f"{Symbols.WARNING} "
            f"{StyleFont.bold_sans('Quick Setup')}:\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('make me admin with all permissions')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('use /help to see all commands')}\n"
            f"{Symbols.ARROW_TRI} "
            f"{StyleFont.small_caps('use /welcome to configure welcome')}\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{Symbols.CROWN} "
            f"{StyleFont.mixed_bold_smallcaps('Owner')}: "
            f"—{Symbols.AI} | "
            f"{StyleFont.bold_sans('RUHI X QNR')}{Symbols.SUME}\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        bot_me = await context.bot.get_me()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"❓ {StyleFont.bold_sans('Help')}",
                    url=f"https://t.me/{bot_me.username}?start=help"
                ),
            ],
        ])

        await context.bot.send_message(
            chat.id, text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )

        # Log
        await bot_logger.log(
            bot=context.bot,
            log_type=LogType.START,
            chat=chat,
            extra="Bot added to group",
        )

    except Exception as e:
        logger.error(f"Bot added handler error: {e}")


# ───────────────────────────────────────────────────────────────
#  MEMBER LEFT HANDLER (Goodbye)
# ───────────────────────────────────────────────────────────────

async def handle_member_left(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle when a member leaves the group"""
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat or not message.left_chat_member:
        return

    left_user = message.left_chat_member

    # Skip bots
    if left_user.is_bot:
        if left_user.id == context.bot.id:
            # Bot was removed
            try:
                await db.deactivate_chat(chat.id)
            except Exception:
                pass
        return

    try:
        settings = await WelcomeDB.get_welcome_settings(chat.id)

        # Clean service message
        if settings.get("clean_service", True):
            try:
                await message.delete()
            except Exception:
                pass

        if not settings.get("goodbye_enabled", True):
            return

        # Clean old goodbye
        if settings.get("clean_goodbye", False):
            old_msg = settings.get("last_goodbye_msg_id", 0)
            if old_msg:
                try:
                    await context.bot.delete_message(chat.id, old_msg)
                except Exception:
                    pass

        # Build goodbye
        custom_text = settings.get("goodbye_text", "")
        media_id = settings.get("goodbye_media_id", "")
        media_type = settings.get("goodbye_media_type", "")

        if custom_text:
            member_count = 0
            try:
                member_count = await context.bot.get_chat_member_count(
                    chat.id
                )
            except Exception:
                pass

            formatted = WelcomeFormatter.format_welcome_text(
                custom_text, left_user, chat, member_count
            )
            cleaned_text, parsed_buttons = WelcomeFormatter.parse_buttons(
                formatted
            )
            keyboard = InlineKeyboardMarkup(parsed_buttons) if parsed_buttons else None
        else:
            cleaned_text = WelcomeFormatter.get_default_goodbye(
                left_user, chat
            )
            keyboard = None
            media_id = ""
            media_type = ""

        # Send goodbye
        sent_msg = None
        try:
            if media_type == "photo" and media_id:
                sent_msg = await context.bot.send_photo(
                    chat.id, photo=media_id,
                    caption=cleaned_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
            elif media_type == "animation" and media_id:
                sent_msg = await context.bot.send_animation(
                    chat.id, animation=media_id,
                    caption=cleaned_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
            else:
                sent_msg = await context.bot.send_message(
                    chat.id, cleaned_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )
        except Exception:
            pass

        if sent_msg:
            await WelcomeDB.update_welcome_setting(
                chat.id, "last_goodbye_msg_id", sent_msg.message_id
            )

        await WelcomeDB.increment_goodbye_count(chat.id)

    except Exception as e:
        logger.error(f"Goodbye handler error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — ADMIN COMMAND HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
#  /welcome — TOGGLE / VIEW WELCOME SETTINGS
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_welcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /welcome — View welcome settings panel.
    /welcome on|off — Toggle welcome.
    /welcome — Interactive settings panel.
    """
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)

    if context.args:
        arg = context.args[0].lower()
        if arg in ("on", "yes", "true", "1"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "welcome_enabled", True
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Welcome Enabled')}! 👋",
                parse_mode=ParseMode.HTML,
            )
            return
        elif arg in ("off", "no", "false", "0"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "welcome_enabled", False
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Welcome Disabled')}!",
                parse_mode=ParseMode.HTML,
            )
            return

    # Show settings panel
    text = WelcomeTemplates.settings_message(chat, settings)
    keyboard = WelcomeKeyboards.welcome_settings_keyboard(
        chat.id, settings
    )

    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# ───────────────────────────────────────────────────────────────
#  /setwelcome — SET CUSTOM WELCOME
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_setwelcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /setwelcome <text> — Set custom welcome message.
    Reply to media with /setwelcome to include media.
    Supports variables and button format.
    """
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    text = ""
    media_id = ""
    media_type = ""

    if context.args:
        text = message.text.split(None, 1)[1]

    reply = message.reply_to_message
    if reply:
        if not text:
            text = reply.text or reply.caption or ""

        if reply.photo:
            media_type = "photo"
            media_id = reply.photo[-1].file_id
        elif reply.video:
            media_type = "video"
            media_id = reply.video.file_id
        elif reply.animation:
            media_type = "animation"
            media_id = reply.animation.file_id
        elif reply.document:
            media_type = "document"
            media_id = reply.document.file_id
        elif reply.sticker:
            media_type = "sticker"
            media_id = reply.sticker.file_id

    if not text and not media_id:
        # Show help
        help_text = WELCOME_VARIABLES_HELP.format(
            StyleFont=StyleFont,
            Symbols=Symbols,
            BOT_NAME=BOT_NAME,
        )
        await message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    # Parse buttons from text
    _, parsed_btns = WelcomeFormatter.parse_buttons(text)
    buttons_json = "[]"
    if parsed_btns:
        btn_data = []
        for row in parsed_btns:
            row_data = []
            for btn in row:
                row_data.append({
                    "text": btn.text,
                    "url": btn.url or ""
                })
            btn_data.append(row_data)
        buttons_json = json.dumps(btn_data)

    success = await WelcomeDB.set_welcome(
        chat.id, text, media_id, media_type, buttons_json
    )

    if success:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Welcome Message Set')}!\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Type')}: "
            f"{media_type or 'text'}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Buttons')}: "
            f"{len(parsed_btns)} {StyleFont.small_caps('rows')}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Length')}: "
            f"{len(text)} {StyleFont.small_caps('chars')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('use /welcome to preview settings')}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed to set welcome')}!",
            parse_mode=ParseMode.HTML,
        )


# ───────────────────────────────────────────────────────────────
#  /resetwelcome — RESET TO DEFAULT
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_resetwelcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/resetwelcome — Reset welcome to default."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    await WelcomeDB.reset_welcome(chat.id)

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Welcome Reset To Default')}!",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /goodbye — TOGGLE GOODBYE
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_goodbye(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/goodbye on|off — Toggle goodbye messages."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    if context.args:
        arg = context.args[0].lower()
        if arg in ("on", "yes", "true", "1"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "goodbye_enabled", True
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Goodbye Enabled')}! 👋",
                parse_mode=ParseMode.HTML,
            )
        elif arg in ("off", "no", "false", "0"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "goodbye_enabled", False
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Goodbye Disabled')}!",
                parse_mode=ParseMode.HTML,
            )
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)
    status = "✅ ᴏɴ" if settings.get("goodbye_enabled", True) else "❌ ᴏғғ"

    await message.reply_text(
        f"{Symbols.INFO} "
        f"{StyleFont.mixed_bold_smallcaps('Goodbye Status')}: {status}\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('use /goodbye on or /goodbye off')}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /setgoodbye — SET CUSTOM GOODBYE
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_setgoodbye(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/setgoodbye <text> — Set custom goodbye message."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    text = ""
    media_id = ""
    media_type = ""

    if context.args:
        text = message.text.split(None, 1)[1]

    reply = message.reply_to_message
    if reply:
        if not text:
            text = reply.text or reply.caption or ""
        if reply.photo:
            media_type = "photo"
            media_id = reply.photo[-1].file_id
        elif reply.animation:
            media_type = "animation"
            media_id = reply.animation.file_id

    if not text and not media_id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide goodbye text')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('usage')}: <code>/setgoodbye Your text</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    success = await WelcomeDB.set_goodbye(
        chat.id, text, media_id, media_type
    )

    if success:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Goodbye Message Set')}!",
            parse_mode=ParseMode.HTML,
        )


# ───────────────────────────────────────────────────────────────
#  /resetgoodbye — RESET GOODBYE
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_resetgoodbye(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/resetgoodbye — Reset goodbye to default."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    await WelcomeDB.reset_goodbye(chat.id)
    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Goodbye Reset To Default')}!",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /cleanwelcome — TOGGLE CLEAN WELCOME
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_cleanwelcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/cleanwelcome on|off — Toggle auto-delete old welcome."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if context.args:
        arg = context.args[0].lower()
        new_val = arg in ("on", "yes", "true", "1")
        await WelcomeDB.update_welcome_setting(
            chat.id, "clean_welcome", new_val
        )
        status = "✅ ᴏɴ" if new_val else "❌ ᴏғғ"
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Clean Welcome')}: {status}",
            parse_mode=ParseMode.HTML,
        )
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)
    status = "✅ ᴏɴ" if settings.get("clean_welcome", True) else "❌ ᴏғғ"
    await message.reply_text(
        f"{Symbols.INFO} "
        f"{StyleFont.mixed_bold_smallcaps('Clean Welcome')}: {status}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /welcomemute — TOGGLE WELCOME MUTE
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_welcomemute(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /welcomemute on|off — Toggle muting new users.
    /welcomemute 10m — Set mute duration.
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if context.args:
        arg = context.args[0].lower()
        if arg in ("on", "yes", "true", "1"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "welcome_mute", True
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Welcome Mute Enabled')}! 🔇",
                parse_mode=ParseMode.HTML,
            )
        elif arg in ("off", "no", "false", "0"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "welcome_mute", False
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Welcome Mute Disabled')}!",
                parse_mode=ParseMode.HTML,
            )
        else:
            parsed = parse_time_arg(arg)
            if parsed:
                await WelcomeDB.update_welcome_setting(
                    chat.id, "welcome_mute_duration", parsed
                )
                await WelcomeDB.update_welcome_setting(
                    chat.id, "welcome_mute", True
                )
                await message.reply_text(
                    f"{Symbols.CHECK2} "
                    f"{StyleFont.mixed_bold_smallcaps('Welcome Mute Duration')}: "
                    f"<b>{get_readable_time(parsed)}</b>",
                    parse_mode=ParseMode.HTML,
                )
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)
    status = "✅ ᴏɴ" if settings.get("welcome_mute", False) else "❌ ᴏғғ"
    dur = get_readable_time(settings.get("welcome_mute_duration", 600))
    await message.reply_text(
        f"{Symbols.INFO} "
        f"{StyleFont.mixed_bold_smallcaps('Welcome Mute')}: {status}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Duration')}: {dur}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /captcha — TOGGLE / CONFIGURE CAPTCHA
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_captcha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /captcha on|off — Toggle CAPTCHA.
    /captcha type button|math|emoji|text — Set type.
    /captcha timeout 120 — Set timeout seconds.
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)

    if not context.args:
        # Show CAPTCHA config
        text = (
            f"🔐 {StyleFont.mixed_bold_smallcaps('Captcha Settings')} 🔐\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Status')}: "
            f"{'✅ ᴏɴ' if settings.get('captcha_enabled') else '❌ ᴏғғ'}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Type')}: "
            f"<b>{settings.get('captcha_type', 'button')}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Timeout')}: "
            f"<b>{get_readable_time(settings.get('captcha_timeout', 120))}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Kick On Fail')}: "
            f"{'✅' if settings.get('captcha_kick_on_fail', True) else '❌'}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Max Attempts')}: "
            f"<b>{settings.get('captcha_max_attempts', 3)}</b>\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        keyboard = WelcomeKeyboards.captcha_config_keyboard(
            chat.id, settings
        )
        await message.reply_text(
            text, parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        return

    arg = context.args[0].lower()

    if arg in ("on", "yes", "true", "1"):
        await WelcomeDB.update_welcome_setting(
            chat.id, "captcha_enabled", True
        )
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Enabled')}! 🔐",
            parse_mode=ParseMode.HTML,
        )
    elif arg in ("off", "no", "false", "0"):
        await WelcomeDB.update_welcome_setting(
            chat.id, "captcha_enabled", False
        )
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Disabled')}!",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "type" and len(context.args) > 1:
        cap_type = context.args[1].lower()
        if cap_type in CaptchaType.ALL:
            await WelcomeDB.update_welcome_setting(
                chat.id, "captcha_type", cap_type
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Captcha Type')}: "
                f"<b>{cap_type}</b>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Invalid type')}!\n"
                f"{Symbols.BULLET} "
                f"{StyleFont.small_caps('available')}: "
                f"<code>{'</code>, <code>'.join(CaptchaType.ALL)}</code>",
                parse_mode=ParseMode.HTML,
            )
    elif arg == "timeout" and len(context.args) > 1:
        try:
            timeout = int(context.args[1])
            timeout = max(30, min(timeout, 600))
            await WelcomeDB.update_welcome_setting(
                chat.id, "captcha_timeout", timeout
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Captcha Timeout')}: "
                f"<b>{get_readable_time(timeout)}</b>",
                parse_mode=ParseMode.HTML,
            )
        except ValueError:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Invalid number')}!",
                parse_mode=ParseMode.HTML,
            )


# ───────────────────────────────────────────────────────────────
#  /antiraid — ANTI-RAID CONTROL
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antiraid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /antiraid on|off — Toggle anti-raid.
    /antiraid set <limit> <seconds> — Configure.
    /antiraid action ban|kick|mute — Set raid action.
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)

    if not context.args:
        ar_on = settings.get("antiraid_enabled", False)
        ar_active = settings.get("antiraid_active", False)
        ar_limit = settings.get("antiraid_limit", 10)
        ar_time = settings.get("antiraid_time", 60)
        ar_action = settings.get("antiraid_action", "mute")

        await message.reply_text(
            f"🚨 {StyleFont.mixed_bold_smallcaps('Anti-Raid Settings')} 🚨\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Enabled')}: "
            f"{'✅ ᴏɴ' if ar_on else '❌ ᴏғғ'}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Active Now')}: "
            f"{'🔴 YES' if ar_active else '🟢 NO'}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Trigger')}: "
            f"<b>{ar_limit}</b> {StyleFont.small_caps('joins in')} "
            f"<b>{ar_time}s</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"<b>{ar_action}</b>\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
        return

    arg = context.args[0].lower()

    if arg in ("on", "yes", "true", "1"):
        await WelcomeDB.update_welcome_setting(
            chat.id, "antiraid_enabled", True
        )
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Raid Enabled')}! 🚨",
            parse_mode=ParseMode.HTML,
        )
    elif arg in ("off", "no", "false", "0"):
        await WelcomeDB.update_welcome_setting(
            chat.id, "antiraid_enabled", False
        )
        if antiraid.is_raid_active(chat.id):
            await antiraid.deactivate_raid(chat.id, context.bot)
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Raid Disabled')}!",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "set" and len(context.args) >= 3:
        try:
            limit = int(context.args[1])
            window = int(context.args[2])
            limit = max(3, min(limit, 100))
            window = max(10, min(window, 300))
            await WelcomeDB.update_welcome_setting(
                chat.id, "antiraid_limit", limit
            )
            await WelcomeDB.update_welcome_setting(
                chat.id, "antiraid_time", window
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Anti-Raid Config')}: "
                f"<b>{limit}</b> joins in <b>{window}s</b>",
                parse_mode=ParseMode.HTML,
            )
        except ValueError:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('Usage')}: "
                f"<code>/antiraid set 10 60</code>",
                parse_mode=ParseMode.HTML,
            )
    elif arg == "action" and len(context.args) >= 2:
        action = context.args[1].lower()
        if action in ("ban", "kick", "mute"):
            await WelcomeDB.update_welcome_setting(
                chat.id, "antiraid_action", action
            )
            await message.reply_text(
                f"{Symbols.CHECK2} "
                f"{StyleFont.mixed_bold_smallcaps('Raid Action')}: "
                f"<b>{action}</b>",
                parse_mode=ParseMode.HTML,
            )


# ───────────────────────────────────────────────────────────────
#  /cleanservice — TOGGLE CLEAN SERVICE MESSAGES
# ───────────────────────────────────────────────────────────────

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_cleanservice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/cleanservice on|off — Auto-delete join/leave service msgs."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if context.args:
        arg = context.args[0].lower()
        new_val = arg in ("on", "yes", "true", "1")
        await WelcomeDB.update_welcome_setting(
            chat.id, "clean_service", new_val
        )
        status = "✅ ᴏɴ" if new_val else "❌ ᴏғғ"
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Clean Service')}: {status}",
            parse_mode=ParseMode.HTML,
        )
        return

    settings = await WelcomeDB.get_welcome_settings(chat.id)
    status = "✅ ᴏɴ" if settings.get("clean_service", True) else "❌ ᴏғғ"
    await message.reply_text(
        f"{Symbols.INFO} "
        f"{StyleFont.mixed_bold_smallcaps('Clean Service')}: {status}",
        parse_mode=ParseMode.HTML,
    )


# ───────────────────────────────────────────────────────────────
#  /welcomehelp — WELCOME FORMAT HELP
# ───────────────────────────────────────────────────────────────

@track_command
@cooldown(5.0)
async def cmd_welcomehelp(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/welcomehelp — Show welcome format variables."""
    message = update.effective_message
    if not message:
        return

    help_text = WELCOME_VARIABLES_HELP.format(
        StyleFont=StyleFont,
        Symbols=Symbols,
        BOT_NAME=BOT_NAME,
    )
    await message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — CAPTCHA CALLBACK HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section3_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle Section 3 callback queries"""
    query = update.callback_query
    if not query:
        return

    data = query.data
    user = query.from_user
    message = query.message

    if not data or not user or not message:
        return

    # ── CAPTCHA Verify (Button) ──
    if data.startswith("captcha_verify_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        target_id = int(parts[3])

        if user.id != target_id:
            await query.answer(
                "⚠️ This verification is not for you!",
                show_alert=True
            )
            return

        captcha = await WelcomeDB.get_captcha(chat_id, target_id)
        if not captcha:
            await query.answer("Verification expired!", show_alert=True)
            return

        await query.answer("✅ Verified!")
        await CaptchaManager.handle_captcha_pass(
            context.bot, chat_id, target_id, captcha
        )

    # ── CAPTCHA Math ──
    elif data.startswith("captcha_math_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        target_id = int(parts[3])
        selected = parts[4]

        if user.id != target_id:
            await query.answer(
                "⚠️ This is not for you!", show_alert=True
            )
            return

        captcha = await WelcomeDB.get_captcha(chat_id, target_id)
        if not captcha:
            await query.answer("Expired!", show_alert=True)
            return

        if selected == captcha["answer"]:
            await query.answer("✅ Correct!")
            await CaptchaManager.handle_captcha_pass(
                context.bot, chat_id, target_id, captcha
            )
        else:
            attempts = await WelcomeDB.increment_captcha_attempts(
                chat_id, target_id
            )
            max_att = captcha.get("max_attempts", 3)

            if attempts >= max_att:
                await query.answer("❌ Too many wrong attempts!")
                settings = await WelcomeDB.get_welcome_settings(chat_id)
                kick = settings.get("captcha_kick_on_fail", True)
                await CaptchaManager.handle_captcha_fail(
                    context.bot, chat_id, target_id, captcha, kick
                )
            else:
                await query.answer(
                    f"❌ Wrong! {attempts}/{max_att} attempts",
                    show_alert=True
                )

    # ── CAPTCHA Emoji ──
    elif data.startswith("captcha_emoji_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        target_id = int(parts[3])
        selected = parts[4]

        if user.id != target_id:
            await query.answer("⚠️ Not for you!", show_alert=True)
            return

        captcha = await WelcomeDB.get_captcha(chat_id, target_id)
        if not captcha:
            await query.answer("Expired!", show_alert=True)
            return

        if selected == captcha["answer"]:
            await query.answer("✅ Correct!")
            await CaptchaManager.handle_captcha_pass(
                context.bot, chat_id, target_id, captcha
            )
        else:
            attempts = await WelcomeDB.increment_captcha_attempts(
                chat_id, target_id
            )
            max_att = captcha.get("max_attempts", 3)

            if attempts >= max_att:
                await query.answer("❌ Failed!")
                settings = await WelcomeDB.get_welcome_settings(chat_id)
                kick = settings.get("captcha_kick_on_fail", True)
                await CaptchaManager.handle_captcha_fail(
                    context.bot, chat_id, target_id, captcha, kick
                )
            else:
                await query.answer(
                    f"❌ Wrong! {attempts}/{max_att}",
                    show_alert=True
                )

    # ── Welcome Settings Toggle ──
    elif data.startswith("wtog_"):
        parts = data.replace("wtog_", "", 1).rsplit("_", 1)
        setting = parts[0]
        chat_id = int(parts[1])

        # Admin check
        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer("Admin only!", show_alert=True)
            return

        settings = await WelcomeDB.get_welcome_settings(chat_id)
        current = settings.get(setting, False)
        new_val = not current

        await WelcomeDB.update_welcome_setting(
            chat_id, setting, new_val
        )

        status = "✅ ON" if new_val else "❌ OFF"
        await query.answer(
            f"{setting.replace('_', ' ').title()}: {status}"
        )

        # Refresh panel
        updated = await WelcomeDB.get_welcome_settings(chat_id)
        try:
            chat = await context.bot.get_chat(chat_id)
        except Exception:
            return

        text = WelcomeTemplates.settings_message(chat, updated)
        keyboard = WelcomeKeyboards.welcome_settings_keyboard(
            chat_id, updated
        )
        try:
            await message.edit_text(
                text, parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except BadRequest:
            pass

    # ── Welcome Settings Panel ──
    elif data.startswith("wsettings_"):
        chat_id = int(data.split("_")[1])

        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer("Admin only!", show_alert=True)
            return

        await query.answer()
        settings = await WelcomeDB.get_welcome_settings(chat_id)
        try:
            chat = await context.bot.get_chat(chat_id)
        except Exception:
            return

        text = WelcomeTemplates.settings_message(chat, settings)
        keyboard = WelcomeKeyboards.welcome_settings_keyboard(
            chat_id, settings
        )
        try:
            await message.edit_text(
                text, parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except BadRequest:
            pass

    # ── CAPTCHA Config Panel ──
    elif data.startswith("wcaptcha_cfg_"):
        chat_id = int(data.split("_")[-1])

        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer("Admin only!", show_alert=True)
            return

        await query.answer()
        settings = await WelcomeDB.get_welcome_settings(chat_id)
        keyboard = WelcomeKeyboards.captcha_config_keyboard(
            chat_id, settings
        )

        text = (
            f"🔐 {StyleFont.mixed_bold_smallcaps('Captcha Configuration')} 🔐\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('select captcha type below')}\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('current')}: "
            f"<b>{settings.get('captcha_type', 'button')}</b>\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        try:
            await message.edit_text(
                text, parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except BadRequest:
            pass

    # ── CAPTCHA Type Change ──
    elif data.startswith("wcaptcha_type_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        cap_type = parts[3]

        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer("Admin only!", show_alert=True)
            return

        if cap_type in CaptchaType.ALL:
            await WelcomeDB.update_welcome_setting(
                chat_id, "captcha_type", cap_type
            )
            await query.answer(f"CAPTCHA type: {cap_type}")

            settings = await WelcomeDB.get_welcome_settings(chat_id)
            keyboard = WelcomeKeyboards.captcha_config_keyboard(
                chat_id, settings
            )
            try:
                await message.edit_reply_markup(
                    reply_markup=keyboard
                )
            except BadRequest:
                pass

    # ── CAPTCHA Timeout Cycle ──
    elif data.startswith("wcaptcha_timeout_"):
        chat_id = int(data.split("_")[-1])

        is_admin = await Permissions.is_user_admin(
            chat_id, user.id, context.bot
        )
        if not is_admin:
            await query.answer("Admin only!", show_alert=True)
            return

        settings = await WelcomeDB.get_welcome_settings(chat_id)
        current = settings.get("captcha_timeout", 120)

        # Cycle: 60 → 120 → 180 → 300 → 60
        cycle = [60, 120, 180, 300]
        try:
            idx = cycle.index(current)
            new_val = cycle[(idx + 1) % len(cycle)]
        except ValueError:
            new_val = 120

        await WelcomeDB.update_welcome_setting(
            chat_id, "captcha_timeout", new_val
        )
        await query.answer(
            f"Timeout: {get_readable_time(new_val)}"
        )

        updated = await WelcomeDB.get_welcome_settings(chat_id)
        keyboard = WelcomeKeyboards.captcha_config_keyboard(
            chat_id, updated
        )
        try:
            await message.edit_reply_markup(reply_markup=keyboard)
        except BadRequest:
            pass

    # ── Welcome Stats ──
    elif data.startswith("wstats_"):
        chat_id = int(data.split("_")[1])
        await query.answer()

        settings = await WelcomeDB.get_welcome_settings(chat_id)

        text = (
            f"📊 {StyleFont.mixed_bold_smallcaps('Welcome Stats')} 📊\n"
            f"{Symbols.divider(6)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Welcomed')}: "
            f"<b>{format_number(settings.get('total_welcomed', 0))}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Goodbyed')}: "
            f"<b>{format_number(settings.get('total_goodbyed', 0))}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Passed')}: "
            f"<b>{settings.get('total_captcha_passed', 0)}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Captcha Failed')}: "
            f"<b>{settings.get('total_captcha_failed', 0)}</b>\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Raids Blocked')}: "
            f"<b>{settings.get('total_raids_blocked', 0)}</b>\n"
            f"\n"
            f"{Symbols.divider(6)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

        try:
            await message.edit_text(
                text, parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"◀️ {StyleFont.bold_sans('Back')}",
                            callback_data=f"wsettings_{chat_id}"
                        ),
                        InlineKeyboardButton(
                            f"🔄 {StyleFont.bold_sans('Close')}",
                            callback_data="close"
                        ),
                    ],
                ]),
            )
        except BadRequest:
            pass

    # ── Format Help ──
    elif data.startswith("wformat_help_"):
        await query.answer()
        chat_id = int(data.split("_")[-1])
        help_text = WELCOME_VARIABLES_HELP.format(
            StyleFont=StyleFont,
            Symbols=Symbols,
            BOT_NAME=BOT_NAME,
        )
        try:
            await message.edit_text(
                help_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"◀️ {StyleFont.bold_sans('Back')}",
                            callback_data=f"wsettings_{chat_id}"
                        ),
                    ],
                ]),
            )
        except BadRequest:
            pass


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ TEXT CAPTCHA HANDLER (for text-type CAPTCHA) ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def text_captcha_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle text messages that might be CAPTCHA answers.
    Only checks if user has a pending text-type CAPTCHA.
    """
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or not chat:
        return
    if user.is_bot or chat.type == ChatType.PRIVATE:
        return
    if not message.text:
        return

    # Check if user has pending text captcha
    captcha = await WelcomeDB.get_captcha(chat.id, user.id)
    if not captcha:
        return
    if captcha.get("captcha_type") != "text":
        return
    if captcha.get("is_resolved", False):
        return

    answer = captcha.get("answer", "").lower().strip()
    user_input = message.text.lower().strip()

    # Delete the user's answer message
    try:
        await message.delete()
    except Exception:
        pass

    if user_input == answer:
        await CaptchaManager.handle_captcha_pass(
            context.bot, chat.id, user.id, captcha
        )
    else:
        attempts = await WelcomeDB.increment_captcha_attempts(
            chat.id, user.id
        )
        max_att = captcha.get("max_attempts", 3)

        if attempts >= max_att:
            settings = await WelcomeDB.get_welcome_settings(chat.id)
            kick = settings.get("captcha_kick_on_fail", True)
            await CaptchaManager.handle_captcha_fail(
                context.bot, chat.id, user.id, captcha, kick
            )
        else:
            try:
                sent = await context.bot.send_message(
                    chat.id,
                    f"❌ {StyleFont.small_caps('wrong answer')}! "
                    f"({attempts}/{max_att})\n"
                    f"{Symbols.BULLET} "
                    f"{StyleFont.small_caps('try again...')}",
                    parse_mode=ParseMode.HTML,
                )
                asyncio.create_task(
                    _auto_delete_message(sent, 5)
                )
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — POST INIT ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section3_post_init(application: Application) -> None:
    """Section 3 initialization"""
    await WelcomeDB.create_tables()

    # Start CAPTCHA timeout checker
    asyncio.create_task(captcha_timeout_checker(application))

    logger.info("✅ Section 3 (Welcome/Goodbye) initialized!")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 3 — REGISTER ALL HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

def register_section3_handlers(application: Application) -> None:
    """Register all Section 3 handlers"""

    # ── New member (welcome) handler ──
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_new_member
        ),
        group=1,
    )

    # ── Member left (goodbye) handler ──
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            handle_member_left
        ),
        group=1,
    )

    # ── Admin commands ──
    application.add_handler(
        CommandHandler("welcome", cmd_welcome)
    )
    application.add_handler(
        CommandHandler("setwelcome", cmd_setwelcome)
    )
    application.add_handler(
        CommandHandler("resetwelcome", cmd_resetwelcome)
    )
    application.add_handler(
        CommandHandler("goodbye", cmd_goodbye)
    )
    application.add_handler(
        CommandHandler("setgoodbye", cmd_setgoodbye)
    )
    application.add_handler(
        CommandHandler("resetgoodbye", cmd_resetgoodbye)
    )
    application.add_handler(
        CommandHandler("cleanwelcome", cmd_cleanwelcome)
    )
    application.add_handler(
        CommandHandler("welcomemute", cmd_welcomemute)
    )
    application.add_handler(
        CommandHandler("captcha", cmd_captcha)
    )
    application.add_handler(
        CommandHandler("antiraid", cmd_antiraid)
    )
    application.add_handler(
        CommandHandler("cleanservice", cmd_cleanservice)
    )
    application.add_handler(
        CommandHandler("welcomehelp", cmd_welcomehelp)
    )

    # ── Section 3 callback handler ──
    application.add_handler(
        CallbackQueryHandler(
            section3_callback_handler,
            pattern=r"^(captcha_|wtog_|wsettings_|wcaptcha_|wstats_|wformat_|wpreview_)"
        )
    )

    # ── Text CAPTCHA handler ──
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            text_captcha_handler
        ),
        group=3,
    )

    logger.info(
        "✅ Section 3 handlers registered: "
        "Welcome/Goodbye System "
        "(12 commands + event handlers)"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ INTEGRATION INSTRUCTIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════
#
# Add these 2 lines in your existing code:
#
# 1. In post_init() function, ADD:
#        await section3_post_init(application)
#
# 2. In register_handlers() function, ADD:
#        register_section3_handlers(application)
#
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#
#   ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#   ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
#   ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║
#   ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║
#   ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#   ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#
#        ██╗  ██╗       █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗
#        ██║  ██║      ██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║
#        ███████║      ███████║██║  ██║██╔████╔██║██║██╔██╗ ██║
#        ╚════██║      ██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║
#             ██║      ██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║
#             ╚═╝      ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝
#
# ═══════════════════════════════════════════════════════════════
#
#   SECTION 4 : ADMIN COMMANDS
#   ──────────────────────────────────────────
#   ✦ Ban / Unban / Kick
#   ✦ Mute / Unmute
#   ✦ Temporary Ban / Temporary Mute
#   ✦ Promote / Demote
#   ✦ Admin List
#   ✦ Pin / Unpin / Unpin All
#   ✦ Invite Link Generate
#   ✦ Set Group Title / Description / Photo
#   ✦ Admin Cache Refresh
#   ✦ Action Logging to DB + Channel
#
#   Powered By: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 4 — ADDITIONAL DB OPERATIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class AdminDB:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   𝐀ᴅᴍɪɴ 𝐀ᴄᴛɪᴏɴs 𝐃ᴀᴛᴀʙᴀsᴇ 𝐎ᴘᴇʀᴀᴛɪᴏɴs                ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    ║
    ║   Logging all admin actions                           ║
    ║   Storing promote/demote history                      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    async def log_action(
        chat_id: int,
        user_id: int,
        admin_id: int,
        action: str,
        reason: str = "",
    ) -> None:
        """Log an admin action to the database"""
        try:
            await db.execute("""
                INSERT INTO action_log (
                    chat_id, user_id, admin_id,
                    action, reason
                ) VALUES ($1, $2, $3, $4, $5);
            """, chat_id, user_id, admin_id, action, reason[:500])
        except Exception as e:
            logger.debug(f"Action log error: {e}")

    @staticmethod
    async def get_action_history(
        chat_id: int,
        user_id: int = 0,
        limit: int = 10
    ) -> list:
        """Get action history for chat or user"""
        try:
            if user_id:
                rows = await db.fetch("""
                    SELECT * FROM action_log
                    WHERE chat_id = $1 AND user_id = $2
                    ORDER BY timestamp DESC
                    LIMIT $3;
                """, chat_id, user_id, limit)
            else:
                rows = await db.fetch("""
                    SELECT * FROM action_log
                    WHERE chat_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2;
                """, chat_id, limit)
            return [dict(r) for r in rows]
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ ADMIN RESPONSE TEMPLATES ◈◈◈
# ═══════════════════════════════════════════════════════════════

class AdminTemplates:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   God-level stylish admin action response templates   ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    def ban_message(
        user_name: str,
        user_id: int,
        admin: User,
        reason: str = "",
        chat: Optional[Chat] = None,
    ) -> str:
        admin_mention = get_user_mention(admin)
        text = (
            f"🔨 {StyleFont.mixed_bold_smallcaps('User Banned')} 🔨\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Ban Info')} "
            f"]{Symbols.BOX_H * 6}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"🔨 {StyleFont.small_caps('permanently banned')}\n"
        )
        if reason:
            text += (
                f"{Symbols.BOX_V} 📋 "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:300])}</i>\n"
            )
        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def tban_message(
        user_name: str,
        user_id: int,
        admin: User,
        duration_str: str,
        reason: str = "",
    ) -> str:
        admin_mention = get_user_mention(admin)
        text = (
            f"🔨 {StyleFont.mixed_bold_smallcaps('User Temp Banned')} ⏱️\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('TBan Info')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⏱️ "
            f"{StyleFont.mixed_bold_smallcaps('Duration')}: "
            f"<b>{duration_str}</b>\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"🔨 {StyleFont.small_caps('temporarily banned')}\n"
        )
        if reason:
            text += (
                f"{Symbols.BOX_V} 📋 "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:300])}</i>\n"
            )
        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def unban_message(
        user_name: str,
        user_id: int,
        admin: User,
    ) -> str:
        admin_mention = get_user_mention(admin)
        return (
            f"🔓 {StyleFont.mixed_bold_smallcaps('User Unbanned')} 🔓\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Unban Info')} "
            f"]{Symbols.BOX_H * 4}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"🔓 {StyleFont.small_caps('unbanned')}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def kick_message(
        user_name: str,
        user_id: int,
        admin: User,
        reason: str = "",
    ) -> str:
        admin_mention = get_user_mention(admin)
        text = (
            f"🦶 {StyleFont.mixed_bold_smallcaps('User Kicked')} 🦶\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Kick Info')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"🦶 {StyleFont.small_caps('kicked (can rejoin)')}\n"
        )
        if reason:
            text += (
                f"{Symbols.BOX_V} 📋 "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:300])}</i>\n"
            )
        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def mute_message(
        user_name: str,
        user_id: int,
        admin: User,
        reason: str = "",
        duration_str: str = "",
    ) -> str:
        admin_mention = get_user_mention(admin)
        action_text = (
            f"🔇 {StyleFont.small_caps('temporarily muted')} ({duration_str})"
            if duration_str
            else f"🔇 {StyleFont.small_caps('permanently muted')}"
        )
        title = "User Temp Muted" if duration_str else "User Muted"
        text = (
            f"🔇 {StyleFont.mixed_bold_smallcaps(title)} 🔇\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Mute Info')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"{action_text}\n"
        )
        if reason:
            text += (
                f"{Symbols.BOX_V} 📋 "
                f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                f"<i>{html_escape(reason[:300])}</i>\n"
            )
        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def unmute_message(
        user_name: str,
        user_id: int,
        admin: User,
    ) -> str:
        admin_mention = get_user_mention(admin)
        return (
            f"🔊 {StyleFont.mixed_bold_smallcaps('User Unmuted')} 🔊\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Unmute Info')} "
            f"]{Symbols.BOX_H * 4}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('Admin')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"🔊 {StyleFont.small_caps('unmuted')}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def promote_message(
        user_name: str,
        user_id: int,
        admin: User,
        title: str = "",
    ) -> str:
        admin_mention = get_user_mention(admin)
        text = (
            f"⬆️ {StyleFont.mixed_bold_smallcaps('User Promoted')} ⬆️\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Promote Info')} "
            f"]{Symbols.BOX_H * 3}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('By')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"⬆️ {StyleFont.small_caps('promoted to admin')}\n"
        )
        if title:
            text += (
                f"{Symbols.BOX_V} 🏷️ "
                f"{StyleFont.mixed_bold_smallcaps('Title')}: "
                f"<i>{html_escape(title)}</i>\n"
            )
        text += (
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text

    @staticmethod
    def demote_message(
        user_name: str,
        user_id: int,
        admin: User,
    ) -> str:
        admin_mention = get_user_mention(admin)
        return (
            f"⬇️ {StyleFont.mixed_bold_smallcaps('User Demoted')} ⬇️\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Demote Info')} "
            f"]{Symbols.BOX_H * 3}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 👤 "
            f"{StyleFont.mixed_bold_smallcaps('User')}: "
            f"<a href='tg://user?id={user_id}'>"
            f"{html_escape(user_name)}</a>\n"
            f"{Symbols.BOX_V} 🆔 "
            f"{StyleFont.mixed_bold_smallcaps('Id')}: "
            f"<code>{user_id}</code>\n"
            f"{Symbols.BOX_V} 👮 "
            f"{StyleFont.mixed_bold_smallcaps('By')}: "
            f"{admin_mention}\n"
            f"{Symbols.BOX_V} ⚡ "
            f"{StyleFont.mixed_bold_smallcaps('Action')}: "
            f"⬇️ {StyleFont.small_caps('demoted from admin')}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def pin_message(admin: User, loud: bool = False) -> str:
        admin_mention = get_user_mention(admin)
        mode = "📌 Loud" if loud else "🔕 Silent"
        return (
            f"📌 {StyleFont.mixed_bold_smallcaps('Message Pinned')} 📌\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('By')}: {admin_mention}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Mode')}: {mode}\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )

    @staticmethod
    def admin_list_message(
        chat: Chat,
        creator: Optional[Dict] = None,
        admins: list = None,
        bots: list = None,
    ) -> str:
        admins = admins or []
        bots = bots or []
        chat_name = html_escape(chat.title or "")

        text = (
            f"👑 {StyleFont.mixed_bold_smallcaps('Admin List')} 👑\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
            f"{chat_name}\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Total Admins')}: "
            f"<b>{1 + len(admins) + len(bots)}</b>\n"
            f"\n"
        )

        # Creator
        if creator:
            c_name = html_escape(creator.get("name", "Unknown"))
            c_id = creator.get("id", 0)
            c_title = creator.get("title", "")
            text += (
                f"👑 {StyleFont.bold_sans('Creator')}:\n"
                f"  {Symbols.CROWN} "
                f"<a href='tg://user?id={c_id}'>{c_name}</a>"
            )
            if c_title:
                text += f" │ <i>{html_escape(c_title)}</i>"
            text += "\n\n"

        # Admins
        if admins:
            text += f"⚡ {StyleFont.bold_sans('Admins')} ({len(admins)}):\n"
            for i, adm in enumerate(admins, 1):
                a_name = html_escape(adm.get("name", "Unknown"))
                a_id = adm.get("id", 0)
                a_title = adm.get("title", "")
                text += (
                    f"  {Symbols.ARROW_TRI} "
                    f"<a href='tg://user?id={a_id}'>{a_name}</a>"
                )
                if a_title:
                    text += f" │ <i>{html_escape(a_title)}</i>"
                text += "\n"
            text += "\n"

        # Bots
        if bots:
            text += f"🤖 {StyleFont.bold_sans('Bots')} ({len(bots)}):\n"
            for bot_info in bots:
                b_name = html_escape(bot_info.get("name", "Bot"))
                b_id = bot_info.get("id", 0)
                text += (
                    f"  {Symbols.ARROW_TRI} "
                    f"<a href='tg://user?id={b_id}'>{b_name}</a>\n"
                )
            text += "\n"

        text += (
            f"{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )
        return text


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ HELPER: EXTRACT TARGET USER ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def _get_target_user(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Extract target user_id, user_name, and reason
    from message (reply or args).
    Returns (user_id, user_name, reason)
    """
    user_id = None
    user_name = ""
    reason = ""

    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        user_id = target.id
        user_name = get_user_full_name(target)
        args = message.text.split(None, 1)
        if len(args) > 1:
            reason = args[1].strip()
    elif context.args:
        target_str = context.args[0]

        # Try @username
        if target_str.startswith("@"):
            try:
                chat_info = await context.bot.get_chat(target_str)
                user_id = chat_info.id
                user_name = chat_info.first_name or target_str
            except Exception:
                return None, None, None
        else:
            # Try user_id
            try:
                user_id = int(target_str)
                try:
                    chat_info = await context.bot.get_chat(user_id)
                    user_name = chat_info.first_name or str(user_id)
                except Exception:
                    user_name = str(user_id)
            except ValueError:
                return None, None, None

        if len(context.args) > 1:
            reason = " ".join(context.args[1:]).strip()

    return user_id, user_name, reason


def _no_target_msg() -> str:
    return (
        f"{Symbols.CROSS3} "
        f"{StyleFont.mixed_bold_smallcaps('Specify A User')}!\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('reply to a message or provide @username / user id')}."
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 4 — COMMAND HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /ban — BAN A USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_ban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /ban — Permanently ban a user from the group.
    Usage: /ban (reply) [reason]
           /ban @username [reason]
           /ban user_id [reason]
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, reason = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    # Permission checks
    can, err = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can:
        await message.reply_text(err, parse_mode=ParseMode.HTML)
        return

    # Self-check
    if target_id == user.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You cannot ban yourself')}! 🤦",
            parse_mode=ParseMode.HTML,
        )
        return

    if target_id == context.bot.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('I am not going to ban myself')}! 😤",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.ban_chat_member(chat.id, target_id)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed to ban')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.ban_message(
        target_name, target_id, user, reason, chat
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    # Log
    await AdminDB.log_action(
        chat.id, target_id, user.id, "ban", reason
    )
    await bot_logger.log(
        bot=context.bot,
        log_type=LogType.BAN,
        chat=chat,
        admin=user,
        user=message.reply_to_message.from_user
            if message.reply_to_message and message.reply_to_message.from_user
            else None,
        reason=reason or "No reason",
    )
    cache.invalidate_admin_cache(chat.id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /tban — TEMPORARY BAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_tban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /tban — Temporarily ban a user.
    Usage: /tban (reply) <time> [reason]
           /tban @user 1h Spamming
    Time: 1m, 1h, 1d, 1w
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id = None
    target_name = ""
    reason = ""
    duration = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = get_user_full_name(target)

        if context.args:
            duration = parse_time_arg(context.args[0])
            if len(context.args) > 1:
                reason = " ".join(context.args[1:])
    elif context.args and len(context.args) >= 2:
        target_str = context.args[0]
        try:
            if target_str.startswith("@"):
                info = await context.bot.get_chat(target_str)
                target_id = info.id
                target_name = info.first_name or target_str
            else:
                target_id = int(target_str)
                try:
                    info = await context.bot.get_chat(target_id)
                    target_name = info.first_name or str(target_id)
                except Exception:
                    target_name = str(target_id)
        except Exception:
            await message.reply_text(
                _no_target_msg(), parse_mode=ParseMode.HTML
            )
            return

        duration = parse_time_arg(context.args[1])
        if len(context.args) > 2:
            reason = " ".join(context.args[2:])

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if not duration:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify time duration')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('examples')}: "
            f"<code>30m</code>, <code>2h</code>, "
            f"<code>1d</code>, <code>1w</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    can, err = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can:
        await message.reply_text(err, parse_mode=ParseMode.HTML)
        return

    try:
        until = datetime.now(timezone.utc) + timedelta(seconds=duration)
        await context.bot.ban_chat_member(
            chat.id, target_id, until_date=until
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    dur_str = get_readable_time(duration)
    text = AdminTemplates.tban_message(
        target_name, target_id, user, dur_str, reason
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, f"tban ({dur_str})", reason
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.BAN, chat=chat,
        admin=user, reason=f"TBan {dur_str}: {reason}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /unban — UNBAN A USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_unban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/unban — Unban a user from the group."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, _ = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if not await Permissions.has_ban_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need ban rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.unban_chat_member(
            chat.id, target_id, only_if_banned=True
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.unban_message(target_name, target_id, user)
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "unban", ""
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.UNBAN, chat=chat,
        admin=user, extra=f"Unbanned {target_id}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /kick — KICK A USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_kick(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/kick — Kick a user (they can rejoin)."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, reason = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    can, err = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can:
        await message.reply_text(err, parse_mode=ParseMode.HTML)
        return

    try:
        await context.bot.ban_chat_member(chat.id, target_id)
        await asyncio.sleep(0.5)
        await context.bot.unban_chat_member(
            chat.id, target_id, only_if_banned=True
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.kick_message(
        target_name, target_id, user, reason
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "kick", reason
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.KICK, chat=chat,
        admin=user, reason=reason or "No reason",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /mute — MUTE A USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_mute(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/mute — Permanently mute a user."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, reason = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    can, err = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can:
        await message.reply_text(err, parse_mode=ParseMode.HTML)
        return

    try:
        await context.bot.restrict_chat_member(
            chat.id, target_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_send_polls=False,
                can_invite_users=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_documents=False,
                can_send_audios=False,
            ),
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.mute_message(
        target_name, target_id, user, reason
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "mute", reason
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.MUTE, chat=chat,
        admin=user, reason=reason or "No reason",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /tmute — TEMPORARY MUTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_tmute(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /tmute — Temporarily mute a user.
    Usage: /tmute (reply) <time> [reason]
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id = None
    target_name = ""
    reason = ""
    duration = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = get_user_full_name(target)
        if context.args:
            duration = parse_time_arg(context.args[0])
            if len(context.args) > 1:
                reason = " ".join(context.args[1:])
    elif context.args and len(context.args) >= 2:
        target_str = context.args[0]
        try:
            if target_str.startswith("@"):
                info = await context.bot.get_chat(target_str)
                target_id = info.id
                target_name = info.first_name or target_str
            else:
                target_id = int(target_str)
                try:
                    info = await context.bot.get_chat(target_id)
                    target_name = info.first_name or str(target_id)
                except Exception:
                    target_name = str(target_id)
        except Exception:
            await message.reply_text(
                _no_target_msg(), parse_mode=ParseMode.HTML
            )
            return
        duration = parse_time_arg(context.args[1])
        if len(context.args) > 2:
            reason = " ".join(context.args[2:])

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if not duration:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Specify time')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('examples')}: "
            f"<code>30m</code>, <code>2h</code>, <code>1d</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    can, err = await Permissions.can_restrict_user(
        chat.id, user.id, target_id, context.bot
    )
    if not can:
        await message.reply_text(err, parse_mode=ParseMode.HTML)
        return

    try:
        until = datetime.now(timezone.utc) + timedelta(seconds=duration)
        await context.bot.restrict_chat_member(
            chat.id, target_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_send_polls=False,
                can_invite_users=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_documents=False,
                can_send_audios=False,
            ),
            until_date=until,
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    dur_str = get_readable_time(duration)
    text = AdminTemplates.mute_message(
        target_name, target_id, user, reason, dur_str
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, f"tmute ({dur_str})", reason
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.MUTE, chat=chat,
        admin=user, reason=f"TMute {dur_str}: {reason}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /unmute — UNMUTE A USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_unmute(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/unmute — Unmute a user."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, _ = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if not await Permissions.has_ban_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need restrict rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.restrict_chat_member(
            chat.id, target_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_documents=True,
                can_send_audios=True,
            ),
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.unmute_message(
        target_name, target_id, user
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "unmute", ""
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.UNMUTE, chat=chat,
        admin=user, extra=f"Unmuted {target_id}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /promote — PROMOTE A USER TO ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_promote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /promote — Promote a user to admin.
    Usage: /promote (reply) [title]
           /promote @user [title]
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    # Check promote permission
    if not await Permissions.has_promote_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need promote rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    # Check bot has promote rights
    bot_member = await context.bot.get_chat_member(
        chat.id, context.bot.id
    )
    if isinstance(bot_member, ChatMemberAdministrator):
        if not bot_member.can_promote_members:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.mixed_bold_smallcaps('I need promote rights')}!",
                parse_mode=ParseMode.HTML,
            )
            return

    target_id, target_name, title = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if target_id == context.bot.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('I cannot promote myself')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.promote_chat_member(
            chat.id,
            target_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_manage_chat=True,
            can_manage_video_chats=True,
        )

        # Set custom title if provided
        if title:
            try:
                await context.bot.set_chat_administrator_custom_title(
                    chat.id, target_id, title[:16]
                )
            except Exception:
                pass

    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.promote_message(
        target_name, target_id, user, title or ""
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    cache.invalidate_admin_cache(chat.id)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "promote", title or ""
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.PROMOTE, chat=chat,
        admin=user, extra=f"Promoted {target_id}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /demote — DEMOTE AN ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_demote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/demote — Demote an admin."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_promote_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need promote rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    target_id, target_name, _ = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if target_id == context.bot.id:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('I cannot demote myself')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    # Check target is admin
    admins = await cache.get_admin_cache(chat.id, context.bot)
    if target_id not in admins:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('User is not an admin')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if isinstance(admins[target_id], ChatMemberOwner):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Cannot demote the group creator')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.promote_chat_member(
            chat.id,
            target_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.demote_message(
        target_name, target_id, user
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    cache.invalidate_admin_cache(chat.id)

    await AdminDB.log_action(
        chat.id, target_id, user.id, "demote", ""
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.DEMOTE, chat=chat,
        admin=user, extra=f"Demoted {target_id}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /title — SET ADMIN CUSTOM TITLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_title(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /title — Set admin custom title.
    Usage: /title (reply) <title>
           /title @user <title>
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    target_id, target_name, title = await _get_target_user(
        message, context
    )

    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return

    if not title:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a title')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('max 16 characters')}",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.set_chat_administrator_custom_title(
            chat.id, target_id, title[:16]
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Admin Title Set')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={target_id}'>"
        f"{html_escape(target_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Title')}: "
        f"<i>{html_escape(title[:16])}</i>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )
    cache.invalidate_admin_cache(chat.id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /adminlist — LIST ALL ADMINS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@cooldown(5.0)
@check_disabled
async def cmd_adminlist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/adminlist — Show all group admins."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    await message.reply_chat_action(ChatAction.TYPING)

    # Force fresh cache
    cache.invalidate_admin_cache(chat.id)
    admins = await cache.get_admin_cache(chat.id, context.bot)

    creator = None
    admin_list = []
    bot_list = []

    for uid, member in admins.items():
        u = member.user
        name = get_user_full_name(u)
        title = ""
        if isinstance(member, ChatMemberAdministrator):
            title = member.custom_title or ""
        elif isinstance(member, ChatMemberOwner):
            title = member.custom_title or ""

        entry = {
            "id": u.id,
            "name": name,
            "title": title,
            "is_bot": u.is_bot,
        }

        if isinstance(member, ChatMemberOwner):
            creator = entry
        elif u.is_bot:
            bot_list.append(entry)
        else:
            admin_list.append(entry)

    text = AdminTemplates.admin_list_message(
        chat, creator, admin_list, bot_list
    )

    await message.reply_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /admincache — REFRESH ADMIN CACHE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@cooldown(10.0)
async def cmd_admincache(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/admincache — Force refresh admin cache."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    cache.invalidate_admin_cache(chat.id)
    admins = await cache.get_admin_cache(chat.id, context.bot)

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Admin Cache Refreshed')}!\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Admins Found')}: "
        f"<b>{len(admins)}</b>",
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /pin — PIN A MESSAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_pin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /pin — Pin the replied message.
    /pin loud — Pin with notification.
    /pin silent — Pin silently (default).
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not message.reply_to_message:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Reply to a message to pin it')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if not await Permissions.has_pin_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need pin rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    loud = False
    if context.args:
        if context.args[0].lower() in ("loud", "notify", "notification"):
            loud = True

    try:
        await context.bot.pin_chat_message(
            chat.id,
            message.reply_to_message.message_id,
            disable_notification=not loud,
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text = AdminTemplates.pin_message(user, loud)
    await message.reply_text(text, parse_mode=ParseMode.HTML)

    await AdminDB.log_action(
        chat.id, 0, user.id, "pin",
        f"Message {message.reply_to_message.message_id}"
    )
    await bot_logger.log(
        bot=context.bot, log_type=LogType.PIN, chat=chat,
        admin=user, extra="Pinned a message",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /unpin — UNPIN A MESSAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(2.0)
async def cmd_unpin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/unpin — Unpin the replied or latest pinned message."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_pin_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need pin rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        if message.reply_to_message:
            await context.bot.unpin_chat_message(
                chat.id,
                message_id=message.reply_to_message.message_id
            )
        else:
            await context.bot.unpin_chat_message(chat.id)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Message Unpinned')}! 📌",
        parse_mode=ParseMode.HTML,
    )

    await bot_logger.log(
        bot=context.bot, log_type=LogType.UNPIN, chat=chat,
        admin=user, extra="Unpinned a message",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /unpinall — UNPIN ALL MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(10.0)
async def cmd_unpinall(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/unpinall — Unpin all pinned messages."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    # Only chat owner or sudo can unpin all
    is_owner = await Permissions.is_user_owner(
        chat.id, user.id, context.bot
    )
    if not is_owner and not cache.is_sudo(user.id):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Only the group owner can unpin all')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.unpin_all_chat_messages(chat.id)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('All Messages Unpinned')}! 📌\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /pinned — GET PINNED MESSAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@cooldown(3.0)
@check_disabled
async def cmd_pinned(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/pinned — Get the current pinned message link."""
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    try:
        chat_info = await context.bot.get_chat(chat.id)
        pinned = chat_info.pinned_message
    except Exception:
        pinned = None

    if not pinned:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No pinned message')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    link = f"https://t.me/c/{str(chat.id)[4:]}/{pinned.message_id}"
    if chat.username:
        link = f"https://t.me/{chat.username}/{pinned.message_id}"

    await message.reply_text(
        f"📌 {StyleFont.mixed_bold_smallcaps('Pinned Message')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Message Id')}: "
        f"<code>{pinned.message_id}</code>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"📌 {StyleFont.bold_sans('Go To Message')}",
                    url=link
                ),
            ],
        ]),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /invitelink — GENERATE INVITE LINK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(5.0)
async def cmd_invitelink(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/invitelink — Generate a new group invite link."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_invite_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need invite rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        link = await context.bot.export_chat_invite_link(chat.id)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"🔗 {StyleFont.mixed_bold_smallcaps('Invite Link Generated')}\n"
        f"{Symbols.divider(6)}\n"
        f"\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
        f"{html_escape(chat.title or '')}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Link')}: "
        f"<code>{link}</code>\n"
        f"\n"
        f"{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔗 {StyleFont.bold_sans('Join Link')}",
                    url=link
                ),
            ],
        ]),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /setgtitle — SET GROUP TITLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(10.0)
async def cmd_setgtitle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/setgtitle <title> — Set the group title."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_manage_chat_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need change info rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a title')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    new_title = " ".join(context.args)

    try:
        await context.bot.set_chat_title(chat.id, new_title[:128])
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Group Title Updated')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('New Title')}: "
        f"<b>{html_escape(new_title[:128])}</b>\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /setgdesc — SET GROUP DESCRIPTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(10.0)
async def cmd_setgdesc(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/setgdesc <text> — Set the group description."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_manage_chat_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need change info rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    desc = ""
    if context.args:
        desc = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        desc = message.reply_to_message.text

    if not desc:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide a description')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.set_chat_description(chat.id, desc[:255])
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Group Description Updated')}!\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /setgphoto — SET GROUP PHOTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(10.0)
async def cmd_setgphoto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/setgphoto — Reply to a photo to set it as group photo."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_manage_chat_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need change info rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Reply to a photo')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    photo = message.reply_to_message.photo[-1]

    try:
        photo_file = await photo.get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        await context.bot.set_chat_photo(
            chat.id, photo=bytes(photo_bytes)
        )
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Group Photo Updated')}! 🖼️\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /delgphoto — DELETE GROUP PHOTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(10.0)
async def cmd_delgphoto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/delgphoto — Remove the group photo."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    if not await Permissions.has_manage_chat_permission(
        chat.id, user.id, context.bot
    ):
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('You need change info rights')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await context.bot.delete_chat_photo(chat.id)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Group Photo Removed')}!",
        parse_mode=ParseMode.HTML,
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 4 — POST INIT ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section4_post_init(application: Application) -> None:
    """Section 4 initialization"""
    logger.info("✅ Section 4 (Admin Commands) initialized!")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 4 — REGISTER ALL HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

def register_section4_handlers(application: Application) -> None:
    """Register all Section 4 handlers"""

    # ── Ban / Unban / Kick ──
    application.add_handler(CommandHandler("ban", cmd_ban))
    application.add_handler(CommandHandler("tban", cmd_tban))
    application.add_handler(CommandHandler("unban", cmd_unban))
    application.add_handler(CommandHandler("kick", cmd_kick))

    # ── Mute / Unmute ──
    application.add_handler(CommandHandler("mute", cmd_mute))
    application.add_handler(CommandHandler("tmute", cmd_tmute))
    application.add_handler(CommandHandler("unmute", cmd_unmute))

    # ── Promote / Demote / Title ──
    application.add_handler(CommandHandler("promote", cmd_promote))
    application.add_handler(CommandHandler("demote", cmd_demote))
    application.add_handler(CommandHandler("title", cmd_title))

    # ── Admin List & Cache ──
    application.add_handler(
        CommandHandler("adminlist", cmd_adminlist)
    )
    application.add_handler(
        CommandHandler("admincache", cmd_admincache)
    )

    # ── Pin / Unpin ──
    application.add_handler(CommandHandler("pin", cmd_pin))
    application.add_handler(CommandHandler("unpin", cmd_unpin))
    application.add_handler(CommandHandler("unpinall", cmd_unpinall))
    application.add_handler(CommandHandler("pinned", cmd_pinned))

    # ── Group Settings ──
    application.add_handler(
        CommandHandler("invitelink", cmd_invitelink)
    )
    application.add_handler(
        CommandHandler("setgtitle", cmd_setgtitle)
    )
    application.add_handler(
        CommandHandler("setgdesc", cmd_setgdesc)
    )
    application.add_handler(
        CommandHandler("setgphoto", cmd_setgphoto)
    )
    application.add_handler(
        CommandHandler("delgphoto", cmd_delgphoto)
    )

    logger.info(
        "✅ Section 4 handlers registered: "
        "Admin Commands (20 commands)"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ INTEGRATION INSTRUCTIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════
#
#  1. In post_init():
#         await section4_post_init(application)
#
#  2. In register_handlers():
#         register_section4_handlers(application)
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
#
#   ███████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#   ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
#   ███████╗█████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║
#   ╚════██║██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║
#   ███████║███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#   ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#
#       ███████╗      ██████╗ ██████╗  ██████╗ ████████╗
#       ██╔════╝      ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
#       ███████╗      ██████╔╝██████╔╝██║   ██║   ██║
#       ╚════██║      ██╔═══╝ ██╔══██╗██║   ██║   ██║
#       ███████║      ██║     ██║  ██║╚██████╔╝   ██║
#       ╚══════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝
#
# ═══════════════════════════════════════════════════════════════
#
#   SECTION 5 : ANTI-SPAM & PROTECTION SYSTEM
#   ──────────────────────────────────────────────
#   ✦ Anti-Flood System
#   ✦ Anti-Spam Detection
#   ✦ Anti-Link (auto delete links)
#   ✦ Anti-Bot (prevent bot adding)
#   ✦ Anti-Forward
#   ✦ Anti-Channel (auto ban channels)
#   ✦ Anti-Arabic / RTL
#   ✦ Anti-Sticker Spam
#   ✦ Anti-GIF Spam
#   ✦ Anti-NSFW (basic image check)
#   ✦ Blacklist Words System
#   ✦ Whitelist URLs
#   ✦ Slowmode Control
#
#   Powered By: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
#
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 5 — DATABASE TABLES ◈◈◈
# ═══════════════════════════════════════════════════════════════

SECTION5_TABLES_SQL = """

-- ══════════════════════════════════════════
-- Protection settings per chat
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS protection_settings (
    chat_id                     BIGINT PRIMARY KEY,

    -- Anti-Flood
    antiflood_enabled           BOOLEAN DEFAULT FALSE,
    antiflood_limit             INTEGER DEFAULT 10,
    antiflood_time_window       INTEGER DEFAULT 45,
    antiflood_action            TEXT DEFAULT 'mute',
    antiflood_action_duration   INTEGER DEFAULT 3600,
    antiflood_del_msg           BOOLEAN DEFAULT TRUE,

    -- Anti-Spam
    antispam_enabled            BOOLEAN DEFAULT FALSE,
    antispam_action             TEXT DEFAULT 'mute',
    antispam_score_threshold    INTEGER DEFAULT 5,

    -- Anti-Link
    antilink_enabled            BOOLEAN DEFAULT FALSE,
    antilink_action             TEXT DEFAULT 'delete',
    antilink_warn               BOOLEAN DEFAULT TRUE,
    antilink_allow_admins       BOOLEAN DEFAULT TRUE,
    antilink_allow_tg_links     BOOLEAN DEFAULT FALSE,

    -- Anti-Bot
    antibot_enabled             BOOLEAN DEFAULT FALSE,
    antibot_action              TEXT DEFAULT 'kick',

    -- Anti-Forward
    antiforward_enabled         BOOLEAN DEFAULT FALSE,
    antiforward_action          TEXT DEFAULT 'delete',
    antiforward_from_channels   BOOLEAN DEFAULT TRUE,
    antiforward_from_users      BOOLEAN DEFAULT FALSE,
    antiforward_from_bots       BOOLEAN DEFAULT TRUE,

    -- Anti-Channel
    antichannel_enabled         BOOLEAN DEFAULT FALSE,

    -- Anti-Arabic / RTL
    antiarabic_enabled          BOOLEAN DEFAULT FALSE,
    antiarabic_action           TEXT DEFAULT 'delete',

    -- Anti-Sticker Spam
    antisticker_enabled         BOOLEAN DEFAULT FALSE,
    antisticker_limit           INTEGER DEFAULT 5,
    antisticker_time_window     INTEGER DEFAULT 30,
    antisticker_action          TEXT DEFAULT 'mute',

    -- Anti-GIF Spam
    antigif_enabled             BOOLEAN DEFAULT FALSE,
    antigif_limit               INTEGER DEFAULT 5,
    antigif_time_window         INTEGER DEFAULT 30,
    antigif_action              TEXT DEFAULT 'mute',

    -- Anti-NSFW
    antinsfw_enabled            BOOLEAN DEFAULT FALSE,
    antinsfw_action             TEXT DEFAULT 'delete',

    -- Slowmode
    slowmode_enabled            BOOLEAN DEFAULT FALSE,
    slowmode_seconds            INTEGER DEFAULT 0,
    slowmode_custom_enabled     BOOLEAN DEFAULT FALSE,
    slowmode_custom_seconds     INTEGER DEFAULT 10,

    -- Stats
    total_flood_actions         BIGINT DEFAULT 0,
    total_spam_actions          BIGINT DEFAULT 0,
    total_link_deleted          BIGINT DEFAULT 0,
    total_bot_kicked            BIGINT DEFAULT 0,
    total_forward_deleted       BIGINT DEFAULT 0,
    total_channel_banned        BIGINT DEFAULT 0,
    total_arabic_deleted        BIGINT DEFAULT 0,
    total_sticker_actions       BIGINT DEFAULT 0,
    total_gif_actions           BIGINT DEFAULT 0,
    total_nsfw_actions          BIGINT DEFAULT 0,
    total_blacklist_actions     BIGINT DEFAULT 0,

    created_at                  TIMESTAMP DEFAULT NOW(),
    updated_at                  TIMESTAMP DEFAULT NOW()
);

-- ══════════════════════════════════════════
-- Blacklist words per chat
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS blacklist_words (
    id              SERIAL PRIMARY KEY,
    chat_id         BIGINT NOT NULL,
    word            TEXT NOT NULL,
    added_by        BIGINT DEFAULT 0,
    reason          TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(chat_id, word)
);

CREATE INDEX IF NOT EXISTS idx_blacklist_words_chat
    ON blacklist_words(chat_id);

-- ══════════════════════════════════════════
-- Blacklist settings per chat
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS blacklist_settings (
    chat_id         BIGINT PRIMARY KEY,
    bl_action       TEXT DEFAULT 'delete',
    bl_action_dur   INTEGER DEFAULT 3600,
    bl_warn         BOOLEAN DEFAULT TRUE,
    bl_log          BOOLEAN DEFAULT TRUE
);

-- ══════════════════════════════════════════
-- Whitelisted URLs per chat
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS whitelist_urls (
    id              SERIAL PRIMARY KEY,
    chat_id         BIGINT NOT NULL,
    url_pattern     TEXT NOT NULL,
    added_by        BIGINT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(chat_id, url_pattern)
);

CREATE INDEX IF NOT EXISTS idx_whitelist_urls_chat
    ON whitelist_urls(chat_id);

-- ══════════════════════════════════════════
-- Approved users (bypass all protections)
-- Already exists from Section 1, but ensure
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS approved_users (
    chat_id         BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    approved_by     BIGINT DEFAULT 0,
    approved_at     TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY(chat_id, user_id)
);

-- ══════════════════════════════════════════
-- Flood action log
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS flood_log (
    id              SERIAL PRIMARY KEY,
    chat_id         BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    messages_count  INTEGER DEFAULT 0,
    time_window     INTEGER DEFAULT 0,
    action_taken    TEXT DEFAULT '',
    timestamp       TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flood_log_chat
    ON flood_log(chat_id);

"""


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ PROTECTION DATABASE OPERATIONS ◈◈◈
# ═══════════════════════════════════════════════════════════════

class ProtectionDB:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ 𝐃ᴀᴛᴀʙᴀsᴇ 𝐎ᴘᴇʀᴀᴛɪᴏɴs                   ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    ║
    ║   All anti-spam & protection DB queries               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """

    @staticmethod
    async def create_tables() -> None:
        try:
            for stmt in SECTION5_TABLES_SQL.split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    try:
                        await db.execute(stmt)
                    except Exception as se:
                        logger.debug(f"Section 5 stmt skip: {se}")
            logger.info("✅ Section 5 tables created!")
        except Exception as e:
            logger.error(f"❌ Section 5 tables error: {e}")

    # ───────────────────────────────────────────────────────
    # PROTECTION SETTINGS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def get_settings(chat_id: int) -> Dict[str, Any]:
        try:
            row = await db.fetchrow(
                "SELECT * FROM protection_settings WHERE chat_id = $1;",
                chat_id
            )
            if row:
                return dict(row)
            await db.execute("""
                INSERT INTO protection_settings (chat_id)
                VALUES ($1) ON CONFLICT (chat_id) DO NOTHING;
            """, chat_id)
            row = await db.fetchrow(
                "SELECT * FROM protection_settings WHERE chat_id = $1;",
                chat_id
            )
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Get protection settings error: {e}")
            return {}

    @staticmethod
    async def update_setting(
        chat_id: int, setting: str, value: Any
    ) -> bool:
        valid = [
            'antiflood_enabled', 'antiflood_limit', 'antiflood_time_window',
            'antiflood_action', 'antiflood_action_duration', 'antiflood_del_msg',
            'antispam_enabled', 'antispam_action', 'antispam_score_threshold',
            'antilink_enabled', 'antilink_action', 'antilink_warn',
            'antilink_allow_admins', 'antilink_allow_tg_links',
            'antibot_enabled', 'antibot_action',
            'antiforward_enabled', 'antiforward_action',
            'antiforward_from_channels', 'antiforward_from_users',
            'antiforward_from_bots',
            'antichannel_enabled',
            'antiarabic_enabled', 'antiarabic_action',
            'antisticker_enabled', 'antisticker_limit',
            'antisticker_time_window', 'antisticker_action',
            'antigif_enabled', 'antigif_limit',
            'antigif_time_window', 'antigif_action',
            'antinsfw_enabled', 'antinsfw_action',
            'slowmode_enabled', 'slowmode_seconds',
            'slowmode_custom_enabled', 'slowmode_custom_seconds',
        ]
        if setting not in valid:
            return False
        try:
            await db.execute(f"""
                INSERT INTO protection_settings (chat_id, {setting}, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO UPDATE SET
                    {setting} = EXCLUDED.{setting},
                    updated_at = NOW();
            """, chat_id, value)
            return True
        except Exception as e:
            logger.error(f"Update protection setting error: {e}")
            return False

    @staticmethod
    async def increment_stat(chat_id: int, stat: str) -> None:
        stat_cols = [
            'total_flood_actions', 'total_spam_actions',
            'total_link_deleted', 'total_bot_kicked',
            'total_forward_deleted', 'total_channel_banned',
            'total_arabic_deleted', 'total_sticker_actions',
            'total_gif_actions', 'total_nsfw_actions',
            'total_blacklist_actions',
        ]
        if stat not in stat_cols:
            return
        try:
            await db.execute(f"""
                UPDATE protection_settings
                SET {stat} = {stat} + 1
                WHERE chat_id = $1;
            """, chat_id)
        except Exception:
            pass

    # ───────────────────────────────────────────────────────
    # BLACKLIST WORDS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def add_blacklist_word(
        chat_id: int, word: str, added_by: int = 0,
        reason: str = ""
    ) -> bool:
        try:
            await db.execute("""
                INSERT INTO blacklist_words (chat_id, word, added_by, reason)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (chat_id, word) DO NOTHING;
            """, chat_id, word.lower().strip(), added_by, reason)
            return True
        except Exception:
            return False

    @staticmethod
    async def remove_blacklist_word(
        chat_id: int, word: str
    ) -> bool:
        try:
            result = await db.execute(
                "DELETE FROM blacklist_words WHERE chat_id = $1 AND word = $2;",
                chat_id, word.lower().strip()
            )
            return result == "DELETE 1"
        except Exception:
            return False

    @staticmethod
    async def get_blacklist_words(chat_id: int) -> List[str]:
        try:
            rows = await db.fetch(
                "SELECT word FROM blacklist_words WHERE chat_id = $1 ORDER BY word;",
                chat_id
            )
            return [r["word"] for r in rows]
        except Exception:
            return []

    @staticmethod
    async def get_blacklist_words_full(chat_id: int) -> list:
        try:
            rows = await db.fetch(
                "SELECT * FROM blacklist_words WHERE chat_id = $1 ORDER BY word;",
                chat_id
            )
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    async def clear_all_blacklist(chat_id: int) -> int:
        try:
            count = await db.fetchval(
                "SELECT COUNT(*) FROM blacklist_words WHERE chat_id = $1;",
                chat_id
            )
            await db.execute(
                "DELETE FROM blacklist_words WHERE chat_id = $1;",
                chat_id
            )
            return count or 0
        except Exception:
            return 0

    @staticmethod
    async def get_blacklist_settings(
        chat_id: int
    ) -> Dict[str, Any]:
        try:
            row = await db.fetchrow(
                "SELECT * FROM blacklist_settings WHERE chat_id = $1;",
                chat_id
            )
            if row:
                return dict(row)
            await db.execute("""
                INSERT INTO blacklist_settings (chat_id)
                VALUES ($1) ON CONFLICT (chat_id) DO NOTHING;
            """, chat_id)
            row = await db.fetchrow(
                "SELECT * FROM blacklist_settings WHERE chat_id = $1;",
                chat_id
            )
            return dict(row) if row else {}
        except Exception:
            return {}

    @staticmethod
    async def update_blacklist_setting(
        chat_id: int, setting: str, value: Any
    ) -> bool:
        valid = ['bl_action', 'bl_action_dur', 'bl_warn', 'bl_log']
        if setting not in valid:
            return False
        try:
            await db.execute(f"""
                INSERT INTO blacklist_settings (chat_id, {setting})
                VALUES ($1, $2)
                ON CONFLICT (chat_id) DO UPDATE SET
                    {setting} = EXCLUDED.{setting};
            """, chat_id, value)
            return True
        except Exception:
            return False

    # ───────────────────────────────────────────────────────
    # WHITELIST URLS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def add_whitelist_url(
        chat_id: int, url_pattern: str, added_by: int = 0
    ) -> bool:
        try:
            await db.execute("""
                INSERT INTO whitelist_urls (chat_id, url_pattern, added_by)
                VALUES ($1, $2, $3)
                ON CONFLICT (chat_id, url_pattern) DO NOTHING;
            """, chat_id, url_pattern.lower().strip(), added_by)
            return True
        except Exception:
            return False

    @staticmethod
    async def remove_whitelist_url(
        chat_id: int, url_pattern: str
    ) -> bool:
        try:
            result = await db.execute(
                "DELETE FROM whitelist_urls WHERE chat_id = $1 AND url_pattern = $2;",
                chat_id, url_pattern.lower().strip()
            )
            return result == "DELETE 1"
        except Exception:
            return False

    @staticmethod
    async def get_whitelist_urls(chat_id: int) -> List[str]:
        try:
            rows = await db.fetch(
                "SELECT url_pattern FROM whitelist_urls WHERE chat_id = $1;",
                chat_id
            )
            return [r["url_pattern"] for r in rows]
        except Exception:
            return []

    @staticmethod
    async def clear_whitelist_urls(chat_id: int) -> int:
        try:
            count = await db.fetchval(
                "SELECT COUNT(*) FROM whitelist_urls WHERE chat_id = $1;",
                chat_id
            )
            await db.execute(
                "DELETE FROM whitelist_urls WHERE chat_id = $1;",
                chat_id
            )
            return count or 0
        except Exception:
            return 0

    # ───────────────────────────────────────────────────────
    # APPROVED USERS
    # ───────────────────────────────────────────────────────

    @staticmethod
    async def approve_user(
        chat_id: int, user_id: int, approved_by: int = 0
    ) -> bool:
        try:
            await db.execute("""
                INSERT INTO approved_users (chat_id, user_id, approved_by)
                VALUES ($1, $2, $3)
                ON CONFLICT (chat_id, user_id) DO NOTHING;
            """, chat_id, user_id, approved_by)
            return True
        except Exception:
            return False

    @staticmethod
    async def unapprove_user(
        chat_id: int, user_id: int
    ) -> bool:
        try:
            result = await db.execute(
                "DELETE FROM approved_users WHERE chat_id = $1 AND user_id = $2;",
                chat_id, user_id
            )
            return result == "DELETE 1"
        except Exception:
            return False

    @staticmethod
    async def is_approved(chat_id: int, user_id: int) -> bool:
        try:
            val = await db.fetchval(
                "SELECT user_id FROM approved_users WHERE chat_id = $1 AND user_id = $2;",
                chat_id, user_id
            )
            return val is not None
        except Exception:
            return False

    @staticmethod
    async def get_approved_users(chat_id: int) -> list:
        try:
            rows = await db.fetch(
                "SELECT * FROM approved_users WHERE chat_id = $1;",
                chat_id
            )
            return [dict(r) for r in rows]
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ PROTECTION SETTINGS CACHE ◈◈◈
# ═══════════════════════════════════════════════════════════════

class ProtectionCache:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   In-memory cache for protection settings            ║
    ║   Reduces DB queries on every message                ║
    ╚═══════════════════════════════════════════════════════╝
    """

    def __init__(self):
        self._settings: Dict[int, Dict[str, Any]] = {}
        self._settings_time: Dict[int, float] = {}
        self._blacklist: Dict[int, List[str]] = {}
        self._blacklist_time: Dict[int, float] = {}
        self._whitelist: Dict[int, List[str]] = {}
        self._whitelist_time: Dict[int, float] = {}
        self._approved: Dict[int, Set[int]] = defaultdict(set)
        self._approved_time: Dict[int, float] = {}
        self._flood_tracker: Dict[str, List[float]] = defaultdict(list)
        self._sticker_tracker: Dict[str, List[float]] = defaultdict(list)
        self._gif_tracker: Dict[str, List[float]] = defaultdict(list)
        self._spam_score: Dict[str, int] = defaultdict(int)
        self._spam_last_reset: Dict[str, float] = {}
        self.CACHE_TTL = 300  # 5 minutes

    async def get_settings(self, chat_id: int) -> Dict[str, Any]:
        now = time.time()
        if (
            chat_id in self._settings
            and now - self._settings_time.get(chat_id, 0) < self.CACHE_TTL
        ):
            return self._settings[chat_id]
        settings = await ProtectionDB.get_settings(chat_id)
        self._settings[chat_id] = settings
        self._settings_time[chat_id] = now
        return settings

    def invalidate_settings(self, chat_id: int) -> None:
        self._settings.pop(chat_id, None)
        self._settings_time.pop(chat_id, None)

    async def get_blacklist(self, chat_id: int) -> List[str]:
        now = time.time()
        if (
            chat_id in self._blacklist
            and now - self._blacklist_time.get(chat_id, 0) < self.CACHE_TTL
        ):
            return self._blacklist[chat_id]
        words = await ProtectionDB.get_blacklist_words(chat_id)
        self._blacklist[chat_id] = words
        self._blacklist_time[chat_id] = now
        return words

    def invalidate_blacklist(self, chat_id: int) -> None:
        self._blacklist.pop(chat_id, None)
        self._blacklist_time.pop(chat_id, None)

    async def get_whitelist(self, chat_id: int) -> List[str]:
        now = time.time()
        if (
            chat_id in self._whitelist
            and now - self._whitelist_time.get(chat_id, 0) < self.CACHE_TTL
        ):
            return self._whitelist[chat_id]
        urls = await ProtectionDB.get_whitelist_urls(chat_id)
        self._whitelist[chat_id] = urls
        self._whitelist_time[chat_id] = now
        return urls

    def invalidate_whitelist(self, chat_id: int) -> None:
        self._whitelist.pop(chat_id, None)
        self._whitelist_time.pop(chat_id, None)

    async def is_approved(self, chat_id: int, user_id: int) -> bool:
        now = time.time()
        if (
            chat_id in self._approved
            and now - self._approved_time.get(chat_id, 0) < self.CACHE_TTL
        ):
            return user_id in self._approved[chat_id]
        approved = await ProtectionDB.get_approved_users(chat_id)
        self._approved[chat_id] = {a["user_id"] for a in approved}
        self._approved_time[chat_id] = now
        return user_id in self._approved[chat_id]

    def invalidate_approved(self, chat_id: int) -> None:
        self._approved.pop(chat_id, None)
        self._approved_time.pop(chat_id, None)

    # ── Flood tracking ──
    def check_flood(
        self, chat_id: int, user_id: int,
        limit: int, window: int
    ) -> bool:
        key = f"flood:{chat_id}:{user_id}"
        now = time.time()
        self._flood_tracker[key] = [
            t for t in self._flood_tracker[key] if now - t < window
        ]
        self._flood_tracker[key].append(now)
        return len(self._flood_tracker[key]) > limit

    def reset_flood(self, chat_id: int, user_id: int) -> None:
        key = f"flood:{chat_id}:{user_id}"
        self._flood_tracker.pop(key, None)

    # ── Sticker tracking ──
    def check_sticker_spam(
        self, chat_id: int, user_id: int,
        limit: int, window: int
    ) -> bool:
        key = f"sticker:{chat_id}:{user_id}"
        now = time.time()
        self._sticker_tracker[key] = [
            t for t in self._sticker_tracker[key] if now - t < window
        ]
        self._sticker_tracker[key].append(now)
        return len(self._sticker_tracker[key]) > limit

    # ── GIF tracking ──
    def check_gif_spam(
        self, chat_id: int, user_id: int,
        limit: int, window: int
    ) -> bool:
        key = f"gif:{chat_id}:{user_id}"
        now = time.time()
        self._gif_tracker[key] = [
            t for t in self._gif_tracker[key] if now - t < window
        ]
        self._gif_tracker[key].append(now)
        return len(self._gif_tracker[key]) > limit

    # ── Spam score ──
    def add_spam_score(
        self, chat_id: int, user_id: int, score: int
    ) -> int:
        key = f"spam:{chat_id}:{user_id}"
        now = time.time()
        if now - self._spam_last_reset.get(key, 0) > 300:
            self._spam_score[key] = 0
            self._spam_last_reset[key] = now
        self._spam_score[key] += score
        return self._spam_score[key]

    def reset_spam_score(self, chat_id: int, user_id: int) -> None:
        key = f"spam:{chat_id}:{user_id}"
        self._spam_score.pop(key, None)


# Global protection cache
prot_cache = ProtectionCache()


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ CONTENT DETECTION UTILITIES ◈◈◈
# ═══════════════════════════════════════════════════════════════

class ContentDetector:
    """
    ╔═══════════════════════════════════════════════════════╗
    ║   Detects links, Arabic/RTL, spam patterns, etc.     ║
    ╚═══════════════════════════════════════════════════════╝
    """

    # ── URL patterns ──
    URL_REGEX = re.compile(
        r'(https?://[^\s<>\"\']+|'
        r'www\.[^\s<>\"\']+|'
        r'[a-zA-Z0-9][-a-zA-Z0-9]*\.'
        r'(?:com|org|net|io|me|co|info|biz|xyz|tk|ml|ga|cf|gq|top|'
        r'online|site|website|space|fun|icu|buzz|club|live|store|'
        r'tech|dev|app|ru|uk|de|fr|in|cn|jp|br|au|ca|us|eu|tv|cc|'
        r'ws|mobi|tel|pro|name|aero|museum|coop|int|post|edu|gov|mil)'
        r'(?:/[^\s<>\"\']*)?)',
        re.IGNORECASE
    )

    TG_LINK_REGEX = re.compile(
        r'(t\.me/[^\s<>\"\']+|'
        r'telegram\.me/[^\s<>\"\']+|'
        r'telegram\.dog/[^\s<>\"\']+)',
        re.IGNORECASE
    )

    # ── Arabic / RTL characters ──
    ARABIC_REGEX = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF'
        r'\uFB50-\uFDCF\uFDF0-\uFDFF\uFE70-\uFEFF'
        r'\u0590-\u05FF]'
    )

    # ── Spam patterns ──
    EXCESSIVE_CAPS_THRESHOLD = 0.7
    EXCESSIVE_EMOJI_THRESHOLD = 10
    REPEATED_CHAR_REGEX = re.compile(r'(.)\1{9,}')
    REPEATED_WORD_REGEX = re.compile(r'\b(\w+)\b(?:\s+\1\b){4,}', re.IGNORECASE)

    @classmethod
    def contains_url(cls, text: str) -> bool:
        if not text:
            return False
        return bool(cls.URL_REGEX.search(text))

    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        if not text:
            return []
        return cls.URL_REGEX.findall(text)

    @classmethod
    def contains_tg_link(cls, text: str) -> bool:
        if not text:
            return False
        return bool(cls.TG_LINK_REGEX.search(text))

    @classmethod
    def contains_arabic(cls, text: str) -> bool:
        if not text:
            return False
        return bool(cls.ARABIC_REGEX.search(text))

    @classmethod
    def arabic_ratio(cls, text: str) -> float:
        if not text:
            return 0.0
        arabic_count = len(cls.ARABIC_REGEX.findall(text))
        total = len(text.strip())
        return arabic_count / max(total, 1)

    @classmethod
    def is_url_whitelisted(
        cls, url: str, whitelist: List[str]
    ) -> bool:
        url_lower = url.lower()
        for pattern in whitelist:
            pat = pattern.lower()
            if pat in url_lower or url_lower.endswith(pat):
                return True
        return False

    @classmethod
    def has_entity_urls(cls, message: Message) -> bool:
        if not message.entities:
            return False
        for entity in message.entities:
            if entity.type in (
                MessageEntityType.URL,
                MessageEntityType.TEXT_LINK,
            ):
                return True
        return False

    @classmethod
    def calculate_spam_score(cls, message: Message) -> int:
        """
        Calculate spam score for a message.
        Higher score = more likely spam.
        """
        score = 0
        text = message.text or message.caption or ""

        if not text:
            return 0

        # Excessive caps
        if len(text) > 10:
            upper_count = sum(1 for c in text if c.isupper())
            if upper_count / len(text) > cls.EXCESSIVE_CAPS_THRESHOLD:
                score += 2

        # Excessive length
        if len(text) > 2000:
            score += 2

        # Repeated characters
        if cls.REPEATED_CHAR_REGEX.search(text):
            score += 2

        # Repeated words
        if cls.REPEATED_WORD_REGEX.search(text):
            score += 2

        # Multiple URLs
        urls = cls.extract_urls(text)
        if len(urls) > 3:
            score += 3

        # Contains links
        if urls:
            score += 1

        # Multiple entities
        if message.entities and len(message.entities) > 10:
            score += 2

        # Forwarded
        if message.forward_date:
            score += 1

        return score

    @classmethod
    def check_message_entities_for_urls(
        cls, message: Message
    ) -> List[str]:
        """Extract URLs from message entities"""
        urls = []
        if not message.entities:
            return urls
        text = message.text or ""
        for entity in message.entities:
            if entity.type == MessageEntityType.URL:
                url = text[entity.offset:entity.offset + entity.length]
                urls.append(url)
            elif entity.type == MessageEntityType.TEXT_LINK:
                if entity.url:
                    urls.append(entity.url)
        return urls


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ PROTECTION ACTION EXECUTOR ◈◈◈
# ═══════════════════════════════════════════════════════════════

class ProtectionAction:
    """Execute protection actions with stylish notifications"""

    @staticmethod
    async def execute(
        bot: Bot,
        chat: Chat,
        user_id: int,
        user_name: str,
        action: str,
        duration: int = 3600,
        reason: str = "",
        delete_msg: bool = True,
        message: Optional[Message] = None,
        notify: bool = True,
        protection_type: str = "",
    ) -> None:
        """Execute a protection action"""
        try:
            # Delete the offending message
            if delete_msg and message:
                try:
                    await message.delete()
                except Exception:
                    pass

            action_text = ""

            if action == "delete":
                action_text = f"🗑️ {StyleFont.small_caps('message deleted')}"

            elif action == "warn":
                if hasattr(UserDB, 'add_warn'):
                    warn_num, warn_limit = await UserDB.add_warn(
                        chat.id, user_id, bot.id, reason
                    )
                    action_text = (
                        f"⚠️ {StyleFont.small_caps('warned')} "
                        f"({warn_num}/{warn_limit})"
                    )

            elif action == "mute":
                try:
                    await bot.restrict_chat_member(
                        chat.id, user_id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                    )
                    action_text = f"🔇 {StyleFont.small_caps('muted permanently')}"
                except Exception:
                    pass

            elif action == "tmute":
                try:
                    until = datetime.now(timezone.utc) + timedelta(
                        seconds=duration
                    )
                    await bot.restrict_chat_member(
                        chat.id, user_id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                        until_date=until,
                    )
                    dur_str = get_readable_time(duration)
                    action_text = (
                        f"🔇 {StyleFont.small_caps('muted for')} "
                        f"{dur_str}"
                    )
                except Exception:
                    pass

            elif action == "kick":
                try:
                    await bot.ban_chat_member(chat.id, user_id)
                    await asyncio.sleep(0.5)
                    await bot.unban_chat_member(
                        chat.id, user_id, only_if_banned=True
                    )
                    action_text = f"🦶 {StyleFont.small_caps('kicked')}"
                except Exception:
                    pass

            elif action == "ban":
                try:
                    await bot.ban_chat_member(chat.id, user_id)
                    action_text = f"🔨 {StyleFont.small_caps('banned')}"
                except Exception:
                    pass

            elif action == "tban":
                try:
                    until = datetime.now(timezone.utc) + timedelta(
                        seconds=duration
                    )
                    await bot.ban_chat_member(
                        chat.id, user_id, until_date=until
                    )
                    dur_str = get_readable_time(duration)
                    action_text = (
                        f"🔨 {StyleFont.small_caps('banned for')} "
                        f"{dur_str}"
                    )
                except Exception:
                    pass

            # Send notification
            if notify and action_text and action != "delete":
                prot_emoji = {
                    "flood": "🌊",
                    "spam": "🚫",
                    "link": "🔗",
                    "bot": "🤖",
                    "forward": "↩️",
                    "channel": "📢",
                    "arabic": "🔤",
                    "sticker": "🎭",
                    "gif": "🎞️",
                    "nsfw": "🔞",
                    "blacklist": "🚫",
                }.get(protection_type, "🛡️")

                prot_name = protection_type.replace("_", " ").title()

                text = (
                    f"{prot_emoji} "
                    f"{StyleFont.mixed_bold_smallcaps(f'Anti-{prot_name}')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('User')}: "
                    f"<a href='tg://user?id={user_id}'>"
                    f"{html_escape(user_name)}</a>\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                    f"{action_text}\n"
                )
                if reason:
                    text += (
                        f"{Symbols.STAR2} "
                        f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                        f"{StyleFont.small_caps(reason)}\n"
                    )
                text += (
                    f"{Symbols.divider(8)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                )

                try:
                    sent = await bot.send_message(
                        chat.id, text,
                        parse_mode=ParseMode.HTML,
                    )
                    asyncio.create_task(
                        _auto_delete_message(sent, 30)
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Protection action error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ BYPASS CHECK ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def _should_bypass(
    chat_id: int, user_id: int, bot: Bot,
    settings: Optional[Dict] = None
) -> bool:
    """Check if user should bypass protection"""
    if cache.is_owner(user_id) or cache.is_sudo(user_id):
        return True
    if cache.is_support(user_id):
        return True
    if await prot_cache.is_approved(chat_id, user_id):
        return True
    if await Permissions.is_user_admin(chat_id, user_id, bot):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ MAIN PROTECTION MESSAGE HANDLER ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def protection_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Main protection handler — runs on EVERY group message.
    Checks all anti-spam & protection rules in order:
    1. Anti-Flood
    2. Anti-Spam Score
    3. Anti-Link
    4. Anti-Forward
    5. Anti-Arabic
    6. Anti-Sticker Spam
    7. Anti-GIF Spam
    8. Blacklist Words
    """
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or not chat:
        return
    if user.is_bot or chat.type == ChatType.PRIVATE:
        return

    # Get settings (cached)
    settings = await prot_cache.get_settings(chat.id)
    if not settings:
        return

    # Quick bypass check
    if await _should_bypass(chat.id, user.id, context.bot, settings):
        return

    user_name = get_user_full_name(user)
    text = message.text or message.caption or ""

    # ═══ 1. ANTI-FLOOD ═══
    if settings.get("antiflood_enabled", False):
        limit = settings.get("antiflood_limit", 10)
        window = settings.get("antiflood_time_window", 45)

        if prot_cache.check_flood(chat.id, user.id, limit, window):
            action = settings.get("antiflood_action", "mute")
            duration = settings.get("antiflood_action_duration", 3600)

            prot_cache.reset_flood(chat.id, user.id)

            await ProtectionAction.execute(
                context.bot, chat, user.id, user_name,
                action, duration,
                reason=f"Sent {limit}+ msgs in {window}s",
                delete_msg=settings.get("antiflood_del_msg", True),
                message=message,
                protection_type="flood",
            )
            await ProtectionDB.increment_stat(
                chat.id, "total_flood_actions"
            )
            return

    # ═══ 2. ANTI-SPAM SCORE ═══
    if settings.get("antispam_enabled", False):
        score = ContentDetector.calculate_spam_score(message)
        if score > 0:
            total = prot_cache.add_spam_score(
                chat.id, user.id, score
            )
            threshold = settings.get("antispam_score_threshold", 5)

            if total >= threshold:
                action = settings.get("antispam_action", "mute")
                prot_cache.reset_spam_score(chat.id, user.id)

                await ProtectionAction.execute(
                    context.bot, chat, user.id, user_name,
                    action, 3600,
                    reason=f"Spam score {total}/{threshold}",
                    message=message,
                    protection_type="spam",
                )
                await ProtectionDB.increment_stat(
                    chat.id, "total_spam_actions"
                )
                return

    # ═══ 3. ANTI-LINK ═══
    if settings.get("antilink_enabled", False):
        has_url = (
            ContentDetector.contains_url(text)
            or ContentDetector.has_entity_urls(message)
        )

        if has_url:
            # Check if TG links allowed
            if settings.get("antilink_allow_tg_links", False):
                urls = ContentDetector.extract_urls(text)
                entity_urls = ContentDetector.check_message_entities_for_urls(
                    message
                )
                all_urls = urls + entity_urls
                non_tg = [
                    u for u in all_urls
                    if not any(
                        tg in u.lower()
                        for tg in ["t.me", "telegram.me", "telegram.dog"]
                    )
                ]
                if not non_tg:
                    has_url = False

            # Check whitelist
            if has_url:
                whitelist = await prot_cache.get_whitelist(chat.id)
                if whitelist:
                    urls = ContentDetector.extract_urls(text)
                    entity_urls = ContentDetector.check_message_entities_for_urls(
                        message
                    )
                    all_urls = urls + entity_urls
                    all_whitelisted = all(
                        ContentDetector.is_url_whitelisted(u, whitelist)
                        for u in all_urls
                    )
                    if all_whitelisted:
                        has_url = False

            if has_url:
                action = settings.get("antilink_action", "delete")

                await ProtectionAction.execute(
                    context.bot, chat, user.id, user_name,
                    action, 3600,
                    reason="Sent a link",
                    message=message,
                    protection_type="link",
                )
                await ProtectionDB.increment_stat(
                    chat.id, "total_link_deleted"
                )
                return

    # ═══ 4. ANTI-FORWARD ═══
    if settings.get("antiforward_enabled", False):
        if message.forward_date:
            should_delete = False

            if message.forward_from_chat and settings.get(
                "antiforward_from_channels", True
            ):
                should_delete = True
            elif message.forward_from:
                if message.forward_from.is_bot and settings.get(
                    "antiforward_from_bots", True
                ):
                    should_delete = True
                elif not message.forward_from.is_bot and settings.get(
                    "antiforward_from_users", False
                ):
                    should_delete = True

            if should_delete:
                action = settings.get("antiforward_action", "delete")
                await ProtectionAction.execute(
                    context.bot, chat, user.id, user_name,
                    action, 3600,
                    reason="Forwarded message",
                    message=message,
                    protection_type="forward",
                )
                await ProtectionDB.increment_stat(
                    chat.id, "total_forward_deleted"
                )
                return

    # ═══ 5. ANTI-ARABIC ═══
    if settings.get("antiarabic_enabled", False):
        if text and ContentDetector.contains_arabic(text):
            ratio = ContentDetector.arabic_ratio(text)
            if ratio > 0.3:
                action = settings.get("antiarabic_action", "delete")
                await ProtectionAction.execute(
                    context.bot, chat, user.id, user_name,
                    action, 3600,
                    reason="Arabic/RTL text",
                    message=message,
                    protection_type="arabic",
                )
                await ProtectionDB.increment_stat(
                    chat.id, "total_arabic_deleted"
                )
                return

    # ═══ 6. ANTI-STICKER SPAM ═══
    if settings.get("antisticker_enabled", False) and message.sticker:
        limit = settings.get("antisticker_limit", 5)
        window = settings.get("antisticker_time_window", 30)

        if prot_cache.check_sticker_spam(
            chat.id, user.id, limit, window
        ):
            action = settings.get("antisticker_action", "mute")
            await ProtectionAction.execute(
                context.bot, chat, user.id, user_name,
                action, 1800,
                reason=f"Sticker spam ({limit}+ in {window}s)",
                message=message,
                protection_type="sticker",
            )
            await ProtectionDB.increment_stat(
                chat.id, "total_sticker_actions"
            )
            return

    # ═══ 7. ANTI-GIF SPAM ═══
    if settings.get("antigif_enabled", False) and message.animation:
        limit = settings.get("antigif_limit", 5)
        window = settings.get("antigif_time_window", 30)

        if prot_cache.check_gif_spam(
            chat.id, user.id, limit, window
        ):
            action = settings.get("antigif_action", "mute")
            await ProtectionAction.execute(
                context.bot, chat, user.id, user_name,
                action, 1800,
                reason=f"GIF spam ({limit}+ in {window}s)",
                message=message,
                protection_type="gif",
            )
            await ProtectionDB.increment_stat(
                chat.id, "total_gif_actions"
            )
            return

    # ═══ 8. BLACKLIST WORDS ═══
    if text:
        bl_words = await prot_cache.get_blacklist(chat.id)
        if bl_words:
            text_lower = text.lower()
            matched = None
            for word in bl_words:
                if word in text_lower:
                    matched = word
                    break

            if matched:
                bl_settings = await ProtectionDB.get_blacklist_settings(
                    chat.id
                )
                action = bl_settings.get("bl_action", "delete")
                duration = bl_settings.get("bl_action_dur", 3600)

                await ProtectionAction.execute(
                    context.bot, chat, user.id, user_name,
                    action, duration,
                    reason=f"Blacklisted: {matched}",
                    message=message,
                    protection_type="blacklist",
                )
                await ProtectionDB.increment_stat(
                    chat.id, "total_blacklist_actions"
                )
                return


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ ANTI-BOT HANDLER (on new member) ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def antibot_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Detect and kick bots added to the group"""
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat or not message.new_chat_members:
        return

    settings = await prot_cache.get_settings(chat.id)
    if not settings.get("antibot_enabled", False):
        return

    for new_user in message.new_chat_members:
        if not new_user.is_bot:
            continue
        if new_user.id == context.bot.id:
            continue

        # Check who added
        adder = message.from_user
        if adder and await _should_bypass(
            chat.id, adder.id, context.bot
        ):
            continue

        action = settings.get("antibot_action", "kick")
        try:
            if action == "ban":
                await context.bot.ban_chat_member(chat.id, new_user.id)
            else:
                await context.bot.ban_chat_member(chat.id, new_user.id)
                await asyncio.sleep(0.5)
                await context.bot.unban_chat_member(
                    chat.id, new_user.id, only_if_banned=True
                )

            sent = await context.bot.send_message(
                chat.id,
                (
                    f"🤖 {StyleFont.mixed_bold_smallcaps('Anti-Bot')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Bot')}: "
                    f"@{new_user.username or new_user.first_name}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                    f"{'🔨 Banned' if action == 'ban' else '🦶 Kicked'}\n"
                    f"{Symbols.STAR2} "
                    f"{StyleFont.mixed_bold_smallcaps('Reason')}: "
                    f"{StyleFont.small_caps('unauthorized bot')}\n"
                    f"{Symbols.divider(8)}\n"
                    f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                    f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
                ),
                parse_mode=ParseMode.HTML,
            )
            asyncio.create_task(_auto_delete_message(sent, 30))
            await ProtectionDB.increment_stat(
                chat.id, "total_bot_kicked"
            )
        except Exception as e:
            logger.error(f"Anti-bot error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ ANTI-CHANNEL HANDLER ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def antichannel_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Ban channels that send messages as channel identity"""
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat:
        return
    if chat.type == ChatType.PRIVATE:
        return

    # Check if message is from a channel (sender_chat)
    if not message.sender_chat:
        return
    if message.sender_chat.type != ChatType.CHANNEL:
        return
    # Linked channel is OK
    if message.sender_chat.id == chat.id:
        return

    settings = await prot_cache.get_settings(chat.id)
    if not settings.get("antichannel_enabled", False):
        return

    channel = message.sender_chat

    try:
        await message.delete()
    except Exception:
        pass

    try:
        await context.bot.ban_chat_sender_chat(
            chat.id, channel.id
        )

        sent = await context.bot.send_message(
            chat.id,
            (
                f"📢 {StyleFont.mixed_bold_smallcaps('Anti-Channel')}\n"
                f"{Symbols.divider(8)}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Channel')}: "
                f"{html_escape(channel.title or str(channel.id))}\n"
                f"{Symbols.STAR2} "
                f"{StyleFont.mixed_bold_smallcaps('Action')}: "
                f"🔨 {StyleFont.small_caps('channel banned')}\n"
                f"{Symbols.divider(8)}\n"
                f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
                f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
            ),
            parse_mode=ParseMode.HTML,
        )
        asyncio.create_task(_auto_delete_message(sent, 30))
        await ProtectionDB.increment_stat(
            chat.id, "total_channel_banned"
        )
    except Exception as e:
        logger.error(f"Anti-channel error: {e}")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SETTINGS TEMPLATE ◈◈◈
# ═══════════════════════════════════════════════════════════════

class ProtectionTemplates:

    @staticmethod
    def settings_message(
        chat: Chat, settings: Dict[str, Any]
    ) -> str:
        def s(val: bool) -> str:
            return "✅" if val else "❌"

        return (
            f"🛡️ {StyleFont.mixed_bold_smallcaps('Protection Settings')} 🛡️\n"
            f"{Symbols.divider(5)}\n"
            f"\n"
            f"{Symbols.STAR2} "
            f"{StyleFont.mixed_bold_smallcaps('Chat')}: "
            f"{html_escape(chat.title or '')}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Anti-Spam')} "
            f"]{Symbols.BOX_H * 5}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 🌊 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Flood')}: "
            f"{s(settings.get('antiflood_enabled', False))} "
            f"({settings.get('antiflood_limit', 10)}/{settings.get('antiflood_time_window', 45)}s)\n"
            f"{Symbols.BOX_V} 🚫 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Spam')}: "
            f"{s(settings.get('antispam_enabled', False))}\n"
            f"{Symbols.BOX_V} 🔗 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Link')}: "
            f"{s(settings.get('antilink_enabled', False))}\n"
            f"{Symbols.BOX_V} 🤖 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Bot')}: "
            f"{s(settings.get('antibot_enabled', False))}\n"
            f"{Symbols.BOX_V} ↩️ "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Forward')}: "
            f"{s(settings.get('antiforward_enabled', False))}\n"
            f"{Symbols.BOX_V} 📢 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Channel')}: "
            f"{s(settings.get('antichannel_enabled', False))}\n"
            f"{Symbols.BOX_V} 🔤 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Arabic')}: "
            f"{s(settings.get('antiarabic_enabled', False))}\n"
            f"{Symbols.BOX_V} 🎭 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Sticker')}: "
            f"{s(settings.get('antisticker_enabled', False))} "
            f"({settings.get('antisticker_limit', 5)}/{settings.get('antisticker_time_window', 30)}s)\n"
            f"{Symbols.BOX_V} 🎞️ "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Gif')}: "
            f"{s(settings.get('antigif_enabled', False))} "
            f"({settings.get('antigif_limit', 5)}/{settings.get('antigif_time_window', 30)}s)\n"
            f"{Symbols.BOX_V} 🔞 "
            f"{StyleFont.mixed_bold_smallcaps('Anti-Nsfw')}: "
            f"{s(settings.get('antinsfw_enabled', False))}\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n"
            f"{Symbols.BOX_TL}{Symbols.BOX_H * 3}[ "
            f"{StyleFont.bold_sans('Stats')} "
            f"]{Symbols.BOX_H * 7}{Symbols.BOX_TR}\n"
            f"{Symbols.BOX_V} 🌊 {StyleFont.small_caps('flood')}: "
            f"<b>{settings.get('total_flood_actions', 0)}</b> │ "
            f"🔗 {StyleFont.small_caps('link')}: "
            f"<b>{settings.get('total_link_deleted', 0)}</b>\n"
            f"{Symbols.BOX_V} 🚫 {StyleFont.small_caps('bl')}: "
            f"<b>{settings.get('total_blacklist_actions', 0)}</b> │ "
            f"📢 {StyleFont.small_caps('chan')}: "
            f"<b>{settings.get('total_channel_banned', 0)}</b>\n"
            f"{Symbols.BOX_BL}{Symbols.BOX_H * 22}{Symbols.BOX_BR}\n"
            f"\n{Symbols.divider(5)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ GENERIC ON/OFF TOGGLE HELPER ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def _handle_toggle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    setting_key: str,
    feature_name: str,
    feature_emoji: str,
) -> None:
    """Generic toggle handler for protection features"""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if context.args:
        arg = context.args[0].lower()
        new_val = arg in ("on", "yes", "true", "1")

        await ProtectionDB.update_setting(chat.id, setting_key, new_val)
        prot_cache.invalidate_settings(chat.id)

        status = "✅ ᴏɴ" if new_val else "❌ ᴏғғ"
        await message.reply_text(
            f"{feature_emoji} "
            f"{StyleFont.mixed_bold_smallcaps(feature_name)}: "
            f"{status}",
            parse_mode=ParseMode.HTML,
        )
        return

    settings = await prot_cache.get_settings(chat.id)
    status = "✅ ᴏɴ" if settings.get(setting_key, False) else "❌ ᴏғғ"
    await message.reply_text(
        f"{feature_emoji} "
        f"{StyleFont.mixed_bold_smallcaps(feature_name)}: {status}\n"
        f"{Symbols.BULLET} "
        f"{StyleFont.small_caps('use')} <code>/{feature_name.lower().replace(' ','')} on/off</code>",
        parse_mode=ParseMode.HTML,
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 5 — COMMAND HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_protection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/protection — View all protection settings panel."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    settings = await prot_cache.get_settings(chat.id)
    text = ProtectionTemplates.settings_message(chat, settings)
    await message.reply_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )

# ── Anti-Flood ──

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antiflood(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /antiflood on|off — Toggle anti-flood.
    /antiflood set <limit> <seconds> — Configure.
    /antiflood action <action> — Set action.
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if not context.args:
        settings = await prot_cache.get_settings(chat.id)
        on = settings.get("antiflood_enabled", False)
        lim = settings.get("antiflood_limit", 10)
        win = settings.get("antiflood_time_window", 45)
        act = settings.get("antiflood_action", "mute")
        await message.reply_text(
            f"🌊 {StyleFont.mixed_bold_smallcaps('Anti-Flood')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Status')}: "
            f"{'✅ ᴏɴ' if on else '❌ ᴏғғ'}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Limit')}: "
            f"<b>{lim}</b> msgs in <b>{win}s</b>\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Action')}: "
            f"<b>{act}</b>\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
        return

    arg = context.args[0].lower()
    if arg in ("on", "off", "yes", "no", "true", "false", "1", "0"):
        new_val = arg in ("on", "yes", "true", "1")
        await ProtectionDB.update_setting(
            chat.id, "antiflood_enabled", new_val
        )
        prot_cache.invalidate_settings(chat.id)
        st = "✅ ᴏɴ" if new_val else "❌ ᴏғғ"
        await message.reply_text(
            f"🌊 {StyleFont.mixed_bold_smallcaps('Anti-Flood')}: {st}",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "set" and len(context.args) >= 3:
        try:
            lim = max(3, min(int(context.args[1]), 100))
            win = max(5, min(int(context.args[2]), 300))
            await ProtectionDB.update_setting(
                chat.id, "antiflood_limit", lim
            )
            await ProtectionDB.update_setting(
                chat.id, "antiflood_time_window", win
            )
            prot_cache.invalidate_settings(chat.id)
            await message.reply_text(
                f"🌊 {StyleFont.mixed_bold_smallcaps('Flood Limit')}: "
                f"<b>{lim}</b> msgs in <b>{win}s</b>",
                parse_mode=ParseMode.HTML,
            )
        except ValueError:
            await message.reply_text(
                f"{Symbols.CROSS3} "
                f"{StyleFont.small_caps('usage')}: "
                f"<code>/antiflood set 10 45</code>",
                parse_mode=ParseMode.HTML,
            )
    elif arg == "action" and len(context.args) >= 2:
        act = context.args[1].lower()
        if act in ("mute", "tmute", "ban", "tban", "kick", "warn"):
            await ProtectionDB.update_setting(
                chat.id, "antiflood_action", act
            )
            prot_cache.invalidate_settings(chat.id)
            await message.reply_text(
                f"🌊 {StyleFont.mixed_bold_smallcaps('Flood Action')}: "
                f"<b>{act}</b>",
                parse_mode=ParseMode.HTML,
            )

# ── Anti-Spam ──

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antispam(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antispam on|off — Toggle anti-spam detection."""
    await _handle_toggle(
        update, context, "antispam_enabled",
        "Anti-Spam", "🚫"
    )

# ── Anti-Link ──

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antilink(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /antilink on|off — Toggle anti-link.
    /antilink action <action> — Set action.
    /antilink tglinks on|off — Allow Telegram links.
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if not context.args:
        settings = await prot_cache.get_settings(chat.id)
        on = settings.get("antilink_enabled", False)
        act = settings.get("antilink_action", "delete")
        tg = settings.get("antilink_allow_tg_links", False)
        await message.reply_text(
            f"🔗 {StyleFont.mixed_bold_smallcaps('Anti-Link')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Status')}: "
            f"{'✅ ᴏɴ' if on else '❌ ᴏғғ'}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Action')}: "
            f"<b>{act}</b>\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Tg Links')}: "
            f"{'✅ Allowed' if tg else '❌ Blocked'}\n"
            f"{Symbols.divider(8)}\n"
            f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
            f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
            parse_mode=ParseMode.HTML,
        )
        return

    arg = context.args[0].lower()
    if arg in ("on", "off", "yes", "no", "true", "false", "1", "0"):
        new_val = arg in ("on", "yes", "true", "1")
        await ProtectionDB.update_setting(
            chat.id, "antilink_enabled", new_val
        )
        prot_cache.invalidate_settings(chat.id)
        st = "✅ ᴏɴ" if new_val else "❌ ᴏғғ"
        await message.reply_text(
            f"🔗 {StyleFont.mixed_bold_smallcaps('Anti-Link')}: {st}",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "action" and len(context.args) >= 2:
        act = context.args[1].lower()
        if act in ("delete", "warn", "mute", "kick", "ban"):
            await ProtectionDB.update_setting(
                chat.id, "antilink_action", act
            )
            prot_cache.invalidate_settings(chat.id)
            await message.reply_text(
                f"🔗 {StyleFont.mixed_bold_smallcaps('Link Action')}: <b>{act}</b>",
                parse_mode=ParseMode.HTML,
            )
    elif arg == "tglinks" and len(context.args) >= 2:
        new_val = context.args[1].lower() in ("on", "yes", "true", "1")
        await ProtectionDB.update_setting(
            chat.id, "antilink_allow_tg_links", new_val
        )
        prot_cache.invalidate_settings(chat.id)
        st = "✅ Allowed" if new_val else "❌ Blocked"
        await message.reply_text(
            f"🔗 {StyleFont.mixed_bold_smallcaps('Tg Links')}: {st}",
            parse_mode=ParseMode.HTML,
        )

# ── Anti-Bot ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antibot(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antibot on|off"""
    await _handle_toggle(
        update, context, "antibot_enabled", "Anti-Bot", "🤖"
    )

# ── Anti-Forward ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antiforward(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antiforward on|off"""
    await _handle_toggle(
        update, context, "antiforward_enabled", "Anti-Forward", "↩️"
    )

# ── Anti-Channel ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antichannel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antichannel on|off"""
    await _handle_toggle(
        update, context, "antichannel_enabled", "Anti-Channel", "📢"
    )

# ── Anti-Arabic ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antiarabic(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antiarabic on|off"""
    await _handle_toggle(
        update, context, "antiarabic_enabled", "Anti-Arabic", "🔤"
    )

# ── Anti-Sticker ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antisticker(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /antisticker on|off
    /antisticker set <limit> <seconds>
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    if not context.args:
        settings = await prot_cache.get_settings(chat.id)
        await message.reply_text(
            f"🎭 {StyleFont.mixed_bold_smallcaps('Anti-Sticker')}: "
            f"{'✅ ᴏɴ' if settings.get('antisticker_enabled') else '❌ ᴏғғ'} "
            f"({settings.get('antisticker_limit', 5)}/{settings.get('antisticker_time_window', 30)}s)",
            parse_mode=ParseMode.HTML,
        )
        return
    arg = context.args[0].lower()
    if arg in ("on", "off", "yes", "no", "true", "false", "1", "0"):
        new_val = arg in ("on", "yes", "true", "1")
        await ProtectionDB.update_setting(chat.id, "antisticker_enabled", new_val)
        prot_cache.invalidate_settings(chat.id)
        await message.reply_text(
            f"🎭 {StyleFont.mixed_bold_smallcaps('Anti-Sticker')}: "
            f"{'✅ ᴏɴ' if new_val else '❌ ᴏғғ'}",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "set" and len(context.args) >= 3:
        try:
            lim = max(2, min(int(context.args[1]), 50))
            win = max(5, min(int(context.args[2]), 120))
            await ProtectionDB.update_setting(chat.id, "antisticker_limit", lim)
            await ProtectionDB.update_setting(chat.id, "antisticker_time_window", win)
            prot_cache.invalidate_settings(chat.id)
            await message.reply_text(
                f"🎭 {StyleFont.mixed_bold_smallcaps('Sticker Limit')}: "
                f"<b>{lim}</b> in <b>{win}s</b>",
                parse_mode=ParseMode.HTML,
            )
        except ValueError:
            pass

# ── Anti-GIF ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antigif(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antigif on|off | /antigif set <limit> <seconds>"""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    if not context.args:
        settings = await prot_cache.get_settings(chat.id)
        await message.reply_text(
            f"🎞️ {StyleFont.mixed_bold_smallcaps('Anti-Gif')}: "
            f"{'✅ ᴏɴ' if settings.get('antigif_enabled') else '❌ ᴏғғ'} "
            f"({settings.get('antigif_limit', 5)}/{settings.get('antigif_time_window', 30)}s)",
            parse_mode=ParseMode.HTML,
        )
        return
    arg = context.args[0].lower()
    if arg in ("on", "off", "yes", "no", "true", "false", "1", "0"):
        new_val = arg in ("on", "yes", "true", "1")
        await ProtectionDB.update_setting(chat.id, "antigif_enabled", new_val)
        prot_cache.invalidate_settings(chat.id)
        await message.reply_text(
            f"🎞️ {StyleFont.mixed_bold_smallcaps('Anti-Gif')}: "
            f"{'✅ ᴏɴ' if new_val else '❌ ᴏғғ'}",
            parse_mode=ParseMode.HTML,
        )
    elif arg == "set" and len(context.args) >= 3:
        try:
            lim = max(2, min(int(context.args[1]), 50))
            win = max(5, min(int(context.args[2]), 120))
            await ProtectionDB.update_setting(chat.id, "antigif_limit", lim)
            await ProtectionDB.update_setting(chat.id, "antigif_time_window", win)
            prot_cache.invalidate_settings(chat.id)
            await message.reply_text(
                f"🎞️ {StyleFont.mixed_bold_smallcaps('Gif Limit')}: "
                f"<b>{lim}</b> in <b>{win}s</b>",
                parse_mode=ParseMode.HTML,
            )
        except ValueError:
            pass

# ── Anti-NSFW ──
@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(3.0)
async def cmd_antinsfw(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/antinsfw on|off"""
    await _handle_toggle(
        update, context, "antinsfw_enabled", "Anti-Nsfw", "🔞"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ BLACKLIST COMMANDS ◈◈◈
# ═══════════════════════════════════════════════════════════════

@track_command
@group_only
@cooldown(3.0)
@check_disabled
async def cmd_blacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/blacklist — List all blacklisted words."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    words = await ProtectionDB.get_blacklist_words(chat.id)
    bl_settings = await ProtectionDB.get_blacklist_settings(chat.id)

    if not words:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No blacklisted words')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('use /addblacklist to add')}",
            parse_mode=ParseMode.HTML,
        )
        return

    word_list = "\n".join(
        f"  {Symbols.ARROW_TRI} <code>{html_escape(w)}</code>"
        for w in words
    )

    await message.reply_text(
        f"🚫 {StyleFont.mixed_bold_smallcaps('Blacklisted Words')} 🚫\n"
        f"{Symbols.divider(6)}\n"
        f"\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Action')}: "
        f"<b>{bl_settings.get('bl_action', 'delete')}</b>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Total')}: "
        f"<b>{len(words)}</b>\n"
        f"\n"
        f"{word_list}\n"
        f"\n{Symbols.divider(6)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )

@track_command
@group_only
@admin_only
@cooldown(2.0)
async def cmd_addblacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/addblacklist <word> — Add word(s) to blacklist."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    if not chat or not user or not message:
        return
    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide word(s)')}!\n"
            f"{Symbols.BULLET} <code>/addblacklist word1 word2</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    added = []
    for word in context.args:
        word = word.lower().strip()
        if len(word) < 2:
            continue
        success = await ProtectionDB.add_blacklist_word(
            chat.id, word, user.id
        )
        if success:
            added.append(word)

    prot_cache.invalidate_blacklist(chat.id)

    if added:
        word_list = ", ".join(f"<code>{w}</code>" for w in added)
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Added To Blacklist')}:\n"
            f"{word_list}",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No new words added')}",
            parse_mode=ParseMode.HTML,
        )

@track_command
@group_only
@admin_only
@cooldown(2.0)
async def cmd_rmblacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/rmblacklist <word> — Remove from blacklist."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide word(s)')}!",
            parse_mode=ParseMode.HTML,
        )
        return

    removed = []
    for word in context.args:
        if await ProtectionDB.remove_blacklist_word(chat.id, word):
            removed.append(word)

    prot_cache.invalidate_blacklist(chat.id)

    if removed:
        word_list = ", ".join(f"<code>{w}</code>" for w in removed)
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Removed From Blacklist')}:\n"
            f"{word_list}",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Words not found in blacklist')}",
            parse_mode=ParseMode.HTML,
        )

@track_command
@group_only
@admin_only
@cooldown(5.0)
async def cmd_clearblacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/clearblacklist — Remove all blacklisted words."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    count = await ProtectionDB.clear_all_blacklist(chat.id)
    prot_cache.invalidate_blacklist(chat.id)
    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('Blacklist Cleared')}! "
        f"({count} {StyleFont.small_caps('words removed')})",
        parse_mode=ParseMode.HTML,
    )

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_blaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/blaction <action> — Set blacklist action."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    if not context.args:
        bl_settings = await ProtectionDB.get_blacklist_settings(chat.id)
        await message.reply_text(
            f"🚫 {StyleFont.mixed_bold_smallcaps('Blacklist Action')}: "
            f"<b>{bl_settings.get('bl_action', 'delete')}</b>\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('options')}: "
            f"delete, warn, mute, kick, ban",
            parse_mode=ParseMode.HTML,
        )
        return
    act = context.args[0].lower()
    if act in ("delete", "warn", "mute", "kick", "ban"):
        await ProtectionDB.update_blacklist_setting(
            chat.id, "bl_action", act
        )
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Blacklist Action')}: "
            f"<b>{act}</b>",
            parse_mode=ParseMode.HTML,
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ WHITELIST URL COMMANDS ◈◈◈
# ═══════════════════════════════════════════════════════════════

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_whitelist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/whitelist — List whitelisted URLs."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    urls = await ProtectionDB.get_whitelist_urls(chat.id)
    if not urls:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No whitelisted urls')}!\n"
            f"{Symbols.BULLET} "
            f"{StyleFont.small_caps('use /addwhitelist <domain>')}",
            parse_mode=ParseMode.HTML,
        )
        return
    url_list = "\n".join(
        f"  {Symbols.ARROW_TRI} <code>{html_escape(u)}</code>"
        for u in urls
    )
    await message.reply_text(
        f"✅ {StyleFont.mixed_bold_smallcaps('Whitelisted Urls')}\n"
        f"{Symbols.divider(6)}\n"
        f"{url_list}\n"
        f"{Symbols.divider(6)}\n"
        f"{Symbols.BULLET} {StyleFont.small_caps('total')}: <b>{len(urls)}</b>\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )

@track_command
@group_only
@admin_only
@cooldown(2.0)
async def cmd_addwhitelist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/addwhitelist <domain> — Whitelist a URL domain."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    if not chat or not user or not message:
        return
    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide domain')}!\n"
            f"{Symbols.BULLET} <code>/addwhitelist youtube.com</code>",
            parse_mode=ParseMode.HTML,
        )
        return
    added = []
    for url in context.args:
        if await ProtectionDB.add_whitelist_url(chat.id, url, user.id):
            added.append(url)
    prot_cache.invalidate_whitelist(chat.id)
    if added:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Whitelisted')}: "
            f"{', '.join(f'<code>{u}</code>' for u in added)}",
            parse_mode=ParseMode.HTML,
        )

@track_command
@group_only
@admin_only
@cooldown(2.0)
async def cmd_rmwhitelist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/rmwhitelist <domain> — Remove from whitelist."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    if not context.args:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Provide domain')}!",
            parse_mode=ParseMode.HTML,
        )
        return
    removed = []
    for url in context.args:
        if await ProtectionDB.remove_whitelist_url(chat.id, url):
            removed.append(url)
    prot_cache.invalidate_whitelist(chat.id)
    if removed:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Removed')}: "
            f"{', '.join(f'<code>{u}</code>' for u in removed)}",
            parse_mode=ParseMode.HTML,
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SLOWMODE CONTROL ◈◈◈
# ═══════════════════════════════════════════════════════════════

@track_command
@group_only
@admin_only
@bot_admin_required
@cooldown(5.0)
async def cmd_slowmode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    /slowmode <seconds> — Set Telegram slowmode.
    /slowmode off — Disable slowmode.
    Values: 0 (off), 10, 30, 60, 300, 900, 3600
    """
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return

    if not context.args:
        try:
            chat_info = await context.bot.get_chat(chat.id)
            current = chat_info.slow_mode_delay or 0
        except Exception:
            current = 0
        await message.reply_text(
            f"🐢 {StyleFont.mixed_bold_smallcaps('Slowmode')}\n"
            f"{Symbols.divider(8)}\n"
            f"{Symbols.STAR2} {StyleFont.mixed_bold_smallcaps('Current')}: "
            f"<b>{get_readable_time(current) if current else 'OFF'}</b>\n"
            f"{Symbols.BULLET} {StyleFont.small_caps('usage')}: "
            f"<code>/slowmode 10</code> or <code>/slowmode off</code>\n"
            f"{Symbols.BULLET} {StyleFont.small_caps('valid')}: "
            f"0, 10, 30, 60, 300, 900, 3600",
            parse_mode=ParseMode.HTML,
        )
        return

    arg = context.args[0].lower()
    if arg in ("off", "0", "disable"):
        seconds = 0
    else:
        try:
            seconds = int(arg)
        except ValueError:
            parsed = parse_time_arg(arg)
            seconds = parsed if parsed else 0

    valid_values = [0, 10, 30, 60, 300, 900, 3600]
    if seconds not in valid_values:
        closest = min(valid_values, key=lambda x: abs(x - seconds))
        seconds = closest

    try:
        await context.bot.set_chat_slow_mode_delay(chat.id, seconds)
    except BadRequest as e:
        await message.reply_text(
            f"{Symbols.CROSS3} "
            f"{StyleFont.mixed_bold_smallcaps('Failed')}: "
            f"<code>{html_escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if seconds == 0:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Slowmode Disabled')}! 🐇",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('Slowmode Set')}: "
            f"<b>{get_readable_time(seconds)}</b> 🐢",
            parse_mode=ParseMode.HTML,
        )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ APPROVE / UNAPPROVE COMMANDS ◈◈◈
# ═══════════════════════════════════════════════════════════════

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_approve(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/approve — Approve user to bypass all protections."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    if not chat or not user or not message:
        return
    target_id, target_name, _ = await _get_target_user(message, context)
    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return
    await ProtectionDB.approve_user(chat.id, target_id, user.id)
    prot_cache.invalidate_approved(chat.id)
    await message.reply_text(
        f"{Symbols.CHECK2} "
        f"{StyleFont.mixed_bold_smallcaps('User Approved')}\n"
        f"{Symbols.divider(8)}\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('User')}: "
        f"<a href='tg://user?id={target_id}'>"
        f"{html_escape(target_name)}</a>\n"
        f"{Symbols.STAR2} "
        f"{StyleFont.mixed_bold_smallcaps('Bypasses')}: "
        f"{StyleFont.small_caps('all protections')}\n"
        f"{Symbols.divider(8)}\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}",
        parse_mode=ParseMode.HTML,
    )

@track_command
@group_only
@admin_only
@cooldown(3.0)
async def cmd_unapprove(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/unapprove — Remove approval."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    target_id, target_name, _ = await _get_target_user(message, context)
    if not target_id:
        await message.reply_text(
            _no_target_msg(), parse_mode=ParseMode.HTML
        )
        return
    removed = await ProtectionDB.unapprove_user(chat.id, target_id)
    prot_cache.invalidate_approved(chat.id)
    if removed:
        await message.reply_text(
            f"{Symbols.CHECK2} "
            f"{StyleFont.mixed_bold_smallcaps('User Unapproved')}: "
            f"<a href='tg://user?id={target_id}'>"
            f"{html_escape(target_name)}</a>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('User was not approved')}",
            parse_mode=ParseMode.HTML,
        )

@track_command
@group_only
@admin_only
@cooldown(5.0)
async def cmd_approved(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/approved — List approved users."""
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    approved = await ProtectionDB.get_approved_users(chat.id)
    if not approved:
        await message.reply_text(
            f"{Symbols.INFO} "
            f"{StyleFont.mixed_bold_smallcaps('No approved users')}",
            parse_mode=ParseMode.HTML,
        )
        return

    text = (
        f"✅ {StyleFont.mixed_bold_smallcaps('Approved Users')} ✅\n"
        f"{Symbols.divider(6)}\n\n"
    )
    for i, a in enumerate(approved, 1):
        uid = a["user_id"]
        try:
            u = await context.bot.get_chat(uid)
            name = u.first_name or str(uid)
        except Exception:
            name = str(uid)
        text += (
            f" {Symbols.ARROW_TRI} "
            f"<a href='tg://user?id={uid}'>"
            f"{html_escape(name)}</a> "
            f"[<code>{uid}</code>]\n"
        )

    text += (
        f"\n{Symbols.divider(6)}\n"
        f"{Symbols.BULLET} {StyleFont.small_caps('total')}: <b>{len(approved)}</b>\n"
        f"{StyleFont.mixed_bold_smallcaps('Powered By')}: "
        f"{Symbols.LBRACKET2} {BOT_NAME} {Symbols.RBRACKET2}"
    )
    await message.reply_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=KeyboardBuilder.close_keyboard(),
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 5 — POST INIT ◈◈◈
# ═══════════════════════════════════════════════════════════════

async def section5_post_init(application: Application) -> None:
    await ProtectionDB.create_tables()
    logger.info("✅ Section 5 (Anti-Spam & Protection) initialized!")


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ SECTION 5 — REGISTER ALL HANDLERS ◈◈◈
# ═══════════════════════════════════════════════════════════════

def register_section5_handlers(application: Application) -> None:
    """Register all Section 5 handlers"""

    # ── Protection message handler (highest priority) ──
    application.add_handler(
        MessageHandler(
            (filters.TEXT | filters.Sticker.ALL | filters.ANIMATION
             | filters.PHOTO | filters.VIDEO | filters.Document.ALL
             | filters.FORWARDED | filters.VIA_BOT | filters.CAPTION)
            & filters.ChatType.GROUPS
            & ~filters.COMMAND
            & ~filters.StatusUpdate.ALL,
            protection_message_handler,
        ),
        group=2,
    )

    # ── Anti-bot (on new members) ──
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            antibot_handler,
        ),
        group=0,  # Before welcome handler
    )

    # ── Anti-channel handler ──
    application.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.SenderChat.CHANNEL,
            antichannel_handler,
        ),
        group=2,
    )

    # ── Admin commands ──
    application.add_handler(CommandHandler("protection", cmd_protection))
    application.add_handler(CommandHandler("antiflood", cmd_antiflood))
    application.add_handler(CommandHandler("antispam", cmd_antispam))
    application.add_handler(CommandHandler("antilink", cmd_antilink))
    application.add_handler(CommandHandler("antibot", cmd_antibot))
    application.add_handler(CommandHandler("antiforward", cmd_antiforward))
    application.add_handler(CommandHandler("antichannel", cmd_antichannel))
    application.add_handler(CommandHandler("antiarabic", cmd_antiarabic))
    application.add_handler(CommandHandler("antisticker", cmd_antisticker))
    application.add_handler(CommandHandler("antigif", cmd_antigif))
    application.add_handler(CommandHandler("antinsfw", cmd_antinsfw))
    application.add_handler(CommandHandler("slowmode", cmd_slowmode))

    # ── Blacklist commands ──
    application.add_handler(CommandHandler("blacklist", cmd_blacklist))
    application.add_handler(CommandHandler("addblacklist", cmd_addblacklist))
    application.add_handler(CommandHandler("rmblacklist", cmd_rmblacklist))
    application.add_handler(CommandHandler("clearblacklist", cmd_clearblacklist))
    application.add_handler(CommandHandler("blaction", cmd_blaction))

    # ── Whitelist commands ──
    application.add_handler(CommandHandler("whitelist", cmd_whitelist))
    application.add_handler(CommandHandler("addwhitelist", cmd_addwhitelist))
    application.add_handler(CommandHandler("rmwhitelist", cmd_rmwhitelist))

    # ── Approve commands ──
    application.add_handler(CommandHandler("approve", cmd_approve))
    application.add_handler(CommandHandler("unapprove", cmd_unapprove))
    application.add_handler(CommandHandler("approved", cmd_approved))

    logger.info(
        "✅ Section 5 handlers registered: "
        "Anti-Spam & Protection (24 commands + 3 event handlers)"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈ INTEGRATION ◈◈◈
# ═══════════════════════════════════════════════════════════════
#
#  1. In post_init():
#         await section5_post_init(application)
#
#  2. In register_handlers():
#         register_section5_handlers(application)
#
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# SECTION 6: FILTERS & NOTES SYSTEM
# ═══════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.1 — DATABASE TABLES FOR FILTERS & NOTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_filters_notes_tables():
    """Create all database tables for Filters & Notes system"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # ╔══════════════════════════════════════╗
        # ║   FILTERS TABLE                       ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filters (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                reply_text TEXT,
                reply_markup TEXT,
                media_type VARCHAR(50),
                media_file_id TEXT,
                media_caption TEXT,
                filter_type VARCHAR(20) DEFAULT 'text',
                added_by BIGINT,
                added_by_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                match_type VARCHAR(20) DEFAULT 'contains',
                case_sensitive BOOLEAN DEFAULT FALSE,
                UNIQUE(chat_id, keyword)
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   FILTER BUTTONS TABLE                ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filter_buttons (
                id SERIAL PRIMARY KEY,
                filter_id INTEGER REFERENCES filters(id) ON DELETE CASCADE,
                chat_id BIGINT NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                button_text VARCHAR(255) NOT NULL,
                button_url TEXT NOT NULL,
                button_row INTEGER DEFAULT 0,
                button_col INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   NOTES TABLE                         ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                note_name VARCHAR(255) NOT NULL,
                note_text TEXT,
                note_markup TEXT,
                media_type VARCHAR(50),
                media_file_id TEXT,
                media_caption TEXT,
                note_type VARCHAR(20) DEFAULT 'text',
                is_private BOOLEAN DEFAULT FALSE,
                added_by BIGINT,
                added_by_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                usage_count INTEGER DEFAULT 0,
                UNIQUE(chat_id, note_name)
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   NOTE BUTTONS TABLE                  ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS note_buttons (
                id SERIAL PRIMARY KEY,
                note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
                chat_id BIGINT NOT NULL,
                note_name VARCHAR(255) NOT NULL,
                button_text VARCHAR(255) NOT NULL,
                button_url TEXT NOT NULL,
                button_row INTEGER DEFAULT 0,
                button_col INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   PRIVATE NOTES SETTINGS TABLE        ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS private_notes_settings (
                chat_id BIGINT PRIMARY KEY,
                is_private BOOLEAN DEFAULT FALSE,
                updated_by BIGINT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   FILTER STATS TABLE                  ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filter_stats (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                triggered_by BIGINT,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ╔══════════════════════════════════════╗
        # ║   NOTE STATS TABLE                    ║
        # ╚══════════════════════════════════════╝
        cur.execute("""
            CREATE TABLE IF NOT EXISTS note_stats (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                note_name VARCHAR(255) NOT NULL,
                accessed_by BIGINT,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_type VARCHAR(20) DEFAULT 'public'
            );
        """)

        # ━━━ Create Indexes for Performance ━━━
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_filters_chat_id 
            ON filters(chat_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_filters_keyword 
            ON filters(chat_id, keyword);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_chat_id 
            ON notes(chat_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_notes_name 
            ON notes(chat_id, note_name);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_filter_stats_chat 
            ON filter_stats(chat_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_note_stats_chat 
            ON note_stats(chat_id);
        """)

        conn.commit()
        logger.info("✅ Filters & Notes tables created successfully!")
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creating Filters & Notes tables: {e}")
    finally:
        cur.close()
        conn.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.2 — FILTER DATABASE OPERATIONS (CRUD)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FilterDB:
    """Complete database operations for Filters system"""

    @staticmethod
    def add_filter(chat_id, keyword, reply_text, added_by, 
                   added_by_name, media_type=None, media_file_id=None,
                   media_caption=None, filter_type='text', 
                   match_type='contains', case_sensitive=False):
        """Add or update a filter in the database"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            keyword_lower = keyword.lower() if not case_sensitive else keyword
            cur.execute("""
                INSERT INTO filters 
                    (chat_id, keyword, reply_text, added_by, added_by_name,
                     media_type, media_file_id, media_caption, filter_type,
                     match_type, case_sensitive, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP)
                ON CONFLICT (chat_id, keyword)
                DO UPDATE SET
                    reply_text = EXCLUDED.reply_text,
                    added_by = EXCLUDED.added_by,
                    added_by_name = EXCLUDED.added_by_name,
                    media_type = EXCLUDED.media_type,
                    media_file_id = EXCLUDED.media_file_id,
                    media_caption = EXCLUDED.media_caption,
                    filter_type = EXCLUDED.filter_type,
                    match_type = EXCLUDED.match_type,
                    case_sensitive = EXCLUDED.case_sensitive,
                    updated_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
                RETURNING id;
            """, (chat_id, keyword_lower, reply_text, added_by, 
                  added_by_name, media_type, media_file_id, 
                  media_caption, filter_type, match_type, case_sensitive))
            
            filter_id = cur.fetchone()[0]
            conn.commit()
            return filter_id
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error adding filter: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def add_filter_buttons(filter_id, chat_id, keyword, buttons_data):
        """
        Add buttons to a filter
        buttons_data format: [{"text": "Button", "url": "https://...", "row": 0, "col": 0}]
        """
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # First remove old buttons for this filter
            cur.execute("""
                DELETE FROM filter_buttons 
                WHERE filter_id = %s AND chat_id = %s;
            """, (filter_id, chat_id))

            # Insert new buttons
            for btn in buttons_data:
                cur.execute("""
                    INSERT INTO filter_buttons 
                        (filter_id, chat_id, keyword, button_text, 
                         button_url, button_row, button_col)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (filter_id, chat_id, keyword.lower(), 
                      btn['text'], btn['url'], 
                      btn.get('row', 0), btn.get('col', 0)))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error adding filter buttons: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_filter(chat_id, keyword):
        """Get a specific filter by keyword"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, chat_id, keyword, reply_text, reply_markup,
                       media_type, media_file_id, media_caption, 
                       filter_type, added_by, added_by_name, 
                       created_at, match_type, case_sensitive
                FROM filters 
                WHERE chat_id = %s AND keyword = %s AND is_active = TRUE;
            """, (chat_id, keyword.lower()))
            result = cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'chat_id': result[1],
                    'keyword': result[2],
                    'reply_text': result[3],
                    'reply_markup': result[4],
                    'media_type': result[5],
                    'media_file_id': result[6],
                    'media_caption': result[7],
                    'filter_type': result[8],
                    'added_by': result[9],
                    'added_by_name': result[10],
                    'created_at': result[11],
                    'match_type': result[12],
                    'case_sensitive': result[13]
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error getting filter: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_filter_buttons(filter_id, chat_id):
        """Get all buttons for a specific filter"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT button_text, button_url, button_row, button_col
                FROM filter_buttons 
                WHERE filter_id = %s AND chat_id = %s
                ORDER BY button_row, button_col;
            """, (filter_id, chat_id))
            results = cur.fetchall()
            buttons = []
            for row in results:
                buttons.append({
                    'text': row[0],
                    'url': row[1],
                    'row': row[2],
                    'col': row[3]
                })
            return buttons
        except Exception as e:
            logger.error(f"❌ Error getting filter buttons: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_filters(chat_id):
        """Get all active filters for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, keyword, filter_type, added_by_name, 
                       created_at, media_type, match_type
                FROM filters 
                WHERE chat_id = %s AND is_active = TRUE
                ORDER BY keyword ASC;
            """, (chat_id,))
            results = cur.fetchall()
            filters_list = []
            for row in results:
                filters_list.append({
                    'id': row[0],
                    'keyword': row[1],
                    'filter_type': row[2],
                    'added_by_name': row[3],
                    'created_at': row[4],
                    'media_type': row[5],
                    'match_type': row[6]
                })
            return filters_list
        except Exception as e:
            logger.error(f"❌ Error getting all filters: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_filter_keywords(chat_id):
        """Get only keywords for matching (performance optimized)"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT keyword, match_type, case_sensitive 
                FROM filters 
                WHERE chat_id = %s AND is_active = TRUE;
            """, (chat_id,))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ Error getting filter keywords: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_filter(chat_id, keyword):
        """Delete (deactivate) a filter"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE filters 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = %s AND keyword = %s AND is_active = TRUE
                RETURNING id;
            """, (chat_id, keyword.lower()))
            result = cur.fetchone()
            conn.commit()
            return result is not None
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error deleting filter: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_all_filters(chat_id):
        """Delete all filters for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE filters 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = %s AND is_active = TRUE
                RETURNING id;
            """, (chat_id,))
            count = cur.rowcount
            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error deleting all filters: {e}")
            return 0
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def count_filters(chat_id):
        """Count active filters for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*) FROM filters 
                WHERE chat_id = %s AND is_active = TRUE;
            """, (chat_id,))
            return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error counting filters: {e}")
            return 0
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def log_filter_trigger(chat_id, keyword, triggered_by):
        """Log when a filter is triggered (for stats)"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO filter_stats 
                    (chat_id, keyword, triggered_by, triggered_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP);
            """, (chat_id, keyword, triggered_by))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error logging filter trigger: {e}")
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_filter_stats(chat_id, keyword=None):
        """Get filter trigger statistics"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            if keyword:
                cur.execute("""
                    SELECT keyword, COUNT(*) as trigger_count,
                           MAX(triggered_at) as last_triggered
                    FROM filter_stats 
                    WHERE chat_id = %s AND keyword = %s
                    GROUP BY keyword;
                """, (chat_id, keyword.lower()))
            else:
                cur.execute("""
                    SELECT keyword, COUNT(*) as trigger_count,
                           MAX(triggered_at) as last_triggered
                    FROM filter_stats 
                    WHERE chat_id = %s
                    GROUP BY keyword
                    ORDER BY trigger_count DESC
                    LIMIT 20;
                """, (chat_id,))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ Error getting filter stats: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def search_filters(chat_id, search_term):
        """Search filters by keyword pattern"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT keyword, filter_type, added_by_name
                FROM filters 
                WHERE chat_id = %s AND is_active = TRUE 
                AND keyword LIKE %s
                ORDER BY keyword ASC
                LIMIT 25;
            """, (chat_id, f'%{search_term.lower()}%'))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ Error searching filters: {e}")
            return []
        finally:
            cur.close()
            conn.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.3 — NOTES DATABASE OPERATIONS (CRUD)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NoteDB:
    """Complete database operations for Notes system"""

    @staticmethod
    def save_note(chat_id, note_name, note_text, added_by, 
                  added_by_name, media_type=None, media_file_id=None,
                  media_caption=None, note_type='text', is_private=False):
        """Save or update a note"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            name_lower = note_name.lower().strip()
            cur.execute("""
                INSERT INTO notes 
                    (chat_id, note_name, note_text, added_by, added_by_name,
                     media_type, media_file_id, media_caption, note_type,
                     is_private, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP)
                ON CONFLICT (chat_id, note_name)
                DO UPDATE SET
                    note_text = EXCLUDED.note_text,
                    added_by = EXCLUDED.added_by,
                    added_by_name = EXCLUDED.added_by_name,
                    media_type = EXCLUDED.media_type,
                    media_file_id = EXCLUDED.media_file_id,
                    media_caption = EXCLUDED.media_caption,
                    note_type = EXCLUDED.note_type,
                    is_private = EXCLUDED.is_private,
                    updated_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
                RETURNING id;
            """, (chat_id, name_lower, note_text, added_by, 
                  added_by_name, media_type, media_file_id, 
                  media_caption, note_type, is_private))
            
            note_id = cur.fetchone()[0]
            conn.commit()
            return note_id
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error saving note: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def add_note_buttons(note_id, chat_id, note_name, buttons_data):
        """Add buttons to a note"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Remove old buttons
            cur.execute("""
                DELETE FROM note_buttons 
                WHERE note_id = %s AND chat_id = %s;
            """, (note_id, chat_id))

            # Insert new buttons
            for btn in buttons_data:
                cur.execute("""
                    INSERT INTO note_buttons 
                        (note_id, chat_id, note_name, button_text, 
                         button_url, button_row, button_col)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (note_id, chat_id, note_name.lower(), 
                      btn['text'], btn['url'], 
                      btn.get('row', 0), btn.get('col', 0)))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error adding note buttons: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_note(chat_id, note_name):
        """Get a specific note"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, chat_id, note_name, note_text, note_markup,
                       media_type, media_file_id, media_caption, 
                       note_type, is_private, added_by, added_by_name,
                       created_at, usage_count
                FROM notes 
                WHERE chat_id = %s AND note_name = %s AND is_active = TRUE;
            """, (chat_id, note_name.lower().strip()))
            result = cur.fetchone()
            if result:
                # Increment usage count
                cur.execute("""
                    UPDATE notes SET usage_count = usage_count + 1 
                    WHERE id = %s;
                """, (result[0],))
                conn.commit()
                
                return {
                    'id': result[0],
                    'chat_id': result[1],
                    'note_name': result[2],
                    'note_text': result[3],
                    'note_markup': result[4],
                    'media_type': result[5],
                    'media_file_id': result[6],
                    'media_caption': result[7],
                    'note_type': result[8],
                    'is_private': result[9],
                    'added_by': result[10],
                    'added_by_name': result[11],
                    'created_at': result[12],
                    'usage_count': result[13]
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error getting note: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_note_buttons(note_id, chat_id):
        """Get all buttons for a note"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT button_text, button_url, button_row, button_col
                FROM note_buttons 
                WHERE note_id = %s AND chat_id = %s
                ORDER BY button_row, button_col;
            """, (note_id, chat_id))
            results = cur.fetchall()
            buttons = []
            for row in results:
                buttons.append({
                    'text': row[0],
                    'url': row[1],
                    'row': row[2],
                    'col': row[3]
                })
            return buttons
        except Exception as e:
            logger.error(f"❌ Error getting note buttons: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_notes(chat_id):
        """Get all active notes for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, note_name, note_type, is_private, 
                       added_by_name, created_at, usage_count, media_type
                FROM notes 
                WHERE chat_id = %s AND is_active = TRUE
                ORDER BY note_name ASC;
            """, (chat_id,))
            results = cur.fetchall()
            notes_list = []
            for row in results:
                notes_list.append({
                    'id': row[0],
                    'note_name': row[1],
                    'note_type': row[2],
                    'is_private': row[3],
                    'added_by_name': row[4],
                    'created_at': row[5],
                    'usage_count': row[6],
                    'media_type': row[7]
                })
            return notes_list
        except Exception as e:
            logger.error(f"❌ Error getting all notes: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_note(chat_id, note_name):
        """Delete a note"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE notes 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = %s AND note_name = %s AND is_active = TRUE
                RETURNING id;
            """, (chat_id, note_name.lower().strip()))
            result = cur.fetchone()
            conn.commit()
            return result is not None
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error deleting note: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_all_notes(chat_id):
        """Delete all notes for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE notes 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = %s AND is_active = TRUE
                RETURNING id;
            """, (chat_id,))
            count = cur.rowcount
            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error deleting all notes: {e}")
            return 0
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def count_notes(chat_id):
        """Count active notes for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*) FROM notes 
                WHERE chat_id = %s AND is_active = TRUE;
            """, (chat_id,))
            return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error counting notes: {e}")
            return 0
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def search_notes(chat_id, search_term):
        """Search notes by name"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT note_name, note_type, is_private, added_by_name
                FROM notes 
                WHERE chat_id = %s AND is_active = TRUE 
                AND note_name LIKE %s
                ORDER BY note_name ASC
                LIMIT 25;
            """, (chat_id, f'%{search_term.lower()}%'))
            return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ Error searching notes: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def log_note_access(chat_id, note_name, accessed_by, access_type='public'):
        """Log note access for stats"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO note_stats 
                    (chat_id, note_name, accessed_by, accessed_at, access_type)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s);
            """, (chat_id, note_name.lower(), accessed_by, access_type))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error logging note access: {e}")
        finally:
            cur.close()
            conn.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.4 — PRIVATE NOTES SETTINGS DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PrivateNoteDB:
    """Database operations for private notes settings"""

    @staticmethod
    def set_private_notes(chat_id, is_private, updated_by):
        """Set private notes on/off for a chat"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO private_notes_settings 
                    (chat_id, is_private, updated_by, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (chat_id)
                DO UPDATE SET
                    is_private = EXCLUDED.is_private,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = CURRENT_TIMESTAMP;
            """, (chat_id, is_private, updated_by))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error setting private notes: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_private_notes(chat_id):
        """Check if private notes is enabled"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT is_private FROM private_notes_settings 
                WHERE chat_id = %s;
            """, (chat_id,))
            result = cur.fetchone()
            return result[0] if result else False
        except Exception as e:
            logger.error(f"❌ Error getting private notes setting: {e}")
            return False
        finally:
            cur.close()
            conn.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.5 — HELPER FUNCTIONS & UTILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_buttons_from_text(text):
    """
    Parse button syntax from text
    Format: [Button Text](buttonurl://https://example.com)
    Same row: [Button](buttonurl://url:same)
    Returns: (clean_text, buttons_data)
    """
    import re
    buttons_data = []
    button_pattern = r'\[(.+?)\]\(buttonurl://(.+?)\)'
    matches = re.findall(button_pattern, text)
    
    clean_text = re.sub(button_pattern, '', text).strip()
    
    current_row = 0
    current_col = 0
    
    for match in matches:
        btn_text = match[0].strip()
        btn_url = match[1].strip()
        
        # Check if same row marker
        same_row = False
        if btn_url.endswith(':same'):
            btn_url = btn_url[:-5]  # Remove :same
            same_row = True
        
        if not same_row and buttons_data:
            current_row += 1
            current_col = 0
        
        buttons_data.append({
            'text': btn_text,
            'url': btn_url,
            'row': current_row,
            'col': current_col
        })
        current_col += 1
    
    return clean_text, buttons_data


def build_inline_keyboard_from_buttons(buttons_data):
    """Build InlineKeyboardMarkup from buttons_data list"""
    if not buttons_data:
        return None
    
    # Group buttons by row
    rows = {}
    for btn in buttons_data:
        row_num = btn.get('row', 0)
        if row_num not in rows:
            rows[row_num] = []
        rows[row_num].append(
            InlineKeyboardButton(
                text=btn['text'], 
                url=btn['url']
            )
        )
    
    # Build keyboard
    keyboard = []
    for row_num in sorted(rows.keys()):
        keyboard.append(rows[row_num])
    
    return InlineKeyboardMarkup(keyboard) if keyboard else None


def format_filter_variables(text, message):
    """
    Replace variables in filter/note text with actual values
    Supported variables:
    {first} - User first name
    {last} - User last name
    {fullname} - Full name
    {username} - @username
    {mention} - Mention user
    {id} - User ID
    {chatname} - Chat name
    {chatid} - Chat ID
    {count} - Member count (if available)
    {rules} - Link to rules
    """
    if not text:
        return text
    
    user = message.from_user
    chat = message.chat
    
    first = user.first_name if user.first_name else "User"
    last = user.last_name if user.last_name else ""
    fullname = f"{first} {last}".strip()
    username = f"@{user.username}" if user.username else first
    mention = f'<a href="tg://user?id={user.id}">{first}</a>'
    
    replacements = {
        '{first}': first,
        '{last}': last,
        '{fullname}': fullname,
        '{username}': username,
        '{mention}': mention,
        '{id}': str(user.id),
        '{chatname}': chat.title if chat.title else "Private Chat",
        '{chatid}': str(chat.id),
    }
    
    for var, value in replacements.items():
        text = text.replace(var, value)
    
    return text


def get_media_type_emoji(media_type):
    """Get emoji for media type"""
    emojis = {
        'photo': '🖼',
        'video': '🎬',
        'animation': '🎭',
        'document': '📄',
        'audio': '🎵',
        'voice': '🎤',
        'video_note': '📹',
        'sticker': '🎨',
        'text': '📝'
    }
    return emojis.get(media_type, '📎')


def get_note_type_icon(note_type, is_private):
    """Get icon for note type"""
    if is_private:
        return '🔒'
    icons = {
        'text': '📝',
        'photo': '🖼',
        'video': '🎬',
        'animation': '🎭',
        'document': '📄',
        'audio': '🎵',
        'sticker': '🎨'
    }
    return icons.get(note_type, '📎')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.6 — STYLISH MESSAGE TEMPLATES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FilterNotesTemplates:
    """All stylish message templates for Filters & Notes"""

    # ═══════════════════════════════════════
    # FILTER TEMPLATES
    # ═══════════════════════════════════════

    FILTER_ADDED = """
✦ 𝐅ɪʟᴛᴇʀ 𝐀ᴅᴅᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🎯 𝐅ɪʟᴛᴇʀ 𝐈ɴғᴏ ]═══╗
║ ✧ 𝐊ᴇʏᴡᴏʀᴅ: <code>{keyword}</code>
║ ✧ 𝐓ʏᴘᴇ: {filter_type}
║ ✧ 𝐌ᴀᴛᴄʜ: {match_type}
║ ✧ 𝐁ᴜᴛᴛᴏɴs: {has_buttons}
║ ✧ 𝐌ᴇᴅɪᴀ: {has_media}
║ ✧ 𝐁ʏ: {added_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
⚡ 𝐅ɪʟᴛᴇʀ ᴡɪʟʟ ᴛʀɪɢɢᴇʀ ᴡʜᴇɴ
   sᴏᴍᴇᴏɴᴇ sᴀʏs "<b>{keyword}</b>"
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    FILTER_UPDATED = """
✦ 𝐅ɪʟᴛᴇʀ 𝐔ᴘᴅᴀᴛᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔄 𝐔ᴘᴅᴀᴛᴇ 𝐈ɴғᴏ ]═══╗
║ ✧ 𝐊ᴇʏᴡᴏʀᴅ: <code>{keyword}</code>
║ ✧ 𝐒ᴛᴀᴛᴜs: ✅ Updated
║ ✧ 𝐁ʏ: {added_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🔄 𝐅ɪʟᴛᴇʀ ʜᴀs ʙᴇᴇɴ ᴜᴘᴅᴀᴛᴇᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    FILTER_DELETED = """
✦ 𝐅ɪʟᴛᴇʀ 𝐃ᴇʟᴇᴛᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🗑 𝐃ᴇʟᴇᴛᴇ 𝐈ɴғᴏ ]═══╗
║ ✧ 𝐊ᴇʏᴡᴏʀᴅ: <code>{keyword}</code>
║ ✧ 𝐒ᴛᴀᴛᴜs: ❌ Deleted
║ ✧ 𝐁ʏ: {deleted_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🗑 𝐅ɪʟᴛᴇʀ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    FILTER_NOT_FOUND = """
✦ 𝐅ɪʟᴛᴇʀ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐄ʀʀᴏʀ ]═══╗
║ ✧ 𝐊ᴇʏᴡᴏʀᴅ: <code>{keyword}</code>
║ ✧ 𝐒ᴛᴀᴛᴜs: 🔍 Not Found
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
❌ 𝐍ᴏ ғɪʟᴛᴇʀ ғᴏᴜɴᴅ ᴡɪᴛʜ ᴛʜɪs ᴋᴇʏᴡᴏʀᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    ALL_FILTERS_DELETED = """
✦ 𝐀ʟʟ 𝐅ɪʟᴛᴇʀs 𝐃ᴇʟᴇᴛᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🗑 𝐁ᴜʟᴋ 𝐃ᴇʟᴇᴛᴇ ]═══╗
║ ✧ 𝐃ᴇʟᴇᴛᴇᴅ: {count} filters
║ ✧ 𝐒ᴛᴀᴛᴜs: ✅ Complete
║ ✧ 𝐁ʏ: {deleted_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🗑 𝐀ʟʟ ғɪʟᴛᴇʀs ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NO_FILTERS = """
✦ 𝐍ᴏ 𝐅ɪʟᴛᴇʀs ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📭 𝐄ᴍᴘᴛʏ ]═══╗
║ ✧ 𝐅ɪʟᴛᴇʀs: 0
║ ✧ 𝐒ᴛᴀᴛᴜs: 📭 Empty
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
📝 𝐔sᴇ /filter &lt;ᴋᴇʏᴡᴏʀᴅ&gt; ᴛᴏ ᴀᴅᴅ ᴏɴᴇ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    FILTER_LIST_HEADER = """
✦ 𝐅ɪʟᴛᴇʀ 𝐋ɪsᴛ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📋 {chat_name} ]═══╗
║ ✧ 𝐓ᴏᴛᴀʟ 𝐅ɪʟᴛᴇʀs: {count}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
"""

    FILTER_LIST_ITEM = """║ {num}. {emoji} <code>{keyword}</code> — {type_info}"""

    FILTER_LIST_FOOTER = """
━━━━━━━━━━━━━━━━━━
⚡ 𝐔sᴇ /filter &lt;keyword&gt; ᴛᴏ ᴀᴅᴅ
🗑 𝐔sᴇ /stop &lt;keyword&gt; ᴛᴏ ᴅᴇʟᴇᴛᴇ
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    FILTER_HELP = """
✦ 𝐅ɪʟᴛᴇʀ 𝐇ᴇʟᴘ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📖 𝐂ᴏᴍᴍᴀɴᴅs ]═══╗
║
║ 🎯 <b>𝐒ᴇᴛ 𝐅ɪʟᴛᴇʀ:</b>
║ ┣ /filter &lt;keyword&gt; &lt;reply&gt;
║ ┣ Reply to media with /filter &lt;keyword&gt;
║ ┗ Buttons: [text](buttonurl://url)
║
║ 🗑 <b>𝐃ᴇʟᴇᴛᴇ 𝐅ɪʟᴛᴇʀ:</b>
║ ┣ /stop &lt;keyword&gt;
║ ┗ /stopall — Delete all filters
║
║ 📋 <b>𝐋ɪsᴛ 𝐅ɪʟᴛᴇʀs:</b>
║ ┣ /filters — List all
║ ┗ /filtersearch &lt;text&gt; — Search
║
║ 📊 <b>𝐅ɪʟᴛᴇʀ 𝐒ᴛᴀᴛs:</b>
║ ┗ /filterstats — View stats
║
║ 🔤 <b>𝐕ᴀʀɪᴀʙʟᴇs:</b>
║ ┣ {first} — First name
║ ┣ {last} — Last name
║ ┣ {fullname} — Full name
║ ┣ {username} — @username
║ ┣ {mention} — Mention
║ ┣ {id} — User ID
║ ┣ {chatname} — Chat name
║ ┗ {chatid} — Chat ID
║
║ 🔘 <b>𝐁ᴜᴛᴛᴏɴ 𝐅ᴏʀᴍᴀᴛ:</b>
║ ┣ [Button](buttonurl://url)
║ ┗ Same row: [Btn](buttonurl://url:same)
║
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    # ═══════════════════════════════════════
    # NOTE TEMPLATES
    # ═══════════════════════════════════════

    NOTE_SAVED = """
✦ 𝐍ᴏᴛᴇ 𝐒ᴀᴠᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📝 𝐍ᴏᴛᴇ 𝐈ɴғᴏ ]═══╗
║ ✧ 𝐍ᴀᴍᴇ: <code>{note_name}</code>
║ ✧ 𝐓ʏᴘᴇ: {note_type}
║ ✧ 𝐏ʀɪᴠᴀᴛᴇ: {is_private}
║ ✧ 𝐁ᴜᴛᴛᴏɴs: {has_buttons}
║ ✧ 𝐌ᴇᴅɪᴀ: {has_media}
║ ✧ 𝐁ʏ: {added_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
💡 𝐔sᴇ <code>#{note_name}</code> ᴏʀ
   <code>/get {note_name}</code> ᴛᴏ ᴀᴄᴄᴇss
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NOTE_DELETED = """
✦ 𝐍ᴏᴛᴇ 𝐃ᴇʟᴇᴛᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🗑 𝐃ᴇʟᴇᴛᴇ 𝐈ɴғᴏ ]═══╗
║ ✧ 𝐍ᴀᴍᴇ: <code>{note_name}</code>
║ ✧ 𝐒ᴛᴀᴛᴜs: ❌ Deleted
║ ✧ 𝐁ʏ: {deleted_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🗑 𝐍ᴏᴛᴇ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NOTE_NOT_FOUND = """
✦ 𝐍ᴏᴛᴇ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐄ʀʀᴏʀ ]═══╗
║ ✧ 𝐍ᴀᴍᴇ: <code>{note_name}</code>
║ ✧ 𝐒ᴛᴀᴛᴜs: 🔍 Not Found
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
❌ 𝐍ᴏ ɴᴏᴛᴇ ғᴏᴜɴᴅ ᴡɪᴛʜ ᴛʜɪs ɴᴀᴍᴇ!
𝐔sᴇ /notes ᴛᴏ sᴇᴇ ᴀʟʟ ɴᴏᴛᴇs
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    ALL_NOTES_DELETED = """
✦ 𝐀ʟʟ 𝐍ᴏᴛᴇs 𝐃ᴇʟᴇᴛᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🗑 𝐁ᴜʟᴋ 𝐃ᴇʟᴇᴛᴇ ]═══╗
║ ✧ 𝐃ᴇʟᴇᴛᴇᴅ: {count} notes
║ ✧ 𝐒ᴛᴀᴛᴜs: ✅ Complete
║ ✧ 𝐁ʏ: {deleted_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🗑 𝐀ʟʟ ɴᴏᴛᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NO_NOTES = """
✦ 𝐍ᴏ 𝐍ᴏᴛᴇs ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📭 𝐄ᴍᴘᴛʏ ]═══╗
║ ✧ 𝐍ᴏᴛᴇs: 0
║ ✧ 𝐒ᴛᴀᴛᴜs: 📭 Empty
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
📝 𝐔sᴇ /save &lt;name&gt; ᴛᴏ ᴀᴅᴅ ᴏɴᴇ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NOTE_LIST_HEADER = """
✦ 𝐍ᴏᴛᴇs 𝐋ɪsᴛ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📋 {chat_name} ]═══╗
║ ✧ 𝐓ᴏᴛᴀʟ 𝐍ᴏᴛᴇs: {count}
║ ✧ 𝐏ʀɪᴠᴀᴛᴇ 𝐌ᴏᴅᴇ: {private_mode}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
"""

    NOTE_LIST_ITEM = """║ {num}. {emoji} <code>#{note_name}</code> — {type_info}"""

    NOTE_LIST_FOOTER = """
━━━━━━━━━━━━━━━━━━
💡 𝐔sᴇ <code>#notename</code> ᴏʀ
   <code>/get notename</code> ᴛᴏ ᴀᴄᴄᴇss
━━━━━━━━━━━━━━━━━━
📝 /save &lt;name&gt; — Save note
🗑 /clear &lt;name&gt; — Delete note
📋 /notes — List all notes
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    PRIVATE_NOTE_REDIRECT = """
✦ 𝐏ʀɪᴠᴀᴛᴇ 𝐍ᴏᴛᴇ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔒 𝐏ʀɪᴠᴀᴛᴇ ]═══╗
║ ✧ 𝐍ᴏᴛᴇ: <code>{note_name}</code>
║ ✧ 𝐌ᴏᴅᴇ: 🔒 Private
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🔒 𝐓ᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ
   ɢᴇᴛ ᴛʜɪs ɴᴏᴛᴇ ɪɴ 𝐏𝐌!
━━━━━━━━━━━━━━━━━━
"""

    PRIVATE_NOTES_ON = """
✦ 𝐏ʀɪᴠᴀᴛᴇ 𝐍ᴏᴛᴇs 𝐄ɴᴀʙʟᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔒 𝐒ᴇᴛᴛɪɴɢs ]═══╗
║ ✧ 𝐏ʀɪᴠᴀᴛᴇ 𝐌ᴏᴅᴇ: ✅ ON
║ ✧ 𝐁ʏ: {updated_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🔒 𝐍ᴏᴛᴇs ᴡɪʟʟ ʙᴇ sᴇɴᴛ ɪɴ 𝐏𝐌
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    PRIVATE_NOTES_OFF = """
✦ 𝐏ʀɪᴠᴀᴛᴇ 𝐍ᴏᴛᴇs 𝐃ɪsᴀʙʟᴇᴅ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔓 𝐒ᴇᴛᴛɪɴɢs ]═══╗
║ ✧ 𝐏ʀɪᴠᴀᴛᴇ 𝐌ᴏᴅᴇ: ❌ OFF
║ ✧ 𝐁ʏ: {updated_by}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🔓 𝐍ᴏᴛᴇs ᴡɪʟʟ ʙᴇ sᴇɴᴛ ɪɴ ɢʀᴏᴜᴘ
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NOTE_HELP = """
✦ 𝐍ᴏᴛᴇs 𝐇ᴇʟᴘ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📖 𝐂ᴏᴍᴍᴀɴᴅs ]═══╗
║
║ 📝 <b>𝐒ᴀᴠᴇ 𝐍ᴏᴛᴇ:</b>
║ ┣ /save &lt;name&gt; &lt;text&gt;
║ ┣ Reply to media with /save &lt;name&gt;
║ ┗ Buttons: [text](buttonurl://url)
║
║ 📖 <b>𝐆ᴇᴛ 𝐍ᴏᴛᴇ:</b>
║ ┣ /get &lt;name&gt;
║ ┣ #notename
║ ┗ /get &lt;name&gt; noformat
║
║ 🗑 <b>𝐃ᴇʟᴇᴛᴇ 𝐍ᴏᴛᴇ:</b>
║ ┣ /clear &lt;name&gt;
║ ┗ /clearall — Delete all notes
║
║ 📋 <b>𝐋ɪsᴛ 𝐍ᴏᴛᴇs:</b>
║ ┣ /notes — List all
║ ┗ /saved — Same as /notes
║
║ 🔒 <b>𝐏ʀɪᴠᴀᴛᴇ 𝐍ᴏᴛᴇs:</b>
║ ┣ /privatenotes on — Send in PM
║ ┗ /privatenotes off — Send in group
║
║ 🔤 <b>𝐕ᴀʀɪᴀʙʟᴇs:</b>
║ ┣ {first} — First name
║ ┣ {last} — Last name
║ ┣ {fullname} — Full name
║ ┣ {username} — @username
║ ┣ {mention} — Mention
║ ┣ {id} — User ID
║ ┣ {chatname} — Chat name
║ ┗ {chatid} — Chat ID
║
║ 🔘 <b>𝐁ᴜᴛᴛᴏɴ 𝐅ᴏʀᴍᴀᴛ:</b>
║ ┣ [Button](buttonurl://url)
║ ┗ Same row: [Btn](buttonurl://url:same)
║
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    NOT_ADMIN = """
✦ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐏ᴇʀᴍɪssɪᴏɴ ]═══╗
║ ✧ 𝐒ᴛᴀᴛᴜs: ❌ Denied
║ ✧ 𝐑ᴇᴀsᴏɴ: Not Admin
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🔒 𝐘ᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    BOT_NOT_ADMIN = """
✦ 𝐁ᴏᴛ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐏ᴇʀᴍɪssɪᴏɴ ]═══╗
║ ✧ 𝐒ᴛᴀᴛᴜs: ❌ Error
║ ✧ 𝐑ᴇᴀsᴏɴ: Bot not admin
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🤖 𝐏ʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    CONFIRM_DELETE_ALL_FILTERS = """
✦ 𝐂ᴏɴғɪʀᴍ 𝐃ᴇʟᴇᴛɪᴏɴ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐖ᴀʀɴɪɴɢ ]═══╗
║ ✧ 𝐀ᴄᴛɪᴏɴ: Delete ALL filters
║ ✧ 𝐂ᴏᴜɴᴛ: {count} filters
║ ✧ 𝐒ᴛᴀᴛᴜs: ⏳ Awaiting confirm
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
⚠️ 𝐓ʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!
━━━━━━━━━━━━━━━━━━
"""

    CONFIRM_DELETE_ALL_NOTES = """
✦ 𝐂ᴏɴғɪʀᴍ 𝐃ᴇʟᴇᴛɪᴏɴ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐖ᴀʀɴɪɴɢ ]═══╗
║ ✧ 𝐀ᴄᴛɪᴏɴ: Delete ALL notes
║ ✧ 𝐂ᴏᴜɴᴛ: {count} notes
║ ✧ 𝐒ᴛᴀᴛᴜs: ⏳ Awaiting confirm
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
⚠️ 𝐓ʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!
━━━━━━━━━━━━━━━━━━
"""

    FILTER_STATS_TEMPLATE = """
✦ 𝐅ɪʟᴛᴇʀ 𝐒ᴛᴀᴛs ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📊 {chat_name} ]═══╗
║ ✧ 𝐓ᴏᴛᴀʟ 𝐅ɪʟᴛᴇʀs: {total}
║ ✧ 𝐓ᴏᴛᴀʟ 𝐓ʀɪɢɢᴇʀs: {triggers}
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
📊 𝐓ᴏᴘ 𝐅ɪʟᴛᴇʀs:
{top_filters}
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

    GROUP_ONLY = """
✦ 𝐆ʀᴏᴜᴘ 𝐎ɴʟʏ ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ⚠️ 𝐄ʀʀᴏʀ ]═══╗
║ ✧ 𝐒ᴛᴀᴛᴜs: ❌ Denied
║ ✧ 𝐑ᴇᴀsᴏɴ: Group command only
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
🏘 𝐔sᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ!
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.7 — ADMIN CHECK HELPER (ROBUST VERSION)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def is_user_admin_filters(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """
    Robust admin check that properly detects admin status.
    Works correctly when bot is admin.
    Also checks owner/sudo users.
    """
    try:
        chat = update.effective_chat
        
        # Owner is always admin
        if user_id == OWNER_ID:
            return True
        
        # Sudo users are always admin
        if user_id in SUDO_USERS:
            return True
        
        # Private chat = always admin
        if chat.type == 'private':
            return True
        
        # Get fresh member info from Telegram API
        try:
            member = await context.bot.get_chat_member(chat.id, user_id)
            if member.status in ['creator', 'administrator']:
                return True
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            # Fallback: try using update's chat member cache
            try:
                admins = await context.bot.get_chat_administrators(chat.id)
                admin_ids = [admin.user.id for admin in admins]
                return user_id in admin_ids
            except Exception as e2:
                logger.error(f"Fallback admin check also failed: {e2}")
                return False
        
        return False
    except Exception as e:
        logger.error(f"Admin check error: {e}")
        return False


async def is_bot_admin_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot is admin in the chat"""
    try:
        chat = update.effective_chat
        if chat.type == 'private':
            return True
        
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        return bot_member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"Bot admin check error: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.8 — FILTER COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filter <keyword> <reply text>
    or reply to a message/media with /filter <keyword>
    
    Supports:
    - Text filters
    - Media filters (photo, video, document, audio, sticker, animation, voice, video_note)
    - Button filters: [Button Text](buttonurl://https://example.com)
    - Same row buttons: [Button](buttonurl://url:same)
    - Variables: {first}, {last}, {fullname}, {username}, {mention}, {id}, {chatname}, {chatid}
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    # ─── Group only check ───
    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    # ─── Admin check ───
    if not await is_user_admin_filters(update, context, user.id):
        await message.reply_text(
            FilterNotesTemplates.NOT_ADMIN,
            parse_mode='HTML'
        )
        return

    # ─── Parse arguments ───
    args = message.text.split(None, 1) if message.text else []
    
    if len(args) < 2 and not message.reply_to_message:
        await message.reply_text(
            FilterNotesTemplates.FILTER_HELP,
            parse_mode='HTML'
        )
        return

    # Get keyword and reply content
    if len(args) >= 2:
        # Split keyword from rest
        rest = args[1]
        parts = rest.split(None, 1)
        keyword = parts[0].lower().strip()
        reply_text = parts[1] if len(parts) > 1 else None
    else:
        keyword = args[1].lower().strip() if len(args) > 1 else None
        reply_text = None

    if not keyword:
        await message.reply_text(
            "⚠️ <b>𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ!</b>",
            parse_mode='HTML'
        )
        return

    # ─── Handle media from reply ───
    media_type = None
    media_file_id = None
    media_caption = None
    filter_type = 'text'

    replied = message.reply_to_message

    if replied:
        if replied.photo:
            media_type = 'photo'
            media_file_id = replied.photo[-1].file_id
            media_caption = replied.caption or replied.caption_html
            filter_type = 'photo'
            if not reply_text:
                reply_text = media_caption
        elif replied.video:
            media_type = 'video'
            media_file_id = replied.video.file_id
            media_caption = replied.caption or replied.caption_html
            filter_type = 'video'
            if not reply_text:
                reply_text = media_caption
        elif replied.animation:
            media_type = 'animation'
            media_file_id = replied.animation.file_id
            media_caption = replied.caption or replied.caption_html
            filter_type = 'animation'
            if not reply_text:
                reply_text = media_caption
        elif replied.document:
            media_type = 'document'
            media_file_id = replied.document.file_id
            media_caption = replied.caption or replied.caption_html
            filter_type = 'document'
            if not reply_text:
                reply_text = media_caption
        elif replied.audio:
            media_type = 'audio'
            media_file_id = replied.audio.file_id
            media_caption = replied.caption or replied.caption_html
            filter_type = 'audio'
            if not reply_text:
                reply_text = media_caption
        elif replied.voice:
            media_type = 'voice'
            media_file_id = replied.voice.file_id
            filter_type = 'voice'
        elif replied.video_note:
            media_type = 'video_note'
            media_file_id = replied.video_note.file_id
            filter_type = 'video_note'
        elif replied.sticker:
            media_type = 'sticker'
            media_file_id = replied.sticker.file_id
            filter_type = 'sticker'
        elif replied.text and not reply_text:
            reply_text = replied.text_html or replied.text

    # ─── Must have some content ───
    if not reply_text and not media_file_id:
        await message.reply_text(
            "⚠️ <b>𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʀᴇᴘʟʏ ᴛᴇxᴛ ᴏʀ ᴍᴇᴅɪᴀ!</b>\n\n"
            "💡 <code>/filter hello Hi there!</code>\n"
            "💡 Reply to a photo with <code>/filter hello</code>",
            parse_mode='HTML'
        )
        return

    # ─── Parse buttons from text ───
    buttons_data = []
    if reply_text:
        reply_text, buttons_data = parse_buttons_from_text(reply_text)
        if buttons_data:
            filter_type = filter_type if media_file_id else 'text_buttons'

    # ─── Check if filter already exists (for update message) ───
    existing = FilterDB.get_filter(chat.id, keyword)
    is_update = existing is not None

    # ─── Save to database ───
    added_by_name = user.first_name or "Unknown"
    filter_id = FilterDB.add_filter(
        chat_id=chat.id,
        keyword=keyword,
        reply_text=reply_text,
        added_by=user.id,
        added_by_name=added_by_name,
        media_type=media_type,
        media_file_id=media_file_id,
        media_caption=media_caption,
        filter_type=filter_type,
        match_type='contains',
        case_sensitive=False
    )

    if filter_id is None:
        await message.reply_text(
            "❌ <b>𝐅ᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ғɪʟᴛᴇʀ!</b>",
            parse_mode='HTML'
        )
        return

    # ─── Save buttons if any ───
    if buttons_data:
        FilterDB.add_filter_buttons(filter_id, chat.id, keyword, buttons_data)

    # ─── Send confirmation ───
    if is_update:
        template = FilterNotesTemplates.FILTER_UPDATED
    else:
        template = FilterNotesTemplates.FILTER_ADDED

    has_buttons_text = f"✅ {len(buttons_data)} buttons" if buttons_data else "❌ None"
    has_media_text = f"✅ {get_media_type_emoji(media_type)} {media_type}" if media_type else "❌ None"

    response = template.format(
        keyword=keyword,
        filter_type=f"{get_media_type_emoji(filter_type)} {filter_type}",
        match_type="📎 Contains",
        has_buttons=has_buttons_text,
        has_media=has_media_text,
        added_by=f'<a href="tg://user?id={user.id}">{added_by_name}</a>'
    )

    await message.reply_text(response, parse_mode='HTML')

    # ─── Log to logger channel ───
    try:
        if LOGGER_CHANNEL:
            log_msg = (
                f"✦ 𝐅ɪʟᴛᴇʀ {'𝐔ᴘᴅᴀᴛᴇᴅ' if is_update else '𝐀ᴅᴅᴇᴅ'} ✦\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"╔═══[ 📋 𝐋ᴏɢ ]═══╗\n"
                f"║ ✧ 𝐂ʜᴀᴛ: {chat.title}\n"
                f"║ ✧ 𝐂ʜᴀᴛ 𝐈ᴅ: <code>{chat.id}</code>\n"
                f"║ ✧ 𝐊ᴇʏᴡᴏʀᴅ: <code>{keyword}</code>\n"
                f"║ ✧ 𝐓ʏᴘᴇ: {filter_type}\n"
                f"║ ✧ 𝐁ʏ: {added_by_name}\n"
                f"╚════════════════╝"
            )
            await context.bot.send_message(
                LOGGER_CHANNEL, log_msg, parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Logger error: {e}")


async def stop_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /stop <keyword> — Delete a specific filter
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    if not await is_user_admin_filters(update, context, user.id):
        await message.reply_text(
            FilterNotesTemplates.NOT_ADMIN,
            parse_mode='HTML'
        )
        return

    args = message.text.split(None, 1) if message.text else []
    if len(args) < 2:
        await message.reply_text(
            "⚠️ <b>𝐔sᴀɢᴇ:</b> <code>/stop &lt;keyword&gt;</code>",
            parse_mode='HTML'
        )
        return

    keyword = args[1].lower().strip()
    deleted_by = user.first_name or "Unknown"

    success = FilterDB.delete_filter(chat.id, keyword)

    if success:
        response = FilterNotesTemplates.FILTER_DELETED.format(
            keyword=keyword,
            deleted_by=f'<a href="tg://user?id={user.id}">{deleted_by}</a>'
        )
    else:
        response = FilterNotesTemplates.FILTER_NOT_FOUND.format(
            keyword=keyword
        )

    await message.reply_text(response, parse_mode='HTML')


async def stop_all_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /stopall — Delete all filters (with confirmation)
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    # Only chat owner or bot owner can delete all
    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status != 'creator' and user.id != OWNER_ID and user.id not in SUDO_USERS:
        await message.reply_text(
            "⚠️ <b>𝐎ɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴄᴀɴ ᴅᴏ ᴛʜɪs!</b>",
            parse_mode='HTML'
        )
        return

    count = FilterDB.count_filters(chat.id)
    if count == 0:
        await message.reply_text(
            FilterNotesTemplates.NO_FILTERS,
            parse_mode='HTML'
        )
        return

    # Show confirmation
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ 𝐘ᴇs, 𝐃ᴇʟᴇᴛᴇ 𝐀ʟʟ", 
                callback_data=f"stopall_confirm_{chat.id}_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ 𝐂ᴀɴᴄᴇʟ", 
                callback_data=f"stopall_cancel_{user.id}"
            )
        ]
    ])

    await message.reply_text(
        FilterNotesTemplates.CONFIRM_DELETE_ALL_FILTERS.format(count=count),
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def stopall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stopall confirmation callbacks"""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("stopall_confirm_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        original_user = int(parts[3])

        if user.id != original_user:
            await query.answer("⚠️ 𝐓ʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
            return

        count = FilterDB.delete_all_filters(chat_id)
        deleted_by = user.first_name or "Unknown"

        await query.edit_message_text(
            FilterNotesTemplates.ALL_FILTERS_DELETED.format(
                count=count,
                deleted_by=f'<a href="tg://user?id={user.id}">{deleted_by}</a>'
            ),
            parse_mode='HTML'
        )

    elif data.startswith("stopall_cancel_"):
        original_user = int(data.split("_")[2])
        if user.id != original_user:
            await query.answer("⚠️ 𝐓ʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
            return

        await query.edit_message_text(
            "✅ <b>𝐂ᴀɴᴄᴇʟʟᴇᴅ!</b> 𝐅ɪʟᴛᴇʀs ᴀʀᴇ sᴀғᴇ.",
            parse_mode='HTML'
        )


async def list_filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filters — List all active filters in the chat
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    filters_list = FilterDB.get_all_filters(chat.id)

    if not filters_list:
        await message.reply_text(
            FilterNotesTemplates.NO_FILTERS,
            parse_mode='HTML'
        )
        return

    # Build filter list message
    chat_name = chat.title or "This Chat"
    response = FilterNotesTemplates.FILTER_LIST_HEADER.format(
        chat_name=chat_name,
        count=len(filters_list)
    )

    for i, f in enumerate(filters_list, 1):
        emoji = get_media_type_emoji(f.get('media_type') or f.get('filter_type', 'text'))
        type_info = f.get('filter_type', 'text')
        if f.get('media_type'):
            type_info = f"{f['media_type']}"
        
        response += FilterNotesTemplates.FILTER_LIST_ITEM.format(
            num=i,
            emoji=emoji,
            keyword=f['keyword'],
            type_info=type_info
        ) + "\n"

    response += FilterNotesTemplates.FILTER_LIST_FOOTER

    # If message too long, split or use pagination
    if len(response) > 4000:
        # Split into pages
        pages = []
        current_page = FilterNotesTemplates.FILTER_LIST_HEADER.format(
            chat_name=chat_name,
            count=len(filters_list)
        )
        
        for i, f in enumerate(filters_list, 1):
            emoji = get_media_type_emoji(f.get('media_type') or f.get('filter_type', 'text'))
            type_info = f.get('filter_type', 'text')
            line = FilterNotesTemplates.FILTER_LIST_ITEM.format(
                num=i, emoji=emoji, keyword=f['keyword'], type_info=type_info
            ) + "\n"
            
            if len(current_page) + len(line) > 3500:
                pages.append(current_page)
                current_page = f"✦ 𝐅ɪʟᴛᴇʀ 𝐋ɪsᴛ (ᴄᴏɴᴛ.) ✦\n━━━━━━━━━━━━━━━━━━\n"
            
            current_page += line
        
        current_page += FilterNotesTemplates.FILTER_LIST_FOOTER
        pages.append(current_page)
        
        for page in pages:
            await message.reply_text(page, parse_mode='HTML')
    else:
        await message.reply_text(response, parse_mode='HTML')


async def filter_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filtersearch <text> — Search filters by keyword
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY, parse_mode='HTML'
        )
        return

    args = message.text.split(None, 1) if message.text else []
    if len(args) < 2:
        await message.reply_text(
            "⚠️ <b>𝐔sᴀɢᴇ:</b> <code>/filtersearch &lt;text&gt;</code>",
            parse_mode='HTML'
        )
        return

    search_term = args[1].strip()
    results = FilterDB.search_filters(chat.id, search_term)

    if not results:
        await message.reply_text(
            f"🔍 <b>𝐍ᴏ ғɪʟᴛᴇʀs ғᴏᴜɴᴅ ᴍᴀᴛᴄʜɪɴɢ:</b> <code>{search_term}</code>",
            parse_mode='HTML'
        )
        return

    response = (
        f"✦ 𝐅ɪʟᴛᴇʀ 𝐒ᴇᴀʀᴄʜ 𝐑ᴇsᴜʟᴛs ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔍 𝐒ᴇᴀʀᴄʜ: <code>{search_term}</code>\n"
        f"📊 𝐅ᴏᴜɴᴅ: {len(results)} filters\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    for i, (keyword, ftype, added_by) in enumerate(results, 1):
        emoji = get_media_type_emoji(ftype)
        response += f"║ {i}. {emoji} <code>{keyword}</code> — {ftype}\n"

    response += (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
    )

    await message.reply_text(response, parse_mode='HTML')


async def filter_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filterstats — Show filter trigger statistics
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY, parse_mode='HTML'
        )
        return

    total = FilterDB.count_filters(chat.id)
    stats = FilterDB.get_filter_stats(chat.id)

    total_triggers = sum(s[1] for s in stats) if stats else 0

    top_filters = ""
    if stats:
        for i, (keyword, count, last) in enumerate(stats[:10], 1):
            bar = "█" * min(count, 20)
            top_filters += f"  {i}. <code>{keyword}</code> — {count}x\n     {bar}\n"
    else:
        top_filters = "  📭 No trigger data yet\n"

    chat_name = chat.title or "This Chat"
    response = FilterNotesTemplates.FILTER_STATS_TEMPLATE.format(
        chat_name=chat_name,
        total=total,
        triggers=total_triggers,
        top_filters=top_filters
    )

    await message.reply_text(response, parse_mode='HTML')


async def filter_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filterhelp — Show filter help
    """
    await update.effective_message.reply_text(
        FilterNotesTemplates.FILTER_HELP,
        parse_mode='HTML'
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.9 — FILTER TRIGGER HANDLER (Message Handler)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def filter_trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Listens to all messages and triggers matching filters.
    This is a MessageHandler that checks every message for filter keywords.
    """
    message = update.effective_message
    chat = update.effective_chat

    if not message or not message.text:
        return

    if chat.type == 'private':
        return

    # Get message text
    msg_text = message.text.lower()

    # Get all filter keywords for this chat (cached for performance)
    cache_key = f"filter_keywords_{chat.id}"
    
    # Try to get from context cache
    if not hasattr(context, '_filter_cache'):
        context._filter_cache = {}
    
    # Cache for 60 seconds
    import time
    now = time.time()
    cached = context._filter_cache.get(cache_key)
    
    if cached and (now - cached['time']) < 60:
        keywords = cached['data']
    else:
        keywords = FilterDB.get_all_filter_keywords(chat.id)
        context._filter_cache[cache_key] = {'data': keywords, 'time': now}

    if not keywords:
        return

    # Check each keyword
    for (keyword, match_type, case_sensitive) in keywords:
        matched = False
        
        if match_type == 'exact':
            if case_sensitive:
                matched = message.text.strip() == keyword
            else:
                matched = msg_text.strip() == keyword.lower()
        elif match_type == 'startswith':
            if case_sensitive:
                matched = message.text.startswith(keyword)
            else:
                matched = msg_text.startswith(keyword.lower())
        else:  # contains (default)
            if case_sensitive:
                matched = keyword in message.text
            else:
                matched = keyword.lower() in msg_text

        if matched:
            # Get full filter data
            filter_data = FilterDB.get_filter(chat.id, keyword)
            if not filter_data:
                continue

            # Log trigger
            FilterDB.log_filter_trigger(chat.id, keyword, message.from_user.id)

            # Invalidate cache after trigger (to update stats)
            # Not strictly necessary but keeps things fresh

            # Process variables in reply text
            reply_text = filter_data.get('reply_text', '')
            if reply_text:
                reply_text = format_filter_variables(reply_text, message)

            # Build buttons
            buttons_markup = None
            filter_buttons = FilterDB.get_filter_buttons(filter_data['id'], chat.id)
            if filter_buttons:
                buttons_markup = build_inline_keyboard_from_buttons(filter_buttons)

            # Send the filter response based on type
            try:
                media_type = filter_data.get('media_type')
                media_file_id = filter_data.get('media_file_id')
                media_caption = filter_data.get('media_caption')

                if media_caption:
                    media_caption = format_filter_variables(media_caption, message)

                if media_type == 'photo' and media_file_id:
                    await message.reply_photo(
                        photo=media_file_id,
                        caption=media_caption or reply_text or "",
                        parse_mode='HTML',
                        reply_markup=buttons_markup
                    )
                elif media_type == 'video' and media_file_id:
                    await message.reply_video(
                        video=media_file_id,
                        caption=media_caption or reply_text or "",
                        parse_mode='HTML',
                        reply_markup=buttons_markup
                    )
                elif media_type == 'animation' and media_file_id:
                    await message.reply_animation(
                        animation=media_file_id,
                        caption=media_caption or reply_text or "",
                        parse_mode='HTML',
                        reply_markup=buttons_markup
                    )
                elif media_type == 'document' and media_file_id:
                    await message.reply_document(
                        document=media_file_id,
                        caption=media_caption or reply_text or "",
                        parse_mode='HTML',
                        reply_markup=buttons_markup
                    )
                elif media_type == 'audio' and media_file_id:
                    await message.reply_audio(
                        audio=media_file_id,
                        caption=media_caption or reply_text or "",
                        parse_mode='HTML',
                        reply_markup=buttons_markup
                    )
                elif media_type == 'voice' and media_file_id:
                    await message.reply_voice(
                        voice=media_file_id,
                        reply_markup=buttons_markup
                    )
                elif media_type == 'video_note' and media_file_id:
                    await message.reply_video_note(
                        video_note=media_file_id,
                        reply_markup=buttons_markup
                    )
                elif media_type == 'sticker' and media_file_id:
                    await message.reply_sticker(
                        sticker=media_file_id,
                        reply_markup=buttons_markup
                    )
                elif reply_text:
                    await message.reply_text(
                        reply_text,
                        parse_mode='HTML',
                        reply_markup=buttons_markup,
                        disable_web_page_preview=True
                    )

            except Exception as e:
                logger.error(f"Error sending filter response: {e}")

            # Only trigger first matching filter
            break


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.10 — NOTES COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def save_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /save <name> <text>
    or reply to a message/media with /save <name>
    
    Supports same formats as filters:
    - Text, Media, Buttons, Variables
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    if not await is_user_admin_filters(update, context, user.id):
        await message.reply_text(
            FilterNotesTemplates.NOT_ADMIN,
            parse_mode='HTML'
        )
        return

    args = message.text.split(None, 1) if message.text else []

    if len(args) < 2 and not message.reply_to_message:
        await message.reply_text(
            FilterNotesTemplates.NOTE_HELP,
            parse_mode='HTML'
        )
        return

    # Parse note name and content
    if len(args) >= 2:
        rest = args[1]
        parts = rest.split(None, 1)
        note_name = parts[0].lower().strip().lstrip('#')
        note_text = parts[1] if len(parts) > 1 else None
    else:
        note_name = None
        note_text = None

    if not note_name:
        await message.reply_text(
            "⚠️ <b>𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴏᴛᴇ ɴᴀᴍᴇ!</b>",
            parse_mode='HTML'
        )
        return

    # ─── Handle media from reply ───
    media_type = None
    media_file_id = None
    media_caption = None
    note_type = 'text'

    replied = message.reply_to_message

    if replied:
        if replied.photo:
            media_type = 'photo'
            media_file_id = replied.photo[-1].file_id
            media_caption = replied.caption_html or replied.caption
            note_type = 'photo'
            if not note_text:
                note_text = media_caption
        elif replied.video:
            media_type = 'video'
            media_file_id = replied.video.file_id
            media_caption = replied.caption_html or replied.caption
            note_type = 'video'
            if not note_text:
                note_text = media_caption
        elif replied.animation:
            media_type = 'animation'
            media_file_id = replied.animation.file_id
            media_caption = replied.caption_html or replied.caption
            note_type = 'animation'
            if not note_text:
                note_text = media_caption
        elif replied.document:
            media_type = 'document'
            media_file_id = replied.document.file_id
            media_caption = replied.caption_html or replied.caption
            note_type = 'document'
            if not note_text:
                note_text = media_caption
        elif replied.audio:
            media_type = 'audio'
            media_file_id = replied.audio.file_id
            media_caption = replied.caption_html or replied.caption
            note_type = 'audio'
            if not note_text:
                note_text = media_caption
        elif replied.voice:
            media_type = 'voice'
            media_file_id = replied.voice.file_id
            note_type = 'voice'
        elif replied.video_note:
            media_type = 'video_note'
            media_file_id = replied.video_note.file_id
            note_type = 'video_note'
        elif replied.sticker:
            media_type = 'sticker'
            media_file_id = replied.sticker.file_id
            note_type = 'sticker'
        elif replied.text and not note_text:
            note_text = replied.text_html or replied.text

    if not note_text and not media_file_id:
        await message.reply_text(
            "⚠️ <b>𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ɴᴏᴛᴇ ᴄᴏɴᴛᴇɴᴛ!</b>\n\n"
            "💡 <code>/save rules Be nice to everyone!</code>\n"
            "💡 Reply to a photo with <code>/save photo1</code>",
            parse_mode='HTML'
        )
        return

    # ─── Parse buttons ───
    buttons_data = []
    if note_text:
        note_text, buttons_data = parse_buttons_from_text(note_text)
        if buttons_data:
            note_type = note_type if media_file_id else 'text_buttons'

    # ─── Save to database ───
    added_by_name = user.first_name or "Unknown"
    note_id = NoteDB.save_note(
        chat_id=chat.id,
        note_name=note_name,
        note_text=note_text,
        added_by=user.id,
        added_by_name=added_by_name,
        media_type=media_type,
        media_file_id=media_file_id,
        media_caption=media_caption,
        note_type=note_type,
        is_private=False
    )

    if note_id is None:
        await message.reply_text(
            "❌ <b>𝐅ᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ɴᴏᴛᴇ!</b>",
            parse_mode='HTML'
        )
        return

    # Save buttons
    if buttons_data:
        NoteDB.add_note_buttons(note_id, chat.id, note_name, buttons_data)

    # Send confirmation
    has_buttons_text = f"✅ {len(buttons_data)} buttons" if buttons_data else "❌ None"
    has_media_text = f"✅ {get_media_type_emoji(media_type)} {media_type}" if media_type else "❌ None"

    response = FilterNotesTemplates.NOTE_SAVED.format(
        note_name=note_name,
        note_type=f"{get_media_type_emoji(note_type)} {note_type}",
        is_private="❌ No",
        has_buttons=has_buttons_text,
        has_media=has_media_text,
        added_by=f'<a href="tg://user?id={user.id}">{added_by_name}</a>'
    )

    await message.reply_text(response, parse_mode='HTML')


async def get_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /get <name> — Get a note
    /get <name> noformat — Get note without formatting
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        # In private, check if it's a private note callback
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    args = message.text.split(None, 2) if message.text else []
    if len(args) < 2:
        await message.reply_text(
            "⚠️ <b>𝐔sᴀɢᴇ:</b> <code>/get &lt;notename&gt;</code>",
            parse_mode='HTML'
        )
        return

    note_name = args[1].lower().strip().lstrip('#')
    no_format = len(args) > 2 and args[2].lower() == 'noformat'

    await send_note(update, context, chat.id, note_name, 
                    message, no_format=no_format)


async def hashtag_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle #notename messages to trigger notes
    """
    message = update.effective_message
    chat = update.effective_chat

    if not message or not message.text:
        return

    if chat.type == 'private':
        return

    text = message.text.strip()
    if not text.startswith('#'):
        return

    # Extract note name (first word after #)
    note_name = text[1:].split()[0].lower().strip()
    if not note_name:
        return

    await send_note(update, context, chat.id, note_name, message)


async def send_note(update, context, chat_id, note_name, message, 
                    no_format=False, send_to_pm=False, pm_chat_id=None):
    """
    Core function to send a note. Used by both /get and #notename.
    Handles private notes redirect, media, buttons, variables.
    """
    user = message.from_user if message.from_user else None
    
    note = NoteDB.get_note(chat_id, note_name)
    if not note:
        await message.reply_text(
            FilterNotesTemplates.NOTE_NOT_FOUND.format(note_name=note_name),
            parse_mode='HTML'
        )
        return

    # Log access
    if user:
        NoteDB.log_note_access(
            chat_id, note_name, user.id,
            'private' if send_to_pm else 'public'
        )

    # Check if private notes is enabled
    is_private_mode = PrivateNoteDB.get_private_notes(chat_id)
    
    if is_private_mode and not send_to_pm and update.effective_chat.type != 'private':
        # Send redirect message with button to get in PM
        bot_username = (await context.bot.get_me()).username
        pm_url = f"https://t.me/{bot_username}?start=note_{chat_id}_{note_name}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔒 𝐆ᴇᴛ 𝐍ᴏᴛᴇ ɪɴ 𝐏𝐌", 
                url=pm_url
            )]
        ])
        
        await message.reply_text(
            FilterNotesTemplates.PRIVATE_NOTE_REDIRECT.format(note_name=note_name),
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return

    # Prepare note content
    note_text = note.get('note_text', '')
    
    if note_text and not no_format:
        note_text = format_filter_variables(note_text, message)

    # Build buttons
    buttons_markup = None
    if not no_format:
        note_buttons = NoteDB.get_note_buttons(note['id'], chat_id)
        if note_buttons:
            buttons_markup = build_inline_keyboard_from_buttons(note_buttons)

    # Determine where to send
    target_chat = pm_chat_id if send_to_pm else None

    try:
        media_type = note.get('media_type')
        media_file_id = note.get('media_file_id')
        media_caption = note.get('media_caption')

        if media_caption and not no_format:
            media_caption = format_filter_variables(media_caption, message)

        parse = None if no_format else 'HTML'

        if no_format and note_text:
            # Send raw text without formatting
            if target_chat:
                await context.bot.send_message(
                    target_chat, note_text, 
                    reply_markup=buttons_markup
                )
            else:
                await message.reply_text(
                    f"<code>{note_text}</code>",
                    parse_mode='HTML'
                )
            return

        if media_type == 'photo' and media_file_id:
            if target_chat:
                await context.bot.send_photo(
                    target_chat, photo=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
            else:
                await message.reply_photo(
                    photo=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
        elif media_type == 'video' and media_file_id:
            if target_chat:
                await context.bot.send_video(
                    target_chat, video=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
            else:
                await message.reply_video(
                    video=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
        elif media_type == 'animation' and media_file_id:
            if target_chat:
                await context.bot.send_animation(
                    target_chat, animation=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
            else:
                await message.reply_animation(
                    animation=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
        elif media_type == 'document' and media_file_id:
            if target_chat:
                await context.bot.send_document(
                    target_chat, document=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
            else:
                await message.reply_document(
                    document=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
        elif media_type == 'audio' and media_file_id:
            if target_chat:
                await context.bot.send_audio(
                    target_chat, audio=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
            else:
                await message.reply_audio(
                    audio=media_file_id,
                    caption=media_caption or note_text or "",
                    parse_mode=parse, reply_markup=buttons_markup
                )
        elif media_type == 'voice' and media_file_id:
            if target_chat:
                await context.bot.send_voice(
                    target_chat, voice=media_file_id,
                    reply_markup=buttons_markup
                )
            else:
                await message.reply_voice(
                    voice=media_file_id,
                    reply_markup=buttons_markup
                )
        elif media_type == 'video_note' and media_file_id:
            if target_chat:
                await context.bot.send_video_note(
                    target_chat, video_note=media_file_id,
                    reply_markup=buttons_markup
                )
            else:
                await message.reply_video_note(
                    video_note=media_file_id,
                    reply_markup=buttons_markup
                )
        elif media_type == 'sticker' and media_file_id:
            if target_chat:
                await context.bot.send_sticker(
                    target_chat, sticker=media_file_id,
                    reply_markup=buttons_markup
                )
            else:
                await message.reply_sticker(
                    sticker=media_file_id,
                    reply_markup=buttons_markup
                )
        elif note_text:
            if target_chat:
                await context.bot.send_message(
                    target_chat, note_text,
                    parse_mode=parse, reply_markup=buttons_markup,
                    disable_web_page_preview=True
                )
            else:
                await message.reply_text(
                    note_text,
                    parse_mode=parse, reply_markup=buttons_markup,
                    disable_web_page_preview=True
                )

    except Exception as e:
        logger.error(f"Error sending note: {e}")
        await message.reply_text(
            f"❌ <b>𝐄ʀʀᴏʀ sᴇɴᴅɪɴɢ ɴᴏᴛᴇ:</b> {str(e)[:100]}",
            parse_mode='HTML'
        )


async def clear_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /clear <name> — Delete a note
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    if not await is_user_admin_filters(update, context, user.id):
        await message.reply_text(
            FilterNotesTemplates.NOT_ADMIN,
            parse_mode='HTML'
        )
        return

    args = message.text.split(None, 1) if message.text else []
    if len(args) < 2:
        await message.reply_text(
            "⚠️ <b>𝐔sᴀɢᴇ:</b> <code>/clear &lt;notename&gt;</code>",
            parse_mode='HTML'
        )
        return

    note_name = args[1].lower().strip().lstrip('#')
    deleted_by = user.first_name or "Unknown"

    success = NoteDB.delete_note(chat.id, note_name)

    if success:
        response = FilterNotesTemplates.NOTE_DELETED.format(
            note_name=note_name,
            deleted_by=f'<a href="tg://user?id={user.id}">{deleted_by}</a>'
        )
    else:
        response = FilterNotesTemplates.NOTE_NOT_FOUND.format(
            note_name=note_name
        )

    await message.reply_text(response, parse_mode='HTML')


async def clear_all_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /clearall — Delete all notes (with confirmation)
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status != 'creator' and user.id != OWNER_ID and user.id not in SUDO_USERS:
        await message.reply_text(
            "⚠️ <b>𝐎ɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴄᴀɴ ᴅᴏ ᴛʜɪs!</b>",
            parse_mode='HTML'
        )
        return

    count = NoteDB.count_notes(chat.id)
    if count == 0:
        await message.reply_text(
            FilterNotesTemplates.NO_NOTES,
            parse_mode='HTML'
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ 𝐘ᴇs, 𝐃ᴇʟᴇᴛᴇ 𝐀ʟʟ",
                callback_data=f"clearall_confirm_{chat.id}_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ 𝐂ᴀɴᴄᴇʟ",
                callback_data=f"clearall_cancel_{user.id}"
            )
        ]
    ])

    await message.reply_text(
        FilterNotesTemplates.CONFIRM_DELETE_ALL_NOTES.format(count=count),
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def clearall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clearall confirmation callbacks"""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("clearall_confirm_"):
        parts = data.split("_")
        chat_id = int(parts[2])
        original_user = int(parts[3])

        if user.id != original_user:
            await query.answer("⚠️ 𝐓ʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
            return

        count = NoteDB.delete_all_notes(chat_id)
        deleted_by = user.first_name or "Unknown"

        await query.edit_message_text(
            FilterNotesTemplates.ALL_NOTES_DELETED.format(
                count=count,
                deleted_by=f'<a href="tg://user?id={user.id}">{deleted_by}</a>'
            ),
            parse_mode='HTML'
        )

    elif data.startswith("clearall_cancel_"):
        original_user = int(data.split("_")[2])
        if user.id != original_user:
            await query.answer("⚠️ 𝐓ʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
            return

        await query.edit_message_text(
            "✅ <b>𝐂ᴀɴᴄᴇʟʟᴇᴅ!</b> 𝐍ᴏᴛᴇs ᴀʀᴇ sᴀғᴇ.",
            parse_mode='HTML'
        )


async def list_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /notes or /saved — List all notes in the chat
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    notes_list = NoteDB.get_all_notes(chat.id)

    if not notes_list:
        await message.reply_text(
            FilterNotesTemplates.NO_NOTES,
            parse_mode='HTML'
        )
        return

    is_private = PrivateNoteDB.get_private_notes(chat.id)
    private_mode = "✅ ON (PM)" if is_private else "❌ OFF (Group)"
    chat_name = chat.title or "This Chat"

    response = FilterNotesTemplates.NOTE_LIST_HEADER.format(
        chat_name=chat_name,
        count=len(notes_list),
        private_mode=private_mode
    )

    for i, n in enumerate(notes_list, 1):
        emoji = get_note_type_icon(n.get('note_type', 'text'), n.get('is_private', False))
        type_info = n.get('note_type', 'text')
        if n.get('media_type'):
            type_info = f"{n['media_type']}"
        if n.get('is_private'):
            type_info += " 🔒"
        
        usage = n.get('usage_count', 0)
        if usage > 0:
            type_info += f" ({usage}x)"

        response += FilterNotesTemplates.NOTE_LIST_ITEM.format(
            num=i,
            emoji=emoji,
            note_name=n['note_name'],
            type_info=type_info
        ) + "\n"

    response += FilterNotesTemplates.NOTE_LIST_FOOTER

    # Handle long messages
    if len(response) > 4000:
        pages = []
        current_page = FilterNotesTemplates.NOTE_LIST_HEADER.format(
            chat_name=chat_name,
            count=len(notes_list),
            private_mode=private_mode
        )
        
        for i, n in enumerate(notes_list, 1):
            emoji = get_note_type_icon(n.get('note_type', 'text'), n.get('is_private', False))
            type_info = n.get('note_type', 'text')
            line = FilterNotesTemplates.NOTE_LIST_ITEM.format(
                num=i, emoji=emoji, note_name=n['note_name'], type_info=type_info
            ) + "\n"
            
            if len(current_page) + len(line) > 3500:
                pages.append(current_page)
                current_page = f"✦ 𝐍ᴏᴛᴇs 𝐋ɪsᴛ (ᴄᴏɴᴛ.) ✦\n━━━━━━━━━━━━━━━━━━\n"
            
            current_page += line
        
        current_page += FilterNotesTemplates.NOTE_LIST_FOOTER
        pages.append(current_page)
        
        for page in pages:
            await message.reply_text(page, parse_mode='HTML')
    else:
        await message.reply_text(response, parse_mode='HTML')


async def private_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /privatenotes on — Send notes in PM
    /privatenotes off — Send notes in group
    """
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await message.reply_text(
            FilterNotesTemplates.GROUP_ONLY,
            parse_mode='HTML'
        )
        return

    if not await is_user_admin_filters(update, context, user.id):
        await message.reply_text(
            FilterNotesTemplates.NOT_ADMIN,
            parse_mode='HTML'
        )
        return

    args = message.text.split(None, 1) if message.text else []
    
    if len(args) < 2:
        current = PrivateNoteDB.get_private_notes(chat.id)
        status = "✅ ON" if current else "❌ OFF"
        await message.reply_text(
            f"✦ 𝐏ʀɪᴠᴀᴛᴇ 𝐍ᴏᴛᴇs 𝐒ᴛᴀᴛᴜs ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🔒 𝐒ᴇᴛᴛɪɴɢs ]═══╗\n"
            f"║ ✧ 𝐒ᴛᴀᴛᴜs: {status}\n"
            f"╚════════════════════╝\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 <code>/privatenotes on</code> — Enable\n"
            f"💡 <code>/privatenotes off</code> — Disable\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            parse_mode='HTML'
        )
        return

    setting = args[1].lower().strip()
    updated_by = user.first_name or "Unknown"

    if setting in ['on', 'yes', 'true', '1', 'enable']:
        PrivateNoteDB.set_private_notes(chat.id, True, user.id)
        response = FilterNotesTemplates.PRIVATE_NOTES_ON.format(
            updated_by=f'<a href="tg://user?id={user.id}">{updated_by}</a>'
        )
    elif setting in ['off', 'no', 'false', '0', 'disable']:
        PrivateNoteDB.set_private_notes(chat.id, False, user.id)
        response = FilterNotesTemplates.PRIVATE_NOTES_OFF.format(
            updated_by=f'<a href="tg://user?id={user.id}">{updated_by}</a>'
        )
    else:
        response = (
            "⚠️ <b>𝐈ɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ!</b>\n\n"
            "💡 <code>/privatenotes on</code>\n"
            "💡 <code>/privatenotes off</code>"
        )

    await message.reply_text(response, parse_mode='HTML')


async def note_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /notehelp — Show notes help
    """
    await update.effective_message.reply_text(
        FilterNotesTemplates.NOTE_HELP,
        parse_mode='HTML'
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.11 — PRIVATE NOTE START HANDLER (for PM notes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_private_note_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start note_CHATID_NOTENAME deep link for private notes.
    This should be integrated into your existing /start handler.
    
    Add this check at the beginning of your start_command:
    
    if args and args[0].startswith('note_'):
        await handle_private_note_start(update, context)
        return
    """
    message = update.effective_message
    user = update.effective_user
    
    args = context.args
    if not args or not args[0].startswith('note_'):
        return False
    
    try:
        parts = args[0].split('_', 2)
        if len(parts) < 3:
            return False
        
        chat_id = int(parts[1])
        note_name = parts[2]
        
        # Get the note
        note = NoteDB.get_note(chat_id, note_name)
        if not note:
            await message.reply_text(
                FilterNotesTemplates.NOTE_NOT_FOUND.format(note_name=note_name),
                parse_mode='HTML'
            )
            return True
        
        # Send note to PM
        await send_note(
            update, context, chat_id, note_name, message,
            send_to_pm=True, pm_chat_id=user.id
        )
        
        return True
    except Exception as e:
        logger.error(f"Error handling private note start: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.12 — INLINE QUERY FOR NOTES (Optional Advanced Feature)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def inline_notes_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline queries for notes (optional feature)
    User can type @botname #notename in any chat
    """
    query = update.inline_query
    if not query:
        return

    query_text = query.query.strip()
    if not query_text.startswith('#'):
        return

    note_name = query_text[1:].lower().strip()
    user_id = query.from_user.id

    # This is tricky for inline - we'd need to know which chat's notes
    # For now, we'll skip this or implement later
    # Just provide a placeholder
    results = []
    await query.answer(results, cache_time=0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.13 — SECTION 6 HELP CALLBACK (for help menu integration)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECTION6_HELP_TEXT = """
✦ 𝐅ɪʟᴛᴇʀs & 𝐍ᴏᴛᴇs ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📖 𝐌ᴏᴅᴜʟᴇ 𝐈ɴғᴏ ]═══╗
║
║ 🎯 <b>𝐅ɪʟᴛᴇʀs:</b>
║ Auto-reply when someone says
║ a specific keyword. Supports
║ text, media, buttons & variables.
║
║ 📝 <b>𝐍ᴏᴛᴇs:</b>
║ Save & retrieve information
║ using #notename or /get command.
║ Supports private notes in PM.
║
╚════════════════════╝
━━━━━━━━━━━━━━━━━━

🎯 <b>𝐅ɪʟᴛᴇʀ 𝐂ᴏᴍᴍᴀɴᴅs:</b>
├ /filter &lt;keyword&gt; &lt;reply&gt; — Add filter
├ /filters — List all filters
├ /stop &lt;keyword&gt; — Remove filter
├ /stopall — Remove all filters
├ /filtersearch &lt;text&gt; — Search
├ /filterstats — View statistics
└ /filterhelp — Detailed help

📝 <b>𝐍ᴏᴛᴇ 𝐂ᴏᴍᴍᴀɴᴅs:</b>
├ /save &lt;name&gt; &lt;text&gt; — Save note
├ /get &lt;name&gt; — Get note
├ #notename — Get note
├ /notes — List all notes
├ /saved — Same as /notes
├ /clear &lt;name&gt; — Delete note
├ /clearall — Delete all notes
├ /privatenotes on/off — PM mode
└ /notehelp — Detailed help

━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""

async def section6_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback handler for help menu Section 6 button"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 𝐅ɪʟᴛᴇʀ 𝐇ᴇʟᴘ", callback_data="help_filter_detail"),
            InlineKeyboardButton("📝 𝐍ᴏᴛᴇ 𝐇ᴇʟᴘ", callback_data="help_note_detail")
        ],
        [
            InlineKeyboardButton("◀️ 𝐁ᴀᴄᴋ", callback_data="help_back_main")
        ]
    ])

    await query.edit_message_text(
        SECTION6_HELP_TEXT,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def filter_detail_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed filter help callback"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ 𝐁ᴀᴄᴋ", callback_data="help_section6")]
    ])

    await query.edit_message_text(
        FilterNotesTemplates.FILTER_HELP,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def note_detail_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed note help callback"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ 𝐁ᴀᴄᴋ", callback_data="help_section6")]
    ])

    await query.edit_message_text(
        FilterNotesTemplates.NOTE_HELP,
        parse_mode='HTML',
        reply_markup=keyboard
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.14 — REGISTER ALL SECTION 6 HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def register_section6_handlers(app):
    """
    Register all Section 6 handlers with the application.
    Call this in your main setup function.
    
    Usage:
        register_section6_handlers(app)
    """
    
    # ═══ FILTER COMMAND HANDLERS ═══
    app.add_handler(CommandHandler(
        "filter", filter_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "stop", stop_filter_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "stopall", stop_all_filters_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        ["filters", "listfilters"], list_filters_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "filtersearch", filter_search_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "filterstats", filter_stats_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "filterhelp", filter_help_command, 
        block=False
    ))

    # ═══ NOTE COMMAND HANDLERS ═══
    app.add_handler(CommandHandler(
        "save", save_note_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "get", get_note_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        ["clear", "delete"], clear_note_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "clearall", clear_all_notes_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        ["notes", "saved"], list_notes_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "privatenotes", private_notes_command, 
        block=False
    ))
    app.add_handler(CommandHandler(
        "notehelp", note_help_command, 
        block=False
    ))

    # ═══ CALLBACK QUERY HANDLERS ═══
    app.add_handler(CallbackQueryHandler(
        stopall_callback, 
        pattern=r"^stopall_(confirm|cancel)_"
    ))
    app.add_handler(CallbackQueryHandler(
        clearall_callback, 
        pattern=r"^clearall_(confirm|cancel)_"
    ))
    app.add_handler(CallbackQueryHandler(
        section6_help_callback, 
        pattern=r"^help_section6$"
    ))
    app.add_handler(CallbackQueryHandler(
        filter_detail_help_callback, 
        pattern=r"^help_filter_detail$"
    ))
    app.add_handler(CallbackQueryHandler(
        note_detail_help_callback, 
        pattern=r"^help_note_detail$"
    ))

    # ═══ HASHTAG NOTE HANDLER ═══
    # This catches messages starting with # for notes
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^#\S+') & ~filters.COMMAND,
        hashtag_note_handler,
        block=False
    ))

    # ═══ FILTER TRIGGER HANDLER ═══
    # This MUST be added LAST or with a low group number
    # so it doesn't interfere with other handlers
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
        filter_trigger_handler,
        block=False
    ), group=99)  # High group number = runs after other handlers

    logger.info("✅ Section 6: Filters & Notes handlers registered!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.15 — INTEGRATION WITH /start COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
╔═════════════════════════════════════════════════════╗
║  ADD THIS TO YOUR EXISTING /start COMMAND HANDLER  ║
╚═════════════════════════════════════════════════════╝

In your existing start_command function, add at the TOP:

    async def start_command(update, context):
        args = context.args
        
        # ─── Handle Private Note Deep Link ───
        if args and args[0].startswith('note_'):
            result = await handle_private_note_start(update, context)
            if result:
                return
        
        # ... rest of your start command ...
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.16 — INTEGRATION WITH HELP MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
╔═════════════════════════════════════════════════════╗
║  ADD THIS BUTTON TO YOUR HELP MENU KEYBOARD        ║
╚═════════════════════════════════════════════════════╝

In your help command's inline keyboard, add:

    InlineKeyboardButton(
        "🎯 𝐅ɪʟᴛᴇʀs & 📝 𝐍ᴏᴛᴇs", 
        callback_data="help_section6"
    )
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.17 — INITIALIZATION (Call this at bot startup)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_section6():
    """
    Initialize Section 6: Create tables and verify setup.
    Call this during bot startup.
    """
    logger.info("🔄 Initializing Section 6: Filters & Notes...")
    create_filters_notes_tables()
    logger.info("✅ Section 6: Filters & Notes initialized!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6.18 — COMPLETE INTEGRATION EXAMPLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
╔══════════════════════════════════════════════════════════╗
║          COMPLETE INTEGRATION IN YOUR bot.py            ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  In your main() function or bot setup:                   ║
║                                                          ║
║  1. Call init_section6() during startup:                 ║
║                                                          ║
║     def main():                                          ║
║         # ... your existing setup ...                    ║
║         init_section6()  # <-- Add this                  ║
║                                                          ║
║  2. Register handlers:                                   ║
║                                                          ║
║     app = ApplicationBuilder().token(TOKEN).build()      ║
║     # ... your existing handlers ...                     ║
║     register_section6_handlers(app)  # <-- Add this      ║
║                                                          ║
║  3. Update /start to handle private notes:               ║
║     (See section 6.15 above)                             ║
║                                                          ║
║  4. Add help button:                                     ║
║     (See section 6.16 above)                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

# ============================================================
# SECTION 7: FUN & GAMES — COMPLETION PART
# ============================================================
# Yeh file wahan se start ho rahi hai jahan pehli file cut off hui thi
# Line 2542 ke baad se - fun_quote callback ke andar se
# ============================================================
# 
# PASTE INSTRUCTIONS:
# ──────────────────────────────────────────────────────────
# Apni pehli file (jo tum upload kiya tha) mein:
#   - Line 2540 tak ka code rakhna (InlineKeyboardButton("📜 tak)
#   - Uske baad yeh POORA file paste karna
#   - Neeche REGISTRATION CODE bhi hai — woh ZAROOR add karna
# ──────────────────────────────────────────────────────────

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [CONTINUATION] fun_quote callback (line 2540 ke baad)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# (Yeh code fun_section_callback function ke andar hai)
# Neeche se paste karo LINE 2540 ke bad:

"""
                    InlineKeyboardButton("📜 𝐍𝐞𝐱𝐭", callback_data="fun_quote"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TRIVIA (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_trivia":
            chat_id = query.message.chat.id
            user_id = query.from_user.id
            question_data = random.choice(TRIVIA_QUESTIONS)
            
            # Store active trivia
            active_trivia[chat_id] = {
                "question": question_data,
                "user_id": user_id,
                "timestamp": time.time()
            }
            
            text = f\"\"\"
✦ 𝐓𝐑𝐈𝐕𝐈𝐀 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🧠 𝐐ᴜɪᴢ 𝐓ɪᴍᴇ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  ❓ {question_data['question']}
║
║  {chr(10).join(['║  ' + opt for opt in question_data['options']])}
║
║  ⏳ 𝐉𝐚𝐥𝐝𝐢 𝐣𝐚𝐰𝐚𝐚𝐛 𝐝𝐨!
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
\"\"\"
            keyboard = [
                [
                    InlineKeyboardButton("🅰️ A", callback_data=f"trivia_A_{chat_id}"),
                    InlineKeyboardButton("🅱️ B", callback_data=f"trivia_B_{chat_id}"),
                ],
                [
                    InlineKeyboardButton("🅲 C", callback_data=f"trivia_C_{chat_id}"),
                    InlineKeyboardButton("🅳 D", callback_data=f"trivia_D_{chat_id}"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DARE ACCEPTED
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "dare_accepted":
            text = f\"\"\"
✦ 𝐃𝐀𝐑𝐄 𝐀𝐂𝐂𝐄𝐏𝐓𝐄𝐃 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ✅ 𝐁𝐫𝐚𝐯𝐞 𝐇𝐨! ]═══╗
║
║  👤 {display_name}
║
║  🏆 𝐃𝐚𝐫𝐞 𝐚𝐜𝐜𝐞𝐩𝐭 𝐤𝐢𝐲𝐚!
║  𝐂𝐡𝐚𝐦𝐩𝐢𝐨𝐧 𝐡𝐚𝐢 𝐭𝐮! 🔥
║
║  😈 𝐀𝐛 𝐤𝐚𝐫𝐤𝐞 𝐝𝐢𝐤𝐡𝐚!
║  𝐒𝐚𝐛 𝐝𝐞𝐤𝐡 𝐫𝐚𝐡𝐞 𝐡𝐚𝐢𝐧! 👀
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
\"\"\"
            keyboard = [
                [
                    InlineKeyboardButton("🔥 𝐍𝐞𝐱𝐭 𝐃𝐚𝐫𝐞", callback_data="fun_dare"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 8BALL INFO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_8ball_info":
            text = f\"\"\"
✦ 𝐌𝐀𝐆𝐈𝐂 𝟖𝐁𝐀𝐋𝐋 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔮 𝟖𝐁𝐚𝐥𝐥 ]═══╗
║
║  🔮 𝐊𝐨𝐢 𝐛𝐡𝐢 𝐬𝐚𝐰𝐚𝐚𝐥 𝐩𝐮𝐜𝐡𝐨!
║  𝐉𝐚𝐝𝐮𝐢 𝟖 𝐛𝐚𝐥𝐥 𝐣𝐚𝐰𝐚𝐚𝐛 𝐝𝐞𝐠𝐚!
║
║  📝 𝐔𝐬𝐞:
║  /8ball <your question>
║
║  💡 𝐄𝐱𝐚𝐦𝐩𝐥𝐞:
║  /8ball Kya main pass hounga?
║  /8ball Kya woh mujhe pasand karta?
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
\"\"\"
            keyboard = [
                [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    except Exception as e:
        print(f"Error in fun_section_callback: {e}")
        try:
            await query.answer("❌ Error! Dubara try karo!", show_alert=True)
        except:
            pass
"""

# ============================================================
# TRIVIA ANSWER CALLBACK HANDLER
# ============================================================
# Yeh alag handler hai — fun_section_callback ke BAAD add karo

async def trivia_answer_callback(update, context):
    """Handle trivia answer callbacks"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        query = update.callback_query
        await query.answer()
        
        data = query.data  # e.g., "trivia_A_123456789"
        parts = data.split("_")
        
        if len(parts) < 3:
            return
        
        user_answer = parts[1]   # A, B, C, or D
        chat_id = int(parts[2])
        
        user = query.from_user
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        # Check if trivia is active for this chat
        if chat_id not in active_trivia:
            await query.answer("⏰ Trivia expire ho gayi! Naya game shuru karo!", show_alert=True)
            return
        
        trivia_data = active_trivia[chat_id]
        question_data = trivia_data["question"]
        correct_answer = question_data["answer"]
        
        # Remove from active games
        del active_trivia[chat_id]
        
        if user_answer == correct_answer:
            result_emoji = "🎉"
            result_text = "𝐒𝐀𝐇𝐈! 𝐁𝐈𝐋𝐊𝐔𝐋 𝐒𝐀𝐇𝐈!"
            result_message = "🏆 Wah! Tu genius hai! Bilkul sahi jawab diya!"
            result_bar = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"
            vibe = "✅ 𝐂𝐎𝐑𝐑𝐄𝐂𝐓"
        else:
            result_emoji = "💀"
            result_text = "𝐆𝐀𝐋𝐀𝐓! 𝐁𝐈𝐋𝐊𝐔𝐋 𝐆𝐀𝐋𝐀𝐓!"
            result_message = f"😅 Tera jawab: {user_answer} | Sahi jawab: {correct_answer}"
            result_bar = "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥"
            vibe = "❌ 𝐖𝐑𝐎𝐍𝐆"
        
        text = f"""
✦ 𝐓𝐑𝐈𝐕𝐈𝐀 𝐑𝐄𝐒𝐔𝐋𝐓 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ {result_emoji} 𝐀𝐧𝐬𝐰𝐞𝐫 ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  ❓ {question_data['question']}
║
║  {result_bar}
║
║  🎯 {vibe}
║  {result_text}
║
║  📝 {result_message}
║
║  💡 𝐄𝐱𝐩𝐥𝐚𝐧𝐚𝐭𝐢𝐨𝐧:
║  {question_data['explanation']}
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🧠 𝐍𝐞𝐱𝐭 𝐐𝐮𝐞𝐬𝐭𝐢𝐨𝐧", callback_data="fun_trivia"),
                InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    except Exception as e:
        print(f"Error in trivia_answer_callback: {e}")


# ============================================================
# REMAINING COMMAND HANDLERS
# ============================================================

async def flip_command(update, context):
    """Flip a coin — Heads ya Tails"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        result = random.choice(["HEADS", "TAILS"])
        
        if result == "HEADS":
            emoji = "👑"
            result_text = "𝐇𝐄𝐀𝐃𝐒 (𝐂𝐡𝐢𝐭)"
            message = "👑 Heads aaya! Kismat chamak rahi hai teri!"
            visual = """
    ╭──────────╮
    │  🪙 HEAD │
    │  WINNER  │
    ╰──────────╯"""
        else:
            emoji = "🔄"
            result_text = "𝐓𝐀𝐈𝐋𝐒 (𝐏𝐚𝐭)"
            message = "🔄 Tails aaya! Ulti kismat!"
            visual = """
    ╭──────────╮
    │  🪙 TAIL │
    │  BETTER  │
    ╰──────────╯"""
        
        text = f"""
✦ 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🪙 𝐂ᴏɪɴ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  🪙 𝐅𝐥𝐢𝐩𝐩𝐢𝐧𝐠...
{visual}
║
║  {emoji} 𝐑𝐞𝐬𝐮𝐥𝐭: {result_text}
║
║  {message}
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
🪙 𝐅𝐥𝐢𝐩 𝐀𝐠𝐚𝐢𝐧? /flip
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🪙 𝐅𝐥𝐢𝐩 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_coin"),
                InlineKeyboardButton("🎲 𝐃𝐢𝐜𝐞", callback_data="fun_dice"),
            ],
            [
                InlineKeyboardButton("🎮 𝐌𝐨𝐫𝐞 𝐆𝐚𝐦𝐞𝐬", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
        
    except Exception as e:
        print(f"Error in flip_command: {e}")
        await update.message.reply_text("❌ 𝐊𝐮𝐜𝐡 𝐠𝐚𝐥𝐚𝐭 𝐡𝐨 𝐠𝐚𝐲𝐚! 𝐃𝐮𝐛𝐚𝐫𝐚 𝐭𝐫𝐲 𝐤𝐚𝐫𝐨!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOVE METER COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def love_command(update, context):
    """Calculate love percentage between two people"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        # Get target person
        target_name = None
        
        # Check if replying to someone
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            target_user = update.message.reply_to_message.from_user
            target_name = target_user.first_name
            if target_user.last_name:
                target_name += f" {target_user.last_name}"
        
        # Check if name/username given as argument
        elif context.args:
            target_name = " ".join(context.args)
            # Remove @ if username
            target_name = target_name.lstrip("@")
        
        # No target given
        if not target_name:
            await update.message.reply_text(
                f"""
✦ 𝐋𝐎𝐕𝐄 𝐌𝐄𝐓𝐄𝐑 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 💕 𝐋ᴏᴠᴇ ]═══╗
║
║  💘 𝐊𝐢𝐬𝐢 𝐤𝐚 𝐧𝐚𝐚𝐦 𝐝𝐨!
║
║  📝 𝐔𝐬𝐞:
║  • /love @username
║  • /love <name>
║  • Reply karke /love
║
║  💡 𝐄𝐱𝐚𝐦𝐩𝐥𝐞:
║  /love @Rahul
║  /love Priya
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
""",
                parse_mode=None
            )
            return
        
        # Calculate love percentage (seed based on both names for consistency)
        seed_str = f"{display_name.lower()}{target_name.lower()}"
        seed_val = sum(ord(c) for c in seed_str)
        random.seed(seed_val)
        love_percent = random.randint(0, 100)
        random.seed()  # Reset seed
        
        # Build love bar
        filled = int(love_percent / 10)
        empty = 10 - filled
        if love_percent >= 80:
            bar_emoji = "💖"
        elif love_percent >= 50:
            bar_emoji = "💛"
        else:
            bar_emoji = "🩶"
        
        love_bar = f"{bar_emoji * filled}{'🤍' * empty}"
        
        # Get response based on percentage
        if love_percent <= 25:
            response = random.choice(LOVE_METER_RESPONSES["low"])
            level = "💔 𝐋𝐨𝐰 𝐋𝐨𝐯𝐞"
        elif love_percent <= 60:
            response = random.choice(LOVE_METER_RESPONSES["medium"])
            level = "💛 𝐌𝐞𝐝𝐢𝐮𝐦 𝐋𝐨𝐯𝐞"
        elif love_percent <= 90:
            response = random.choice(LOVE_METER_RESPONSES["high"])
            level = "💕 𝐇𝐢𝐠𝐡 𝐋𝐨𝐯𝐞"
        else:
            response = random.choice(LOVE_METER_RESPONSES["perfect"])
            level = "💘 𝐏𝐄𝐑𝐅𝐄𝐂𝐓 𝐋𝐎𝐕𝐄"
        
        # Cute heart scale
        if love_percent == 100:
            heart_display = "💘💘💘💘💘💘💘💘💘💘"
        elif love_percent >= 80:
            heart_display = "💕💕💕💕💕💕💕💕💕🤍"
        elif love_percent >= 60:
            heart_display = "💛💛💛💛💛💛💛🤍🤍🤍"
        elif love_percent >= 40:
            heart_display = "🧡🧡🧡🧡🧡🤍🤍🤍🤍🤍"
        elif love_percent >= 20:
            heart_display = "🩶🩶🩶🤍🤍🤍🤍🤍🤍🤍"
        else:
            heart_display = "💔🤍🤍🤍🤍🤍🤍🤍🤍🤍"
        
        text = f"""
✦ 𝐋𝐎𝐕𝐄 𝐌𝐄𝐓𝐄𝐑 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 💕 𝐋ᴏᴠᴇ 𝐀𝐧𝐚𝐥𝐲𝐬𝐢𝐬 ]═══╗
║
║  💑 𝐂𝐨𝐮𝐩𝐥𝐞:
║  💫 {display_name}
║  ❤️ × ❤️
║  💫 {target_name}
║
║  ━━━━━━━━━━━━━━━
║
║  💯 𝐋𝐨𝐯𝐞 %: {love_percent}%
║  🎯 𝐋𝐞𝐯𝐞𝐥: {level}
║
║  {heart_display}
║  {love_bar}
║
║  💌 {response}
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("💕 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_love_info"),
                InlineKeyboardButton("🎮 𝐌𝐨𝐫𝐞 𝐆𝐚𝐦𝐞𝐬", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in love_command: {e}")
        await update.message.reply_text("❌ 𝐊𝐮𝐜𝐡 𝐠𝐚𝐥𝐚𝐭 𝐡𝐨 𝐠𝐚𝐲𝐚! 𝐃𝐮𝐛𝐚𝐫𝐚 𝐭𝐫𝐲 𝐤𝐚𝐫𝐨!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROAST COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def roast_command(update, context):
    """Roast a user — mazaak mein!"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        user = update.effective_user
        if not user:
            return
        
        # Check who to roast
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            target = update.message.reply_to_message.from_user
            target_name = target.first_name
            if target.last_name:
                target_name += f" {target.last_name}"
        else:
            target_name = user.first_name
            if user.last_name:
                target_name += f" {user.last_name}"
        
        roast = random.choice(ROAST_MESSAGES)
        intensity = random.choice([
            "🌶️ Mild",
            "🌶️🌶️ Medium", 
            "🌶️🌶️🌶️ Hot 🔥",
            "🌶️🌶️🌶️🌶️ Extra Hot 🥵",
            "💀☢️ NUCLEAR ROAST ☢️💀"
        ])
        
        text = f"""
✦ 𝐑𝐎𝐀𝐒𝐓 𝐌𝐎𝐃𝐄 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔥 𝐑ᴏᴀsᴛ ]═══╗
║
║  🎯 𝐓𝐚𝐫𝐠𝐞𝐭:
║  💀 {target_name}
║
║  🌶️ 𝐈𝐧𝐭𝐞𝐧𝐬𝐢𝐭𝐲:
║  {intensity}
║
║  ━━━━━━━━━━━━━━━
║
║  🔥 {roast}
║
║  ━━━━━━━━━━━━━━━
║  😂 𝐌𝐚𝐳𝐚𝐚𝐤 𝐡𝐚𝐢 𝐛𝐡𝐚𝐢!
║  𝐁𝐮𝐫𝐚 𝐦𝐚𝐭 𝐦𝐚𝐧𝐨! 💀🤣
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🔥 𝐑𝐨𝐚𝐬𝐭 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_roast"),
                InlineKeyboardButton("💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭", callback_data="fun_compliment"),
            ],
            [
                InlineKeyboardButton("🎮 𝐌𝐨𝐫𝐞 𝐆𝐚𝐦𝐞𝐬", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in roast_command: {e}")
        await update.message.reply_text("❌ Error! Dubara try karo!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPLIMENT COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def compliment_command(update, context):
    """Send a sweet compliment!"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        user = update.effective_user
        if not user:
            return
        
        # Check who to compliment
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            target = update.message.reply_to_message.from_user
            target_name = target.first_name
            if target.last_name:
                target_name += f" {target.last_name}"
        else:
            target_name = user.first_name
            if user.last_name:
                target_name += f" {user.last_name}"
        
        compliment = random.choice(COMPLIMENT_MESSAGES)
        sweetness = random.choice([
            "🍫 Chocolate Level",
            "🍯 Honey Sweet",
            "🧁 Cupcake Vibes",
            "🍰 Cake Wala Pyaar",
            "🎂 Birthday Special ✨",
            "🌹 Rose Level Romantic",
            "💎 Diamond Pure",
        ])
        
        text = f"""
✦ 𝐂𝐎𝐌𝐏𝐋𝐈𝐌𝐄𝐍𝐓 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 💖 𝐒𝐰𝐞𝐞𝐭 𝐕𝐢𝐛𝐞𝐬 ]═══╗
║
║  🌸 𝐅𝐨𝐫:
║  ✨ {target_name}
║
║  🍬 𝐒𝐰𝐞𝐞𝐭𝐧𝐞𝐬𝐬:
║  {sweetness}
║
║  ━━━━━━━━━━━━━━━
║
║  💝 {compliment}
║
║  ━━━━━━━━━━━━━━━
║  💖 𝐒𝐩𝐫𝐞𝐚𝐝 𝐋𝐨𝐯𝐞!
║  𝐃𝐮𝐧𝐢𝐲𝐚 𝐛𝐞𝐡𝐭𝐚𝐫 𝐛𝐚𝐧𝐞𝐠𝐢! 🌍
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("💖 𝐌𝐨𝐫𝐞", callback_data="fun_compliment"),
                InlineKeyboardButton("🔥 𝐑𝐨𝐚𝐬𝐭", callback_data="fun_roast"),
            ],
            [
                InlineKeyboardButton("🎮 𝐌𝐨𝐫𝐞 𝐆𝐚𝐦𝐞𝐬", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in compliment_command: {e}")
        await update.message.reply_text("❌ Error! Dubara try karo!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JOKE COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def joke_command(update, context):
    """Send a random Hinglish joke!"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        joke = random.choice(JOKES_LIST)
        laugh_level = random.choice([
            "😂 Halki Hansi",
            "🤣 Puri Hansi",
            "😆 LOL Wala",
            "💀 Dead ho gaya",
            "🤡 Comedy King Level",
            "😹 Tears aa gaye",
            "🥴 Pagal ho gaya main",
        ])
        
        text = f"""
✦ 𝐉𝐎𝐊𝐄 𝐎𝐅 𝐓𝐇𝐄 𝐌𝐎𝐌𝐄𝐍𝐓 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 😂 𝐇𝐚𝐬𝐨 𝐙𝐚𝐫𝐚 ]═══╗
║
║  👤 𝐅𝐨𝐫: {display_name}
║  🎭 𝐋𝐞𝐯𝐞𝐥: {laugh_level}
║
║  ━━━━━━━━━━━━━━━
║
║  😄 {joke['q']}
║
║  🤣 {joke['a']}
║
║  ━━━━━━━━━━━━━━━
║  😂😂😂😂😂😂😂😂😂😂
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("😂 𝐍𝐞𝐱𝐭 𝐉𝐨𝐤𝐞", callback_data="fun_joke"),
                InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in joke_command: {e}")
        await update.message.reply_text("❌ Error! Dubara try karo!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUOTE COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def quote_command(update, context):
    """Send motivational quote of the day!"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        from datetime import datetime
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        # Use date as seed for "Quote of the Day" effect
        today = datetime.now().strftime("%Y%m%d")
        random.seed(int(today) + user.id)
        quote_data = random.choice(QUOTES_LIST)
        random.seed()  # Reset seed
        
        motivation_mode = random.choice([
            "⚡ Energy Mode",
            "🔥 Fire Mode",
            "💪 Beast Mode",
            "🚀 Rocket Mode",
            "👑 King Mode",
            "🌟 Star Mode",
            "💎 Diamond Mode",
            "🦁 Lion Mode",
            "🏆 Champion Mode",
        ])
        
        # Day greeting based on time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "☀️ 𝐒𝐮𝐛𝐡 𝐤𝐢 𝐮𝐩𝐚𝐣!"
        elif 12 <= hour < 17:
            greeting = "🌤️ 𝐃𝐨𝐩𝐡𝐚𝐫 𝐤𝐢 𝐝𝐨𝐳 𝐨𝐟 𝐦𝐨𝐭𝐢𝐯𝐚𝐭𝐢𝐨𝐧!"
        elif 17 <= hour < 20:
            greeting = "🌅 𝐒𝐡𝐚𝐚𝐦 𝐤𝐢 𝐯𝐢𝐛𝐞𝐬!"
        else:
            greeting = "🌙 𝐑𝐚𝐚𝐭 𝐤𝐢 𝐩𝐫𝐞𝐫𝐚𝐧𝐚!"
        
        text = f"""
✦ 𝐐𝐔𝐎𝐓𝐄 𝐎𝐅 𝐓𝐇𝐄 𝐃𝐀𝐘 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📜 𝐌𝐨𝐭𝐢𝐯𝐚𝐭𝐢𝐨𝐧 ]═══╗
║
║  👤 𝐅𝐨𝐫: {display_name}
║  🕐 {greeting}
║  💪 𝐌𝐨𝐝𝐞: {motivation_mode}
║
║  ━━━━━━━━━━━━━━━
║
║  ✨ "{quote_data['quote']}"
║
║  📝 — {quote_data['author']}
║
║  ━━━━━━━━━━━━━━━
║  🌟 𝐀𝐚𝐣 𝐤𝐚 𝐝𝐢𝐧 𝐓𝐄𝐑𝐀 𝐡𝐚𝐢!
║  𝐁𝐚𝐬 𝐜𝐡𝐚𝐥𝐭𝐞 𝐫𝐡𝐨! 🔥💪
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📜 𝐀𝐧𝐨𝐭𝐡𝐞𝐫", callback_data="fun_quote"),
                InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in quote_command: {e}")
        await update.message.reply_text("❌ Error! Dubara try karo!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRIVIA COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def trivia_command(update, context):
    """Start a Trivia Quiz!"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        import time
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        chat = update.effective_chat
        chat_id = chat.id
        
        question_data = random.choice(TRIVIA_QUESTIONS)
        
        # Store active trivia
        active_trivia[chat_id] = {
            "question": question_data,
            "user_id": user.id,
            "timestamp": time.time()
        }
        
        options_text = "\n".join([f"║  {opt}" for opt in question_data['options']])
        
        text = f"""
✦ 𝐓𝐑𝐈𝐕𝐈𝐀 𝐐𝐔𝐈𝐙 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🧠 𝐁𝐫𝐚𝐢𝐧 𝐓𝐞𝐬𝐭 ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  ━━━━━━━━━━━━━━━
║  ❓ 𝐐𝐮𝐞𝐬𝐭𝐢𝐨𝐧:
║  {question_data['question']}
║
║  ━━━━━━━━━━━━━━━
║  📋 𝐎𝐩𝐭𝐢𝐨𝐧𝐬:
{options_text}
║
║  ━━━━━━━━━━━━━━━
║  ⚡ 𝐉𝐚𝐥𝐝𝐢 𝐣𝐚𝐰𝐚𝐚𝐛 𝐝𝐨!
║  𝐍𝐞𝐞𝐜𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧 𝐝𝐚𝐛𝐚𝐨! 👇
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🅰️  A", callback_data=f"trivia_A_{chat_id}"),
                InlineKeyboardButton("🅱️  B", callback_data=f"trivia_B_{chat_id}"),
            ],
            [
                InlineKeyboardButton("🅲  C", callback_data=f"trivia_C_{chat_id}"),
                InlineKeyboardButton("🅳  D", callback_data=f"trivia_D_{chat_id}"),
            ],
            [
                InlineKeyboardButton("🎮 𝐌𝐨𝐫𝐞 𝐆𝐚𝐦𝐞𝐬", callback_data="fun_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in trivia_command: {e}")
        await update.message.reply_text("❌ Error! Dubara try karo!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUN GAMES MAIN MENU COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def fun_command(update, context):
    """Main Fun & Games Menu"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user = update.effective_user
        if not user:
            return
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        text = f"""
✦ 𝐅𝐔𝐍 & 𝐆𝐀𝐌𝐄𝐒 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🎮 𝐌𝐞𝐧𝐮 ]═════╗
║
║  👤 𝐇𝐞𝐲: {display_name}!
║
║  🎭 𝐓ʀᴜᴛʜ ᴏʀ 𝐃ᴀʀᴇ
║  🔮 𝐌𝐚𝐠𝐢𝐜 𝟖𝐁𝐚𝐥𝐥
║  🎲 𝐃𝐢𝐜𝐞 𝐑𝐨𝐥𝐥
║  🪙 𝐂𝐨𝐢𝐧 𝐅𝐥𝐢𝐩
║  💕 𝐋𝐨𝐯𝐞 𝐌𝐞𝐭𝐞𝐫
║  🔥 𝐑𝐨𝐚𝐬𝐭
║  💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭
║  😂 𝐉𝐨𝐤𝐞𝐬
║  📜 𝐐𝐮𝐨𝐭𝐞𝐬
║  🧠 𝐓𝐫𝐢𝐯𝐢𝐚 𝐐𝐮𝐢𝐳
║
║  ⬇️ 𝐒𝐞𝐥𝐞𝐜𝐭 𝐤𝐚𝐫𝐨!
║
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 𝐓𝐫𝐮𝐭𝐡", callback_data="fun_truth"),
                InlineKeyboardButton("🔥 𝐃𝐚𝐫𝐞", callback_data="fun_dare"),
            ],
            [
                InlineKeyboardButton("🔮 𝟖𝐁𝐚𝐥𝐥", callback_data="fun_8ball_info"),
                InlineKeyboardButton("💕 𝐋𝐨𝐯𝐞", callback_data="fun_love_info"),
            ],
            [
                InlineKeyboardButton("🎲 𝐃𝐢𝐜𝐞", callback_data="fun_dice"),
                InlineKeyboardButton("🪙 𝐅𝐥𝐢𝐩", callback_data="fun_coin"),
            ],
            [
                InlineKeyboardButton("🔥 𝐑𝐨𝐚𝐬𝐭", callback_data="fun_roast"),
                InlineKeyboardButton("💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭", callback_data="fun_compliment"),
            ],
            [
                InlineKeyboardButton("😂 𝐉𝐨𝐤𝐞", callback_data="fun_joke"),
                InlineKeyboardButton("📜 𝐐𝐮𝐨𝐭𝐞", callback_data="fun_quote"),
            ],
            [
                InlineKeyboardButton("🧠 𝐓𝐫𝐢𝐯𝐢𝐚 𝐐𝐮𝐢𝐳", callback_data="fun_trivia"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=None
        )
    
    except Exception as e:
        print(f"Error in fun_command: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUN SECTION CALLBACK HANDLER (FULL VERSION)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NOTE: Apni pehli file mein jo fun_section_callback hai usse
# is se REPLACE karo (poora function)

async def fun_section_callback(update, context):
    """Handle all fun & games inline button callbacks"""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        import time
        
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        
        display_name = user.first_name
        if user.last_name:
            display_name += f" {user.last_name}"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # MAIN MENU
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if data == "fun_menu":
            text = f"""
✦ 𝐅𝐔𝐍 & 𝐆𝐀𝐌𝐄𝐒 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🎮 𝐌𝐞𝐧𝐮 ]═════╗
║
║  👤 𝐇𝐞𝐲: {display_name}!
║
║  🎭 𝐓ʀᴜᴛʜ ᴏʀ 𝐃ᴀʀᴇ
║  🔮 𝐌𝐚𝐠𝐢𝐜 𝟖𝐁𝐚𝐥𝐥
║  🎲 𝐃𝐢𝐜𝐞 𝐑𝐨𝐥𝐥
║  🪙 𝐂𝐨𝐢𝐧 𝐅𝐥𝐢𝐩
║  💕 𝐋𝐨𝐯𝐞 𝐌𝐞𝐭𝐞𝐫
║  🔥 𝐑𝐨𝐚𝐬𝐭
║  💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭
║  😂 𝐉𝐨𝐤𝐞𝐬
║  📜 𝐐𝐮𝐨𝐭𝐞𝐬
║  🧠 𝐓𝐫𝐢𝐯𝐢𝐚 𝐐𝐮𝐢𝐳
║
║  ⬇️ 𝐒𝐞𝐥𝐞𝐜𝐭 𝐤𝐚𝐫𝐨!
║
╚════════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🎭 𝐓𝐫𝐮𝐭𝐡", callback_data="fun_truth"),
                    InlineKeyboardButton("🔥 𝐃𝐚𝐫𝐞", callback_data="fun_dare"),
                ],
                [
                    InlineKeyboardButton("🔮 𝟖𝐁𝐚𝐥𝐥", callback_data="fun_8ball_info"),
                    InlineKeyboardButton("💕 𝐋𝐨𝐯𝐞", callback_data="fun_love_info"),
                ],
                [
                    InlineKeyboardButton("🎲 𝐃𝐢𝐜𝐞", callback_data="fun_dice"),
                    InlineKeyboardButton("🪙 𝐅𝐥𝐢𝐩", callback_data="fun_coin"),
                ],
                [
                    InlineKeyboardButton("🔥 𝐑𝐨𝐚𝐬𝐭", callback_data="fun_roast"),
                    InlineKeyboardButton("💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭", callback_data="fun_compliment"),
                ],
                [
                    InlineKeyboardButton("😂 𝐉𝐨𝐤𝐞", callback_data="fun_joke"),
                    InlineKeyboardButton("📜 𝐐𝐮𝐨𝐭𝐞", callback_data="fun_quote"),
                ],
                [
                    InlineKeyboardButton("🧠 𝐓𝐫𝐢𝐯𝐢𝐚 𝐐𝐮𝐢𝐳", callback_data="fun_trivia"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TRUTH
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_truth":
            question = random.choice(TRUTH_QUESTIONS)
            text = f"""
✦ 𝐓𝐑𝐔𝐓𝐇 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🎭 𝐓ʀᴜᴛʜ 𝐓ɪᴍᴇ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  🎯 𝐐𝐮𝐞𝐬𝐭𝐢𝐨𝐧:
║  {question}
║
║  ⚠️ 𝐒𝐚𝐜𝐡 𝐛𝐨𝐥𝐧𝐚 𝐩𝐚𝐝𝐞𝐠𝐚!
║  𝐉𝐡𝐨𝐨𝐭𝐡 𝐛𝐨𝐥𝐚 𝐭𝐨𝐡 𝐬𝐚𝐛𝐤𝐨
║  𝐩𝐚𝐭𝐚 𝐜𝐡𝐚𝐥 𝐣𝐚𝐲𝐞𝐠𝐚! 😏
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🔄 𝐍𝐞𝐱𝐭 𝐓𝐫𝐮𝐭𝐡", callback_data="fun_truth"),
                    InlineKeyboardButton("🔥 𝐃𝐚𝐫𝐞", callback_data="fun_dare"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DARE
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_dare":
            dare = random.choice(DARE_CHALLENGES)
            text = f"""
✦ 𝐃𝐀𝐑𝐄 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔥 𝐃ᴀʀᴇ 𝐓ɪᴍᴇ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  🎯 𝐂𝐡𝐚𝐥𝐥𝐞𝐧𝐠𝐞:
║  {dare}
║
║  ⚡ 𝐃𝐚𝐫𝐞 𝐚𝐜𝐜𝐞𝐩𝐭 𝐤𝐚𝐫!
║  𝐁𝐡𝐚𝐚𝐠𝐧𝐚 𝐦𝐚𝐭 —
║  𝐬𝐚𝐛 𝐝𝐞𝐤𝐡 𝐫𝐚𝐡𝐞 𝐡𝐚𝐢𝐧! 👀
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("✅ 𝐀𝐜𝐜𝐞𝐩𝐭𝐞𝐝!", callback_data="dare_accepted"),
                    InlineKeyboardButton("😱 𝐒𝐤𝐢𝐩", callback_data="fun_dare"),
                ],
                [
                    InlineKeyboardButton("🎭 𝐓𝐫𝐮𝐭𝐡", callback_data="fun_truth"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DARE ACCEPTED
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "dare_accepted":
            text = f"""
✦ 𝐃𝐀𝐑𝐄 𝐀𝐂𝐂𝐄𝐏𝐓𝐄𝐃 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ ✅ 𝐁𝐫𝐚𝐯𝐞! ]═══╗
║
║  👤 {display_name}
║
║  🏆 𝐃𝐚𝐫𝐞 𝐚𝐜𝐜𝐞𝐩𝐭 𝐤𝐢𝐲𝐚!
║  𝐂𝐡𝐚𝐦𝐩𝐢𝐨𝐧 𝐡𝐚𝐢 𝐭𝐮! 🔥
║
║  😈 𝐀𝐛 𝐤𝐚𝐫𝐤𝐞 𝐝𝐢𝐤𝐡𝐚!
║  𝐒𝐚𝐛 𝐝𝐞𝐤𝐡 𝐫𝐚𝐡𝐞 𝐡𝐚𝐢𝐧! 👀
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🔥 𝐍𝐞𝐱𝐭 𝐃𝐚𝐫𝐞", callback_data="fun_dare"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 8BALL INFO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_8ball_info":
            text = f"""
✦ 𝐌𝐀𝐆𝐈𝐂 𝟖𝐁𝐀𝐋𝐋 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔮 𝟖𝐁𝐚𝐥𝐥 ]═══╗
║
║  🔮 𝐊𝐨𝐢 𝐛𝐡𝐢 𝐬𝐚𝐰𝐚𝐚𝐥 𝐩𝐮𝐜𝐡𝐨!
║  𝐉𝐚𝐝𝐮𝐢 𝟖𝐛𝐚𝐥𝐥 𝐣𝐚𝐰𝐚𝐚𝐛 𝐝𝐞𝐠𝐚!
║
║  📝 𝐔𝐬𝐞:
║  /8ball <your question>
║
║  💡 𝐄𝐱𝐚𝐦𝐩𝐥𝐞:
║  /8ball Kya main pass hounga?
║  /8ball Kya woh mujhe like karta?
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DICE (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_dice":
            dice_value = random.randint(1, 6)
            dice_emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
            dice_messages = {
                1: "💀 𝐀𝐫𝐞 𝐲𝐚𝐚𝐫! Ekdum khatam!",
                2: "😅 𝐓𝐡𝐨𝐝𝐚 𝐚𝐮𝐫 try karo!",
                3: "😐 𝐀𝐯𝐞𝐫𝐚𝐠𝐞 raha... meh!",
                4: "😊 𝐍𝐢𝐜𝐞! Acha hai yaar!",
                5: "🔥 𝐖𝐨𝐰! Almost perfect!",
                6: "🎉 𝐒𝐈𝐗𝐄𝐑! 🏏 Champion tu!"
            }
            bar_filled = "🟩" * dice_value
            bar_empty = "⬜" * (6 - dice_value)
            text = f"""
✦ 𝐃𝐈𝐂𝐄 𝐑𝐎𝐋𝐋 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🎲 𝐃ɪᴄᴇ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  🎲 𝐃ɪᴄᴇ: {dice_emojis[dice_value]}
║  🔢 𝐕𝐚𝐥𝐮𝐞: {dice_value}/6
║
║  {bar_filled}{bar_empty}
║
║  {dice_messages[dice_value]}
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🎲 𝐑𝐨𝐥𝐥 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_dice"),
                    InlineKeyboardButton("🪙 𝐂𝐨𝐢𝐧", callback_data="fun_coin"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COIN FLIP (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_coin":
            result = random.choice(["HEADS", "TAILS"])
            if result == "HEADS":
                result_text = "𝐇𝐄𝐀𝐃𝐒 (𝐂𝐡𝐢𝐭) 👑"
                message = "👑 Heads aaya! Kismat chamak rahi hai!"
            else:
                result_text = "𝐓𝐀𝐈𝐋𝐒 (𝐏𝐚𝐭) 🔄"
                message = "🔄 Tails aaya! Ulti kismat!"
            text = f"""
✦ 𝐂𝐎𝐈𝐍 𝐅𝐋𝐈𝐏 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🪙 𝐂ᴏɪɴ ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║  🪙 𝐑𝐞𝐬𝐮𝐥𝐭: {result_text}
║
║  {message}
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🪙 𝐅𝐥𝐢𝐩 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_coin"),
                    InlineKeyboardButton("🎲 𝐃𝐢𝐜𝐞", callback_data="fun_dice"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # LOVE INFO (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_love_info":
            text = f"""
✦ 𝐋𝐎𝐕𝐄 𝐌𝐄𝐓𝐄𝐑 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 💕 𝐋ᴏᴠᴇ ]═══╗
║
║  💘 𝐊𝐢𝐬𝐢 𝐤𝐚 𝐧𝐚𝐚𝐦 𝐝𝐨!
║
║  📝 𝐔𝐬𝐞:
║  • /love @username
║  • /love <name>
║  • Reply karke /love
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ROAST (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_roast":
            roast = random.choice(ROAST_MESSAGES)
            intensity = random.choice([
                "🌶️ Mild",
                "🌶️🌶️ Medium",
                "🌶️🌶️🌶️ Hot 🔥",
                "🌶️🌶️🌶️🌶️ Extra Hot 🥵",
                "💀☢️ NUCLEAR ☢️💀"
            ])
            text = f"""
✦ 𝐑𝐎𝐀𝐒𝐓 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🔥 𝐑ᴏᴀsᴛ ]═══╗
║
║  🎯 𝐓𝐚𝐫𝐠𝐞𝐭: {display_name}
║  🌶️ 𝐈𝐧𝐭𝐞𝐧𝐬𝐢𝐭𝐲: {intensity}
║
║  🔥 {roast}
║
║  😂 𝐌𝐚𝐳𝐚𝐚𝐤 𝐡𝐚𝐢 𝐛𝐡𝐚𝐢! 💀
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🔥 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_roast"),
                    InlineKeyboardButton("💖 𝐂𝐨𝐦𝐩𝐥𝐢𝐦𝐞𝐧𝐭", callback_data="fun_compliment"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COMPLIMENT (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_compliment":
            compliment = random.choice(COMPLIMENT_MESSAGES)
            sweetness = random.choice([
                "🍫 Chocolate Level",
                "🍯 Honey Sweet",
                "🧁 Cupcake Vibes",
                "🍰 Cake Wala Pyaar",
                "🎂 Birthday Special ✨",
            ])
            text = f"""
✦ 𝐂𝐎𝐌𝐏𝐋𝐈𝐌𝐄𝐍𝐓 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 💖 𝐂ᴏᴍᴘʟɪᴍᴇɴᴛ ]═══╗
║
║  🎯 𝐅𝐨𝐫: {display_name}
║  🌟 𝐒𝐰𝐞𝐞𝐭𝐧𝐞𝐬𝐬: {sweetness}
║
║  {compliment}
║
║  💖 𝐒𝐩𝐫𝐞𝐚𝐝 𝐋𝐨𝐯𝐞! 🌍
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("💖 𝐀𝐠𝐚𝐢𝐧", callback_data="fun_compliment"),
                    InlineKeyboardButton("🔥 𝐑𝐨𝐚𝐬𝐭", callback_data="fun_roast"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # JOKE (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_joke":
            joke = random.choice(JOKES_LIST)
            laugh = random.choice(["😂 Halki Hansi", "🤣 Puri Hansi", "😆 LOL", "💀 Dead 😂😂😂", "🤡 Comedy King"])
            text = f"""
✦ 𝐉𝐎𝐊𝐄 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 😂 𝐉ᴏᴋᴇ ]═══╗
║
║  👤 𝐅𝐨𝐫: {display_name}
║  🎭 𝐋𝐞𝐯𝐞𝐥: {laugh}
║
║  😄 {joke['q']}
║
║  🤣 {joke['a']}
║
║  😂😂😂😂😂😂😂😂😂😂
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("😂 𝐍𝐞𝐱𝐭", callback_data="fun_joke"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # QUOTE (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_quote":
            quote_data = random.choice(QUOTES_LIST)
            motivation = random.choice([
                "⚡ Energy Mode",
                "🔥 Fire Mode",
                "💪 Beast Mode",
                "🚀 Rocket Mode",
                "👑 King Mode",
                "🌟 Star Mode",
                "💎 Diamond Mode"
            ])
            text = f"""
✦ 𝐐𝐔𝐎𝐓𝐄 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 📜 𝐌ᴏᴛɪᴠᴀᴛɪᴏɴ ]═══╗
║
║  👤 𝐅𝐨𝐫: {display_name}
║  💪 𝐌𝐨𝐝𝐞: {motivation}
║
║  ✨ "{quote_data['quote']}"
║
║  📝 — {quote_data['author']}
║
║  🌟 𝐀𝐚𝐣 𝐤𝐚 𝐝𝐢𝐧 𝐓𝐄𝐑𝐀 𝐡𝐚𝐢! 🔥
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("📜 𝐍𝐞𝐱𝐭", callback_data="fun_quote"),
                    InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TRIVIA (via callback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif data == "fun_trivia":
            chat_id = query.message.chat.id
            question_data = random.choice(TRIVIA_QUESTIONS)
            active_trivia[chat_id] = {
                "question": question_data,
                "user_id": user.id,
                "timestamp": time.time()
            }
            options_text = "\n".join([f"║  {opt}" for opt in question_data['options']])
            text = f"""
✦ 𝐓𝐑𝐈𝐕𝐈𝐀 ✦
━━━━━━━━━━━━━━━━━━
╔═══[ 🧠 𝐐𝐮𝐢𝐳 ]═══╗
║
║  👤 𝐏ʟᴀʏᴇʀ: {display_name}
║
║  ❓ {question_data['question']}
║
{options_text}
║
║  ⚡ 𝐉𝐚𝐥𝐝𝐢 𝐣𝐚𝐰𝐚𝐚𝐛 𝐝𝐨!
║
╚══════════════════╝
━━━━━━━━━━━━━━━━━━
𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』
"""
            keyboard = [
                [
                    InlineKeyboardButton("🅰️ A", callback_data=f"trivia_A_{chat_id}"),
                    InlineKeyboardButton("🅱️ B", callback_data=f"trivia_B_{chat_id}"),
                ],
                [
                    InlineKeyboardButton("🅲 C", callback_data=f"trivia_C_{chat_id}"),
                    InlineKeyboardButton("🅳 D", callback_data=f"trivia_D_{chat_id}"),
                ],
                [InlineKeyboardButton("🎮 𝐌𝐞𝐧𝐮", callback_data="fun_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    except Exception as e:
        print(f"Error in fun_section_callback: {e}")
        try:
            await query.answer("❌ Error! Dubara try karo!", show_alert=True)
        except:
            pass


# ============================================================
# ████████████████████████████████████████████████████████████
# HANDLER REGISTRATION CODE — ZAROOR ADD KARO!
# ████████████████████████████████████████████████████████████
# ============================================================
#
# Apne main() function mein (jahan application.add_handler hai),
# yeh SAARI lines add karo SECTION 7 ke liye:
#
# ──────────────────────────────────────────────────────────────
# Section 7 — Fun & Games Handlers
# ──────────────────────────────────────────────────────────────
#
# from telegram.ext import CommandHandler, CallbackQueryHandler
#
# # Command handlers
# application.add_handler(CommandHandler("fun", fun_command))
# application.add_handler(CommandHandler("games", fun_command))       # Alias
# application.add_handler(CommandHandler("truth", truth_command))
# application.add_handler(CommandHandler("dare", dare_command))
# application.add_handler(CommandHandler("8ball", eightball_command))
# application.add_handler(CommandHandler("dice", dice_command))
# application.add_handler(CommandHandler("flip", flip_command))
# application.add_handler(CommandHandler("love", love_command))
# application.add_handler(CommandHandler("roast", roast_command))
# application.add_handler(CommandHandler("compliment", compliment_command))
# application.add_handler(CommandHandler("joke", joke_command))
# application.add_handler(CommandHandler("quote", quote_command))
# application.add_handler(CommandHandler("trivia", trivia_command))
#
# # Callback handlers — PATTERN se match karo
# application.add_handler(CallbackQueryHandler(fun_section_callback, pattern="^fun_"))
# application.add_handler(CallbackQueryHandler(fun_section_callback, pattern="^dare_accepted$"))
# application.add_handler(CallbackQueryHandler(trivia_answer_callback, pattern="^trivia_[ABCD]_"))
#
# ──────────────────────────────────────────────────────────────

# ============================================================
# HELP TEXT ADDITION — /help command mein yeh add karo
# ============================================================
#
# Section 7 Commands:
# • /fun or /games — Main Fun Menu (inline buttons)
# • /truth — Random Truth Question
# • /dare — Random Dare Challenge
# • /8ball <question> — Magic 8 Ball
# • /dice — Roll a Dice
# • /flip — Coin Flip
# • /love @user or /love name — Love Meter
# • /roast [reply to user] — Roast karo!
# • /compliment [reply to user] — Compliment bhejo!
# • /joke — Random Hinglish Joke
# • /quote — Quote of the Day
# • /trivia — Trivia Quiz
#
# ============================================================

# ============================================================
# REQUIREMENTS — requirements.txt mein yeh hone chahiye
# ============================================================
#
# python-telegram-bot==20.7
# psycopg2-binary
# aiohttp
# python-dotenv
#
# ============================================================

# ============================================================
# SECTION 7 COMPLETE ✅
# ============================================================
# Summary of what's in Section 7:
#
# DATA LISTS:
#   ✅ TRUTH_QUESTIONS      — 50+ hinglish truths
#   ✅ DARE_CHALLENGES      — 50+ dare challenges
#   ✅ EIGHTBALL_ANSWERS    — 30 answers (positive/neutral/negative)
#   ✅ ROAST_MESSAGES       — 50+ roasts
#   ✅ COMPLIMENT_MESSAGES  — 50+ compliments
#   ✅ JOKES_LIST           — 30+ hinglish jokes
#   ✅ QUOTES_LIST          — 20+ motivational quotes
#   ✅ TRIVIA_QUESTIONS      — 25+ trivia (multiple choice)
#   ✅ LOVE_METER_RESPONSES  — 4 categories (low/medium/high/perfect)
#
# COMMAND HANDLERS:
#   ✅ fun_command           — /fun /games (main menu)
#   ✅ truth_command         — /truth
#   ✅ dare_command          — /dare
#   ✅ eightball_command     — /8ball <question>
#   ✅ dice_command          — /dice (real Telegram dice)
#   ✅ flip_command          — /flip (coin flip)
#   ✅ love_command          — /love @user or name
#   ✅ roast_command         — /roast [reply]
#   ✅ compliment_command    — /compliment [reply]
#   ✅ joke_command          — /joke
#   ✅ quote_command         — /quote (date-based QOTD)
#   ✅ trivia_command        — /trivia (MCQ quiz)
#
# CALLBACK HANDLERS:
#   ✅ fun_section_callback  — Sab fun_ callbacks handle karta hai
#   ✅ trivia_answer_callback — Trivia answers (A/B/C/D) handle karta hai
#
# FEATURES:
#   ✅ Stylish Unicode fonts (𝐁𝐨𝐥𝐝, ᴜɴɪᴄᴏᴅᴇ ˢᴬˢᴱᴿ)
#   ✅ Inline keyboard buttons sab features pe
#   ✅ God-level UI with box borders ╔═══╗ ╚═══╝
#   ✅ Hinglish language throughout
#   ✅ Error handling har command mein
#   ✅ Love meter — name-based consistent result (seed)
#   ✅ Quote — date-based QOTD (user ke liye consistent)
#   ✅ Dice — Telegram native dice animation use karta hai
#   ✅ Trivia — active game tracking per chat
#   ✅ Roast/Compliment — reply support (kisi ko target kar sakte ho)
# ============================================================



# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   SECTIONS 8–13  ─  RUHI X ASSISTANT                        ║
# ║   ─────────────────────────────────────────────────────      ║
# ║   Section  8: Tools & Utilities                              ║
# ║   Section  9: Group Settings                                 ║
# ║   Section 10: Misc & Advanced                                ║
# ║   Section 11: Media & Stickers                               ║
# ║   Section 12: Owner Only                                     ║
# ║   Section 13: Ranking & XP System                            ║
# ║                                                              ║
# ║   ✅ Uses  db  object  (DatabaseManager from Section 1)      ║
# ║   ✅ No duplicate imports                                     ║
# ║   ✅ No command / function name conflicts                     ║
# ║   ✅ Full error handling everywhere                           ║
# ║   ✅ register_section8_13_handlers(application) ready        ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

# NOTE: This file is appended to Bot.py, so all imports from
# Section 1 are already available. We only add what is missing.

import aiohttp          # aiohttp session (web is already imported)
import subprocess       # for shell commands (Section 12)

# ───────────────────────────────────────────────────────────────
# In-memory caches used across sections
# ───────────────────────────────────────────────────────────────
_night_mode_cache: Dict[int, Dict] = {}   # {chat_id: {enabled, start, end}}
_xp_cooldown: Dict[Tuple[int, int], float] = {}   # {(chat_id, user_id): timestamp}
_daily_claimed: Dict[int, str] = {}       # {user_id: "YYYY-MM-DD"}
_user_connections: Dict[int, int] = {}    # {user_id: chat_id}

# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 8 ─ TOOLS & UTILITIES
# ██████████████████████████████████████████████████████████████
# ═══════════════════════════════════════════════════════════════

# ── 8.1  Telegraph ─────────────────────────────────────────────

async def s8_telegraph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /telegraph [Title | Content]
    OR  reply to any message with  /telegraph [Title]
    Pastes text to Telegra.ph and returns the URL.
    """
    msg  = update.effective_message
    user = update.effective_user

    reply = msg.reply_to_message

    if reply and (reply.text or reply.caption):
        content = reply.text or reply.caption or ""
        title   = " ".join(context.args).strip() if context.args else "Ruhi X Paste"
    elif context.args:
        raw = " ".join(context.args)
        if "|" in raw:
            title, content = raw.split("|", 1)
            title   = title.strip()
            content = content.strip()
        else:
            title   = "Ruhi X Paste"
            content = raw.strip()
    else:
        await msg.reply_text(
            "╔═══[ 📝 TELEGRAPH ]═══╗\n"
            "║\n"
            "║  Usage:\n"
            "║  /telegraph Title | Content\n"
            "║  OR reply to message:\n"
            "║  /telegraph [Title]\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    wait = await msg.reply_text("⏳ Uploading to Telegraph...")

    try:
        # Build content nodes
        nodes = []
        for line in content.split("\n"):
            if line.strip():
                nodes.append({"tag": "p", "children": [line]})
        if not nodes:
            nodes = [{"tag": "p", "children": [content]}]

        async with aiohttp.ClientSession() as session:
            # Create account
            async with session.get(
                "https://api.telegra.ph/createAccount",
                params={"short_name": "RuhiBot", "author_name": "Ruhi X Assistant"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                acc = await r.json()
            if not acc.get("ok"):
                raise RuntimeError("Telegraph account creation failed")
            token = acc["result"]["access_token"]

            # Create page
            async with session.post(
                "https://api.telegra.ph/createPage",
                data={
                    "access_token": token,
                    "title":        title[:256],
                    "content":      json.dumps(nodes),
                    "return_content": "false",
                },
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r2:
                page = await r2.json()
            if not page.get("ok"):
                raise RuntimeError("Page creation failed")

        link = page["result"]["url"]
        await wait.edit_text(
            f"✦ 𝐓𝐄𝐋𝐄𝐆𝐑𝐀𝐏𝐇 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 📝 Uploaded ]═══╗\n"
            f"║\n"
            f"║  👤 {html_escape(user.first_name)}\n"
            f"║  📌 {html_escape(title[:50])}\n"
            f"║  🔗 {link}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Open Page", url=link)]]
            )
        )
    except Exception as e:
        await wait.edit_text(f"❌ Telegraph Error: {html_escape(str(e)[:300])}")


# ── 8.2  URL Shortener ─────────────────────────────────────────

async def s8_shorturl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /shorturl <url>   Shortens a URL using TinyURL (no API key needed).
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /shorturl <url>")
        return

    url = context.args[0]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    wait = await msg.reply_text("⏳ Shortening URL...")
    try:
        encoded = urllib.parse.quote(url, safe="")
        api_url = f"https://tinyurl.com/api-create.php?url={encoded}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                short = (await r.text()).strip()

        if not short.startswith("http"):
            raise ValueError("Invalid TinyURL response")

        await wait.edit_text(
            f"✦ 𝐔𝐑𝐋 𝐒𝐇𝐎𝐑𝐓𝐄𝐍𝐄𝐑 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🔗 Result ]═══╗\n"
            f"║\n"
            f"║  👤 {html_escape(user.first_name)}\n"
            f"║\n"
            f"║  📌 Original:\n"
            f"║  <code>{html_escape(url[:80])}</code>\n"
            f"║\n"
            f"║  ✅ Short URL:\n"
            f"║  <code>{short}</code>\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Open", url=short)]]
            )
        )
    except Exception as e:
        await wait.edit_text(f"❌ URL Error: {html_escape(str(e)[:200])}")


# ── 8.3  QR Code ───────────────────────────────────────────────

async def s8_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /qr <text or url>   Generates a QR code image.
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /qr <text or url>")
        return

    data = " ".join(context.args)
    wait = await msg.reply_text("⏳ Generating QR Code...")

    try:
        encoded = urllib.parse.quote(data, safe="")
        qr_url  = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"

        async with aiohttp.ClientSession() as session:
            async with session.get(qr_url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    raise ValueError(f"QR API returned {r.status}")
                img_bytes = await r.read()

        caption = (
            f"✦ 𝐐𝐑 𝐂𝐎𝐃𝐄 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 📷 Generated ]═══╗\n"
            f"║  👤 {html_escape(user.first_name)}\n"
            f"║  📝 {html_escape(data[:60])}\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )
        await wait.delete()
        await msg.reply_photo(photo=io.BytesIO(img_bytes), caption=caption)
    except Exception as e:
        await wait.edit_text(f"❌ QR Error: {html_escape(str(e)[:200])}")


# ── 8.4  Calculator ────────────────────────────────────────────

_CALC_SAFE_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sum": sum, "divmod": divmod,
    "sqrt":    math.sqrt,   "log":   math.log,
    "log10":   math.log10,  "log2":  math.log2,
    "sin":     math.sin,    "cos":   math.cos,
    "tan":     math.tan,    "asin":  math.asin,
    "acos":    math.acos,   "atan":  math.atan,
    "pi":      math.pi,     "e":     math.e,
    "ceil":    math.ceil,   "floor": math.floor,
    "factorial": math.factorial, "gcd": math.gcd,
    "inf":     math.inf,    "tau":   math.tau,
}

async def s8_calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /calc <expression>   Safe math evaluator.
    Supports: +−×÷ sqrt log sin cos tan pi e ceil floor factorial
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text(
            "╔═══[ 🧮 CALCULATOR ]═══╗\n"
            "║\n"
            "║  Usage: /calc <expression>\n"
            "║  Examples:\n"
            "║   /calc 2 ** 10\n"
            "║   /calc sqrt(144)\n"
            "║   /calc sin(pi/2)\n"
            "║   /calc factorial(10)\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    raw_expr = " ".join(context.args)
    # Allow only safe characters
    clean = re.sub(r"[^0-9+\-*/().%^ a-zA-Z_,]", "", raw_expr)

    try:
        result = eval(clean, _CALC_SAFE_GLOBALS.copy())  # type: ignore[arg-type]
        if isinstance(result, float):
            result_str = (
                str(int(result)) if result == int(result)
                else f"{result:.10g}"
            )
        else:
            result_str = str(result)

        text = (
            f"✦ 𝐂𝐀𝐋𝐂𝐔𝐋𝐀𝐓𝐎𝐑 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🧮 Result ]═══╗\n"
            f"║\n"
            f"║  📝 <code>{html_escape(raw_expr[:200])}</code>\n"
            f"║\n"
            f"║  ✅ <b>{html_escape(result_str[:300])}</b>\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )
    except ZeroDivisionError:
        text = "❌ Zero se divide nahi kar sakte!"
    except OverflowError:
        text = "❌ Number bahut bada hai!"
    except Exception:
        text = f"❌ Invalid expression:\n<code>{html_escape(raw_expr[:200])}</code>"

    await msg.reply_text(text, parse_mode=ParseMode.HTML)


# ── 8.5  Translate ─────────────────────────────────────────────

async def s8_tr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /tr <lang> <text>   OR   reply to message with  /tr <lang>
    Uses Google Translate unofficial API. Language codes: hi en ur es fr de ja ko etc.
    """
    msg  = update.effective_message
    user = update.effective_user
    reply = msg.reply_to_message

    if reply and (reply.text or reply.caption):
        src_text = (reply.text or reply.caption or "").strip()
        tgt_lang = context.args[0] if context.args else "en"
    elif len(context.args) >= 2:
        tgt_lang = context.args[0]
        src_text = " ".join(context.args[1:])
    else:
        await msg.reply_text(
            "╔═══[ 🌐 TRANSLATE ]═══╗\n"
            "║\n"
            "║  Usage:\n"
            "║  /tr <lang> <text>\n"
            "║  OR reply to a message:\n"
            "║  /tr <lang>\n"
            "║\n"
            "║  Common lang codes:\n"
            "║  hi  en  ur  es  fr\n"
            "║  de  ja  ko  ar  tr\n"
            "║  zh  pt  ru  it  nl\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    wait = await msg.reply_text("⏳ Translating...")
    try:
        encoded = urllib.parse.quote(src_text, safe="")
        api_url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=auto&tl={urllib.parse.quote(tgt_lang)}"
            f"&dt=t&q={encoded}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                data = await r.json(content_type=None)

        translated = "".join(
            part[0] for part in data[0] if part and part[0]
        )
        detected = data[2] if len(data) > 2 and data[2] else "auto"

        await wait.edit_text(
            f"✦ 𝐓𝐑𝐀𝐍𝐒𝐋𝐀𝐓𝐄 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🌐 Result ]═══╗\n"
            f"║\n"
            f"║  👤 {html_escape(user.first_name)}\n"
            f"║  🔍 Detected: <b>{html_escape(str(detected))}</b>\n"
            f"║  🎯 Target: <b>{html_escape(tgt_lang)}</b>\n"
            f"║\n"
            f"║  📝 Original:\n"
            f"║  {html_escape(src_text[:300])}\n"
            f"║\n"
            f"║  ✅ Translated:\n"
            f"║  {html_escape(translated[:300])}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await wait.edit_text(f"❌ Translate Error: {html_escape(str(e)[:200])}")


# ── 8.6  TTS ───────────────────────────────────────────────────

async def s8_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /tts <text>   Converts text to speech using Google TTS.
    """
    msg  = update.effective_message
    user = update.effective_user
    reply = msg.reply_to_message

    if reply and (reply.text or reply.caption):
        text_in = (reply.text or reply.caption or "").strip()[:200]
    elif context.args:
        text_in = " ".join(context.args)[:200]
    else:
        await msg.reply_text("❌ Usage: /tts <text>")
        return

    wait = await msg.reply_text("⏳ Generating audio...")
    try:
        encoded = urllib.parse.quote(text_in, safe="")
        tts_url = (
            "https://translate.google.com/translate_tts"
            f"?ie=UTF-8&tl=en&client=tw-ob&q={encoded}"
        )
        headers = {"User-Agent": "Mozilla/5.0 (compatible; RuhiBot/3.0)"}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(tts_url, timeout=aiohttp.ClientTimeout(total=20)) as r:
                if r.status != 200:
                    raise ValueError(f"TTS API status {r.status}")
                audio = await r.read()

        bio = io.BytesIO(audio)
        bio.name = "tts_audio.mp3"
        caption = (
            f"✦ 𝐓𝐓𝐒 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 {html_escape(user.first_name)}\n"
            f"📝 {html_escape(text_in[:100])}\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )
        await wait.delete()
        await msg.reply_audio(audio=bio, filename="tts_audio.mp3", caption=caption)
    except Exception as e:
        await wait.edit_text(f"❌ TTS Error: {html_escape(str(e)[:200])}")


# ── 8.7  Weather ───────────────────────────────────────────────

async def s8_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /weather <city>   Fetches current weather using wttr.in (no API key needed).
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /weather <city>\nExample: /weather Mumbai")
        return

    city = " ".join(context.args)
    wait = await msg.reply_text("⏳ Fetching weather...")
    try:
        encoded = urllib.parse.quote(city, safe="")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://wttr.in/{encoded}?format=j1",
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "curl/7.68.0"}
            ) as r:
                if r.status != 200:
                    raise ValueError(f"City not found (status {r.status})")
                data = await r.json(content_type=None)

        cur  = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country   = area["country"][0]["value"]

        temp_c    = cur["temp_C"]
        temp_f    = cur["temp_F"]
        feels_c   = cur["FeelsLikeC"]
        humidity  = cur["humidity"]
        wind      = cur["windspeedKmph"]
        desc      = cur["weatherDesc"][0]["value"]
        visibility= cur["visibility"]
        cloud     = cur["cloudcover"]
        pressure  = cur.get("pressure", "N/A")

        desc_l = desc.lower()
        if "sun" in desc_l or "clear" in desc_l:   we = "☀️"
        elif "rain" in desc_l or "shower" in desc_l: we = "🌧️"
        elif "snow" in desc_l:                       we = "❄️"
        elif "storm" in desc_l or "thunder" in desc_l: we = "⛈️"
        elif "fog" in desc_l or "mist" in desc_l:   we = "🌫️"
        elif "cloud" in desc_l or "overcast" in desc_l: we = "☁️"
        else:                                        we = "🌤️"

        await wait.edit_text(
            f"✦ 𝐖𝐄𝐀𝐓𝐇𝐄𝐑 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ {we} {html_escape(city_name)}, {html_escape(country)} ]═══╗\n"
            f"║\n"
            f"║  🌡️ Temp:     <b>{temp_c}°C / {temp_f}°F</b>\n"
            f"║  🤔 Feels:    {feels_c}°C\n"
            f"║  💧 Humidity: {humidity}%\n"
            f"║  💨 Wind:     {wind} km/h\n"
            f"║  👁️ Visible:  {visibility} km\n"
            f"║  ☁️ Cloud:    {cloud}%\n"
            f"║  🌡️ Pressure: {pressure} hPa\n"
            f"║\n"
            f"║  📋 {html_escape(desc)}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await wait.edit_text(
            f"❌ Weather Error: {html_escape(str(e)[:200])}\n\nCity ka naam sahi likho!"
        )


# ── 8.8  Wikipedia ─────────────────────────────────────────────

async def s8_wiki(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /wiki <query>   Searches Wikipedia and returns a summary.
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /wiki <query>\nExample: /wiki Python programming")
        return

    query = " ".join(context.args)
    wait  = await msg.reply_text("⏳ Searching Wikipedia...")
    try:
        encoded = urllib.parse.quote(query, safe="")
        base    = "https://en.wikipedia.org/w/api.php"
        async with aiohttp.ClientSession() as session:
            # Search
            async with session.get(
                f"{base}?action=query&list=search&srsearch={encoded}"
                f"&format=json&srlimit=1&utf8=1",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                search = await r.json(content_type=None)

            results = search.get("query", {}).get("search", [])
            if not results:
                await wait.edit_text("❌ Koi result nahi mila Wikipedia pe!")
                return

            page_id = results[0]["pageid"]
            title   = results[0]["title"]

            # Summary
            async with session.get(
                f"{base}?action=query&prop=extracts&exintro&explaintext"
                f"&pageids={page_id}&format=json&utf8=1",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r2:
                detail = await r2.json(content_type=None)

        extract = (
            detail["query"]["pages"][str(page_id)].get("extract", "No summary available.")
        )
        # Trim to 800 chars
        extract = extract.strip()[:900]
        if len(extract) == 900:
            extract = extract[:extract.rfind(" ")] + "…"

        link = f"https://en.wikipedia.org/?curid={page_id}"

        await wait.edit_text(
            f"✦ 𝐖𝐈𝐊𝐈𝐏𝐄𝐃𝐈𝐀 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 📚 {html_escape(title[:40])} ]═══╗\n"
            f"║\n"
            f"{html_escape(extract)}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📖 Full Article", url=link)]]
            )
        )
    except Exception as e:
        await wait.edit_text(f"❌ Wiki Error: {html_escape(str(e)[:200])}")


# ── 8.9  Google Search ─────────────────────────────────────────

async def s8_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /google <query>   Returns DuckDuckGo instant answers + Google search link.
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /google <query>")
        return

    query   = " ".join(context.args)
    encoded = urllib.parse.quote(query, safe="")
    g_link  = f"https://www.google.com/search?q={encoded}"
    wait    = await msg.reply_text("⏳ Searching...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json(content_type=None)

        abstract  = data.get("AbstractText", "").strip()
        answer    = data.get("Answer", "").strip()
        source    = data.get("AbstractSource", "").strip() or data.get("AnswerType", "").strip()
        definition= data.get("Definition", "").strip()

        content = answer or abstract or definition or ""

        if content:
            body = (
                f"✦ 𝐆𝐎𝐎𝐆𝐋𝐄 ✦\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"╔═══[ 🔍 {html_escape(query[:40])} ]═══╗\n"
                f"║\n"
                f"{html_escape(content[:700])}\n"
            )
            if source:
                body += f"\n📌 Source: {html_escape(source)}\n"
            body += (
                f"║\n"
                f"╚═══════════════════════╝\n"
                f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
            )
        else:
            body = (
                f"🔍 <b>{html_escape(query)}</b>\n\n"
                f"ℹ️ Direct result nahi mila.\n"
                f"Niche Google pe dekho! 👇"
            )

        await wait.edit_text(
            body[:4000],
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔍 Google pe Dekho", url=g_link)]]
            )
        )
    except Exception as e:
        await wait.edit_text(
            f"🔍 <b>{html_escape(query)}</b>\n\n❌ Error: {html_escape(str(e)[:100])}",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔍 Google pe Dekho", url=g_link)]]
            )
        )


# ── 8.10  IMDb ─────────────────────────────────────────────────

async def s8_imdb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /imdb <movie name>   Fetches movie info from OMDb API.
    Set OMDB_API_KEY env var for better results (free at omdbapi.com).
    """
    msg  = update.effective_message
    user = update.effective_user

    if not context.args:
        await msg.reply_text("❌ Usage: /imdb <movie name>\nExample: /imdb Interstellar")
        return

    movie   = " ".join(context.args)
    wait    = await msg.reply_text("⏳ Searching IMDb...")
    omdb_key= os.environ.get("OMDB_API_KEY", "trilogy")

    try:
        encoded = urllib.parse.quote(movie, safe="")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://www.omdbapi.com/?t={encoded}&apikey={omdb_key}&plot=short",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json(content_type=None)

        if data.get("Response") == "False":
            await wait.edit_text(
                f"❌ Movie nahi mili: <b>{html_escape(movie)}</b>\n\nSahi naam likhein!",
                parse_mode=ParseMode.HTML
            )
            return

        title     = data.get("Title", "N/A")
        year      = data.get("Year", "N/A")
        rated     = data.get("Rated", "N/A")
        released  = data.get("Released", "N/A")
        runtime   = data.get("Runtime", "N/A")
        genre     = data.get("Genre", "N/A")
        director  = data.get("Director", "N/A")
        actors    = data.get("Actors", "N/A")
        plot      = data.get("Plot", "N/A")
        language  = data.get("Language", "N/A")
        awards    = data.get("Awards", "N/A")
        imdb_r    = data.get("imdbRating", "N/A")
        imdb_v    = data.get("imdbVotes", "N/A")
        imdb_id   = data.get("imdbID", "")
        poster    = data.get("Poster", "")
        boxoffice = data.get("BoxOffice", "N/A")

        imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""

        try:
            stars = "⭐" * min(5, round(float(imdb_r) / 2))
        except Exception:
            stars = "⭐"

        caption = (
            f"✦ 𝐈𝐌𝐃𝐁 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🎬 {html_escape(title)} ({year}) ]═══╗\n"
            f"║\n"
            f"║  ⭐ Rating:   <b>{imdb_r}/10</b> {stars}\n"
            f"║  🗳️ Votes:    {imdb_v}\n"
            f"║  🎭 Genre:    {html_escape(genre)}\n"
            f"║  ⏱️ Runtime:  {runtime}\n"
            f"║  📅 Released: {released}\n"
            f"║  🔞 Rated:    {rated}\n"
            f"║  🎬 Director: {html_escape(director[:50])}\n"
            f"║  🌟 Actors:   {html_escape(actors[:80])}\n"
            f"║  🌐 Language: {html_escape(language)}\n"
            f"║  💰 Box Office: {boxoffice}\n"
            f"║  🏆 Awards:   {html_escape(awards[:80])}\n"
            f"║\n"
            f"║  📝 Plot:\n"
            f"║  {html_escape(plot[:400])}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )

        kb = []
        if imdb_link:
            kb.append([InlineKeyboardButton("🎬 IMDb pe Dekho", url=imdb_link)])
        markup = InlineKeyboardMarkup(kb) if kb else None

        if poster and poster != "N/A":
            try:
                await wait.delete()
                await msg.reply_photo(
                    photo=poster,
                    caption=caption[:1024],
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup
                )
                return
            except Exception:
                pass  # fall through to text

        await wait.edit_text(caption[:4000], parse_mode=ParseMode.HTML, reply_markup=markup)

    except Exception as e:
        await wait.edit_text(f"❌ IMDb Error: {html_escape(str(e)[:200])}")


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 9 ─ GROUP SETTINGS
# ██████████████████████████████████████████████████████████════
# ═══════════════════════════════════════════════════════════════

# ── Helper decorator ───────────────────────────────────────────

def _group_admin_only(func: Callable) -> Callable:
    """Decorator: Only group admins, sudo users, or owner can run this."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        user = update.effective_user
        chat = update.effective_chat
        msg  = update.effective_message

        if chat.type == "private":
            await msg.reply_text("❌ Yeh command sirf group mein use karo!")
            return

        # Owner / sudo bypass
        if user.id == OWNER_ID or user.id in INITIAL_SUDO_USERS:
            return await func(update, context)

        try:
            member = await chat.get_member(user.id)
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return await func(update, context)
        except Exception:
            pass

        await msg.reply_text("❌ Sirf admins yeh command use kar sakte hain!")
    return wrapper


# ── 9.1  Lock / Unlock ─────────────────────────────────────────

_LOCK_PERMISSION_MAP: Dict[str, str] = {
    "msg":    "can_send_messages",
    "media":  "can_send_media_messages",
    "other":  "can_send_other_messages",
    "link":   "can_add_web_page_previews",
    "poll":   "can_send_polls",
    "info":   "can_change_info",
    "invite": "can_invite_users",
    "pin":    "can_pin_messages",
}

def _build_permissions(current: ChatPermissions, key: str, value: bool) -> ChatPermissions:
    """Return a new ChatPermissions with one field changed."""
    fields = {
        "can_send_messages":       current.can_send_messages,
        "can_send_media_messages": current.can_send_media_messages,
        "can_send_other_messages": current.can_send_other_messages,
        "can_add_web_page_previews": current.can_add_web_page_previews,
        "can_send_polls":          current.can_send_polls,
        "can_change_info":         current.can_change_info,
        "can_invite_users":        current.can_invite_users,
        "can_pin_messages":        current.can_pin_messages,
    }
    fields[key] = value
    return ChatPermissions(**fields)


@_group_admin_only
async def s9_lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /lock <type>   Restricts that permission for all non-admin members.
    Types: msg  media  other  link  poll  info  invite  pin
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        types_list = "  ".join(f"<code>{k}</code>" for k in _LOCK_PERMISSION_MAP)
        await msg.reply_text(
            f"╔═══[ 🔒 LOCK ]═══╗\n"
            f"║\n"
            f"║  Usage: /lock <type>\n"
            f"║\n"
            f"║  Types:\n"
            f"║  {types_list}\n"
            f"║\n"
            f"╚═══════════════════════╝",
            parse_mode=ParseMode.HTML
        )
        return

    lock_type = context.args[0].lower()
    if lock_type not in _LOCK_PERMISSION_MAP:
        await msg.reply_text(
            f"❌ Unknown type: <code>{html_escape(lock_type)}</code>\n"
            f"Valid: {', '.join(_LOCK_PERMISSION_MAP.keys())}",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        current = await chat.get_permissions() if hasattr(chat, "get_permissions") else chat.permissions
        new_perms = _build_permissions(current, _LOCK_PERMISSION_MAP[lock_type], False)
        await chat.set_permissions(new_perms)
        await msg.reply_text(
            f"🔒 <b>{lock_type.upper()}</b> locked!\n"
            f"Non-admins ab yeh nahi kar sakte.",
            parse_mode=ParseMode.HTML
        )
    except Forbidden:
        await msg.reply_text("❌ Bot ko admin bana do pehle!")
    except Exception as e:
        await msg.reply_text(f"❌ Lock fail: {html_escape(str(e)[:200])}")


@_group_admin_only
async def s9_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /unlock <type>   Restores that permission for all members.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        await msg.reply_text("❌ Usage: /unlock <type>")
        return

    lock_type = context.args[0].lower()
    if lock_type not in _LOCK_PERMISSION_MAP:
        await msg.reply_text(
            f"❌ Unknown type: <code>{html_escape(lock_type)}</code>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        current = await chat.get_permissions() if hasattr(chat, "get_permissions") else chat.permissions
        new_perms = _build_permissions(current, _LOCK_PERMISSION_MAP[lock_type], True)
        await chat.set_permissions(new_perms)
        await msg.reply_text(
            f"🔓 <b>{lock_type.upper()}</b> unlocked!",
            parse_mode=ParseMode.HTML
        )
    except Forbidden:
        await msg.reply_text("❌ Bot ko admin bana do pehle!")
    except Exception as e:
        await msg.reply_text(f"❌ Unlock fail: {html_escape(str(e)[:200])}")


# ── 9.2  Rules ─────────────────────────────────────────────────

async def s9_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /rules   Shows the group's rules (stored in DB).
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if chat.type == "private":
        await msg.reply_text("❌ Group mein use karo!")
        return

    try:
        row = await db.fetchrow(
            "SELECT rules FROM chats WHERE chat_id = $1", chat.id
        )
        rules_text = row["rules"].strip() if (row and row["rules"]) else ""
    except Exception:
        rules_text = ""

    if not rules_text:
        await msg.reply_text(
            "╔═══[ 📜 RULES ]═══╗\n"
            "║\n"
            "║  ℹ️ Is group ke rules\n"
            "║  abhi set nahi hain.\n"
            "║\n"
            "║  Admin: /setrules <text>\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    await msg.reply_text(
        f"✦ 𝐑𝐔𝐋𝐄𝐒 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 📜 {html_escape((chat.title or 'Group')[:30])} ]═══╗\n"
        f"║\n"
        f"{html_escape(rules_text[:3500])}\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


@_group_admin_only
async def s9_setrules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /setrules <text>   Sets group rules. Saved to DB.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        await msg.reply_text("❌ Usage: /setrules <your rules>")
        return

    rules_text = " ".join(context.args)
    try:
        await db.execute(
            "UPDATE chats SET rules = $1 WHERE chat_id = $2",
            rules_text, chat.id
        )
        await msg.reply_text("✅ Rules set kar diye! /rules se dekh sakte hain.")
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


@_group_admin_only
async def s9_resetrules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /resetrules   Clears the group's rules.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    try:
        await db.execute(
            "UPDATE chats SET rules = '' WHERE chat_id = $1",
            chat.id
        )
        await msg.reply_text("✅ Rules reset kar diye!")
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


# ── 9.3  Group Language ────────────────────────────────────────

_SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "🇬🇧 English",  "hi": "🇮🇳 Hindi",    "ur": "🇵🇰 Urdu",
    "es": "🇪🇸 Spanish",  "fr": "🇫🇷 French",   "de": "🇩🇪 German",
    "ar": "🇸🇦 Arabic",   "tr": "🇹🇷 Turkish",  "pt": "🇧🇷 Portuguese",
    "ru": "🇷🇺 Russian",  "ja": "🇯🇵 Japanese", "ko": "🇰🇷 Korean",
    "zh": "🇨🇳 Chinese",  "it": "🇮🇹 Italian",  "nl": "🇳🇱 Dutch",
}

@_group_admin_only
async def s9_setlang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /setlang <code>   Sets the group's language (stored in DB).
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        lang_list = "\n".join(
            f"║  <code>{k}</code>  {v}" for k, v in _SUPPORTED_LANGUAGES.items()
        )
        await msg.reply_text(
            f"╔═══[ 🌐 SET LANGUAGE ]═══╗\n"
            f"║\n"
            f"║  Usage: /setlang <code>\n"
            f"║\n"
            f"{lang_list}\n"
            f"║\n"
            f"╚═══════════════════════╝",
            parse_mode=ParseMode.HTML
        )
        return

    lang = context.args[0].lower()
    if lang not in _SUPPORTED_LANGUAGES:
        await msg.reply_text(
            f"❌ Unsupported: <code>{html_escape(lang)}</code>\n"
            f"/setlang se list dekho.",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        await db.execute(
            "UPDATE chats SET language = $1 WHERE chat_id = $2",
            lang, chat.id
        )
        await msg.reply_text(
            f"✅ Language set: <b>{_SUPPORTED_LANGUAGES[lang]}</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


# ── 9.4  Report System ─────────────────────────────────────────

async def s9_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /report [reason]   Reply to a message to report that user to admins.
    """
    msg    = update.effective_message
    chat   = update.effective_chat
    user   = update.effective_user

    if chat.type == "private":
        await msg.reply_text("❌ Group mein use karo!")
        return

    if not msg.reply_to_message:
        await msg.reply_text("❌ Kisi user ke message ko reply karo phir /report karo!")
        return

    reported = msg.reply_to_message.from_user
    if not reported:
        await msg.reply_text("❌ User identify nahi hua!")
        return
    if reported.id == user.id:
        await msg.reply_text("❌ Apne aap ko report nahi kar sakte!")
        return
    if reported.is_bot:
        await msg.reply_text("❌ Bot ko report nahi kar sakte!")
        return

    reason = " ".join(context.args) if context.args else "Koi reason nahi diya"

    try:
        admins = await chat.get_administrators()
        admin_mentions = " ".join(
            f"<a href='tg://user?id={a.user.id}'>·</a>"
            for a in admins if not a.user.is_bot
        )

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔨 Ban",     callback_data=f"rpt_ban_{reported.id}_{chat.id}"),
            InlineKeyboardButton("🔇 Mute",    callback_data=f"rpt_mute_{reported.id}_{chat.id}"),
            InlineKeyboardButton("✅ Dismiss",  callback_data=f"rpt_dismiss_{reported.id}_{chat.id}"),
        ]])

        await msg.reply_to_message.reply_text(
            f"🚨 <b>REPORT</b> 🚨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ ⚠️ Admin Alert ]═══╗\n"
            f"║\n"
            f"║  👤 By:     {mention_html(user.id, user.first_name)}\n"
            f"║  🎯 User:   {mention_html(reported.id, reported.first_name)}\n"
            f"║  📝 Reason: {html_escape(reason[:200])}\n"
            f"║  💬 Group:  {html_escape((chat.title or '')[:40])}\n"
            f"║\n"
            f"╚═══════════════════════╝\n"
            f"🔔 Admins: {admin_mentions}",
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
        await msg.reply_text("✅ Report bhej diya! Admins dekh lenge.")
    except Exception as e:
        await msg.reply_text(f"❌ Report fail: {html_escape(str(e)[:200])}")


async def s9_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles ban / mute / dismiss actions from the report inline keyboard."""
    query = update.callback_query
    user  = query.from_user
    chat  = query.message.chat
    await query.answer()

    parts  = query.data.split("_")  # rpt_ban_12345_67890
    action = parts[1]
    target_id = int(parts[2])
    chat_id   = int(parts[3]) if len(parts) > 3 else chat.id

    # Verify caller is admin
    try:
        member = await chat.get_member(user.id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            if user.id != OWNER_ID and user.id not in INITIAL_SUDO_USERS:
                await query.answer("❌ Sirf admins yeh kar sakte hain!", show_alert=True)
                return
    except Exception:
        await query.answer("❌ Permission check fail!", show_alert=True)
        return

    try:
        if action == "ban":
            await context.bot.ban_chat_member(chat_id, target_id)
            new_text = f"🔨 User banned by {mention_html(user.id, user.first_name)}!"
        elif action == "mute":
            await context.bot.restrict_chat_member(
                chat_id, target_id,
                ChatPermissions(can_send_messages=False)
            )
            new_text = f"🔇 User muted by {mention_html(user.id, user.first_name)}!"
        elif action == "dismiss":
            new_text = f"✅ Report dismissed by {mention_html(user.id, user.first_name)}."
        else:
            return

        await query.edit_message_text(new_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await query.answer(f"❌ {str(e)[:100]}", show_alert=True)


# ── 9.5  Staff List ────────────────────────────────────────────

async def s9_staff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /staff   Shows the bot's owner and sudo users.
    """
    msg = update.effective_message

    # Load sudo users from DB
    try:
        rows = await db.fetch(
            "SELECT user_id FROM sudo_users ORDER BY added_at"
        )
        sudo_ids = [r["user_id"] for r in rows]
    except Exception:
        sudo_ids = list(INITIAL_SUDO_USERS)

    sudo_lines = (
        "\n".join(f"║  • <a href='tg://user?id={uid}'>{uid}</a>" for uid in sudo_ids)
        if sudo_ids else "║  • Koi sudo user nahi"
    )

    await msg.reply_text(
        f"✦ 𝐒𝐓𝐀𝐅𝐅 𝐋𝐈𝐒𝐓 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 👑 Bot Staff ]═══╗\n"
        f"║\n"
        f"║  👑 OWNER:\n"
        f"║  • <a href='tg://user?id={OWNER_ID}'>@{html_escape(OWNER_USERNAME)}</a>\n"
        f"║\n"
        f"║  ⚡ SUDO USERS:\n"
        f"{sudo_lines}\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 9.6  Disable / Enable Commands ────────────────────────────

@_group_admin_only
async def s9_disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /disable <command>   Prevents that command from working in this group.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        try:
            rows = await db.fetch(
                "SELECT command FROM disabled_commands WHERE chat_id = $1 ORDER BY command",
                chat.id
            )
            cmds = [r["command"] for r in rows]
        except Exception:
            cmds = []

        if cmds:
            cmd_list = "\n".join(f"║  • /{c}" for c in cmds)
        else:
            cmd_list = "║  • Koi disabled nahi"

        await msg.reply_text(
            f"╔═══[ 🚫 DISABLED COMMANDS ]═══╗\n"
            f"║\n"
            f"{cmd_list}\n"
            f"║\n"
            f"║  Usage: /disable <cmd>\n"
            f"╚═══════════════════════╝"
        )
        return

    cmd_name = context.args[0].lower().lstrip("/")
    try:
        await db.execute(
            "INSERT INTO disabled_commands (chat_id, command, disabled_by) "
            "VALUES ($1, $2, $3) ON CONFLICT (chat_id, command) DO NOTHING",
            chat.id, cmd_name, update.effective_user.id
        )
        await msg.reply_text(
            f"🚫 <code>/{html_escape(cmd_name)}</code> disabled in this group!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


@_group_admin_only
async def s9_enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /enable <command>   Re-enables a previously disabled command.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        await msg.reply_text("❌ Usage: /enable <command>")
        return

    cmd_name = context.args[0].lower().lstrip("/")
    try:
        result = await db.execute(
            "DELETE FROM disabled_commands WHERE chat_id = $1 AND command = $2",
            chat.id, cmd_name
        )
        if "DELETE 0" in str(result):
            await msg.reply_text(f"ℹ️ /{cmd_name} was not disabled.")
        else:
            await msg.reply_text(
                f"✅ <code>/{html_escape(cmd_name)}</code> re-enabled!",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


# ── 9.7  Night Mode ────────────────────────────────────────────

@_group_admin_only
async def s9_nightmode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /nightmode on <start_hour> <end_hour>   Auto-lock group at night.
    /nightmode off
    Example: /nightmode on 23 7
    """
    msg  = update.effective_message
    chat = update.effective_chat

    current = _night_mode_cache.get(chat.id, {})

    if not context.args:
        status = "ON 🌙" if current.get("enabled") else "OFF ☀️"
        s      = current.get("start", 23)
        e      = current.get("end", 7)
        await msg.reply_text(
            f"╔═══[ 🌙 NIGHT MODE ]═══╗\n"
            f"║\n"
            f"║  Status:  <b>{status}</b>\n"
            f"║  Lock at: {s}:00\n"
            f"║  Unlock:  {e}:00\n"
            f"║\n"
            f"║  Usage:\n"
            f"║  /nightmode on 23 7\n"
            f"║  /nightmode off\n"
            f"║\n"
            f"╚═══════════════════════╝",
            parse_mode=ParseMode.HTML
        )
        return

    action = context.args[0].lower()

    if action == "off":
        _night_mode_cache[chat.id] = {"enabled": False, "start": 23, "end": 7}
        await msg.reply_text("☀️ Night mode OFF kar diya!")
        return

    if action == "on":
        try:
            start = int(context.args[1]) if len(context.args) > 1 else 23
            end   = int(context.args[2]) if len(context.args) > 2 else 7
        except ValueError:
            await msg.reply_text("❌ Hours 0–23 ke beech hone chahiye!")
            return

        if not (0 <= start <= 23 and 0 <= end <= 23):
            await msg.reply_text("❌ Hours 0–23 ke beech hone chahiye!")
            return

        _night_mode_cache[chat.id] = {"enabled": True, "start": start, "end": end, "chat_id": chat.id}
        await msg.reply_text(
            f"🌙 Night mode ON!\n"
            f"Group {start}:00 pe lock aur {end}:00 pe unlock hoga.\n"
            f"⚠️ Bot ko admin hona chahiye!",
        )
        return

    await msg.reply_text("❌ Usage: /nightmode on|off")


async def _night_mode_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled job: apply night mode every hour."""
    now_hour = datetime.now().hour
    for chat_id, cfg in list(_night_mode_cache.items()):
        if not cfg.get("enabled"):
            continue
        start, end = cfg.get("start", 23), cfg.get("end", 7)
        # Determine if currently in night window
        if start > end:   # crosses midnight (e.g., 23–7)
            in_night = (now_hour >= start or now_hour < end)
        else:             # same day (e.g., 2–6)
            in_night = (start <= now_hour < end)
        try:
            if in_night:
                await context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
            else:
                await context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    )
                )
        except Exception as ex:
            logger.warning(f"Night mode job error for {chat_id}: {ex}")


# ── 9.8  Log Channel ───────────────────────────────────────────

@_group_admin_only
async def s9_setlog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /setlog <channel_id>   Sets the log channel for this group.
    Example: /setlog -100123456789
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if not context.args:
        await msg.reply_text(
            "❌ Usage: /setlog <channel_id>\n"
            "Example: /setlog -100123456789\n\n"
            "Note: Bot ko us channel ka admin banana padega."
        )
        return

    try:
        log_id = int(context.args[0])
    except ValueError:
        await msg.reply_text("❌ Valid channel ID do! (usually starts with -100)")
        return

    try:
        await db.execute(
            "UPDATE chats SET log_channel = $1 WHERE chat_id = $2",
            log_id, chat.id
        )
        await msg.reply_text(
            f"✅ Log channel set: <code>{log_id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 10 ─ MISC & ADVANCED
# ██████████████████████████████████████████████████════════════
# ═══════════════════════════════════════════════════════════════

# ── 10.1  Broadcast to Users ───────────────────────────────────

async def s10_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /broadcast <message>   Owner only. Sends to all bot users.
    OR reply to a message with /broadcast.
    """
    user = update.effective_user
    msg  = update.effective_message

    if user.id != OWNER_ID:
        await msg.reply_text("❌ Sirf Owner yeh kar sakta hai!")
        return

    if not context.args and not msg.reply_to_message:
        await msg.reply_text(
            "❌ Usage: /broadcast <message>\n"
            "OR reply karo kisi message ko /broadcast se."
        )
        return

    fwd_msg   = msg.reply_to_message if msg.reply_to_message else None
    bcast_text= " ".join(context.args) if (not fwd_msg and context.args) else None

    wait = await msg.reply_text("⏳ Fetching user list...")

    try:
        rows = await db.fetch("SELECT user_id FROM users WHERE is_active = TRUE AND is_bot = FALSE")
        uids = [r["user_id"] for r in rows]
    except Exception as e:
        await wait.edit_text(f"❌ DB Error: {html_escape(str(e)[:200])}")
        return

    if not uids:
        await wait.edit_text("❌ Koi user DB mein nahi mila!")
        return

    await wait.edit_text(f"📡 Broadcasting to {len(uids)} users...")

    done = fail = 0
    for uid in uids:
        try:
            if fwd_msg:
                await fwd_msg.copy(chat_id=uid)
            else:
                await context.bot.send_message(chat_id=uid, text=bcast_text)
            done += 1
        except (Forbidden, BadRequest):
            # User blocked the bot or deleted their account
            fail += 1
        except RetryAfter as e_ra:
            await asyncio.sleep(e_ra.retry_after)
        except Exception:
            fail += 1
        await asyncio.sleep(0.04)  # ~25 msg/s — within Telegram limits

    await wait.edit_text(
        f"✅ Broadcast Complete!\n\n"
        f"  ✔️ Sent:   {done}\n"
        f"  ❌ Failed: {fail}"
    )


async def s10_gbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /gbroadcast <message>   Owner only. Sends to all groups.
    """
    user = update.effective_user
    msg  = update.effective_message

    if user.id != OWNER_ID:
        await msg.reply_text("❌ Sirf Owner yeh kar sakta hai!")
        return

    if not context.args and not msg.reply_to_message:
        await msg.reply_text("❌ Usage: /gbroadcast <message>")
        return

    fwd_msg   = msg.reply_to_message if msg.reply_to_message else None
    bcast_text= " ".join(context.args) if (not fwd_msg and context.args) else None

    wait = await msg.reply_text("⏳ Fetching group list...")
    try:
        rows = await db.fetch("SELECT chat_id FROM chats WHERE is_active = TRUE")
        gids = [r["chat_id"] for r in rows]
    except Exception as e:
        await wait.edit_text(f"❌ DB Error: {html_escape(str(e)[:200])}")
        return

    if not gids:
        await wait.edit_text("❌ Koi group DB mein nahi mila!")
        return

    await wait.edit_text(f"📡 Broadcasting to {len(gids)} groups...")

    done = fail = 0
    for gid in gids:
        try:
            if fwd_msg:
                await fwd_msg.copy(chat_id=gid)
            else:
                await context.bot.send_message(chat_id=gid, text=bcast_text)
            done += 1
        except (Forbidden, BadRequest):
            fail += 1
        except RetryAfter as e_ra:
            await asyncio.sleep(e_ra.retry_after)
        except Exception:
            fail += 1
        await asyncio.sleep(0.04)

    await wait.edit_text(
        f"✅ Group Broadcast Complete!\n\n"
        f"  ✔️ Sent:   {done}\n"
        f"  ❌ Failed: {fail}"
    )


# ── 10.2  Extended Stats ───────────────────────────────────────

async def s10_botstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /botstats   Detailed stats. Sudo / Owner only.
    """
    user = update.effective_user
    msg  = update.effective_message

    if user.id != OWNER_ID and user.id not in INITIAL_SUDO_USERS:
        await msg.reply_text("❌ Sirf staff dekh sakta hai!")
        return

    uptime = str(timedelta(seconds=int(time.time() - BOT_START_TIME)))

    try:
        total_users  = await db.fetchval("SELECT COUNT(*) FROM users WHERE is_bot = FALSE") or 0
        total_chats  = await db.fetchval("SELECT COUNT(*) FROM chats WHERE is_active = TRUE") or 0
        total_gbans  = await db.fetchval("SELECT COUNT(*) FROM gbans") or 0
        total_warns  = await db.fetchval("SELECT COUNT(*) FROM warnings") or 0
        total_notes  = await db.fetchval("SELECT COUNT(*) FROM notes") or 0
        total_filters= await db.fetchval("SELECT COUNT(*) FROM filters") or 0
    except Exception:
        total_users = total_chats = total_gbans = total_warns = total_notes = total_filters = "N/A"

    await msg.reply_text(
        f"✦ 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐒 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 📊 Statistics ]═══╗\n"
        f"║\n"
        f"║  👥 Users:    <b>{total_users}</b>\n"
        f"║  💬 Chats:    <b>{total_chats}</b>\n"
        f"║  🚫 GBans:    <b>{total_gbans}</b>\n"
        f"║  ⚠️ Warns:    <b>{total_warns}</b>\n"
        f"║  📝 Notes:    <b>{total_notes}</b>\n"
        f"║  🎯 Filters:  <b>{total_filters}</b>\n"
        f"║\n"
        f"║  ⏱️ Uptime:   <b>{uptime}</b>\n"
        f"║  📦 Version:  <b>v{BOT_VERSION}</b>\n"
        f"║  🐍 Python:   <b>{sys.version[:10]}</b>\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 10.3  Global Ban (Section-10 version) ─────────────────────
# Note: Uses existing `gbans` table from Section 1 DB setup.

async def s10_gban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /gban [reply | user_id] [reason]   Global ban. Sudo/Owner only.
    """
    user = update.effective_user
    msg  = update.effective_message

    if user.id != OWNER_ID and user.id not in INITIAL_SUDO_USERS:
        await msg.reply_text("❌ Sirf sudo/owner yeh kar sakta hai!")
        return

    target_id   = None
    target_name = "Unknown"
    reason      = "No reason provided"

    if msg.reply_to_message and msg.reply_to_message.from_user:
        target_id   = msg.reply_to_message.from_user.id
        target_name = msg.reply_to_message.from_user.first_name
        reason = " ".join(context.args) if context.args else reason
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = str(target_id)
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else reason
        except ValueError:
            await msg.reply_text("❌ Valid user ID do!")
            return
    else:
        await msg.reply_text("❌ Usage: /gban <user_id or reply> [reason]")
        return

    if target_id == OWNER_ID:
        await msg.reply_text("❌ Owner ko gban nahi kar sakte!")
        return

    try:
        await db.execute(
            "INSERT INTO gbans (user_id, reason, banned_by, banned_at) "
            "VALUES ($1, $2, $3, NOW()) "
            "ON CONFLICT (user_id) DO UPDATE SET reason = $2, banned_by = $3, banned_at = NOW()",
            target_id, reason, user.id
        )
        await db.execute(
            "UPDATE users SET is_gbanned = TRUE, gban_reason = $1 WHERE user_id = $2",
            reason, target_id
        )
        await msg.reply_text(
            f"🔨 <b>GLOBAL BAN</b>\n\n"
            f"👤 User:   {mention_html(target_id, target_name)}\n"
            f"📝 Reason: {html_escape(reason[:300])}\n"
            f"👮 By:     {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


async def s10_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /ungban [reply | user_id]   Remove global ban. Sudo/Owner only.
    """
    user = update.effective_user
    msg  = update.effective_message

    if user.id != OWNER_ID and user.id not in INITIAL_SUDO_USERS:
        await msg.reply_text("❌ Sirf sudo/owner yeh kar sakta hai!")
        return

    if msg.reply_to_message and msg.reply_to_message.from_user:
        target_id   = msg.reply_to_message.from_user.id
        target_name = msg.reply_to_message.from_user.first_name
    elif context.args:
        try:
            target_id   = int(context.args[0])
            target_name = str(target_id)
        except ValueError:
            await msg.reply_text("❌ Valid user ID do!")
            return
    else:
        await msg.reply_text("❌ Usage: /ungban <user_id or reply>")
        return

    try:
        result = await db.execute("DELETE FROM gbans WHERE user_id = $1", target_id)
        await db.execute(
            "UPDATE users SET is_gbanned = FALSE, gban_reason = '' WHERE user_id = $1",
            target_id
        )
        if "DELETE 0" in str(result):
            await msg.reply_text("ℹ️ User globally banned nahi tha.")
        else:
            await msg.reply_text(
                f"✅ Global ban remove: {mention_html(target_id, target_name)}",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")


async def _s10_gban_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto-kick globally banned users who appear in groups."""
    if not (update.effective_user and update.effective_chat):
        return
    u = update.effective_user
    c = update.effective_chat
    if c.type == "private" or u.is_bot:
        return
    try:
        row = await db.fetchrow("SELECT reason FROM gbans WHERE user_id = $1", u.id)
        if row:
            await c.ban_member(u.id)
            try:
                await update.effective_message.reply_text(
                    f"🚫 {mention_html(u.id, u.first_name)} globally banned hai!\n"
                    f"📝 Reason: {html_escape(row['reason'] or 'N/A')}\n"
                    f"Auto-removed.",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass
    except Exception:
        pass


# ── 10.4  Connection System ────────────────────────────────────

async def s10_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /connect <chat_id>   Connect your PM to a group so you can use group commands from PM.
    """
    user = update.effective_user
    msg  = update.effective_message

    if update.effective_chat.type != "private":
        connected = _user_connections.get(user.id)
        if connected:
            await msg.reply_text(
                f"ℹ️ Already connected to: <code>{connected}</code>\n"
                f"Use /connect in PM to manage.",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.reply_text(
                f"ℹ️ To connect, send in PM:\n"
                f"<code>/connect {update.effective_chat.id}</code>",
                parse_mode=ParseMode.HTML
            )
        return

    if not context.args:
        connected = _user_connections.get(user.id)
        if connected:
            await msg.reply_text(
                f"╔═══[ 🔗 CONNECTED ]═══╗\n"
                f"║\n"
                f"║  📌 Chat ID: <code>{connected}</code>\n"
                f"║\n"
                f"║  /disconnect  — Disconnect\n"
                f"╚═══════════════════════╝",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.reply_text(
                "╔═══[ 🔗 CONNECT ]═══╗\n"
                "║\n"
                "║  Usage: /connect <chat_id>\n"
                "║  Group mein ja ke ID copy karo.\n"
                "║\n"
                "╚═══════════════════════╝"
            )
        return

    try:
        chat_id = int(context.args[0])
    except ValueError:
        await msg.reply_text("❌ Valid chat ID do!")
        return

    _user_connections[user.id] = chat_id
    # Persist in DB
    try:
        await db.execute(
            "INSERT INTO connections (user_id, chat_id) VALUES ($1, $2) "
            "ON CONFLICT (user_id) DO UPDATE SET chat_id = $2, connected_at = NOW()",
            user.id, chat_id
        )
    except Exception:
        pass

    await msg.reply_text(
        f"✅ Connected to: <code>{chat_id}</code>",
        parse_mode=ParseMode.HTML
    )


async def s10_disconnect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /disconnect   Removes PM connection.
    """
    user = update.effective_user
    msg  = update.effective_message

    _user_connections.pop(user.id, None)
    try:
        await db.execute("DELETE FROM connections WHERE user_id = $1", user.id)
    except Exception:
        pass

    await msg.reply_text("✅ Disconnected!")


# ── 10.5  Reminder ─────────────────────────────────────────────

async def s10_remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /remind <time> <text>   Set a reminder.
    Time formats: 30s  10m  2h  1d  (max 7d, min 10s)
    """
    msg  = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if len(context.args) < 2:
        await msg.reply_text(
            "╔═══[ ⏰ REMINDER ]═══╗\n"
            "║\n"
            "║  Usage: /remind <time> <text>\n"
            "║\n"
            "║  Time formats:\n"
            "║   30s → 30 seconds\n"
            "║   10m → 10 minutes\n"
            "║   2h  → 2 hours\n"
            "║   1d  → 1 day\n"
            "║\n"
            "║  Example:\n"
            "║   /remind 30m Meeting!\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    time_str = context.args[0]
    text_rem = " ".join(context.args[1:])

    match = re.fullmatch(r"(\d+)([smhd])", time_str, re.IGNORECASE)
    if not match:
        await msg.reply_text("❌ Invalid format! Use: 30s / 10m / 2h / 1d")
        return

    amount = int(match.group(1))
    unit   = match.group(2).lower()
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    seconds = amount * multipliers[unit]

    if seconds < 10:
        await msg.reply_text("❌ Minimum 10 seconds!")
        return
    if seconds > 7 * 86400:
        await msg.reply_text("❌ Maximum 7 din!")
        return

    # Human-readable
    if unit == "s":  disp = f"{amount} second"
    elif unit == "m": disp = f"{amount} minute"
    elif unit == "h": disp = f"{amount} hour"
    else:             disp = f"{amount} day"

    await msg.reply_text(
        f"✅ Reminder set!\n"
        f"⏰ <b>{disp}</b> baad remind karunga:\n"
        f"📝 {html_escape(text_rem)}",
        parse_mode=ParseMode.HTML
    )

    # Save to DB (best-effort)
    remind_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    try:
        await db.execute(
            "INSERT INTO reminders (user_id, chat_id, reminder_text, remind_at) "
            "VALUES ($1, $2, $3, $4)",
            user.id, chat.id, text_rem, remind_at
        )
    except Exception:
        pass

    async def _fire_reminder() -> None:
        await asyncio.sleep(seconds)
        try:
            await msg.reply_text(
                f"⏰ <b>REMINDER</b> ⏰\n\n"
                f"{mention_html(user.id, user.first_name)},\n\n"
                f"📝 {html_escape(text_rem)}",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass
        # Mark done
        try:
            await db.execute(
                "UPDATE reminders SET is_done = TRUE "
                "WHERE user_id = $1 AND chat_id = $2 AND remind_at = $3",
                user.id, chat.id, remind_at
            )
        except Exception:
            pass

    asyncio.create_task(_fire_reminder())


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 11 ─ MEDIA & STICKERS
# ██████████████████████████████████████████████████════════════
# ═══════════════════════════════════════════════════════════════

# ── 11.1  Sticker ID ───────────────────────────────────────────

async def s11_stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stickerid   Reply to a sticker to get its file_id and info.
    """
    msg = update.effective_message

    if not (msg.reply_to_message and msg.reply_to_message.sticker):
        await msg.reply_text("❌ Kisi sticker ko reply karo!")
        return

    s = msg.reply_to_message.sticker
    await msg.reply_text(
        f"✦ 𝐒𝐓𝐈𝐂𝐊𝐄𝐑 𝐈𝐃 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🎭 Sticker Info ]═══╗\n"
        f"║\n"
        f"║  📌 File ID:\n"
        f"║  <code>{s.file_id}</code>\n"
        f"║\n"
        f"║  📌 Unique ID:\n"
        f"║  <code>{s.file_unique_id}</code>\n"
        f"║\n"
        f"║  📦 Set:      {html_escape(s.set_name or 'N/A')}\n"
        f"║  😊 Emoji:    {s.emoji or 'N/A'}\n"
        f"║  📐 Size:     {s.width}×{s.height}\n"
        f"║  🎬 Animated: {'Yes' if s.is_animated else 'No'}\n"
        f"║  📹 Video:    {'Yes' if s.is_video else 'No'}\n"
        f"║\n"
        f"╚═══════════════════════╝",
        parse_mode=ParseMode.HTML
    )


# ── 11.2  Kang Sticker ─────────────────────────────────────────

async def s11_kang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /kang [emoji]   Reply to a sticker or photo to add it to your personal pack.
    """
    msg  = update.effective_message
    user = update.effective_user

    if not msg.reply_to_message:
        await msg.reply_text(
            "╔═══[ 🎭 KANG ]═══╗\n"
            "║\n"
            "║  Kisi sticker ya photo\n"
            "║  ko reply karo /kang se!\n"
            "║\n"
            "║  /kang [emoji]\n"
            "║\n"
            "╚═══════════════════════╝"
        )
        return

    reply   = msg.reply_to_message
    emoji   = context.args[0] if context.args else "😎"
    wait    = await msg.reply_text("⏳ Sticker pack mein add ho raha hai...")

    try:
        bot_info  = await context.bot.get_me()
        pack_name = f"u{user.id}_by_{bot_info.username}"
        pack_title= f"{user.first_name[:32]}'s Pack"

        # Download file
        if reply.sticker:
            stk = reply.sticker
            if stk.is_animated:
                await wait.edit_text("❌ Animated stickers support nahi hain abhi!")
                return
            file_obj  = await stk.get_file()
            raw_bytes = await file_obj.download_as_bytearray()
            ext       = "webm" if stk.is_video else "webp"
            fmt       = "video" if stk.is_video else "static"
            use_emoji = stk.emoji or emoji
        elif reply.photo:
            file_obj  = await reply.photo[-1].get_file()
            raw_bytes = await file_obj.download_as_bytearray()
            ext       = "webp"
            fmt       = "static"
            use_emoji = emoji
            # Resize/convert via Pillow if available
            try:
                from PIL import Image as _PILImage
                img = _PILImage.open(io.BytesIO(bytes(raw_bytes))).convert("RGBA")
                img.thumbnail((512, 512), _PILImage.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="WEBP")
                raw_bytes = buf.getvalue()
            except ImportError:
                pass
        else:
            await wait.edit_text("❌ Sticker ya photo reply karo!")
            return

        sticker_bio      = io.BytesIO(bytes(raw_bytes))
        sticker_bio.name = f"sticker.{ext}"

        # Check if pack exists
        pack_exists = True
        try:
            await context.bot.get_sticker_set(pack_name)
        except BadRequest:
            pack_exists = False

        sticker_bio.seek(0)
        sticker_input = {
            "sticker":    sticker_bio,
            "emoji_list": [use_emoji],
        }

        if pack_exists:
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                sticker=sticker_input
            )
        else:
            await context.bot.create_new_sticker_set(
                user_id=user.id,
                name=pack_name,
                title=pack_title,
                stickers=[sticker_input],
                sticker_format=fmt
            )

        link = f"https://t.me/addstickers/{pack_name}"
        await wait.edit_text(
            f"✅ Sticker kanged!\n\n"
            f"🎭 Emoji: {use_emoji}\n"
            f"📦 Pack: {pack_title}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎭 Pack Dekho", url=link)]]
            )
        )
    except Exception as e:
        await wait.edit_text(
            f"❌ Kang fail!\n\n"
            f"Error: {html_escape(str(e)[:300])}\n\n"
            f"Note: Bot ko pehle ek baar /start karo PM mein."
        )


# ── 11.3  Get Sticker as File ──────────────────────────────────

async def s11_getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /getsticker   Reply to a sticker to download it as a file.
    """
    msg = update.effective_message

    if not (msg.reply_to_message and msg.reply_to_message.sticker):
        await msg.reply_text("❌ Kisi sticker ko reply karo!")
        return

    wait = await msg.reply_text("⏳ Downloading sticker...")
    try:
        stk  = msg.reply_to_message.sticker
        f    = await stk.get_file()
        data = await f.download_as_bytearray()
        ext  = "tgs" if stk.is_animated else ("webm" if stk.is_video else "webp")
        bio  = io.BytesIO(bytes(data))
        bio.name = f"sticker.{ext}"
        await wait.delete()
        await msg.reply_document(
            document=bio,
            filename=f"sticker.{ext}",
            caption=f"✅ Sticker as .{ext} file!"
        )
    except Exception as e:
        await wait.edit_text(f"❌ Error: {html_escape(str(e)[:200])}")


# ── 11.4  Sticker → Image ──────────────────────────────────────

async def s11_stoi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stoi   Reply to a static sticker to convert it to a PNG image.
    """
    msg = update.effective_message

    if not (msg.reply_to_message and msg.reply_to_message.sticker):
        await msg.reply_text("❌ Kisi sticker ko reply karo!")
        return

    stk = msg.reply_to_message.sticker
    if stk.is_animated or stk.is_video:
        await msg.reply_text("❌ Sirf static stickers convert ho sakte hain!")
        return

    wait = await msg.reply_text("⏳ Converting sticker to image...")
    try:
        f    = await stk.get_file()
        data = await f.download_as_bytearray()

        try:
            from PIL import Image as _PILImage
            img = _PILImage.open(io.BytesIO(bytes(data))).convert("RGBA")
            out = io.BytesIO()
            img.save(out, format="PNG")
            out.seek(0)
            await wait.delete()
            await msg.reply_photo(photo=out, caption="✅ Sticker → PNG image!")
        except ImportError:
            # Send raw webp if Pillow not installed
            bio = io.BytesIO(bytes(data))
            bio.name = "sticker.webp"
            await wait.delete()
            await msg.reply_document(document=bio, filename="sticker.webp",
                                      caption="✅ Sticker file (Pillow not installed)!")
    except Exception as e:
        await wait.edit_text(f"❌ Error: {html_escape(str(e)[:200])}")


# ── 11.5  Image → Sticker ──────────────────────────────────────

async def s11_itos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /itos   Reply to a photo to convert it to sticker-compatible WebP format.
    """
    msg = update.effective_message

    if not (msg.reply_to_message and msg.reply_to_message.photo):
        await msg.reply_text("❌ Kisi photo ko reply karo!")
        return

    wait = await msg.reply_text("⏳ Converting image to sticker format...")
    try:
        photo= msg.reply_to_message.photo[-1]
        f    = await photo.get_file()
        data = await f.download_as_bytearray()

        try:
            from PIL import Image as _PILImage
            img = _PILImage.open(io.BytesIO(bytes(data))).convert("RGBA")
            img.thumbnail((512, 512), _PILImage.LANCZOS)
            out = io.BytesIO()
            img.save(out, format="WEBP")
            out.seek(0)
            out.name = "sticker.webp"
            await wait.delete()
            await msg.reply_document(
                document=out,
                filename="sticker.webp",
                caption="✅ Image → Sticker format! /kang se use kar sakte ho."
            )
        except ImportError:
            bio = io.BytesIO(bytes(data))
            bio.name = "image.webp"
            await wait.delete()
            await msg.reply_document(document=bio, filename="image.webp",
                                      caption="✅ Raw image (Pillow install karo for proper conversion)!")
    except Exception as e:
        await wait.edit_text(f"❌ Error: {html_escape(str(e)[:200])}")


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 12 ─ OWNER ONLY COMMANDS
# ██████████████████████████████████████████████████════════════
# ═══════════════════════════════════════════════════════════════

def _owner_only(func: Callable) -> Callable:
    """Decorator: Only the bot owner can use this command."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
        if update.effective_user.id != OWNER_ID:
            await update.effective_message.reply_text("❌ Sirf Owner yeh kar sakta hai!")
            return
        return await func(update, context)
    return wrapper


# ── 12.1  Eval ─────────────────────────────────────────────────

@_owner_only
async def s12_eval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /eval <expression>   Evaluate a Python expression. Owner only.
    """
    msg = update.effective_message

    code = (
        " ".join(context.args)
        if context.args
        else (msg.reply_to_message.text if msg.reply_to_message else None)
    )
    if not code:
        await msg.reply_text("❌ Usage: /eval <code>")
        return

    wait = await msg.reply_text(f"⚡ Evaluating...\n<code>{html_escape(code[:200])}</code>",
                                  parse_mode=ParseMode.HTML)

    _eval_globals = {
        "update": update, "context": context,
        "bot": context.bot, "msg": msg,
        "chat": update.effective_chat,
        "user": update.effective_user,
        "db": db, "asyncio": asyncio,
        "os": os, "sys": sys, "json": json,
        "datetime": datetime, "time": time,
        "__builtins__": __builtins__,
    }

    try:
        result = eval(code, _eval_globals)  # type: ignore[arg-type]
        if asyncio.iscoroutine(result):
            result = await result
        out = str(result)[:3000]
    except Exception:
        out = traceback.format_exc()[:3000]

    await wait.edit_text(
        f"⚡ <b>EVAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 Input:\n<code>{html_escape(code[:500])}</code>\n\n"
        f"✅ Output:\n<code>{html_escape(out)}</code>",
        parse_mode=ParseMode.HTML
    )


# ── 12.2  Exec ─────────────────────────────────────────────────

@_owner_only
async def s12_exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /exec <code>   Execute Python statements. Owner only.
    Multi-line code: reply to a code message.
    """
    msg = update.effective_message

    code = (
        msg.reply_to_message.text
        if msg.reply_to_message
        else (" ".join(context.args) if context.args else None)
    )
    if not code:
        await msg.reply_text("❌ Usage: /exec <code>  OR  reply to code message")
        return

    wait = await msg.reply_text("⚡ Executing...")

    # Capture stdout
    _old_stdout = sys.stdout
    sys.stdout  = _buf = io.StringIO()

    _exec_globals = {
        "update": update, "context": context,
        "bot": context.bot, "msg": msg,
        "chat": update.effective_chat,
        "user": update.effective_user,
        "db": db, "asyncio": asyncio,
        "os": os, "sys": sys, "json": json,
        "datetime": datetime, "time": time,
        "__builtins__": __builtins__,
    }
    try:
        exec(code, _exec_globals)  # type: ignore[arg-type]
        out = _buf.getvalue().strip() or "✅ Executed (no stdout)"
    except Exception:
        out = traceback.format_exc().strip()
    finally:
        sys.stdout = _old_stdout

    await wait.edit_text(
        f"⚡ <b>EXEC</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<code>{html_escape(out[:3500])}</code>",
        parse_mode=ParseMode.HTML
    )


# ── 12.3  Shell ────────────────────────────────────────────────

@_owner_only
async def s12_shell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /sh <command>   Run a shell command. Owner only. 30-second timeout.
    """
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("❌ Usage: /sh <command>")
        return

    cmd  = " ".join(context.args)
    wait = await msg.reply_text(
        f"🖥️ Running:\n<code>{html_escape(cmd)}</code>",
        parse_mode=ParseMode.HTML
    )

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        except asyncio.TimeoutError:
            proc.kill()
            await wait.edit_text("❌ Command timeout (30s limit)!")
            return

        out = (stdout.decode("utf-8", errors="replace").strip() or
               stderr.decode("utf-8", errors="replace").strip() or
               "✅ Command executed (no output)")

        await wait.edit_text(
            f"🖥️ <b>SHELL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 CMD: <code>{html_escape(cmd)}</code>\n\n"
            f"<code>{html_escape(out[:3000])}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await wait.edit_text(f"❌ Shell Error: {html_escape(str(e)[:300])}")


# ── 12.4  Leave Chat ───────────────────────────────────────────

@_owner_only
async def s12_leavechat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /leavechat <chat_id>   Make the bot leave a chat. Owner only.
    """
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("❌ Usage: /leavechat <chat_id>")
        return

    try:
        cid = int(context.args[0])
        await context.bot.leave_chat(cid)
        await msg.reply_text(f"✅ Left chat: <code>{cid}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {html_escape(str(e)[:200])}")


# ── 12.5  System Status ────────────────────────────────────────

@_owner_only
async def s12_system(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /system   Shows bot uptime, Python version, and resource usage.
    """
    msg  = update.effective_message
    wait = await msg.reply_text("⏳ Fetching system info...")

    uptime = str(timedelta(seconds=int(time.time() - BOT_START_TIME)))

    cpu_p = mem_p = disk_p = "N/A"
    try:
        import psutil
        cpu_p  = f"{psutil.cpu_percent(interval=1):.1f}%"
        mem_p  = f"{psutil.virtual_memory().percent:.1f}%"
        disk_p = f"{psutil.disk_usage('/').percent:.1f}%"
    except ImportError:
        pass

    await wait.edit_text(
        f"✦ 𝐒𝐘𝐒𝐓𝐄𝐌 𝐒𝐓𝐀𝐓𝐔𝐒 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🖥️ System ]═══╗\n"
        f"║\n"
        f"║  ⏱️ Uptime:  <b>{uptime}</b>\n"
        f"║  🐍 Python:  {sys.version[:15]}\n"
        f"║  📦 Version: v{BOT_VERSION}\n"
        f"║\n"
        f"║  💻 CPU:    {cpu_p}\n"
        f"║  🧠 RAM:    {mem_p}\n"
        f"║  💾 Disk:   {disk_p}\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 12.6  Restart Bot ──────────────────────────────────────────

@_owner_only
async def s12_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /restart   Restart the bot process. Owner only.
    On Render, the process will restart automatically.
    """
    msg = update.effective_message
    await msg.reply_text("🔄 Restarting bot...")
    logger.info(f"Restart requested by owner {update.effective_user.id}")

    # Save restart info so bot can notify when back online
    try:
        with open("restart_info.json", "w") as fp:
            json.dump({"chat_id": msg.chat.id, "msg_id": msg.message_id}, fp)
    except Exception:
        pass

    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)


# ── 12.7  Database Stats ───────────────────────────────────────

@_owner_only
async def s12_dbstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /dbstats   Shows row counts for all DB tables. Owner only.
    """
    msg  = update.effective_message
    wait = await msg.reply_text("⏳ Querying database...")

    try:
        await db._ensure_connected()
        async with db.pool.acquire() as conn:
            tables = await conn.fetch(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            lines = []
            for tbl in tables:
                name = tbl["table_name"]
                try:
                    cnt = await conn.fetchval(f'SELECT COUNT(*) FROM "{name}"')
                    lines.append(f"║  📊 {name}: <b>{cnt}</b>")
                except Exception:
                    lines.append(f"║  📊 {name}: N/A")

        body = "\n".join(lines) if lines else "║  No tables found"
        await wait.edit_text(
            f"✦ 𝐃𝐁 𝐒𝐓𝐀𝐓𝐒 ✦\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"╔═══[ 🗄️ Database ]═══╗\n"
            f"║\n"
            f"{body}\n"
            f"║\n"
            f"╚═══════════════════════╝",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await wait.edit_text(f"❌ DB Error: {html_escape(str(e)[:300])}")


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   SECTION 13 ─ RANKING & XP SYSTEM
# ██████████████████████████████████████████████████════════════
# ═══════════════════════════════════════════════════════════════

# XP table is created in _s13_create_xp_table() at bot startup.

_XP_PER_MSG     = 5    # base XP per message
_XP_COOLDOWN    = 30   # seconds between XP awards per user in a group
_XP_DAILY       = 100  # daily reward XP

# ── Level math ─────────────────────────────────────────────────

def _xp_to_level(xp: int) -> int:
    """Determine level from total XP (progressive curve)."""
    level, needed = 1, 100
    while xp >= needed:
        xp -= needed
        level += 1
        needed = int(needed * 1.5)
    return level

def _xp_in_level(xp: int) -> Tuple[int, int, int]:
    """Return (level, xp_earned_in_this_level, xp_needed_for_next_level)."""
    level, needed = 1, 100
    while xp >= needed:
        xp -= needed
        level += 1
        needed = int(needed * 1.5)
    return level, xp, needed

def _rank_title(level: int) -> str:
    if level <  5: return "🌱 Newbie"
    if level < 10: return "⚡ Rising Star"
    if level < 20: return "🔥 Active Member"
    if level < 30: return "💎 Diamond"
    if level < 50: return "👑 Legend"
    return "🌟 God"

# ── XP Table creation ──────────────────────────────────────────

async def _s13_create_xp_table() -> None:
    """Creates the user_xp table if it doesn't exist."""
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_xp (
                chat_id   BIGINT    NOT NULL,
                user_id   BIGINT    NOT NULL,
                xp        INTEGER   NOT NULL DEFAULT 0,
                username  TEXT      DEFAULT '',
                full_name TEXT      DEFAULT '',
                updated_at TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (chat_id, user_id)
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id       BIGINT  PRIMARY KEY,
                last_claimed  DATE,
                streak        INTEGER DEFAULT 0
            );
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_xp_chat_xp
            ON user_xp (chat_id, xp DESC);
        """)
        logger.info("✅ Section 13 XP tables created!")
    except Exception as e:
        logger.error(f"❌ XP table creation error: {e}")


# ── 13.1  XP Message Handler ───────────────────────────────────

async def s13_xp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Gives XP for every group message (with cooldown).
    Attached as MessageHandler in group=3.
    """
    if not (update.effective_user and update.effective_chat and update.effective_message):
        return
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private" or user.is_bot:
        return

    # Cooldown check
    key  = (chat.id, user.id)
    now  = time.time()
    last = _xp_cooldown.get(key, 0.0)
    if now - last < _XP_COOLDOWN:
        return
    _xp_cooldown[key] = now

    # XP gain (random to feel organic)
    gain = random.randint(_XP_PER_MSG - 2, _XP_PER_MSG + 3)

    # Fetch current XP to check for level-up
    try:
        row = await db.fetchrow(
            "SELECT xp FROM user_xp WHERE chat_id=$1 AND user_id=$2",
            chat.id, user.id
        )
        old_xp = row["xp"] if row else 0
    except Exception:
        old_xp = 0

    new_xp = old_xp + gain

    try:
        await db.execute(
            """
            INSERT INTO user_xp (chat_id, user_id, xp, username, full_name, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT (chat_id, user_id) DO UPDATE
              SET xp        = user_xp.xp + $3,
                  username  = EXCLUDED.username,
                  full_name = EXCLUDED.full_name,
                  updated_at= NOW()
            """,
            chat.id, user.id, gain,
            user.username or "", user.full_name or user.first_name
        )
    except Exception as e:
        logger.debug(f"XP save error: {e}")
        return

    # Level-up notification
    old_level = _xp_to_level(old_xp)
    new_level = _xp_to_level(new_xp)
    if new_level > old_level:
        try:
            await update.effective_message.reply_text(
                f"🎉 <b>LEVEL UP!</b> 🎉\n\n"
                f"🎊 {mention_html(user.id, user.first_name)}\n"
                f"⬆️ Level <b>{old_level}</b> → <b>{new_level}</b>\n"
                f"🏆 {_rank_title(new_level)}\n\n"
                f"✨ Keep chatting!",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass


# ── 13.2  Rank Command ─────────────────────────────────────────

async def s13_rank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /rank [reply]   Shows rank card for you or the replied user.
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if chat.type == "private":
        await msg.reply_text("❌ Group mein use karo!")
        return

    target = (
        msg.reply_to_message.from_user
        if (msg.reply_to_message and msg.reply_to_message.from_user)
        else update.effective_user
    )
    if target.is_bot:
        await msg.reply_text("❌ Bots ka rank nahi hota!")
        return

    try:
        row = await db.fetchrow(
            "SELECT xp FROM user_xp WHERE chat_id=$1 AND user_id=$2",
            chat.id, target.id
        )
        total_xp = row["xp"] if row else 0

        rank_pos = await db.fetchval(
            "SELECT COUNT(*)+1 FROM user_xp WHERE chat_id=$1 AND xp > $2",
            chat.id, total_xp
        ) or 1
    except Exception:
        total_xp = 0
        rank_pos = "?"

    level, xp_in, xp_need = _xp_in_level(total_xp)

    # Progress bar (10 blocks)
    filled = int((xp_in / max(xp_need, 1)) * 10)
    bar    = "█" * filled + "░" * (10 - filled)

    await msg.reply_text(
        f"✦ 𝐑𝐀𝐍𝐊 𝐂𝐀𝐑𝐃 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🏆 {html_escape(target.first_name[:20])} ]═══╗\n"
        f"║\n"
        f"║  {_rank_title(level)}\n"
        f"║\n"
        f"║  🌟 Level:   <b>{level}</b>\n"
        f"║  📊 Rank:    <b>#{rank_pos}</b>\n"
        f"║  ✨ Total XP: <b>{total_xp}</b>\n"
        f"║\n"
        f"║  📈 Progress:\n"
        f"║  [{bar}]\n"
        f"║  {xp_in}/{xp_need} XP\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 13.3  Group Leaderboard ────────────────────────────────────

async def s13_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /leaderboard   Shows top 10 users in this group by XP.
    Alias: /top
    """
    msg  = update.effective_message
    chat = update.effective_chat

    if chat.type == "private":
        await msg.reply_text("❌ Group mein use karo!")
        return

    wait = await msg.reply_text("⏳ Leaderboard load ho raha hai...")
    try:
        rows = await db.fetch(
            "SELECT user_id, xp, full_name FROM user_xp "
            "WHERE chat_id=$1 ORDER BY xp DESC LIMIT 10",
            chat.id
        )
    except Exception as e:
        await wait.edit_text(f"❌ DB Error: {html_escape(str(e)[:200])}")
        return

    if not rows:
        await wait.edit_text("❌ Koi XP data nahi! Pehle chat karo.")
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines  = []
    for i, r in enumerate(rows):
        lvl    = _xp_to_level(r["xp"])
        name   = html_escape((r["full_name"] or str(r["user_id"]))[:20])
        uid    = r["user_id"]
        medal  = medals[i] if i < len(medals) else f"{i+1}."
        lines.append(
            f"║  {medal} <a href='tg://user?id={uid}'>{name}</a>\n"
            f"║     Lv.{lvl} · {r['xp']} XP"
        )

    body = "\n║\n".join(lines)
    await wait.edit_text(
        f"✦ 𝐋𝐄𝐀𝐃𝐄𝐑𝐁𝐎𝐀𝐑𝐃 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🏆 {html_escape((chat.title or 'Group')[:25])} ]═══╗\n"
        f"║\n"
        f"{body}\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 13.4  Global Top ───────────────────────────────────────────

async def s13_globaltop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /gtop   Global top 10 users across all groups.
    """
    msg  = update.effective_message
    wait = await msg.reply_text("⏳ Global top fetch ho raha hai...")

    try:
        rows = await db.fetch(
            """
            SELECT user_id, SUM(xp) AS total_xp, MAX(full_name) AS name
            FROM user_xp
            GROUP BY user_id
            ORDER BY total_xp DESC
            LIMIT 10
            """
        )
    except Exception as e:
        await wait.edit_text(f"❌ DB Error: {html_escape(str(e)[:200])}")
        return

    if not rows:
        await wait.edit_text("❌ Koi global XP data nahi!")
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines  = []
    for i, r in enumerate(rows):
        total = int(r["total_xp"])
        lvl   = _xp_to_level(total)
        uid   = r["user_id"]
        name  = html_escape((r["name"] or str(uid))[:20])
        medal = medals[i] if i < len(medals) else f"{i+1}."
        lines.append(
            f"║  {medal} <a href='tg://user?id={uid}'>{name}</a>\n"
            f"║     Lv.{lvl} · {total} XP"
        )

    body = "\n║\n".join(lines)
    await wait.edit_text(
        f"✦ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐓𝐎𝐏 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🌍 Top Users ]═══╗\n"
        f"║\n"
        f"{body}\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ── 13.5  Daily Reward ─────────────────────────────────────────

async def s13_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /daily   Claim a daily XP bonus. Resets at midnight UTC.
    """
    user = update.effective_user
    msg  = update.effective_message
    chat = update.effective_chat

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Check last claim
    try:
        row = await db.fetchrow(
            "SELECT last_claimed, streak FROM daily_rewards WHERE user_id = $1",
            user.id
        )
        if row and str(row["last_claimed"]) == today:
            await msg.reply_text(
                f"╔═══[ ⏰ DAILY ]═══╗\n"
                f"║\n"
                f"║  ❌ Aaj ka reward le liya!\n"
                f"║  Kal dobara aana 🌙\n"
                f"║\n"
                f"╚═══════════════════════╝"
            )
            return

        # Calculate streak
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        old_streak = row["streak"] if row else 0
        new_streak = (old_streak + 1) if (row and str(row["last_claimed"]) == yesterday) else 1
    except Exception:
        new_streak = 1

    # Streak bonus
    bonus = min(new_streak * 10, 150)   # +10 XP per day, max +150
    total_reward = _XP_DAILY + bonus

    try:
        await db.execute(
            """
            INSERT INTO daily_rewards (user_id, last_claimed, streak)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
              SET last_claimed = $2, streak = $3
            """,
            user.id, today, new_streak
        )
        # Add XP in current group (if group)
        if chat.type != "private":
            await db.execute(
                """
                INSERT INTO user_xp (chat_id, user_id, xp, username, full_name, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (chat_id, user_id) DO UPDATE
                  SET xp = user_xp.xp + $3, updated_at = NOW()
                """,
                chat.id, user.id, total_reward,
                user.username or "", user.full_name or user.first_name
            )
    except Exception as e:
        await msg.reply_text(f"❌ DB Error: {html_escape(str(e)[:200])}")
        return

    streak_fire = "🔥" * min(new_streak, 7)

    await msg.reply_text(
        f"✦ 𝐃𝐀𝐈𝐋𝐘 𝐑𝐄𝐖𝐀𝐑𝐃 ✦\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"╔═══[ 🎁 Reward ]═══╗\n"
        f"║\n"
        f"║  👤 {mention_html(user.id, user.first_name)}\n"
        f"║\n"
        f"║  ✅ Base XP:   +{_XP_DAILY}\n"
        f"║  {streak_fire} Streak:  Day {new_streak} (+{bonus})\n"
        f"║  🎯 Total:    +{total_reward} XP\n"
        f"║\n"
        f"║  🌟 Kal dobara aana!\n"
        f"║\n"
        f"╚═══════════════════════╝\n"
        f"𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』",
        parse_mode=ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████
#   REGISTER ALL SECTION 8–13 HANDLERS
# ██████████████████████████████████████████████████════════════
# ═══════════════════════════════════════════════════════════════

def register_section8_13_handlers(application: "Application") -> None:
    """
    Call this in your main() / post_init, after all other sections.

    Usage in post_init:
        register_section8_13_handlers(application)
        asyncio.create_task(_s13_create_xp_table())
    """

    # ── SECTION 8 ─ Tools & Utilities ──────────────────────────
    application.add_handler(CommandHandler(["telegraph", "paste"],  s8_telegraph))
    application.add_handler(CommandHandler(["shorturl", "shorten"], s8_shorturl))
    application.add_handler(CommandHandler(["qr", "qrcode"],        s8_qr))
    application.add_handler(CommandHandler(["calc", "calculate"],   s8_calc))
    application.add_handler(CommandHandler(["tr", "translate"],     s8_tr))
    application.add_handler(CommandHandler(["tts", "speak"],        s8_tts))
    application.add_handler(CommandHandler(["weather", "wttr"],     s8_weather))
    application.add_handler(CommandHandler(["wiki", "wikipedia"],   s8_wiki))
    application.add_handler(CommandHandler(["google", "g"],         s8_google))
    application.add_handler(CommandHandler(["imdb", "movie"],       s8_imdb))

    # ── SECTION 9 ─ Group Settings ──────────────────────────────
    application.add_handler(CommandHandler(["lock"],                s9_lock))
    application.add_handler(CommandHandler(["unlock"],              s9_unlock))
    application.add_handler(CommandHandler(["rules"],               s9_rules))
    application.add_handler(CommandHandler(["setrules"],            s9_setrules))
    application.add_handler(CommandHandler(["resetrules"],          s9_resetrules))
    application.add_handler(CommandHandler(["setlang"],             s9_setlang))
    application.add_handler(CommandHandler(["report"],              s9_report))
    application.add_handler(CommandHandler(["staff"],               s9_staff))
    application.add_handler(CommandHandler(["disable"],             s9_disable))
    application.add_handler(CommandHandler(["enable"],              s9_enable))
    application.add_handler(CommandHandler(["nightmode", "night"],  s9_nightmode))
    application.add_handler(CommandHandler(["setlog"],              s9_setlog))

    # Report callback
    application.add_handler(CallbackQueryHandler(s9_report_callback, pattern=r"^rpt_"))

    # Night mode: run every hour
    if application.job_queue:
        application.job_queue.run_repeating(
            _night_mode_job, interval=3600, first=60, name="night_mode_job"
        )

    # ── SECTION 10 ─ Misc & Advanced ────────────────────────────
    application.add_handler(CommandHandler(["broadcast"],           s10_broadcast))
    application.add_handler(CommandHandler(["gbroadcast"],          s10_gbroadcast))
    application.add_handler(CommandHandler(["botstats"],            s10_botstats))
    application.add_handler(CommandHandler(["gban"],                s10_gban))
    application.add_handler(CommandHandler(["ungban"],              s10_ungban))
    application.add_handler(CommandHandler(["connect"],             s10_connect))
    application.add_handler(CommandHandler(["disconnect"],          s10_disconnect))
    application.add_handler(CommandHandler(["remind", "reminder"],  s10_remind))

    # Global ban filter (early group so it runs before XP, etc.)
    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS,
            _s10_gban_filter
        ),
        group=1
    )

    # ── SECTION 11 ─ Media & Stickers ───────────────────────────
    application.add_handler(CommandHandler(["stickerid", "sid"],    s11_stickerid))
    application.add_handler(CommandHandler(["kang"],                s11_kang))
    application.add_handler(CommandHandler(["getsticker", "gsticker"], s11_getsticker))
    application.add_handler(CommandHandler(["stoi"],                s11_stoi))
    application.add_handler(CommandHandler(["itos"],                s11_itos))

    # ── SECTION 12 ─ Owner Only ──────────────────────────────────
    application.add_handler(CommandHandler(["eval"],                s12_eval))
    application.add_handler(CommandHandler(["exec"],                s12_exec))
    application.add_handler(CommandHandler(["sh", "shell"],         s12_shell))
    application.add_handler(CommandHandler(["leavechat"],           s12_leavechat))
    application.add_handler(CommandHandler(["system", "sysinfo"],   s12_system))
    application.add_handler(CommandHandler(["restart"],             s12_restart))
    application.add_handler(CommandHandler(["dbstats"],             s12_dbstats))

    # ── SECTION 13 ─ Ranking & XP ───────────────────────────────
    application.add_handler(CommandHandler(["rank", "level"],       s13_rank))
    application.add_handler(CommandHandler(["leaderboard", "lb"],   s13_leaderboard))
    application.add_handler(CommandHandler(["gtop", "globaltop"],   s13_globaltop))
    application.add_handler(CommandHandler(["daily"],               s13_daily))

    # XP message handler — group=3 so it runs AFTER other msg handlers
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            s13_xp_handler
        ),
        group=3
    )

    logger.info(
        "✅ Sections 8–13 handlers registered! "
        "(Tools / Group / Advanced / Stickers / Owner / XP)"
    )


# ═══════════════════════════════════════════════════════════════
# ◈◈◈  HOW TO INTEGRATE  ◈◈◈
# ═══════════════════════════════════════════════════════════════
#
# 1. Append this entire file to the end of Bot.py
#
# 2. Inside  post_init()  (already defined in Section 1),
#    add these two lines AFTER  await cache.load_from_db() :
#
#        register_section8_13_handlers(application)
#        asyncio.create_task(_s13_create_xp_table())
#
# 3. In  register_handlers()  (Section 1),
#    call it from there instead if you prefer — just add:
#
#        register_section8_13_handlers(application)
#
# 4. Optional env vars:
#        OMDB_API_KEY  — free from https://www.omdbapi.com/
#
# 5. Optional pip packages for full sticker conversion:
#        pip install Pillow
#        pip install psutil   (for /system CPU / RAM info)
#
# ═══════════════════════════════════════════════════════════════
# SECTION 8–13 COMPLETE ✅
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ◈ MISSING FUN FUNCTIONS (Section 7)
# ═══════════════════════════════════════════════════════════════

TRUTH_QUESTIONS = [
    "Kabhi kisi ko bina bole pasand kiya hai?",
    "Teri crush kaun hai group mein?",
    "Last time kab roya/royi tha?",
    "Sabse bada jhooth kya bola hai life mein?",
    "Kabhi kisi ki diary/phone padhi hai?",
    "Pehli crush ka naam batao?",
    "Life ka sabse embarrassing moment?",
    "Kabhi cheating ki hai exam mein?",
    "Aaj tak ka sabse bada regret?",
    "Apni life ka sabse bada secret?",
]
DARE_CHALLENGES = [
    "Apna profile pic 1 ghante ke liye funny photo se replace karo!",
    "Group mein ek shayari likho abhi!",
    "10 pushups karo aur proof bhejo!",
    "Kisi member ko compliment do publicly!",
    "Ab se 10 minutes tak sirf caps lock mein baat karo!",
    "Ek joke sunao jo genuinely funny ho!",
    "Group mein apna favorite meme share karo!",
    "Apne baare mein 5 fun facts batao!",
    "5 minute ke liye sirf hindi mein baat karo!",
    "Kisi ko \'you are amazing\' wala message karo!",
]
EIGHTBALL_ANSWERS = [
    "✅ Bilkul haan! 100% sure!",
    "✅ Definitely yes!",
    "✅ Mere hisaab se haan!",
    "🤔 Abhi clear nahi hai...",
    "🤔 Dubara poochho thodi der baad!",
    "❌ Nahi lagta...",
    "❌ Bilkul nahi!",
    "❌ Outlook not so good!",
]

async def truth_command(update, context):
    try:
        user = update.effective_user
        if not user: return
        q = random.choice(TRUTH_QUESTIONS)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 New", callback_data="fun_truth"),
            InlineKeyboardButton("🎮 Menu", callback_data="fun_menu"),
        ]])
        await update.effective_message.reply_text(
            f"✦ 𝐓𝐑𝐔𝐓𝐇 ✦\n━━━━━━━━━━━━━━━━━━\n"
            f"║  👤 {mention_html(user.id, user.first_name)}\n║  ❓ {q}",
            parse_mode=ParseMode.HTML, reply_markup=kb)
    except: pass

async def dare_command(update, context):
    try:
        user = update.effective_user
        if not user: return
        d = random.choice(DARE_CHALLENGES)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 New", callback_data="fun_dare"),
            InlineKeyboardButton("🎮 Menu", callback_data="fun_menu"),
        ]])
        await update.effective_message.reply_text(
            f"✦ 𝐃𝐀𝐑𝐄 ✦\n━━━━━━━━━━━━━━━━━━\n"
            f"║  👤 {mention_html(user.id, user.first_name)}\n║  ⚡ {d}",
            parse_mode=ParseMode.HTML, reply_markup=kb)
    except: pass

async def eightball_command(update, context):
    try:
        user = update.effective_user
        msg = update.effective_message
        if not user or not msg: return
        question = " ".join(context.args) if context.args else ""
        if not question and msg.reply_to_message and msg.reply_to_message.text:
            question = msg.reply_to_message.text
        if not question:
            await msg.reply_text("❓ Sawaal poochho!\nExample: <code>/8ball Kya job milegi?</code>", parse_mode=ParseMode.HTML)
            return
        ans = random.choice(EIGHTBALL_ANSWERS)
        await msg.reply_text(
            f"🎱 ❓ {html_escape(question[:200])}\n\n{ans}",
            parse_mode=ParseMode.HTML)
    except: pass

async def dice_command(update, context):
    try:
        user = update.effective_user
        if not user: return
        await update.effective_message.reply_text(
            f"🎲 {mention_html(user.id, user.first_name)} ne dice roll kiya!", parse_mode=ParseMode.HTML)
        await context.bot.send_dice(update.effective_chat.id)
    except: pass

async def roll_command(update, context):
    try:
        user = update.effective_user
        if not user: return
        result = random.randint(1, 6)
        faces = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
        await update.effective_message.reply_text(
            f"🎲 {mention_html(user.id, user.first_name)} ka roll: {faces[result-1]} ({result})",
            parse_mode=ParseMode.HTML)
    except: pass

def register_section7_handlers(application):
    application.add_handler(CommandHandler(["fun","games"],    fun_command))
    application.add_handler(CommandHandler("truth",            truth_command))
    application.add_handler(CommandHandler("dare",             dare_command))
    application.add_handler(CommandHandler(["8ball","ball"],   eightball_command))
    application.add_handler(CommandHandler("dice",             dice_command))
    application.add_handler(CommandHandler("roll",             roll_command))
    application.add_handler(CommandHandler("flip",             flip_command))
    application.add_handler(CommandHandler("love",             love_command))
    application.add_handler(CommandHandler("roast",            roast_command))
    application.add_handler(CommandHandler("compliment",       compliment_command))
    application.add_handler(CommandHandler("joke",             joke_command))
    application.add_handler(CommandHandler("quote",            quote_command))
    application.add_handler(CommandHandler("trivia",           trivia_command))
    application.add_handler(CallbackQueryHandler(fun_section_callback,   pattern="^fun_"))
    application.add_handler(CallbackQueryHandler(fun_section_callback,   pattern="^dare_accepted$"))
    application.add_handler(CallbackQueryHandler(trivia_answer_callback, pattern=r"^trivia_[ABCD]_"))
    logger.info("✅ Section 7: Fun & Games registered!")


# ═══════════════════════════════════════════════════════════════
# ◈ REGISTER ALL HANDLERS
# ═══════════════════════════════════════════════════════════════

def register_handlers(application: "Application") -> None:
    application.add_handler(CommandHandler("start",       cmd_start))
    application.add_handler(CommandHandler("help",        cmd_help))
    application.add_handler(CommandHandler("about",       cmd_about))
    application.add_handler(CommandHandler("alive",       cmd_alive))
    application.add_handler(CommandHandler("ping",        cmd_ping))
    application.add_handler(CommandHandler("id",          cmd_id))
    application.add_handler(CommandHandler("info",        cmd_info))
    application.add_handler(CommandHandler("stats",       cmd_stats))
    application.add_handler(CommandHandler("addsudo",     cmd_addsudo))
    application.add_handler(CommandHandler("rmsudo",      cmd_rmsudo))
    application.add_handler(CommandHandler("sudolist",    cmd_sudolist))
    application.add_handler(CommandHandler("addsupport",  cmd_addsupport))
    application.add_handler(CommandHandler("rmsupport",   cmd_rmsupport))
    application.add_handler(CommandHandler("supportlist", cmd_supportlist))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, track_user_chat), group=99)
    register_section2_handlers(application)
    register_section3_handlers(application)
    register_section4_handlers(application)
    register_section5_handlers(application)
    register_section6_handlers(application)
    register_section7_handlers(application)
    register_section8_13_handlers(application)
    application.add_error_handler(error_handler)
    logger.info("✅ ALL handlers registered — Sections 1-13!")


# ═══════════════════════════════════════════════════════════════
# ◈ POST INIT
# ═══════════════════════════════════════════════════════════════

async def post_init(application: "Application") -> None:
    logger.info("🔄 Running post-init...")
    try:
        await db.connect()
        logger.info("✅ DB connected")
    except Exception as e:
        logger.error(f"❌ DB connect error: {e}")

    try: await cache.load_from_db()
    except Exception as e: logger.error(f"Cache error: {e}")

    for name, fn in [
        ("Sec2", section2_post_init),
        ("Sec3", section3_post_init),
        ("Sec4", section4_post_init),
        ("Sec5", section5_post_init),
    ]:
        try: await fn(application)
        except Exception as e: logger.error(f"{name} post_init error: {e}")

    asyncio.create_task(_s13_create_xp_table())

    # ── Keep-alive ping to prevent Render free tier from sleeping ──
    async def _keep_alive():
        import aiohttp
        while True:
            await asyncio.sleep(8 * 60)  # ping every 8 minutes
            try:
                if RENDER_EXTERNAL_URL:
                    async with aiohttp.ClientSession() as session:
                        await session.get(f"{RENDER_EXTERNAL_URL}/health", timeout=aiohttp.ClientTimeout(total=10))
                    logger.info("💓 Keep-alive ping sent")
            except Exception:
                pass
    if RENDER_EXTERNAL_URL:
        asyncio.create_task(_keep_alive())

    try:
        await application.bot.set_my_commands([
            BotCommand("start","✦ Start"), BotCommand("help","❓ Help"),
            BotCommand("id","🆔 ID"), BotCommand("info","👤 Info"),
            BotCommand("ping","🏓 Ping"), BotCommand("alive","💚 Alive"),
        ], scope=BotCommandScopeAllPrivateChats())
        await application.bot.set_my_commands([
            BotCommand("ban","🔨 Ban"), BotCommand("mute","🔇 Mute"),
            BotCommand("warn","⚠️ Warn"), BotCommand("kick","👢 Kick"),
            BotCommand("pin","📌 Pin"), BotCommand("id","🆔 ID"),
            BotCommand("info","👤 Info"), BotCommand("rules","📋 Rules"),
            BotCommand("notes","📝 Notes"), BotCommand("report","📢 Report"),
        ], scope=BotCommandScopeAllGroupChats())
    except Exception as e: logger.error(f"Commands set error: {e}")

    try:
        bot_me = await application.bot.get_me()
        logger.info(f"✅ Bot: @{bot_me.username}")
        if LOG_CHANNEL_ID:
            await application.bot.send_message(
                LOG_CHANNEL_ID,
                f"🚀 <b>Bot Started</b>\n• @{bot_me.username}\n• v{BOT_VERSION}\n• DB: ✅",
                parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f"Startup log error: {e}")


async def post_shutdown(application: "Application") -> None:
    logger.info("🔄 Shutting down...")
    await db.close()
    logger.info("✅ Done.")


# ═══════════════════════════════════════════════════════════════
# ◈ MAIN
# ═══════════════════════════════════════════════════════════════

async def main() -> None:
    if not BOT_TOKEN:   logger.error("❌ BOT_TOKEN missing!");   sys.exit(1)
    if not DATABASE_URL: logger.error("❌ DATABASE_URL missing!"); sys.exit(1)
    if not OWNER_ID:    logger.error("❌ OWNER_ID missing!");    sys.exit(1)

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .concurrent_updates(True)
        .connect_timeout(30).read_timeout(30).write_timeout(30)
        .build()
    )
    register_handlers(application)

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"
        await application.initialize()
        await application.start()
        await application.bot.set_webhook(
            url=webhook_url, secret_token=WEBHOOK_SECRET,
            allowed_updates=["message","edited_message","callback_query",
                "chat_member","my_chat_member","inline_query","chosen_inline_result"],
            drop_pending_updates=True)
        logger.info(f"✅ Webhook: {webhook_url}")
        web_server = WebServer(application)
        runner = web.AppRunner(web_server.app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        logger.info(f"✅ Web server on port {PORT}")
        stop_event = asyncio.Event()
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try: loop.add_signal_handler(sig, lambda: stop_event.set())
            except NotImplementedError: pass
        await stop_event.wait()
        await application.bot.delete_webhook()
        await application.stop()
        await application.shutdown()
        await runner.cleanup()
    else:
        await application.run_polling(drop_pending_updates=True,
            allowed_updates=["message","edited_message","callback_query","chat_member","my_chat_member"])


# ═══════════════════════════════════════════════════════════════
# ◈ RUN  ← LAST LINE OF FILE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"Starting {BOT_NAME} v{BOT_VERSION}...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped.")
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)
