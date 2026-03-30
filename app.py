import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon ASIN Content Prioritization Tool", layout="wide")

st.title("Amazon ASIN Content Prioritization Tool")
st.caption("Upload a CSV, map your columns, and score listing quality.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])


def safe_number(value):
    try:
        if pd.isna(value):
            return 0
        text = str(value).strip().replace("$", "").replace(",", "")
        if text == "":
            return 0
        return float(text)
    except:
        return 0


def get_text_value(row, column_name):
    if not column_name:
        return ""
    return str(row.get(column_name, "")).strip()


def suggest_column(columns, keywords):
    for col in columns:
        col_clean = str(col).strip().lower()
        for keyword in keywords:
            if keyword in col_clean:
                return col
    return columns[0] if columns else None


def get_index(columns, suggested):
    if suggested in columns:
        return columns.index(suggested)
    return 0


def get_smart_aplus_status(row, col_map):
    reasons = []

    title = get_text_value(row, col_map["title"])
    bullets = get_text_value(row, col_map["bullets"])
    description = get_text_value(row, col_map["description"])

    images = safe_number(row.get(col_map["images"], 0))
    reviews = safe_number(row.get(col_map["reviews"], 0))

    if len(title) < 20:
        reasons.append("Short title")

    if len(bullets) < 30:
        reasons.append("Missing or weak bullets")

    if len(description) < 40:
        reasons.append("Missing description")

    if images < 5:
        reasons.append("Less than 5 images")

    if reviews <= 0:
        reasons.append("No product reviews")

    if len(reasons) == 0:
        return "Yes", ""
    else:
        return "No", "; ".join(reasons)


def score_row(row, col_map):
    score = 0
    tips = []

    title = get_text_value(row, col_map["title"])
    bullets = get_text_value(row, col_map["bullets"])
    description = get_text_value(row, col_map["description"])

    images = safe_number(row.get(col_map["images"], 0))
    reviews = safe_number(row.get(col_map["reviews"], 0))
    price = safe_number(row.get(col_map["price"], 0))

    if len(title) >= 20:
        score += 1
    else:
        tips.append("Improve title")

    if len(bullets) >= 30:
        score += 1
    else:
        tips.append("Add bullets")

    if len(description) >= 40:
        score += 1
    else:
        tips.append("Improve description")

    if images >= 5:
        score += 1
    else:
        tips.append("Add more images")

    if reviews >= 10:
        score += 1
    else:
        tips.append("Increase review count")

    if price > 0:
        score += 1
    else:
        tips.append("Invalid price")

    if score >= 5:
        priority = "Low"
    elif score >= 3:
        priority = "Medium"
    else:
        priority = "High"

    return score, priority, "; ".join(tips)


if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [str(col).strip() for col in df.columns]
        columns = df.columns.tolist()

        st.sidebar.header("Column Mapping")

        asin_default = suggest_column(columns, ["asin"])
        title_default = suggest_column(columns, ["title", "name"])
        bullets_default = suggest_column(columns, ["bullets", "bullet", "features"])
        description_default = suggest_column(columns, ["description"])
        images_default = suggest_column(columns, ["images", "image"])
        reviews_default = suggest_column(columns, ["reviews", "review", "rating count"])
        price_default = suggest_column(columns, ["price"])

        asin_col = st.sidebar.selectbox(
            "ASIN column",
            columns,
            index=get_index(columns, asin_default),
        )

        title_col = st.sidebar.selectbox(
            "Title column",
            columns,
            index=get_index(columns, title_default),
        )

        bullets_col = st.sidebar.selectbox(
            "Bullets column",
            columns,
            index=get_index(columns, bullets_default),
        )

        description_col = st.sidebar.selectbox(
            "Description column",
            columns,
            index=get_index(columns, description_default),
        )

        images_col = st.sidebar.selectbox(
            "Images column",
            columns,
            index=get_index(columns, images_default),
        )

        reviews_col = st.sidebar.selectbox(
            "Reviews column",
            columns,
            index=get_index(columns, reviews_default),
        )

        price_col = st.sidebar.selectbox(
            "Price column",
            columns,
            index=get_index(columns, price_default),
        )

        col_map = {
            "asin": asin_col,
            "title": title_col,
            "bullets": bullets_col,
            "description": description_col,
            "images": images_col,
            "reviews": reviews_col,
            "price": price_col,
        }

        st.subheader("Selected Mapping")
        mapping_df = pd.DataFrame(
            {"Field": list(col_map.keys()), "Selected Column": list(col_map.values())}
        )
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)

        selected_columns = list(col_map.values())
        duplicate_columns = [
            col for col in set(selected_columns) if selected_columns.count(col) > 1
        ]

        if duplicate_columns:
            st.warning(
                "You selected the same column more than once: "
                + ", ".join(duplicate_columns)
                + ". Double-check your mapping before running analysis."
            )

        run_analysis = st.button(
            "Run Analysis", type="primary", use_container_width=True
        )

        if run_analysis:
            aplus_results = df.apply(
                lambda row: get_smart_aplus_status(row, col_map), axis=1
            )
            df["smart_a_plus_check"] = [x[0] for x in aplus_results]
            df["smart_a_plus_reason"] = [x[1] for x in aplus_results]

            scores = df.apply(lambda row: score_row(row, col_map), axis=1)
            df["optimization_score"] = [x[0] for x in scores]
            df["priority"] = [x[1] for x in scores]
            df["optimization_tips"] = [x[2] for x in scores]

            priority_cols = [
                asin_col,
                title_col,
                "optimization_score",
                "priority",
                "smart_a_plus_check",
                "smart_a_plus_reason",
                "optimization_tips",
            ]

            remaining_cols = [col for col in df.columns if col not in priority_cols]
            df = df[priority_cols + remaining_cols]

            total_rows = len(df)
            high_count = (df["priority"] == "High").sum()
            medium_count = (df["priority"] == "Medium").sum()
            low_count = (df["priority"] == "Low").sum()

            st.subheader("Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", total_rows)
            col2.metric("High Priority", high_count)
            col3.metric("Medium Priority", medium_count)
            col4.metric("Low Priority", low_count)

            st.subheader("Results")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Results CSV",
                data=csv,
                file_name="amazon_asin_results.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info(
        "Get started by uploading a CSV file containing your product listing data. After upload, map your columns in the sidebar and run the analysis."
    )
