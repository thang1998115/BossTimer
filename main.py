import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

# ====== CẤU HÌNH CƠ BẢN ======
TZ = ZoneInfo("Asia/Ho_Chi_Minh")  # múi giờ VN
PREFIX = "!"
DATA_FILE = "data.json"

from keep_alive import keep_alive

keep_alive()  # giữ Replit luôn "thức" (sẽ kết hợp UptimeRobot ở bước 4)

# TOKEN: đặt bằng Replit Secret (Settings → Secrets)
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ====== DANH SÁCH ĐỊA ĐIỂM → THỜI GIAN HỒI (PHÚT) + TỈ LỆ (%) ======
# Lưu ý: chỉ dùng địa điểm (English), bỏ tiếng Trung.
# Bạn có thể gõ alias tắt, ví dụ: fe, ant, gah, cruma_b6, ...
LOCATIONS = {
    # key: (Label, respawn_minutes, spawn_rate, [aliases...])
    "repirio": ("Repirio", 7 * 60, 50, ["repirio", "repiro", "repi"]),
    "orfen": ("Orfen", 24 * 60, 33, ["orfen", "or"]),
    "queen_ant": ("Queen Ant/Ant Nest (B3)", 6 * 60, 33,
                  ["queen ant", "queenant", "ant", "antb3", "ant_nest_b3", "ant3", "b3", "queen"]),
    "gahareth": ("Gahareth/Tanor Canyon", 9 * 60, 50,
                 ["gahareth", "gah", "tanor", "tanor_canyon", "canyon"]),
    "felis": ("Felis/Bee Hive", 3 * 60, 50,
              ["felis", "fe", "fel", "beehive", "bee", "hive", "bee hive"]),
    "pan_narod": ("Pan Narod/Gorgon Flower Garden", 5 * 60, 50,
                  ["pan narod", "pannarod", "panna", "narod", "gorgon", "gfg", "flower", "gorgon flower garden"]),
    "timiniel": ("Timiniel", 8 * 60, 100, ["timiniel", "timin"]),
    "timitris": ("Timitris/Floran Fields", 8 * 60, 100,
                 ["timitris", "timit", "floran", "flor", "floran_fields", "floran fields"]),
    "mutated_cruma": ("Mutated Cruma/Cruma Marshlands", 8 * 60, 100,
                      ["mutated cruma", "mutated", "muta", "cruma_marsh", "marshlands", "marsh", "cruma marshlands"]),
    "contaminated_cruma": ("Contaminated Cruma/Cruma Tower (B3)", 8 * 60, 100,
                           ["contaminated cruma", "contaminated", "contami", "conta", "cont", "cruma_b3", "ct_b3", "cruma3", "cruma tower b3"]),
    "basila": ("Basila/Southern Wasteland", 4 * 60, 50,
               ["basila", "basil", "bas", "southern", "southern_wasteland", "waste", "southern wasteland"]),
    "dragon": ("Dragon/Antharas Lair (B6)", 12 * 60, 33,
               ["dragon", "dra", "antharas_b6", "antharas", "b6", "antharas lair", "antharas lair b6"]),
    "core_susceptor": ("Core Susceptor/Cruma Tower (B7)", 10 * 60, 33,
                       ["core susceptor", "core", "susceptor", "sus", "cruma_b7", "ct_b7", "cruma7", "cruma tower b7"]),
    "breka": ("Breka/Breka's Stronghold", 6 * 60, 50,
              ["breka", "brekas", "breka's stronghold", "stronghold"]),
    "talkin": ("Talkin/Leto Lizardman", 8 * 60, 50,
               ["talkin", "tal", "leto", "lizardman", "leto lizardman"]),
    "tempest": ("Tempest/Morgue", 6 * 60, 50,
                ["tempest", "tem", "temp", "morgue"]),
    "chertuba": ("Chertuba/Chertuba's Barracks", 6 * 60, 50,
                 ["chertuba", "barracks", "chertuba's barracks"]),
    "matura": ("Matura/Pillagers' Outpost", 6 * 60, 50,
               ["matura", "mat", "pillagers", "outpost", "pillagers' outpost", "pillagers outpost"]),
    "enkura": ("Enkura/Dion Plains", 6 * 60, 50,
               ["enkura", "enk", "dion", "plains", "dion_plains", "dion plains"]),
    "stonegeist": ("Stonegeist/Giants' Vestige", 7 * 60, 100,
                   ["stonegeist", "stone", "giants", "vestige", "giants_vestige", "giants' vestige", "giants vestige"]),
    "tromba": ("Tromba/Bloodstained Swampland", 7 * 60, 50,
               ["tromba", "trom", "bloodstained", "swamp", "blood_swamp", "bloodstained swampland"]),
    "kelsus": ("Kelsus/Ruins of Despair", 10 * 60, 50,
               ["kelsus", "kel", "despair", "ruins_of_despair", "ruins of despair"]),
    "talakin": ("Talakin/Rebel Territory", 10 * 60, 100,
                ["talakin", "tala", "rebel", "rebel_territory", "rebel territory"]),
    "medusa": ("Medusa/Medusa Garden", 10 * 60, 100,
               ["medusa", "med", "medusa_garden", "medusa garden"]),
    "sarka": ("Sarka/Delu Dwellings", 10 * 60, 100,
              ["sarka", "sar", "delu", "delu_dwellings", "delu dwellings"]),
    "katan": ("Katan/Cruma Tower (B6)", 10 * 60, 100,
              ["katan", "kat", "cruma_b6", "ct_b6", "cruma6", "cruma tower b6"]),
    "black_lily": ("Black Lily/Death Pass", 12 * 60, 100,
                   ["black lily", "blacklily", "black", "lily", "death", "death_pass", "death pass"]),
    "behemoth": ("Behemoth/Dragon Valley (North)", 9 * 60, 100,
                 ["behemoth", "behe", "dragon", "dv_north", "dv", "dragon_valley", "dragon valley", "dragon valley north"]),
    "pan_draeed": ("Pan Dra'eed/Dion Hills", 12 * 60, 100,
                   ["pan dra'eed", "pan draeed", "pandraeed", "pan", "draeed", "dion_hills", "hills", "dion hills"]),
    "saban": ("Saban/Ant Nest (B2)", 12 * 60, 100,
              ["saban", "sab", "antb2", "ant_nest_b2", "ant2", "b2", "ant nest b2"]),
    "selu": ("Selu/Timak Orc Outpost", 12 * 60, 50,
             ["selu", "sel", "timak", "orc_outpost", "timak_orc", "timak orc", "orc outpost"])
}


# ====== LƯU / TẢI DỮ LIỆU ======
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"records": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()


def normalize_string(s: str) -> str:
    """Normalize string by removing spaces and converting to lowercase for comparison"""
    return re.sub(r'\s+', '', s.lower())


def find_key_by_alias(word: str):
    """Find location key by alias with case-insensitive and space-insensitive matching"""
    normalized_word = normalize_string(word)
    
    for key, (label, _m, _r, aliases) in LOCATIONS.items():
        # Check if the normalized word matches the key or any alias
        if normalized_word == normalize_string(key):
            return key
        
        for alias in aliases:
            if normalized_word == normalize_string(alias):
                return key
    
    return None


# ====== NHIỆM VỤ NỀN: NHẮC TRƯỚC 5' & BÁO "SPAWN" ======
@tasks.loop(seconds=30)
async def notifier():
    now = datetime.now(TZ)
    changed = False
    for rec in data["records"]:
        # rec: {key,label,killed_at,respawn_at,channel_id,warned,done}
        if rec.get("done"):
            continue
        respawn_at = datetime.fromisoformat(rec["respawn_at"])
        delta = respawn_at - now

        try:
            channel = bot.get_channel(int(rec["channel_id"]))
        except:
            channel = None

        # Nhắc trước 5 phút
        if delta.total_seconds() <= 300 and delta.total_seconds() > 0 and not rec.get("warned"):
            if channel and hasattr(channel, 'send') and callable(getattr(channel, 'send', None)):
                try:
                    await channel.send(
                        f"⏰ **{rec['label']}** sẽ xuất hiện **trong 5 phút** (hồi lúc {respawn_at.strftime('%H:%M')})."
                    )
                except:
                    pass  # Ignore send errors for invalid channel types
            rec["warned"] = True
            changed = True

        # Báo đã spawn
        if delta.total_seconds() <= 0 and not rec.get("done"):
            if channel and hasattr(channel, 'send') and callable(getattr(channel, 'send', None)):
                try:
                    await channel.send(
                        f"✅ **{rec['label']}** **đã hồi sinh** (giờ: {respawn_at.strftime('%H:%M')})."
                    )
                except:
                    pass  # Ignore send errors for invalid channel types
            rec["done"] = True
            changed = True

    if changed:
        save_data(data)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    if not notifier.is_running():
        notifier.start()


# ====== NHẬN LỆNH DẠNG: "<địa_điểm> <HHMM>" ======
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    content = message.content.strip()

    # bỏ qua nếu là command có prefix (để commands.* xử lý)
    if content.startswith(PREFIX):
        return await bot.process_commands(message)

    m = re.match(r"([a-zA-Z0-9_\s']+)\s+(\d{4})$", content)
    if not m:
        return  # không phải input theo format này

    alias, hhmm = m.group(1).strip(), m.group(2)
    key = find_key_by_alias(alias)
    if not key:
        return await message.channel.send(
            f"❌ Không tìm thấy địa điểm `{alias}`. Gõ `!list` để xem danh sách alias."
        )

    label, respawn_min, rate, _ = LOCATIONS[key]

    # dựng thời điểm "chết" theo HHMM hôm nay (nếu đã qua thì coi là ngày mai)
    now = datetime.now(TZ)
    killed_at = now.replace(hour=int(hhmm[:2]),
                            minute=int(hhmm[2:]),
                            second=0,
                            microsecond=0)
    if killed_at > now + timedelta(minutes=1):
        # nếu nhập giờ tương lai quá xa so với hiện tại -> coi là của hôm qua (tránh sai lệch)
        killed_at -= timedelta(days=1)

    respawn_at = killed_at + timedelta(minutes=respawn_min)

    # lưu record (mỗi key chỉ giữ 1 record mới nhất)
    # nếu thích nhiều record / multi-channels thì có thể append thay vì replace
    existing = [r for r in data["records"] if r["key"] == key]
    for r in existing:
        data["records"].remove(r)

    rec = {
        "key": key,
        "label": label,
        "killed_at": killed_at.isoformat(),
        "respawn_at": respawn_at.isoformat(),
        "channel_id": str(message.channel.id),
        "warned": False,
        "done": False,
        "rate": rate
    }
    data["records"].append(rec)
    save_data(data)

    await message.channel.send(
        f"☠️ **{label}** chết lúc **{killed_at.strftime('%H:%M')}** → "
        f"hồi lúc **{respawn_at.strftime('%H:%M')}** (*{respawn_min//60}h, {rate}%*)."
    )

    await bot.process_commands(message)


# ====== LỆNH HIỂN THỊ ======
@bot.command(help="Hiện danh sách đã ghi & thời gian còn lại")
async def boss(ctx: commands.Context):
    if not data["records"]:
        return await ctx.send(
            "📭 Chưa có dữ liệu. Nhập theo mẫu: `fe 1304`, `ant 0930`, `gah 1445`, ..."
        )

    now = datetime.now(TZ)
    rows = []
    for r in data["records"]:
        respawn_at = datetime.fromisoformat(r["respawn_at"])
        remain = respawn_at - now
        remain_txt = "đã hồi" if remain.total_seconds() <= 0 else \
            (f"{remain.seconds//3600}h{(remain.seconds%3600)//60:02d}m")
        rows.append((respawn_at,
                     f"- **{r['label']}** → {respawn_at.strftime('%H:%M')} "
                     f"({remain_txt}) — {r['rate']}%"))

    rows.sort(key=lambda x: x[0])
    msg = "**📜 Boss/Location timers:**\n" + "\n".join(r[1] for r in rows)
    await ctx.send(msg)


@bot.command(help="Danh sách địa điểm + alias + thời gian hồi + tỉ lệ")
async def list(ctx: commands.Context):
    lines = []
    for key, (label, minutes, rate, aliases) in LOCATIONS.items():
        h = minutes // 60
        primary_alias = aliases[0] if aliases else key
        lines.append(f"- **{label}** — {h}h / {rate}% — alias: `{primary_alias}`")
    await ctx.send("**📚 Location list (gõ tắt):**\n" + "\n".join(lines))


@bot.command(name="del", help="Xoá 1 timer theo alias/key, ví dụ: !del fe")
async def del_(ctx: commands.Context, alias: str):
    key = find_key_by_alias(alias)
    if not key:
        return await ctx.send("❌ Alias không hợp lệ. Gõ `!list` để xem.")
    before = len(data["records"])
    data["records"] = [r for r in data["records"] if r["key"] != key]
    save_data(data)
    await ctx.send("🗑️ Đã xoá." if len(data["records"]) <
                   before else "ℹ️ Không có record để xoá.")


@bot.command(help="Xoá toàn bộ timers (admin dùng)")
@commands.has_permissions(manage_guild=True)
async def clear(ctx: commands.Context):
    data["records"].clear()
    save_data(data)
    await ctx.send("🧹 Đã xoá toàn bộ timers.")


# ====== CHẠY BOT ======
if not TOKEN:
    raise SystemExit("⚠️ Chưa đặt DISCORD_TOKEN trong Secrets của Replit.")
bot.run(TOKEN)
