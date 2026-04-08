import math
from datetime import datetime, time

import akshare as ak
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


APP_TITLE = "期货复盘总结"
APP_CAPTION = "收盘后抓取行情与资讯，使用本地规则自动生成更像客户日报的复盘内容。"
DEFAULT_PRODUCT = "螺纹钢"


FUTURE_CONFIG = {
    "螺纹钢": {"exchange": "上期所", "main_symbol": "RB0", "inventory_symbol": "rb", "spot_symbol": "RB", "keywords": ["螺纹钢", "钢材", "钢厂", "黑色系", "地产", "基建"]},
    "热卷": {"exchange": "上期所", "main_symbol": "HC0", "inventory_symbol": "hc", "spot_symbol": "HC", "keywords": ["热卷", "卷板", "钢材", "制造业", "黑色系"]},
    "沪铜": {"exchange": "上期所", "main_symbol": "CU0", "inventory_symbol": "cu", "spot_symbol": "CU", "keywords": ["铜", "有色", "电网", "新能源", "冶炼"]},
    "沪铝": {"exchange": "上期所", "main_symbol": "AL0", "inventory_symbol": "al", "spot_symbol": "AL", "keywords": ["铝", "氧化铝", "电解铝", "有色", "电力"]},
    "沪锌": {"exchange": "上期所", "main_symbol": "ZN0", "inventory_symbol": "zn", "spot_symbol": "ZN", "keywords": ["锌", "有色", "镀锌", "基建"]},
    "沪镍": {"exchange": "上期所", "main_symbol": "NI0", "inventory_symbol": "ni", "spot_symbol": "NI", "keywords": ["镍", "不锈钢", "新能源", "印尼"]},
    "沪金": {"exchange": "上期所", "main_symbol": "AU0", "inventory_symbol": "au", "spot_symbol": "AU", "keywords": ["黄金", "金价", "美联储", "避险", "美元", "地缘"]},
    "沪银": {"exchange": "上期所", "main_symbol": "AG0", "inventory_symbol": "AG", "spot_symbol": "AG", "keywords": ["白银", "贵金属", "美联储", "避险", "美元"]},
    "原油": {"exchange": "上海国际能源交易中心", "main_symbol": "SC0", "inventory_symbol": None, "spot_symbol": None, "keywords": ["原油", "OPEC", "中东", "油价", "能源"]},
    "沥青": {"exchange": "上期所", "main_symbol": "BU0", "inventory_symbol": "bu", "spot_symbol": "BU", "keywords": ["沥青", "原油", "基建", "炼厂"]},
    "燃油": {"exchange": "上期所", "main_symbol": "FU0", "inventory_symbol": "fu", "spot_symbol": "FU", "keywords": ["燃油", "原油", "能源", "炼厂"]},
    "橡胶": {"exchange": "上期所", "main_symbol": "RU0", "inventory_symbol": "ru", "spot_symbol": "RU", "keywords": ["橡胶", "轮胎", "汽车", "东南亚"]},
    "纸浆": {"exchange": "上期所", "main_symbol": "SP0", "inventory_symbol": "sp", "spot_symbol": "SP", "keywords": ["纸浆", "造纸", "纸价", "木浆"]},
    "纯碱": {"exchange": "郑商所", "main_symbol": "SA0", "inventory_symbol": "SA", "spot_symbol": "SA", "keywords": ["纯碱", "玻璃", "光伏", "重碱", "轻碱"]},
    "玻璃": {"exchange": "郑商所", "main_symbol": "FG0", "inventory_symbol": "FG", "spot_symbol": "FG", "keywords": ["玻璃", "地产", "光伏", "深加工"]},
    "甲醇": {"exchange": "郑商所", "main_symbol": "MA0", "inventory_symbol": "MA", "spot_symbol": "MA", "keywords": ["甲醇", "煤化工", "烯烃", "港口"]},
    "PTA": {"exchange": "郑商所", "main_symbol": "TA0", "inventory_symbol": "TA", "spot_symbol": "TA", "keywords": ["PTA", "聚酯", "原油", "PX", "纺织"]},
    "尿素": {"exchange": "郑商所", "main_symbol": "UR0", "inventory_symbol": "UR", "spot_symbol": "UR", "keywords": ["尿素", "化肥", "农业", "煤化工"]},
    "白糖": {"exchange": "郑商所", "main_symbol": "SR0", "inventory_symbol": "SR", "spot_symbol": "SR", "keywords": ["白糖", "甘蔗", "巴西", "印度", "食糖"]},
    "棉花": {"exchange": "郑商所", "main_symbol": "CF0", "inventory_symbol": "CF", "spot_symbol": "CF", "keywords": ["棉花", "纺织", "服装", "种植"]},
    "苹果": {"exchange": "郑商所", "main_symbol": "AP0", "inventory_symbol": "AP", "spot_symbol": "AP", "keywords": ["苹果", "冷库", "农业", "水果"]},
    "豆一": {"exchange": "大商所", "main_symbol": "A0", "inventory_symbol": "a", "spot_symbol": "A", "keywords": ["豆一", "大豆", "农业", "进口", "压榨"]},
    "豆粕": {"exchange": "大商所", "main_symbol": "M0", "inventory_symbol": "m", "spot_symbol": "M", "keywords": ["豆粕", "饲料", "养殖", "大豆", "压榨"]},
    "豆油": {"exchange": "大商所", "main_symbol": "Y0", "inventory_symbol": "y", "spot_symbol": "Y", "keywords": ["豆油", "油脂", "压榨", "大豆"]},
    "棕榈油": {"exchange": "大商所", "main_symbol": "P0", "inventory_symbol": "p", "spot_symbol": "P", "keywords": ["棕榈油", "油脂", "马来西亚", "印尼"]},
    "玉米": {"exchange": "大商所", "main_symbol": "C0", "inventory_symbol": "c", "spot_symbol": "C", "keywords": ["玉米", "饲料", "深加工", "农业"]},
    "铁矿石": {"exchange": "大商所", "main_symbol": "I0", "inventory_symbol": "i", "spot_symbol": "I", "keywords": ["铁矿石", "矿山", "钢厂", "黑色系"]},
    "焦炭": {"exchange": "大商所", "main_symbol": "J0", "inventory_symbol": "j", "spot_symbol": "J", "keywords": ["焦炭", "煤焦", "钢厂", "黑色系"]},
    "焦煤": {"exchange": "大商所", "main_symbol": "JM0", "inventory_symbol": "jm", "spot_symbol": "JM", "keywords": ["焦煤", "煤矿", "煤焦", "黑色系"]},
    "聚丙烯": {"exchange": "大商所", "main_symbol": "PP0", "inventory_symbol": "pp", "spot_symbol": "PP", "keywords": ["聚丙烯", "化工", "塑料", "原油"]},
    "PVC": {"exchange": "大商所", "main_symbol": "V0", "inventory_symbol": "v", "spot_symbol": "V", "keywords": ["PVC", "化工", "地产", "电石"]},
    "乙二醇": {"exchange": "大商所", "main_symbol": "EG0", "inventory_symbol": "eg", "spot_symbol": "EG", "keywords": ["乙二醇", "化工", "聚酯", "原油"]},
    "生猪": {"exchange": "大商所", "main_symbol": "LH0", "inventory_symbol": "lh", "spot_symbol": "LH", "keywords": ["生猪", "养殖", "猪价", "饲料"]},
    "沪深300股指": {"exchange": "中金所", "main_symbol": "IF0", "inventory_symbol": "IF", "spot_symbol": None, "keywords": ["股指", "沪深300", "A股", "政策", "流动性"]},
    "中证500股指": {"exchange": "中金所", "main_symbol": "IC0", "inventory_symbol": "IC", "spot_symbol": None, "keywords": ["股指", "中证500", "A股", "政策", "流动性"]},
    "中证1000股指": {"exchange": "中金所", "main_symbol": "IM0", "inventory_symbol": "IM", "spot_symbol": None, "keywords": ["股指", "中证1000", "A股", "政策", "流动性"]},
    "10年期国债": {"exchange": "中金所", "main_symbol": "T0", "inventory_symbol": "T", "spot_symbol": None, "keywords": ["国债", "利率", "央行", "债券", "流动性"]},
    "工业硅": {"exchange": "广期所", "main_symbol": "SI0", "inventory_symbol": "si", "spot_symbol": "SI", "keywords": ["工业硅", "有机硅", "多晶硅", "光伏"]},
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
        "report_text": "",
        "analysis_context": None,
        "last_auto_fetch_date": None,
        "last_refresh_ts": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum", "hold": "last", "settle": "last"})
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


def get_snapshot_market(config):
    return "FF" if config["exchange"] == "中金所" else "CF"


@st.cache_data(ttl=120)
def load_fast_snapshot(main_symbol, market):
    snapshot_df = ak.futures_zh_spot(symbol=main_symbol, market=market, adjust="0")
    if snapshot_df.empty:
        return None
    return snapshot_df.iloc[0].to_dict()


def append_snapshot_row_if_needed(df, config):
    now = datetime.now()
    today = pd.Timestamp(now.date())
    latest_date = pd.Timestamp(df["date"].max())

    if now.time() < time(15, 0):
        return df, {"data_source": "日线", "snapshot_time": None}

    if latest_date >= today:
        return df, {"data_source": "日线", "snapshot_time": None}

    try:
        snapshot = load_fast_snapshot(config["main_symbol"], get_snapshot_market(config))
        if not snapshot:
            return df, {"data_source": "日线", "snapshot_time": None}

        snapshot_row = {
            "date": today,
            "open": pd.to_numeric(snapshot.get("open"), errors="coerce"),
            "high": pd.to_numeric(snapshot.get("high"), errors="coerce"),
            "low": pd.to_numeric(snapshot.get("low"), errors="coerce"),
            "close": pd.to_numeric(snapshot.get("current_price"), errors="coerce"),
            "volume": pd.to_numeric(snapshot.get("volume"), errors="coerce"),
            "hold": pd.to_numeric(snapshot.get("hold"), errors="coerce"),
            "settle": pd.to_numeric(snapshot.get("last_settle_price"), errors="coerce"),
        }
        if pd.isna(snapshot_row["settle"]):
            snapshot_row["settle"] = snapshot_row["close"]

        patched_df = pd.concat([df, pd.DataFrame([snapshot_row])], ignore_index=True)
        return patched_df, {
            "data_source": "收盘快照补全",
            "snapshot_time": str(snapshot.get("time", "")),
        }
    except Exception:
        return df, {"data_source": "日线", "snapshot_time": None}


@st.cache_data(ttl=180)
def load_daily_data(main_symbol):
    df = ak.futures_zh_daily_sina(symbol=main_symbol)
    df["date"] = pd.to_datetime(df["date"])
    for column in ["open", "high", "low", "close", "volume", "hold", "settle"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=["close"]).sort_values("date").reset_index(drop=True)


@st.cache_data(ttl=1800)
def load_inventory_data(inventory_symbol):
    if not inventory_symbol:
        return None
    return ak.futures_inventory_em(symbol=inventory_symbol)


@st.cache_data(ttl=180)
def load_news_data():
    return ak.stock_info_global_cls(symbol="全部")


@st.cache_data(ttl=180)
def load_basis_data(trade_date, spot_symbol):
    if not spot_symbol:
        return None
    return ak.futures_spot_price(date=trade_date, vars_list=[spot_symbol])


def describe_price_structure(latest):
    if latest["close"] > latest["ma5"] > latest["ma20"] > latest["ma60"]:
        return "均线呈多头排列，短中期趋势偏强。"
    if latest["close"] < latest["ma5"] < latest["ma20"] < latest["ma60"]:
        return "均线呈空头排列，短中期趋势偏弱。"
    if latest["close"] > latest["ma20"] and latest["ma20"] > latest["ma60"]:
        return "价格位于中期均线上方，结构偏强，但延续性仍需确认。"
    if latest["close"] < latest["ma20"] and latest["ma20"] < latest["ma60"]:
        return "价格位于中期均线下方，结构偏弱，但需防止超跌反弹。"
    if pd.notna(latest["ma250"]) and latest["close"] > latest["ma250"]:
        return "短线反复，但长期仍位于年线之上。"
    if pd.notna(latest["ma250"]) and latest["close"] < latest["ma250"]:
        return "短线反复，长期仍位于年线之下。"
    return "均线缠绕明显，趋势信号暂不清晰。"


def describe_macd(latest, previous):
    if latest["dif"] > latest["dea"] and previous["dif"] <= previous["dea"]:
        return "MACD 刚形成金叉，动能有转强迹象。"
    if latest["dif"] < latest["dea"] and previous["dif"] >= previous["dea"]:
        return "MACD 刚形成死叉，动能有转弱迹象。"
    return "MACD 位于零轴上方，趋势动能偏多。" if latest["macd"] > 0 else "MACD 位于零轴下方，趋势动能偏空。"


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
        weekly_change_pct = (weekly_df.iloc[-1]["close"] - weekly_df.iloc[-2]["close"]) / weekly_df.iloc[-2]["close"] * 100
    daily_body = abs(latest["close"] - latest["open"])
    daily_range = latest["high"] - latest["low"]
    candle_text = "日K 形态中性，方向尚未完全走顺。"
    if daily_range > 0 and daily_body / daily_range >= 0.6:
        candle_text = "日K 实体较长，当日方向比较明确。"
    elif daily_range > 0 and daily_body / daily_range <= 0.25:
        candle_text = "日K 实体较短，多空分歧较大。"
    technical_text = "\n".join([
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
    ])
    latest_metrics = {
        "date": latest["date"], "close": latest["close"], "open": latest["open"], "high": latest["high"], "low": latest["low"],
        "change_pct": change_pct, "ma5": latest["ma5"], "ma20": latest["ma20"], "ma60": latest["ma60"], "ma250": latest["ma250"],
        "dif": latest["dif"], "dea": latest["dea"], "macd": latest["macd"], "volume": latest["volume"], "hold": latest["hold"],
        "settle": latest["settle"], "weekly_change_pct": weekly_change_pct,
    }
    return technical_text, latest_metrics


def build_inventory_text(config):
    symbol = config["inventory_symbol"]
    if not symbol:
        return "库存：当前品种暂未配置库存接口。", {"inventory_bias": "neutral", "inventory_note": "暂无库存数据支撑"}
    try:
        inventory_df = load_inventory_data(symbol)
        if inventory_df is None or inventory_df.empty:
            return "库存：未获取到库存数据。", {"inventory_bias": "neutral", "inventory_note": "库存数据缺失"}
        latest = inventory_df.iloc[-1]
        previous = inventory_df.iloc[-2] if len(inventory_df) >= 2 else latest
        delta = safe_float(latest["增减"])
        if pd.notna(delta) and delta < 0:
            interpretation, bias = "库存继续回落，对盘面形成一定支撑。", "bullish"
        elif pd.notna(delta) and delta > 0:
            interpretation, bias = "库存边际增加，供给端压力略有抬升。", "bearish"
        else:
            interpretation, bias = "库存变化不大，库存端暂未提供明确方向。", "neutral"
        text = "\n".join([
            "库存数据：",
            f"最新日期：{latest['日期']}",
            f"最新库存：{format_number(latest['库存'], 0)}",
            f"较上一期增减：{format_number(latest['增减'], 0)}",
            f"库存解读：{interpretation}",
            f"上一期库存：{format_number(previous['库存'], 0)}",
        ])
        return text, {"inventory_bias": bias, "inventory_note": interpretation}
    except Exception as exc:
        return f"库存数据：获取失败，原因：{exc}", {"inventory_bias": "neutral", "inventory_note": "库存抓取失败"}


def build_basis_text(config, trade_date):
    spot_symbol = config["spot_symbol"]
    if not spot_symbol:
        return "期现与产业链：当前品种暂未配置现货/基差接口。", {"basis_bias": "neutral", "basis_note": "暂无基差结构判断"}
    try:
        basis_df = load_basis_data(trade_date.strftime("%Y%m%d"), spot_symbol)
        if basis_df is None or basis_df.empty:
            return "期现与产业链：未获取到现货和基差数据。", {"basis_bias": "neutral", "basis_note": "基差数据缺失"}
        latest = basis_df.iloc[0]
        dom_basis = safe_float(latest["dom_basis"])
        dom_basis_rate = safe_float(latest["dom_basis_rate"])
        if pd.notna(dom_basis) and dom_basis > 0:
            interpretation, bias = "主力合约维持升水结构，远月预期相对偏强。", "bullish"
        elif pd.notna(dom_basis) and dom_basis < 0:
            interpretation, bias = "主力合约维持贴水结构，现货端相对更强。", "bearish"
        else:
            interpretation, bias = "期现基差整体中性，未形成明显方向引导。", "neutral"
        text = "\n".join([
            "期现与产业链代理指标：",
            f"现货价格：{format_number(latest['spot_price'])}",
            f"主力合约：{latest['dominant_contract']}，主力价格：{format_number(latest['dominant_contract_price'])}",
            f"主力基差：{format_number(dom_basis)}，基差率：{format_number(dom_basis_rate * 100 if pd.notna(dom_basis_rate) else math.nan)}%",
            f"解读：{interpretation}",
        ])
        return text, {"basis_bias": bias, "basis_note": interpretation}
    except Exception as exc:
        return f"期现与产业链：获取失败，原因：{exc}", {"basis_bias": "neutral", "basis_note": "基差抓取失败"}


def classify_news_sentiment(text_blob):
    bullish_words = ["提振", "减产", "去库", "支撑", "紧张", "上涨", "改善"]
    bearish_words = ["回落", "走弱", "增产", "累库", "下跌", "压制", "疲弱"]
    bullish_score = sum(word in text_blob for word in bullish_words)
    bearish_score = sum(word in text_blob for word in bearish_words)
    if bullish_score > bearish_score:
        return "bullish", "相关新闻对盘面情绪偏正面，但仍需观察其是否持续传导到供需端。"
    if bearish_score > bullish_score:
        return "bearish", "相关新闻对盘面情绪偏负面，短线需防范情绪继续发酵。"
    return "neutral", "消息面对盘面影响偏中性，短线仍需更多跟踪验证。"


def build_news_text(config):
    try:
        news_df = load_news_data()
        if news_df.empty:
            return "消息面：未获取到财联社电报。", {"news_bias": "neutral", "news_note": "消息面暂缺"}
        rows = []
        for _, row in news_df.head(200).iterrows():
            haystack = f"{row['标题']} {row['内容']}"
            if any(keyword in haystack for keyword in config["keywords"]):
                rows.append(row)
            if len(rows) >= 5:
                break
        if not rows:
            return "消息面：当日未筛到高度相关资讯，建议结合产业资讯做人工补充。", {"news_bias": "neutral", "news_note": "消息面暂无高相关事件"}
        lines = ["财联社相关新闻："]
        text_blob = ""
        for row in rows:
            lines.append(f"- {row['发布日期']} {row['发布时间']} | {row['标题']}")
            text_blob += f"{row['标题']} {row['内容']} "
        news_bias, conclusion = classify_news_sentiment(text_blob)
        lines.append(f"消息解读：{conclusion}")
        return "\n".join(lines), {"news_bias": news_bias, "news_note": conclusion}
    except Exception as exc:
        return f"消息面：财联社新闻获取失败，原因：{exc}", {"news_bias": "neutral", "news_note": "消息抓取失败"}


def build_fundamental_text(product_name, config, latest_metrics):
    inventory_text, inventory_signal = build_inventory_text(config)
    basis_text, basis_signal = build_basis_text(config, latest_metrics["date"])
    news_text, news_signal = build_news_text(config)
    text = "\n\n".join([
        f"品种：{product_name}",
        f"交易所：{config['exchange']}",
        "\n".join(["行情概况：", f"收盘价：{latest_metrics['close']:.2f}", f"结算价：{format_number(latest_metrics['settle'])}", f"成交量：{format_number(latest_metrics['volume'], 0)}", f"持仓量：{format_number(latest_metrics['hold'], 0)}"]),
        inventory_text,
        basis_text,
        news_text,
    ])
    signals = {}
    signals.update(inventory_signal)
    signals.update(basis_signal)
    signals.update(news_signal)
    return text, signals


def evaluate_market_state(latest_metrics, signals):
    score = 0
    reasons = []
    checks = [
        (latest_metrics["close"] > latest_metrics["ma20"], "价格运行于 MA20 上方", "价格运行于 MA20 下方"),
        (latest_metrics["close"] > latest_metrics["ma60"], "价格运行于 MA60 上方", "价格运行于 MA60 下方"),
        (latest_metrics["ma20"] > latest_metrics["ma60"], "中期均线结构偏强", "中期均线结构偏弱"),
        (latest_metrics["macd"] > 0, "MACD 位于零轴上方", "MACD 位于零轴下方"),
    ]
    for condition, pos_text, neg_text in checks:
        score += 1 if condition else -1
        reasons.append(pos_text if condition else neg_text)
    for key, pos_text, neg_text in [
        ("inventory_bias", "库存端对价格形成支撑", "库存端对价格形成压制"),
        ("basis_bias", "期现结构偏强", "期现结构偏弱"),
        ("news_bias", "消息情绪偏正面", "消息情绪偏负面"),
    ]:
        if signals.get(key) == "bullish":
            score += 1
            reasons.append(pos_text)
        elif signals.get(key) == "bearish":
            score -= 1
            reasons.append(neg_text)
    if score >= 4:
        bias, confidence = "偏多", "较强"
    elif score >= 1:
        bias, confidence = "偏多", "中等"
    elif score <= -4:
        bias, confidence = "偏空", "较强"
    elif score <= -1:
        bias, confidence = "偏空", "中等"
    else:
        bias, confidence = "震荡", "中等"
    return {"score": score, "bias": bias, "confidence": confidence, "reasons": reasons}


def build_strategy_text(product_name, latest_metrics, signals, market_state):
    bias = market_state["bias"]
    if bias == "偏多":
        return "\n".join([
            f"综合结论：{product_name} 当前维持偏多交易思路。",
            "主观策略倾向：优先考虑顺势回调低吸，不建议脱离均线结构追高。",
            "执行建议：重点观察回踩 MA5 或 MA20 后的承接情况，若缩量回踩、放量上行，可考虑轻仓试多。",
            "确认条件：价格持续站稳 MA20 上方，且 MACD 不出现明显走弱。",
            "风险提示：若收盘重新跌回 MA20 下方，同时库存与消息面同步转弱，则需下调多头预期。",
        ])
    if bias == "偏空":
        return "\n".join([
            f"综合结论：{product_name} 当前维持偏空交易思路。",
            "主观策略倾向：优先考虑反弹承压后的顺势交易，不建议在连续急跌后继续追空。",
            "执行建议：重点观察反抽 MA5 或 MA20 后的压力确认，若上攻乏力，可考虑轻仓试空。",
            "确认条件：价格持续位于 MA20 下方，且 MACD 维持弱势结构。",
            "风险提示：若价格快速收复 MA20 并伴随放量，空头逻辑需要及时降级。",
        ])
    return "\n".join([
        f"综合结论：{product_name} 当前更适合按震荡整理思路处理。",
        "主观策略倾向：暂不抢方向，优先等待区间突破后的确认信号。",
        "执行建议：把重点放在区间上沿和下沿的突破确认，不建议在均线缠绕阶段频繁试单。",
        "确认条件：放量突破近几日高点可转向偏多，跌破近几日低点可转向偏空。",
        "风险提示：横盘阶段来回波动较大，仓位应明显小于趋势行情。",
    ])


def build_local_daily_report(product_name, latest_metrics, signals, market_state):
    bias = market_state["bias"]
    confidence = market_state["confidence"]
    leading_reasons = "；".join(market_state["reasons"][:4]) if market_state["reasons"] else "当前盘面信号中性"

    headline = f"{product_name}复盘日报"
    source_text = latest_metrics.get("data_source", "日线")
    if latest_metrics.get("snapshot_time"):
        source_text = f"{source_text} {latest_metrics['snapshot_time']}"
    subline = f"日期：{latest_metrics['date'].strftime('%Y-%m-%d')} | 方向判断：{bias} | 强度：{confidence} | 数据来源：{source_text}"

    core_view = (
        f"{product_name} 当前整体判断为{bias}，信号强度为{confidence}。"
        f"从盘面与基本面代理指标看，主要逻辑集中在：{leading_reasons}。"
    )

    technical_section = "\n".join([
        f"日线收盘价报 {format_number(latest_metrics['close'])}，当日涨跌幅 {format_number(latest_metrics['change_pct'])}%。",
        f"均线方面，MA5/20/60/250 分别为 {format_number(latest_metrics['ma5'])} / {format_number(latest_metrics['ma20'])} / {format_number(latest_metrics['ma60'])} / {format_number(latest_metrics['ma250'])}。",
        f"MACD 指标显示 DIF/DEA/MACD 分别为 {format_number(latest_metrics['dif'])} / {format_number(latest_metrics['dea'])} / {format_number(latest_metrics['macd'])}。",
        "若价格继续稳定在中期均线之上，技术面仍有望维持偏强结构；反之若重新失守关键均线，则需降低趋势判断强度。"
        if bias == "偏多"
        else "若价格继续受压于中期均线，弱势结构更容易延续；若重新收复关键均线，则需修正偏空判断。"
        if bias == "偏空"
        else "当前技术结构更接近整理阶段，后续方向仍需等待区间突破确认。",
    ])

    fundamental_section = "\n".join([
        f"库存端：{signals.get('inventory_note', '暂无库存判断')}。",
        f"期现结构：{signals.get('basis_note', '暂无基差判断')}。",
        f"消息面：{signals.get('news_note', '暂无消息判断')}。",
        "若库存、期现结构与消息面后续继续朝同一方向共振，则基本面信号的参考价值会进一步提升。",
    ])

    if bias == "偏多":
        trading_section = "\n".join([
            "交易上建议以顺势回调布局为主，不建议高位追涨。",
            "可重点跟踪回踩 MA5 或 MA20 后的承接情况，若缩量回踩后重新放量上行，可考虑轻仓尝试。",
            "若收盘重新回落至 MA20 下方，且动能同步转弱，则短线偏多逻辑暂时失效。",
        ])
    elif bias == "偏空":
        trading_section = "\n".join([
            "交易上建议以反弹承压后的顺势思路为主，不建议在急跌后继续追空。",
            "可重点跟踪反抽 MA5 或 MA20 后的压力确认，若上攻乏力，可考虑轻仓尝试。",
            "若价格重新站回 MA20 上方并伴随量能修复，则偏空逻辑暂时失效。",
        ])
    else:
        trading_section = "\n".join([
            "交易上以等待为主，重点关注区间上沿与下沿的突破确认。",
            "若放量突破近几日高点，可转向偏多应对；若跌破近几日低点，可转向偏空应对。",
            "在均线缠绕、方向不清的阶段，不建议频繁交易或重仓押注单边方向。",
        ])

    risk_section = "\n".join([
        "免费数据源可能存在延迟或临时缺失，需注意数据质量风险。",
        "若消息面快速反转，短线技术判断可能被打断。",
        "本报告由本地规则自动生成，适合复盘辅助，不等同于实时投顾服务。",
        "以上内容仅供复盘交流，不构成投资建议。",
    ])

    return "\n\n".join([
        headline,
        subline,
        "一、今日核心观点",
        core_view,
        "二、技术面跟踪",
        technical_section,
        "三、基本面与消息面跟踪",
        fundamental_section,
        "四、交易思路参考",
        trading_section,
        "五、风险提示",
        risk_section,
    ])


def build_analysis_context(product_name):
    config = FUTURE_CONFIG[product_name]
    daily_df = load_daily_data(config["main_symbol"])
    daily_df, freshness = append_snapshot_row_if_needed(daily_df, config)
    if len(daily_df) < 30:
        raise ValueError("历史数据太少，暂时无法完成完整分析。")
    technical_text, latest_metrics = build_technical_text(product_name, daily_df)
    latest_metrics["data_source"] = freshness["data_source"]
    latest_metrics["snapshot_time"] = freshness["snapshot_time"]
    fundamental_text, signals = build_fundamental_text(product_name, config, latest_metrics)
    market_state = evaluate_market_state(latest_metrics, signals)
    strategy_text = build_strategy_text(product_name, latest_metrics, signals, market_state)
    report_text = build_local_daily_report(product_name, latest_metrics, signals, market_state)
    return {
        "product_name": product_name,
        "technical_text": technical_text,
        "fundamental_text": fundamental_text,
        "strategy_text": strategy_text,
        "report_text": report_text,
        "latest_metrics": latest_metrics,
        "signals": signals,
        "market_state": market_state,
        "freshness": freshness,
    }


def refresh_summary(product_name, clear_report=False):
    context = build_analysis_context(product_name)
    st.session_state.selected_product = product_name
    st.session_state.technical_text = context["technical_text"]
    st.session_state.fundamental_text = context["fundamental_text"]
    st.session_state.strategy_text = context["strategy_text"]
    st.session_state.analysis_context = context
    st.session_state.last_auto_fetch_date = datetime.now().strftime("%Y-%m-%d")
    st.session_state.last_refresh_ts = datetime.now().timestamp()
    if clear_report:
        st.session_state.report_text = ""


def ensure_summary(product_name):
    if st.session_state.analysis_context is None or st.session_state.selected_product != product_name:
        refresh_summary(product_name)


def maybe_auto_refresh(product_name):
    now = datetime.now()
    seconds_since_refresh = now.timestamp() - float(st.session_state.get("last_refresh_ts", 0.0))
    if now.time() >= time(15, 0) and seconds_since_refresh >= 300:
        try:
            refresh_summary(product_name)
            st.info("检测到已过收盘后时间，已自动刷新数据。")
        except Exception as exc:
            st.warning(f"自动抓取失败：{exc}")


def render_status_cards():
    context = st.session_state.analysis_context
    if not context:
        return
    market_state = context["market_state"]
    latest_metrics = context["latest_metrics"]
    freshness = context.get("freshness", {})
    source_label = freshness.get("data_source", "日线")
    if freshness.get("snapshot_time"):
        source_label = f"{source_label} {freshness['snapshot_time']}"
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("方向判断", market_state["bias"])
    col2.metric("信号强度", market_state["confidence"])
    col3.metric("单日涨跌幅", f"{latest_metrics['change_pct']:.2f}%")
    col4.metric("收盘价", format_number(latest_metrics["close"]))
    col5.metric("数据来源", source_label)


def render_actions(product_name):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("手动获取收盘数据并填充", use_container_width=True):
            try:
                with st.spinner("正在抓取期货数据..."):
                    load_daily_data.clear()
                    load_basis_data.clear()
                    load_news_data.clear()
                    load_fast_snapshot.clear()
                    refresh_summary(product_name, clear_report=False)
                st.success("已获取最新数据并填充。")
            except Exception as exc:
                st.error(f"获取失败：{exc}")
    with col2:
        if st.button("生成客户日报", use_container_width=True):
            try:
                ensure_summary(product_name)
                st.session_state.report_text = st.session_state.analysis_context["report_text"]
                st.success("已生成客户日报。")
            except Exception as exc:
                st.error(f"生成失败：{exc}")
    with col3:
        if st.button("清空客户日报", use_container_width=True):
            st.session_state.report_text = ""
            st.success("已清空客户日报。")


def render_text_sections():
    st.text_area("技术面特征（含日K/周K、均线、MACD）", key="technical_text", height=320)
    st.text_area("基本面与消息面（新闻、库存、期现/产业链代理指标）", key="fundamental_text", height=360)
    st.text_area("我的主观策略倾向", key="strategy_text", height=220)


def render_report_section():
    st.subheader("客户日报")
    if st.session_state.report_text:
        st.markdown(st.session_state.report_text.replace("\n", "  \n"))
    else:
        st.info("点击“生成客户日报”后，这里会显示本地规则生成的日报内容。")


def main():
    init_page()
    init_state()
    if datetime.now().time() >= time(15, 0):
        st_autorefresh(interval=300000, key="after_close_refresh")
    product_name = st.selectbox(
        "选择期货品种",
        options=list(FUTURE_CONFIG.keys()),
        index=list(FUTURE_CONFIG.keys()).index(st.session_state.selected_product),
    )
    if product_name != st.session_state.selected_product:
        try:
            with st.spinner("正在切换品种并刷新数据..."):
                refresh_summary(product_name, clear_report=True)
            st.info("已根据新选择的品种自动刷新基础分析。")
        except Exception as exc:
            st.warning(f"切换品种后自动刷新失败：{exc}")
    maybe_auto_refresh(product_name)
    render_status_cards()
    render_actions(product_name)
    render_text_sections()
    render_report_section()


if __name__ == "__main__":
    main()
