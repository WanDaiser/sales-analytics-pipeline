from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from sales_analysis.pipeline import (
    clean_and_enrich,
    compute_product_stats,
    compute_revenue_metrics,
    detect_high_value_sales,
    generate_data,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📊 Sales Analysis Dashboard")
st.markdown("Synthetic sales data pipeline — interactive explorer")
st.divider()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Pipeline Settings")
    size = st.slider("Number of records", min_value=20, max_value=1000, value=100, step=10)
    seed = st.number_input("Random seed", min_value=0, max_value=9999, value=42)
    start_date = st.date_input("Start date", value=pd.Timestamp("2025-01-01"))
    st.divider()
    run = st.button("▶ Run Pipeline", use_container_width=True, type="primary")

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run or "df_clean" not in st.session_state:
    raw_df = generate_data(size=size, seed=seed, start_date=str(start_date))
    df_clean = clean_and_enrich(raw_df)
    product_stats = compute_product_stats(df_clean)
    avg_revenue, std_dev = compute_revenue_metrics(df_clean)
    high_value = detect_high_value_sales(df_clean, avg=avg_revenue, std=std_dev)

    st.session_state["df_clean"] = df_clean
    st.session_state["product_stats"] = product_stats
    st.session_state["avg_revenue"] = avg_revenue
    st.session_state["std_dev"] = std_dev
    st.session_state["high_value"] = high_value

df_clean = st.session_state["df_clean"]
product_stats = st.session_state["product_stats"]
avg_revenue = st.session_state["avg_revenue"]
std_dev = st.session_state["std_dev"]
high_value = st.session_state["high_value"]

# ── KPI Cards ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Records", f"{len(df_clean):,}")
col2.metric("💰 Avg Revenue", f"${avg_revenue:,.2f}")
col3.metric("📉 Std Deviation", f"${std_dev:,.2f}")
col4.metric("🔥 High-Value Txns", f"{len(high_value):,}")

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📦 Revenue by Product")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        product_stats["product_id"].astype(str),
        product_stats["total_revenue"],
        color=["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"],
    )
    ax.set_xlabel("Product ID")
    ax.set_ylabel("Total Revenue ($)")
    ax.set_title("Total Revenue per Product")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_right:
    st.subheader("📈 Revenue Distribution")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.hist(df_clean["total_revenue"], bins=30, color="#4C72B0", edgecolor="white")
    ax2.axvline(avg_revenue, color="orange", linewidth=2, label=f"Avg: ${avg_revenue:,.0f}")
    threshold = avg_revenue + std_dev
    ax2.axvline(
        threshold, color="red", linewidth=2, linestyle="--", label=f"Threshold: ${threshold:,.0f}"
    )
    ax2.set_xlabel("Total Revenue ($)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Revenue Distribution")
    ax2.legend()
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.divider()

# ── Product Stats Table ───────────────────────────────────────────────────────
st.subheader("🗂️ Product Summary")
st.dataframe(
    product_stats.style.format({"total_revenue": "${:,.2f}", "rating": "{:.2f}"}),
    use_container_width=True,
)

st.divider()

# ── High Value Transactions ───────────────────────────────────────────────────
st.subheader(f"🔥 High-Value Transactions ({len(high_value)} rows)")
threshold_display = f"${avg_revenue:,.2f} + ${std_dev:,.2f} = ${avg_revenue + std_dev:,.2f}"
st.caption(f"Threshold: avg + std = {threshold_display}")
st.dataframe(
    high_value.reset_index(drop=True).style.format({
        "unit_price": "${:,.2f}",
        "total_revenue": "${:,.2f}",
        "rating": "{:.2f}",
    }),
    use_container_width=True,
)

st.divider()

# ── Raw Data ──────────────────────────────────────────────────────────────────
with st.expander("🔍 View Raw Cleaned Data"):
    st.dataframe(
        df_clean.style.format({
            "unit_price": "${:,.2f}",
            "total_revenue": "${:,.2f}",
            "rating": "{:.2f}",
        }),
        use_container_width=True,
    )
    col_dl1, col_dl2 = st.columns(2)
    col_dl1.download_button(
        "⬇ Download Transactions CSV",
        data=df_clean.to_csv(index=False),
        file_name="transactions.csv",
        mime="text/csv",
        use_container_width=True,
    )
    col_dl2.download_button(
        "⬇ Download Report CSV",
        data=product_stats.to_csv(index=False),
        file_name="report.csv",
        mime="text/csv",
        use_container_width=True,
    )
