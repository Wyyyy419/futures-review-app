import math
import os
from datetime import datetime, time

import akshare as ak
import pandas as pd
import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None


APP_TITLE = "期货复盘总结"
APP_CAPTION = "收盘后抓取行情与资讯，再交给 Gemini 生成更像专业投顾报告的文字。"
DEFAULT_PRODUCT = "螺纹钢"
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"]


FUTURE_CONFIG = {
    "螺纹钢": {
        "exchange": "上期所",
        "main_symbol": "RB0",
        "inventory_symbol": "rb",
        "spot_symbol": "RB",
        "keywords": ["螺纹钢", "钢材", "钢厂", "黑色系", "地产", "基建"],
    },
    "热卷": {
        "exchange": "上期所",
        "main_symbol": "HC0",
        "inventory_symbol": "hc",
        "spot_symbol": "HC",
        "keywords": ["热卷", "卷板", "钢材", "制造业", "黑色系"],
    },
    "沪铜": {
        "exchange": "上期所",
        "main_symbol": "CU0",
        "inventory_symbol": "cu",
        "spot_symbol": "CU",
        "keywords": ["铜", "有色", "电网", "新能源", "冶炼"],
    },
    "沪铝": {
        "exchange": "上期所",
        "main_symbol": "AL0",
        "inventory_symbol": "al",
        "spot_symbol": "AL",
        "keywords": ["铝", "氧化铝", "电解铝", "有色", "电力"],
    },
    "沪锌": {
        "exchange": "上期所",
        "main_symbol": "ZN0",
        "inventory_symbol": "zn",
        "spot_symbol": "ZN",
        "keywords": ["锌", "有色", "镀锌", "基建"],
    },
    "沪镍": {
        "exchange": "上期所",
        "main_symbol": "NI0",
        "inventory_symbol": "ni",
        "spot_symbol": "NI",
        "keywords": ["镍", "不锈钢", "新能源", "印尼"],
    },
    "沪金": {
        "exchange": "上期所",
        "main_symbol": "AU0",
        "inventory_symbol": "au",
        "spot_symbol": "AU",
        "keywords": ["黄金", "金价", "美联储", "避险", "美元", "地缘"],
    },
    "沪银": {
        "exchange": "上期所",
        "main_symbol": "AG0",
        "inventory_symbol": "AG",
        "spot_symbol": "AG",
        "keywords": ["白银", "贵金属", "美联储", "避险", "美元"],
    },
    "原油": {
        "exchange": "上海国际能源交易中心",
        "main_symbol": "SC0",
        "inventory_symbol": None,
        "spot_symbol": None,
        "keywords": ["原油", "OPEC", "中东", "油价", "能源"],
    },
    "沥青": {
        "exchange": "上期所",
        "main_symbol": "BU0",
        "inventory_symbol": "bu",
        "spot_symbol": "BU",
        "keywords": ["沥青", "原油", "基建", "炼厂"],
    },
    "燃油": {
        "exchange": "上期所",
        "main_symbol": "FU0",
        "inventory_symbol": "fu",
        "spot_symbol": "FU",
        "keywords": ["燃油", "原油", "能源", "炼厂"],
    },
    "橡胶": {
        "exchange": "上期所",
        "main_symbol": "RU0",
        "inventory_symbol": "ru",
        "spot_symbol": "RU",
        "keywords": ["橡胶", "轮胎", "汽车", "东南亚"],
    },
    "纸浆": {
        "exchange": "上期所",
        "main_symbol": "SP0",
        "inventory_symbol": "sp",
        "spot_symbol": "SP",
        "keywords": ["纸浆", "造纸", "纸价", "木浆"],
    },
    "纯碱": {
        "exchange": "郑商所",
        "main_symbol": "SA0",
        "inventory_symbol": "SA",
        "spot_symbol": "SA",
        "keywords": ["纯碱", "玻璃", "光伏", "重碱", "轻碱"],
    },
    "玻璃": {
        "exchange": "郑商所",
        "main_symbol": "FG0",
        "inventory_symbol": "FG",
        "spot_symbol": "FG",
        "keywords": ["玻璃", "地产", "光伏", "深加工"],
    },
    "甲醇": {
        "exchange": "郑商所",
        "main_symbol": "MA0",
        "inventory_symbol": "MA",
        "spot_symbol": "MA",
        "keywords": ["甲醇", "煤化工", "烯烃", "港口"],
    },
    "PTA": {
        "exchange": "郑商所",
        "main_symbol": "TA0",
        "inventory_symbol": "TA",
        "spot_symbol": "TA",
        "keywords": ["PTA", "聚酯", "原油", "PX", "纺织"],
    },
    "尿素": {
        "exchange": "郑商所",
        "main_symbol": "UR0",
        "inventory_symbol": "UR",
        "spot_symbol": "UR",
        "keywords": ["尿素", "化肥", "农业", "煤化工"],
    },
    "白糖": {
        "exchange": "郑商所",
        "main_symbol": "SR0",
        "inventory_symbol": "SR",
        "spot_symbol": "SR",
        "keywords": ["白糖", "甘蔗", "巴西", "印度", "食糖"],
    },
    "棉花": {
        "exchange": "郑商所",
        "main_symbol": "CF0",
        "inventory_symbol": "CF",
        "spot_symbol": "CF",
        "keywords": ["棉花", "纺织", "服装", "种植"],
    },
    "苹果": {
        "exchange": "郑商所",
        "main_symbol": "AP0",
        "inventory_symbol": "AP",
        "spot_symbol": "AP",
        "keywords": ["苹果", "冷库", "农业", "水果"],
    },
    "豆一": {
        "exchange": "大商所",
        "main_symbol": "A0",
        "inventory_symbol": "a",
        "spot_symbol": "A",
        "keywords": ["豆一", "大豆", "农业", "进口", "压榨"],
    },
    "豆粕": {
        "exchange": "大商所",
        "main_symbol": "M0",
        "inventory_symbol": "m",
        "spot_symbol": "M",
        "keywords": ["豆粕", "饲料", "养殖", "大豆", "压榨"],
    },
    "豆油": {
        "exchange": "大商所",
        "main_symbol": "Y0",
        "inventory_symbol": "y",
        "spot_symbol": "Y",
        "keywords": ["豆油", "油脂", "压榨", "大豆"],
    },
    "棕榈油": {
        "exchange": "大商所",
        "main_symbol": "P0",
        "inventory_symbol": "p",
        "spot_symbol": "P",
        "keywords": ["棕榈油", "油脂", "马来西亚", "印尼"],
    },
    "玉米": {
        "exchange": "大商所",
        "main_symbol": "C0",
        "inventory_symbol": "c",
        "spot_symbol": "C",
        "keywords": ["玉米", "饲料", "深加工", "农业"],
    },
    "铁矿石": {
        "exchange": "大商所",
        "main_symbol": "I0",
        "inventory_symbol": "i",
        "spot_symbol": "I",
        "keywords": ["铁矿石", "矿山", "钢厂", "黑色系"],
    },
    "焦炭": {
        "exchange": "大商所",
        "main_symbol": "J0",
        "inventory_symbol": "j",
        "spot_symbol": "J",
        "keywords": ["焦炭", "煤焦", "钢厂", "黑色系"],
    },
    "焦煤": {
        "exchange": "大商所",
        "main_symbol": "JM0",
        "inventory_symbol": "jm",
        "spot_symbol": "JM",
        "keywords": ["焦煤", "煤矿", "煤焦", "黑色系"],
    },
    "聚丙烯": {
        "exchange": "大商所",
        "main_symbol": "PP0",
        "inventory_symbol": "pp",
        "spot_symbol": "PP",
        "keywords": ["聚丙烯", "化工", "塑料", "原油"],
    },
    "PVC": {
        "exchange": "大商所",
        "main_symbol": "V0",
        "inventory_symbol": "v",
        "spot_symbol": "V",
        "keywords": ["PVC", "化工", "地产", "电石"],
    },
    "乙二醇": {
        "exchange": "大商所",
        "main_symbol": "EG0",
        "inventory_symbol": "eg",
        "spot_symbol": "EG",
        "keywords": ["乙二醇", "化工", "聚酯", "原油"],
    },
    "生猪": {
        "exchange": "大商所",
        "main_symbol": "LH0",
        "inventory_symbol": "lh",
        "spot_symbol": "LH",
        "keywords": ["生猪", "养殖", "猪价", "饲料"],
    },
    "沪深300股指": {
        "exchange": "中金所",
        "main_symbol": "IF0",
        "inventory_symbol": "IF",
        "spot_symbol": None,
        "keywords": ["股指", "沪深300", "A股", "政策", "流动性"],
    },
    "中证500股指": {
        "exchange": "中金所",
        "main_symbol": "IC0",
        "inventory_symbol": "IC",
        "spot_symbol": None,
        "keywords": ["股指", "中证500", "A股", "政策", "流动性"],
    },
    "中证1000股指": {
        "exchange": "中金所",
        "main_symbol": "IM0",
        "inventory_symbol": "IM",
        "spot_symbol": None,
        "keywords": ["股指", "中证1000", "A股", "政策", "流动性"],
    },
    "10年期国债": {
        "exchange": "中金所",
        "main_symbol": "T0",
        "inventory_symbol": "T",
        "spot_symbol": None,
        "keywords": ["国债", "利率", "央行", "债券", "流动性"],
    },
    "工业硅": {
        "exchange": "广期所",
        "main_symbol": "SI0",
        "inventory_symbol": "si",
        "spot_symbol": "SI",
        "keywords": ["工业硅", "有机硅", "多晶硅", "光伏"],
    },
}


def init_page():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)


def init_state():
    defaults = {
        "selected_product": DEFAULT_PRODUCT,
        "technical_text": "",
        "fundamental_text": "",
        "strategy_text": "",
        "ai_report": "",
        "last_auto_fetch_date": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_gemini_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY", "")


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def format_number(value, digits=2):
    if pd.isna(value):
        return "暂无"
    return f"{float(value):.{digits}f}"


def calculate_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    macd = (dif - dea) * 2
    return dif, dea, macd


def resample_weekly(df):
    return (
        df.set_index("date")
        .resample("W-FRI")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "hold": "last",
                "settle": "last",
            }
        )
        .dropna(subset=["close"])
        .reset_index()
    )


def enrich_indicators(df):
    enriched = df.copy()
    for window in (5, 20, 60, 250):
        enriched[f"ma{window}"] = enriched["close"].rolling(window).mean()
    dif, dea, macd = calculate_macd(enriched["close"])
    enriched["dif"] = dif
    enriched["dea"] = dea
    enriched["macd"] = macd
    return enriched


@st.cache_data(ttl=1800)
def load_daily_data(main_symbol):
    df = ak.futures_zh_daily_sina(symbol=main_symbol)
    df["date"] = pd.to_datetime(df["date"])
    numeric_columns = ["open", "high", "low", "close", "volume", "hold", "settle"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)


@st.cache_data(ttl=1800)
def load_inventory_data(inventory_symbol):
    if not inventory_symbol:
        return None
    return ak.futures_inventory_em(symbol=inventory_symbol)


@st.cache_data(ttl=900)
def load_news_data():
    return ak.stock_info_global_cls(symbol="全部")


@st.cache_data(ttl=1800)
def load_basis_data(trade_date, spot_symbol):
    if not spot_symbol:
        return None
    return ak.futures_spot_price(date=trade_date, vars_list=[spot_symbol])


def describe_price_structure(latest):
    close_price = latest["close"]
    ma5 = latest["ma5"]
    ma20 = latest["ma20"]
    ma60 = latest["ma60"]
    ma250 = latest["ma250"]

    if close_price > ma5 > ma20 > ma60:
        return "均线呈多头排列，短中期趋势偏强。"
    if close_price < ma5 < ma20 < ma60:
        return "均线呈空头排列，短中期趋势偏弱。"
    if close_price > ma20 and ma20 > ma60:
        return "价格位于中期均线上方，结构偏强，但延续性仍需确认。"
    if close_price < ma20 and ma20 < ma60:
        return "价格位于中期均线下方，结构偏弱，但需防止超跌反弹。"
    if pd.notna(ma250) and close_price > ma250:
        return "短线反复，但长期仍位于年线之上。"
    if pd.notna(ma250) and close_price < ma250:
        return "短线反复，长期仍位于年线之下。"
    return "均线缠绕明显，趋势信号暂不清晰。"


def describe_macd(latest, previous):
    if latest["dif"] > latest["dea"] and previous["dif"] <= previous["dea"]:
        return "MACD 刚形成金叉，动能有转强迹象。"
    if latest["dif"] < latest["dea"] and previous["dif"] >= previous["dea"]:
        return "MACD 刚形成死叉，动能有转弱迹象。"
    if latest["macd"] > 0:
        return "MACD 位于零轴上方，趋势动能偏多。"
    return "MACD 位于零轴下方，趋势动能偏空。"


def describe_weekly_structure(weekly_df):
    if len(weekly_df) < 2:
        return "周线样本不足，暂不做周线判断。"

    latest = weekly_df.iloc[-1]
    previous = weekly_df.iloc[-2]
    if latest["close"] > previous["high"]:
        return "周线收盘突破前一周高点，中期承接偏强。"
    if latest["close"] < previous["low"]:
        return "周线收盘跌破前一周低点，中期压力较大。"
    if latest["close"] > latest["ma20"]:
        return "周线位于20周均线上方，中期结构偏强。"
    return "周线仍在整理区间内，方向需要继续确认。"


def build_technical_text(product_name, daily_df):
    daily_df = enrich_indicators(daily_df)
    weekly_df = enrich_indicators(resample_weekly(daily_df))

    latest = daily_df.iloc[-1]
    previous = daily_df.iloc[-2]
    latest_week = weekly_df.iloc[-1] if not weekly_df.empty else None
    change_pct = (latest["close"] - previous["close"]) / previous["close"] * 100

    weekly_change_pct = None
    if len(weekly_df) >= 2:
        weekly_change_pct = (
            (weekly_df.iloc[-1]["close"] - weekly_df.iloc[-2]["close"])
            / weekly_df.iloc[-2]["close"]
            * 100
        )

    daily_body = abs(latest["close"] - latest["open"])
    daily_range = latest["high"] - latest["low"]
    if daily_range > 0 and daily_body / daily_range >= 0.6:
        candle_text = "日K 实体较长，当日方向比较明确。"
    elif daily_range > 0 and daily_body / daily_range <= 0.25:
        candle_text = "日K 实体较短，多空分歧较大。"
    else:
        candle_text = "日K 形态中性，方向尚未完全走顺。"

    technical_text = "\n".join(
        [
            f"品种：{product_name}",
            f"数据日期：{latest['date'].strftime('%Y-%m-%d')}",
            f"日线收盘价：{latest['close']:.2f}，较上一交易日涨跌幅：{change_pct:.2f}%",
            f"日线 MA5/20/60/250：{format_number(latest['ma5'])} / {format_number(latest['ma20'])} / {format_number(latest['ma60'])} / {format_number(latest['ma250'])}",
            f"MACD(DIF/DEA/MACD)：{format_number(latest['dif'])} / {format_number(latest['dea'])} / {format_number(latest['macd'])}",
            f"日K 观察：{candle_text}",
            f"日线结构：{describe_price_structure(latest)}",
            f"动能判断：{describe_macd(latest, previous)}",
            f"周线判断：{describe_weekly_structure(weekly_df)}",
            f"本周涨跌幅：{weekly_change_pct:.2f}%" if weekly_change_pct is not None else "本周涨跌幅：周线样本不足",
            f"周线 MA5/20：{format_number(latest_week['ma5'])} / {format_number(latest_week['ma20'])}" if latest_week is not None else "周线 MA5/20：暂无",
        ]
    )

    latest_metrics = {
        "date": latest["date"],
        "close": latest["close"],
        "change_pct": change_pct,
        "ma5": latest["ma5"],
        "ma20": latest["ma20"],
        "ma60": latest["ma60"],
        "ma250": latest["ma250"],
        "dif": latest["dif"],
        "dea": latest["dea"],
        "macd": latest["macd"],
        "volume": latest["volume"],
        "hold": latest["hold"],
        "settle": latest["settle"],
    }
    return technical_text, latest_metrics


def build_inventory_text(config):
    inventory_symbol = config["inventory_symbol"]
    if not inventory_symbol:
        return "库存：当前品种暂未配置库存接口。", {"inventory_bias": "neutral"}

    try:
        inventory_df = load_inventory_data(inventory_symbol)
        if inventory_df is None or inventory_df.empty:
            return "库存：未获取到库存数据。", {"inventory_bias": "neutral"}

        latest = inventory_df.iloc[-1]
        previous = inventory_df.iloc[-2] if len(inventory_df) >= 2 else latest
        delta = safe_float(latest["增减"])

        if pd.notna(delta) and delta < 0:
            interpretation = "库存下降，对价格有一定支撑。"
            bias = "bullish"
        elif pd.notna(delta) and delta > 0:
            interpretation = "库存增加，供给压力略有抬升。"
            bias = "bearish"
        else:
            interpretation = "库存变化不大，库存端暂未给出强信号。"
            bias = "neutral"

        text = "\n".join(
            [
                "库存数据：",
                f"最新日期：{latest['日期']}",
                f"最新库存：{format_number(latest['库存'], 0)}",
                f"较上一期增减：{format_number(latest['增减'], 0)}",
                f"库存解读：{interpretation}",
                f"上一期库存：{format_number(previous['库存'], 0)}",
            ]
        )
        return text, {"inventory_bias": bias}
    except Exception as exc:
        return f"库存数据：获取失败，原因：{exc}", {"inventory_bias": "neutral"}


def build_basis_text(config, trade_date):
    spot_symbol = config["spot_symbol"]
    if not spot_symbol:
        return "期现与产业链：当前品种暂未配置现货/基差接口。", {"basis_bias": "neutral"}

    try:
        basis_df = load_basis_data(trade_date.strftime("%Y%m%d"), spot_symbol)
        if basis_df is None or basis_df.empty:
            return "期现与产业链：未获取到现货和基差数据。", {"basis_bias": "neutral"}

        latest = basis_df.iloc[0]
        dom_basis = safe_float(latest["dom_basis"])
        dom_basis_rate = safe_float(latest["dom_basis_rate"])

        if pd.notna(dom_basis) and dom_basis > 0:
            interpretation = "主力合约升水现货，市场对远月预期偏强。"
            bias = "bullish"
        elif pd.notna(dom_basis) and dom_basis < 0:
            interpretation = "主力合约贴水现货，现货端相对更强。"
            bias = "bearish"
        else:
            interpretation = "基差信号中性。"
            bias = "neutral"

        text = "\n".join(
            [
                "期现与产业链代理指标：",
                f"现货价格：{format_number(latest['spot_price'])}",
                f"主力合约：{latest['dominant_contract']}，主力价格：{format_number(latest['dominant_contract_price'])}",
                f"主力基差：{format_number(dom_basis)}，基差率：{format_number(dom_basis_rate * 100 if pd.notna(dom_basis_rate) else math.nan)}%",
                f"解读：{interpretation}",
            ]
        )
        return text, {"basis_bias": bias}
    except Exception as exc:
        return f"期现与产业链：获取失败，原因：{exc}", {"basis_bias": "neutral"}


def classify_news_sentiment(text_blob):
    bullish_words = ["提振", "减产", "去库", "支撑", "紧张", "上涨", "改善"]
    bearish_words = ["回落", "走弱", "增产", "累库", "下跌", "压制", "疲弱"]
    bullish_score = sum(word in text_blob for word in bullish_words)
    bearish_score = sum(word in text_blob for word in bearish_words)

    if bullish_score > bearish_score:
        return "bullish", "消息解读：新闻情绪略偏多，但仍需确认是否真正影响供需。"
    if bearish_score > bullish_score:
        return "bearish", "消息解读：新闻情绪略偏空，需留意是否继续发酵。"
    return "neutral", "消息解读：新闻偏中性，短线更多还是跟随价格本身。"


def build_news_text(config):
    keywords = config["keywords"]
    try:
        news_df = load_news_data()
        if news_df.empty:
            return "消息面：未获取到财联社电报。", {"news_bias": "neutral"}

        rows = []
        for _, row in news_df.head(200).iterrows():
            haystack = f"{row['标题']} {row['内容']}"
            if any(keyword in haystack for keyword in keywords):
                rows.append(row)
            if len(rows) >= 5:
                break

        if not rows:
            return (
                "消息面：财联社电报中暂未筛到与该品种高度相关的当日关键词新闻，可人工补充产业资讯。",
                {"news_bias": "neutral"},
            )

        lines = ["财联社相关新闻："]
        text_blob = ""
        for row in rows:
            lines.append(f"- {row['发布日期']} {row['发布时间']} | {row['标题']}")
            text_blob += f"{row['标题']} {row['内容']} "

        news_bias, conclusion = classify_news_sentiment(text_blob)
        lines.append(conclusion)
        return "\n".join(lines), {"news_bias": news_bias}
    except Exception as exc:
        return f"消息面：财联社新闻获取失败，原因：{exc}", {"news_bias": "neutral"}


def build_fundamental_text(product_name, config, latest_metrics):
    inventory_text, inventory_signal = build_inventory_text(config)
    basis_text, basis_signal = build_basis_text(config, latest_metrics["date"])
    news_text, news_signal = build_news_text(config)

    text = "\n\n".join(
        [
            f"品种：{product_name}",
            f"交易所：{config['exchange']}",
            "\n".join(
                [
                    "行情概况：",
                    f"收盘价：{latest_metrics['close']:.2f}",
                    f"结算价：{format_number(latest_metrics['settle'])}",
                    f"成交量：{format_number(latest_metrics['volume'], 0)}",
                    f"持仓量：{format_number(latest_metrics['hold'], 0)}",
                ]
            ),
            inventory_text,
            basis_text,
            news_text,
        ]
    )

    signals = {}
    signals.update(inventory_signal)
    signals.update(basis_signal)
    signals.update(news_signal)
    return text, signals


def build_strategy_text(product_name, latest_metrics, signals):
    score = 0
    score += 1 if latest_metrics["close"] > latest_metrics["ma20"] else -1
    score += 1 if latest_metrics["close"] > latest_metrics["ma60"] else -1
    score += 1 if latest_metrics["macd"] > 0 else -1

    for key in ("inventory_bias", "basis_bias", "news_bias"):
        if signals.get(key) == "bullish":
            score += 1
        elif signals.get(key) == "bearish":
            score -= 1

    if score >= 3:
        bias_title = "偏多思路"
        lines = [
            "主观策略倾向：偏多，但更适合顺势而不是追高。",
            "执行建议：优先等待日内回踩 MA5 或 MA20 附近再观察承接，若回踩不破可考虑轻仓试多。",
            "确认条件：价格放量站稳日线 MA20，且 MACD 维持在零轴附近或零轴上方。",
            "风险提示：若收盘重新跌回 MA20 下方，说明趋势延续性不足，应降低仓位或暂停尝试。",
        ]
    elif score <= -3:
        bias_title = "偏空思路"
        lines = [
            "主观策略倾向：偏空，但更适合反弹承压后的顺势交易。",
            "执行建议：优先等反抽 MA5 或 MA20 后确认压力，再考虑轻仓试空，不建议在急跌后盲目加仓。",
            "确认条件：价格持续位于 MA20 下方，且 MACD 维持弱势结构。",
            "风险提示：若价格快速收复 MA20 并伴随放量，空头逻辑需要及时降级。",
        ]
    else:
        bias_title = "震荡思路"
        lines = [
            "主观策略倾向：以震荡整理看待，当前更适合等待而不是抢方向。",
            "执行建议：把重点放在区间上沿和下沿的突破确认，不要在均线缠绕阶段频繁试单。",
            "确认条件：若放量突破近几日高点，可转向偏多；若跌破近几日低点，可转向偏空。",
            "风险提示：横盘阶段最容易来回打止损，仓位应明显小于趋势行情。",
        ]

    return "\n".join([f"综合结论：{product_name} 当前属于{bias_title}。"] + lines)


def get_full_summary(product_name):
    config = FUTURE_CONFIG[product_name]
    daily_df = load_daily_data(config["main_symbol"])
    if len(daily_df) < 30:
        raise ValueError("历史数据太少，暂时无法完成完整分析。")

    technical_text, latest_metrics = build_technical_text(product_name, daily_df)
    fundamental_text, signals = build_fundamental_text(product_name, config, latest_metrics)
    strategy_text = build_strategy_text(product_name, latest_metrics, signals)
    return technical_text, fundamental_text, strategy_text


def refresh_summary(product_name, clear_ai=True):
    technical_text, fundamental_text, strategy_text = get_full_summary(product_name)
    st.session_state.selected_product = product_name
    st.session_state.technical_text = technical_text
    st.session_state.fundamental_text = fundamental_text
    st.session_state.strategy_text = strategy_text
    st.session_state.last_auto_fetch_date = datetime.now().strftime("%Y-%m-%d")
    if clear_ai:
        st.session_state.ai_report = ""


def ensure_summary(product_name):
    if not st.session_state.technical_text or st.session_state.selected_product != product_name:
        refresh_summary(product_name)


def extract_gemini_text(response):
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    parts = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if content and getattr(content, "parts", None):
            for part in content.parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    parts.append(part_text)

    merged = "\n".join(parts).strip()
    if merged:
        return merged
    raise ValueError("Gemini 返回了空结果。")


def build_gemini_prompt(product_name, technical_text, fundamental_text, strategy_text):
    return f"""
你是一名服务专业客户的期货研究员，请基于以下材料，输出一份结构清晰、语言专业、偏卖方研究风格的中文复盘建议。

要求：
1. 不要虚构数据，只能基于已提供内容推演。
2. 先给结论，再给依据，再给交易执行建议。
3. 必须包含以下小标题：
   一、核心结论
   二、技术面解读
   三、基本面与消息面解读
   四、交易策略建议
   五、风险提示
4. “交易策略建议”里要写出：
   - 偏多 / 偏空 / 震荡 的判断
   - 适合关注的入场思路
   - 不成立时的止损或失效条件
5. 口吻专业，但避免夸张和绝对化表述。
6. 最后加一句：以上内容仅供复盘交流，不构成投资建议。

品种：{product_name}

【技术面特征】
{technical_text}

【基本面与消息面】
{fundamental_text}

【我的主观策略倾向】
{strategy_text}
""".strip()


def generate_gemini_report(product_name, technical_text, fundamental_text, strategy_text, api_key, model_name):
    if genai is None:
        raise ImportError("当前环境未安装 google-genai 包，请先执行：python -m pip install google-genai")

    client = genai.Client(api_key=api_key)
    prompt = build_gemini_prompt(product_name, technical_text, fundamental_text, strategy_text)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={"temperature": 0.4},
    )
    return extract_gemini_text(response)


def maybe_auto_refresh(product_name):
    now = datetime.now()
    today_text = now.strftime("%Y-%m-%d")
    if now.time() >= time(15, 5) and st.session_state.last_auto_fetch_date != today_text:
        try:
            refresh_summary(product_name, clear_ai=False)
            st.info("检测到已过收盘后时间，已自动抓取一次数据。")
        except Exception as exc:
            st.warning(f"自动抓取失败：{exc}")


def render_sidebar():
    with st.sidebar:
        st.subheader("Gemini 设置")
        api_key = st.text_input(
            "Gemini API Key",
            value=get_gemini_api_key(),
            type="password",
            help="本地可用环境变量，部署到 Streamlit Community Cloud 时建议用 Secrets。",
        )
        model_name = st.selectbox(
            "模型",
            options=GEMINI_MODELS,
            index=0,
            help="建议先用 gemini-2.5-flash，速度和成本更平衡。",
        )
        st.caption("如果生成失败，优先检查 API Key、账户额度和网络连接。")
        return api_key, model_name


def render_actions(product_name, api_key, model_name):
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("手动获取收盘数据并填充", use_container_width=True):
            try:
                with st.spinner("正在抓取期货数据..."):
                    refresh_summary(product_name)
                st.success("已获取最新数据并填充。")
            except Exception as exc:
                st.error(f"获取失败：{exc}")

    with col2:
        if st.button("生成 Gemini 专业客户建议", use_container_width=True):
            try:
                ensure_summary(product_name)
                if not api_key:
                    st.error("请先在左侧输入 Gemini API Key，或在 Streamlit Secrets 中配置。")
                else:
                    with st.spinner("Gemini 正在生成专业客户建议..."):
                        st.session_state.ai_report = generate_gemini_report(
                            product_name=product_name,
                            technical_text=st.session_state.technical_text,
                            fundamental_text=st.session_state.fundamental_text,
                            strategy_text=st.session_state.strategy_text,
                            api_key=api_key,
                            model_name=model_name,
                        )
                    st.success("已生成 Gemini 专业客户建议。")
            except Exception as exc:
                st.error(f"生成失败：{exc}")

    with col3:
        if st.button("清空 Gemini 报告", use_container_width=True):
            st.session_state.ai_report = ""
            st.success("已清空 Gemini 报告。")


def render_text_sections():
    st.text_area(
        "技术面特征（含日K/周K、均线、MACD）",
        key="technical_text",
        height=320,
    )
    st.text_area(
        "基本面与消息面（新闻、库存、期现/产业链代理指标）",
        key="fundamental_text",
        height=360,
    )
    st.text_area(
        "我的主观策略倾向",
        key="strategy_text",
        height=220,
    )


def render_ai_report():
    st.subheader("Gemini 专业客户建议")
    if st.session_state.ai_report:
        st.markdown(st.session_state.ai_report)
    else:
        st.info("点击“生成 Gemini 专业客户建议”后，这里会显示模型生成的复盘报告。")


def main():
    init_page()
    init_state()
    api_key, model_name = render_sidebar()

    product_name = st.selectbox(
        "选择期货品种",
        options=list(FUTURE_CONFIG.keys()),
        index=list(FUTURE_CONFIG.keys()).index(st.session_state.selected_product),
    )

    if product_name != st.session_state.selected_product:
        try:
            with st.spinner("正在切换品种并刷新数据..."):
                refresh_summary(product_name)
            st.info("已根据新选择的品种自动刷新基础分析。")
        except Exception as exc:
            st.warning(f"切换品种后自动刷新失败：{exc}")

    maybe_auto_refresh(product_name)
    render_actions(product_name, api_key, model_name)
    render_text_sections()
    render_ai_report()


if __name__ == "__main__":
    main()
