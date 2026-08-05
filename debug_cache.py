# -*- coding: utf8 -*-
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta


def mask(text, head=4, tail=4):
    """对字符串进行脱敏，保留头部和尾部指定长度"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    if len(text) <= head + tail:
        return text
    return f"{text[:head]}****{text[-tail:]}"


def mask_account(account):
    """对账号（手机号/邮箱）脱敏"""
    if not isinstance(account, str):
        account = str(account)
    # 邮箱：保留前2位和@之后的域名首字符
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", account):
        local, domain = account.split("@", 1)
        if len(local) <= 2:
            return f"{local}@{domain[0]}***.{domain.split('.')[-1]}"
        return f"{local[:2]}****@{domain[0]}***.{domain.split('.')[-1]}"
    # 手机号（含+86）：保留前3位和后4位
    phone = account.replace("+", "").replace(" ", "")
    if phone.isdigit() and len(phone) >= 7:
        return f"{phone[:3]}****{phone[-4:]}"
    return mask(account, 3, 3)


def format_timestamp(ts):
    """将时间戳转为北京时间字符串"""
    if not ts:
        return "未知"
    try:
        bj_tz = timezone(timedelta(hours=8))
        utc_dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        return utc_dt.astimezone(bj_tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def is_expired(ts, days=30):
    """判断缓存时间是否超过指定天数"""
    if not ts:
        return True
    try:
        return (time.time() - float(ts)) > days * 86400
    except Exception:
        return True


if __name__ == "__main__":
    cache_file = os.environ.get("TOKEN_CACHE_FILE", "token_cache.json")

    if not os.path.exists(cache_file):
        print(f"缓存文件不存在: {cache_file}")
        exit(0)

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 {cache_file} 失败: {e}")
        exit(1)

    if not isinstance(data, dict) or not data:
        print("缓存文件为空或格式不正确")
        exit(0)

    print(f"共缓存 {len(data)} 个账号")
    print("-" * 40)

    for account, info in data.items():
        login_token = info.get("login_token", "")
        user_id = info.get("user_id", "")
        app_token = info.get("app_token", "")
        cached_at = info.get("cached_at", 0)

        expired_flag = " [已过期]" if is_expired(cached_at) else ""

        print(f"账号: {mask_account(account)}")
        print(f"  cached_at : {format_timestamp(cached_at)}{expired_flag}")
        print(f"  login_token: {mask(login_token)} (长度 {len(str(login_token))})")
        print(f"  user_id    : {mask(user_id)} (长度 {len(str(user_id))})")
        print(f"  app_token  : {mask(app_token)} (长度 {len(str(app_token))})")
        print("-" * 40)
