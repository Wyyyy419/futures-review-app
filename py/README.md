# 期货复盘总结网页

这是一个基于 Streamlit 的期货复盘网页，当前版本完全不依赖外部大模型 API，支持：

- 选择主流期货品种
- 自动抓取行情、库存、财联社相关新闻、期现基差
- 生成技术面、基本面和主观策略摘要
- 使用本地规则自动生成专业复盘建议

## 本地运行

安装依赖：

```bash
pip install -r requirements.txt
```

运行：

```bash
streamlit run app.py
```

## Streamlit Community Cloud 部署

1. 把本项目上传到 GitHub
2. 在 Streamlit Community Cloud 选择仓库并部署 `app.py`
3. 本项目当前不需要配置任何 API Key

## 说明

- 免费数据源可能会偶尔失效或延迟
- 本项目更适合做学习和复盘辅助，不适合作为唯一交易决策依据
