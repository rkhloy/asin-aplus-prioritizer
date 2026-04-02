import streamlit as st
import pandas as pd
import re
from io import BytesIO
from collections import Counter

st.set_page_config(page_title="ASIN A+ Prioritizer V2", layout="wide")

st.title("ASIN A+ Prioritizer V2")
st.caption(
    "Analyze product listing data from CSV or Excel, score listing quality, and prioritize which products need optimization first."
)

st.markdown(
    """
### What this version adds
- Richer field mapping: SKU, brand, category, features, images, pricing, meta title, channel/source
- Weighted 100-point scoring model
- Failure reason tracking and issue categories
- Dashboard charts for priorities, failure reasons, and score bands
- Stronger downloadable output for internal review
"""
)

st.markdown(
    """
    <style>
    div.stDownloadButton > button {
        width: 100%;
        height: 3.2em;
        font-size: 1.05rem;
        font-weight: 700;
        border-radius: 10px;
        border: 2px solid #2e7d32;
    }
    div.stDownloadButton > button:hover {
        border: 2px solid #1b5e20;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])


# -----------------------------
# Helper functions
# -----------------------------
def safe_number(value):
    try:
        if pd.isna(value):
            return 0.0
        text = str(value).strip().replace("$", "").replace(",", "")
        if text == "":
            return 0.0
        return float(text)
    except Exception:
        return 0.0


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def get_text_value(row, column_name):
    if not column_name or column_name == "-- Not Mapped --":
        return ""
    return clean_text(row.get(column_name, ""))


def get_value(row, column_name):
    if not column_name or column_name == "-- Not Mapped --":
        return None
    return row.get(column_name, None)


def suggest_column(columns, keywords):
    for col in columns:
        col_clean = str(col).strip().lower()
        for keyword in keywords:
            if keyword in col_clean:
                return col
    return "-- Not Mapped --"


def get_index(options, suggested):
    if suggested in options:
        return options.index(suggested)
    return 0


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", clean_text(text).lower()))


def text_overlap_score(text1, text2):
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    overlap = len(tokens1.intersection(tokens2))
    return overlap / max(len(tokens1), len(tokens2))


def is_blank(value):
    return clean_text(value) == ""


def looks_like_url(value):
    text = clean_text(value).lower()
    return (
        text.startswith("http://")
        or text.startswith("https://")
        or text.startswith("www.")
    )


def add_reason(reasons, category_counter, reason, category):
    reasons.append(reason)
    category_counter[category] += 1


def score_binary(condition, points_if_true):
    return points_if_true if condition else 0


def score_tiered(value, tiers):
    # tiers format: [(condition, points), ...]
    for condition, points in tiers:
        if condition:
            return points
    return 0


def analyze_row(row, col_map):
    reasons = []
    tips = []
    categories = Counter()
    critical_issue = False

    asin = get_text_value(row, col_map["asin"])
    sku = get_text_value(row, col_map["sku"])
    title = get_text_value(row, col_map["title"])
    brand = get_text_value(row, col_map["brand"])
    category = get_text_value(row, col_map["category"])
    description = get_text_value(row, col_map["description"])
    meta_title = get_text_value(row, col_map["meta_title"])
    channel = get_text_value(row, col_map["channel"])

    bullet_values = [
        get_text_value(row, col_map[key])
        for key in ["bullet1", "bullet2", "bullet3", "bullet4"]
    ]
    feature_values = [
        get_text_value(row, col_map[key])
        for key in ["feature1", "feature2", "feature3", "feature4"]
    ]
    image_values = [
        get_text_value(row, col_map[key])
        for key in ["image1", "image2", "image3", "image4", "image5"]
    ]

    default_price = safe_number(get_value(row, col_map["default_price"]))
    sale_price = safe_number(get_value(row, col_map["sale_price"]))
    reviews = safe_number(get_value(row, col_map["reviews"]))

    populated_bullets = [x for x in bullet_values if x]
    populated_features = [x for x in feature_values if x]
    populated_images = [x for x in image_values if x]

    # -----------------------------
    # 1) Content completeness - 30
    # -----------------------------
    content_score = 0

    title_points = score_tiered(
        len(title),
        [
            (len(title) >= 60, 8),
            (len(title) >= 40, 6),
            (len(title) >= 20, 3),
        ],
    )
    content_score += title_points
    if len(title) == 0:
        add_reason(reasons, categories, "Missing title", "Content")
        tips.append("Add product title")
        critical_issue = True
    elif len(title) < 20:
        add_reason(reasons, categories, "Short title", "Content")
        tips.append("Improve title length and clarity")

    desc_points = score_tiered(
        len(description),
        [
            (len(description) >= 150, 8),
            (len(description) >= 80, 6),
            (len(description) >= 40, 3),
        ],
    )
    content_score += desc_points
    if len(description) == 0:
        add_reason(reasons, categories, "Missing description", "Content")
        tips.append("Add product description")
        critical_issue = True
    elif len(description) < 40:
        add_reason(reasons, categories, "Weak description", "Content")
        tips.append("Expand description details")

    bullet_feature_count = len(populated_bullets) + len(populated_features)
    bf_points = score_tiered(
        bullet_feature_count,
        [
            (bullet_feature_count >= 6, 10),
            (bullet_feature_count >= 4, 8),
            (bullet_feature_count >= 2, 5),
            (bullet_feature_count >= 1, 2),
        ],
    )
    content_score += bf_points
    if bullet_feature_count == 0:
        add_reason(reasons, categories, "Missing bullets and features", "Content")
        tips.append("Add bullets or feature fields")
        critical_issue = True
    elif bullet_feature_count < 4:
        add_reason(reasons, categories, "Weak bullets/features", "Content")
        tips.append("Complete more bullets and feature fields")

    brand_category_points = 0
    if brand:
        brand_category_points += 2
    else:
        add_reason(reasons, categories, "Missing brand", "Identity")
        tips.append("Populate brand field")
    if category:
        brand_category_points += 2
    else:
        add_reason(reasons, categories, "Missing category", "Identity")
        tips.append("Populate category field")
    content_score += brand_category_points

    # -----------------------------
    # 2) Image readiness - 20
    # -----------------------------
    image_score = 0
    image1 = image_values[0]

    if image1 and looks_like_url(image1):
        image_score += 8
    else:
        add_reason(reasons, categories, "Primary image missing or invalid", "Images")
        tips.append("Add a valid primary image URL")
        critical_issue = True

    additional_images_count = sum(
        1 for x in image_values[1:] if x and looks_like_url(x)
    )
    image_score += score_tiered(
        additional_images_count,
        [
            (additional_images_count >= 4, 12),
            (additional_images_count >= 3, 9),
            (additional_images_count >= 2, 6),
            (additional_images_count >= 1, 3),
        ],
    )
    if len(populated_images) < 5:
        add_reason(reasons, categories, "Less than 5 images", "Images")
        tips.append("Add more gallery images")

    duplicate_images = len(set([x for x in populated_images if x])) < len(
        [x for x in populated_images if x]
    )
    if duplicate_images and populated_images:
        add_reason(reasons, categories, "Duplicate image URLs", "Images")
        tips.append("Replace duplicate image URLs")

    image_completeness_pct = round((sum(1 for x in image_values if x) / 5) * 100, 1)
    missing_image_count = 5 - sum(1 for x in image_values if x)

    # -----------------------------
    # 3) Pricing integrity - 15
    # -----------------------------
    pricing_score = 0

    if default_price > 0:
        pricing_score += 5
    else:
        add_reason(reasons, categories, "Invalid default price", "Pricing")
        tips.append("Fix default price")
        critical_issue = True

    sale_price_mapped = col_map["sale_price"] != "-- Not Mapped --"
    if sale_price_mapped:
        if sale_price >= 0:
            pricing_score += 5
        else:
            add_reason(reasons, categories, "Invalid sale price", "Pricing")
            tips.append("Fix sale price value")
    else:
        pricing_score += 5

    pricing_issue_flag = "No"
    discount_pct = 0.0
    if default_price > 0 and sale_price_mapped and sale_price > 0:
        discount_pct = round(((default_price - sale_price) / default_price) * 100, 2)
        if sale_price <= default_price:
            pricing_score += 5
        else:
            add_reason(
                reasons, categories, "Sale price exceeds default price", "Pricing"
            )
            tips.append("Review sale price logic")
            critical_issue = True
            pricing_issue_flag = "Yes"
        if discount_pct > 80:
            add_reason(reasons, categories, "Extreme discount flagged", "Pricing")
            tips.append("Review extreme discount")
            pricing_issue_flag = "Yes"
    elif default_price > 0 and sale_price_mapped:
        pricing_score += 3
    else:
        pricing_score += 5

    if any(
        r in reasons
        for r in [
            "Invalid default price",
            "Invalid sale price",
            "Sale price exceeds default price",
        ]
    ):
        pricing_issue_flag = "Yes"

    # -----------------------------
    # 4) Search & merchandising quality - 15
    # -----------------------------
    search_score = 0

    if meta_title:
        search_score += score_tiered(
            len(meta_title),
            [
                (len(meta_title) >= 40, 5),
                (len(meta_title) >= 20, 3),
            ],
        )
    else:
        add_reason(reasons, categories, "Missing meta title", "SEO / Meta")
        tips.append("Add meta title")

    overlap = text_overlap_score(title, meta_title)
    if title and meta_title:
        if overlap >= 0.5:
            search_score += 5
        elif overlap >= 0.25:
            search_score += 3
            add_reason(reasons, categories, "Partial title/meta mismatch", "SEO / Meta")
            tips.append("Align meta title with product title")
        else:
            add_reason(reasons, categories, "Title/meta mismatch", "SEO / Meta")
            tips.append("Improve title and meta title consistency")
    else:
        if title or meta_title:
            add_reason(reasons, categories, "Incomplete title/meta pair", "SEO / Meta")

    title_category_text = f"{title} {meta_title}".lower()
    if category:
        if category.lower() in title_category_text:
            search_score += 5
        else:
            add_reason(
                reasons,
                categories,
                "Category not reflected in title/meta",
                "SEO / Meta",
            )
            tips.append("Align title/meta with category keywords")
    else:
        search_score += 0

    # -----------------------------
    # 5) Reviews/social proof - 10
    # -----------------------------
    reviews_score = 0
    if reviews > 0:
        reviews_score += 4
    else:
        add_reason(reasons, categories, "No product reviews", "Reviews")
        tips.append("Build review count")

    if reviews >= 50:
        reviews_score += 6
    elif reviews >= 10:
        reviews_score += 4
    elif reviews >= 1:
        reviews_score += 2

    # -----------------------------
    # 6) Channel consistency / governance - 10
    # -----------------------------
    channel_score = 0
    channel_mismatch_flag = "No"

    if channel:
        channel_score += 4
    else:
        add_reason(reasons, categories, "Missing channel/source", "Channel Governance")
        tips.append("Populate channel/source")

    if asin:
        channel_score += 3
    else:
        add_reason(reasons, categories, "Missing ASIN", "Identity")
        tips.append("Populate ASIN")
        critical_issue = True

    if sku:
        channel_score += 3
    else:
        add_reason(reasons, categories, "Missing SKU", "Identity")
        tips.append("Populate SKU")
        critical_issue = True

    # Placeholder governance check for future multi-channel comparison
    if not channel:
        channel_mismatch_flag = "Review"

    # -----------------------------
    # Final score and labels
    # -----------------------------
    total_score = round(
        content_score
        + image_score
        + pricing_score
        + search_score
        + reviews_score
        + channel_score,
        1,
    )

    if critical_issue or total_score < 60:
        priority = "High"
    elif total_score < 80:
        priority = "Medium"
    else:
        priority = "Low"

    if total_score < 40:
        score_band = "0-39 Critical"
    elif total_score < 60:
        score_band = "40-59 High Priority"
    elif total_score < 80:
        score_band = "60-79 Medium Priority"
    else:
        score_band = "80-100 Healthy"

    filled_fields = [
        asin,
        sku,
        title,
        brand,
        category,
        description,
        meta_title,
        channel,
        *bullet_values,
        *feature_values,
        *image_values,
        default_price if default_price > 0 else "",
        sale_price if sale_price > 0 else "",
        reviews if reviews > 0 else "",
    ]
    total_possible_fields = 8 + 4 + 4 + 5 + 3
    populated_count = sum(1 for x in filled_fields if clean_text(x) != "")
    completeness_pct = round((populated_count / total_possible_fields) * 100, 1)

    feature_completeness_pct = round((len(populated_features) / 4) * 100, 1)
    bullet_completeness_pct = round((len(populated_bullets) / 4) * 100, 1)

    smart_aplus_readiness = "Yes" if total_score >= 80 and not critical_issue else "No"
    failure_reasons = "; ".join(dict.fromkeys(reasons))
    optimization_tips = "; ".join(dict.fromkeys(tips))
    top_issue_category = categories.most_common(1)[0][0] if categories else "None"

    return {
        "optimization_score": total_score,
        "priority": priority,
        "score_band": score_band,
        "smart_a_plus_readiness": smart_aplus_readiness,
        "completeness_pct": completeness_pct,
        "issue_count": len(set(reasons)),
        "failure_reasons": failure_reasons,
        "optimization_tips": optimization_tips,
        "top_issue_category": top_issue_category,
        "image_completeness_pct": image_completeness_pct,
        "missing_image_count": missing_image_count,
        "feature_completeness_pct": feature_completeness_pct,
        "bullet_completeness_pct": bullet_completeness_pct,
        "pricing_issue_flag": pricing_issue_flag,
        "discount_pct": discount_pct,
        "title_meta_consistency_flag": "Yes" if overlap >= 0.25 else "No",
        "channel_mismatch_flag": channel_mismatch_flag,
    }


# -----------------------------
# Main app logic
# -----------------------------
if uploaded_file is not None:
    try:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            st.stop()

        df.columns = [str(col).strip() for col in df.columns]
        raw_columns = df.columns.tolist()
        columns = ["-- Not Mapped --"] + raw_columns

        st.sidebar.header("Column Mapping")
        st.sidebar.caption(
            "Map the columns that best match your file. Optional fields can stay unmapped."
        )

        default_map = {
            "asin": suggest_column(raw_columns, ["asin"]),
            "sku": suggest_column(raw_columns, ["sku", "item sku"]),
            "title": suggest_column(raw_columns, ["title", "name", "product name"]),
            "brand": suggest_column(raw_columns, ["brand"]),
            "category": suggest_column(raw_columns, ["category", "product type"]),
            "description": suggest_column(raw_columns, ["description"]),
            "meta_title": suggest_column(
                raw_columns, ["meta title", "meta", "seo title"]
            ),
            "channel": suggest_column(
                raw_columns, ["channel", "source", "marketplace"]
            ),
            "bullet1": suggest_column(raw_columns, ["bullet1", "bullet 1"]),
            "bullet2": suggest_column(raw_columns, ["bullet2", "bullet 2"]),
            "bullet3": suggest_column(raw_columns, ["bullet3", "bullet 3"]),
            "bullet4": suggest_column(raw_columns, ["bullet4", "bullet 4"]),
            "feature1": suggest_column(
                raw_columns, ["feature1", "feature 1", "bullet", "features"]
            ),
            "feature2": suggest_column(raw_columns, ["feature2", "feature 2"]),
            "feature3": suggest_column(raw_columns, ["feature3", "feature 3"]),
            "feature4": suggest_column(raw_columns, ["feature4", "feature 4"]),
            "image1": suggest_column(raw_columns, ["image1", "image 1", "main image"]),
            "image2": suggest_column(raw_columns, ["image2", "image 2"]),
            "image3": suggest_column(raw_columns, ["image3", "image 3"]),
            "image4": suggest_column(raw_columns, ["image4", "image 4"]),
            "image5": suggest_column(raw_columns, ["image5", "image 5"]),
            "default_price": suggest_column(
                raw_columns, ["default price", "price", "regular price"]
            ),
            "sale_price": suggest_column(
                raw_columns, ["sale price", "special price", "promo price"]
            ),
            "reviews": suggest_column(
                raw_columns, ["reviews", "review count", "rating count"]
            ),
        }

        required_fields = [
            "asin",
            "sku",
            "title",
            "brand",
            "category",
            "description",
            "image1",
            "default_price",
        ]
        optional_fields = [
            "meta_title",
            "channel",
            "bullet1",
            "bullet2",
            "bullet3",
            "bullet4",
            "feature1",
            "feature2",
            "feature3",
            "feature4",
            "image2",
            "image3",
            "image4",
            "image5",
            "sale_price",
            "reviews",
        ]

        col_map = {}

        with st.sidebar.expander("Required fields", expanded=True):
            for field in required_fields:
                col_map[field] = st.selectbox(
                    f"{field.replace('_', ' ').title()}",
                    columns,
                    index=get_index(columns, default_map[field]),
                    key=f"map_{field}",
                )

        with st.sidebar.expander("Optional fields", expanded=False):
            for field in optional_fields:
                col_map[field] = st.selectbox(
                    f"{field.replace('_', ' ').title()}",
                    columns,
                    index=get_index(columns, default_map[field]),
                    key=f"map_{field}",
                )

        mapping_df = pd.DataFrame(
            {
                "Field": list(col_map.keys()),
                "Selected Column": list(col_map.values()),
                "Type": [
                    "Required" if f in required_fields else "Optional"
                    for f in col_map.keys()
                ],
            }
        )

        st.subheader("Selected Mapping")
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)

        selected_columns = [v for v in col_map.values() if v != "-- Not Mapped --"]
        duplicate_columns = [
            col for col in set(selected_columns) if selected_columns.count(col) > 1
        ]
        if duplicate_columns:
            st.warning(
                "You selected the same column more than once: "
                + ", ".join(duplicate_columns)
                + ". Double-check your mapping before running analysis."
            )

        missing_required = [
            field for field in required_fields if col_map[field] == "-- Not Mapped --"
        ]
        if missing_required:
            st.error("Missing required mappings: " + ", ".join(missing_required))
            st.stop()

        run_analysis = st.button(
            "Run Analysis", type="primary", use_container_width=True
        )

        if run_analysis:
            results_df = df.apply(
                lambda row: pd.Series(analyze_row(row, col_map)), axis=1
            )
            output_df = pd.concat([df.copy(), results_df], axis=1)

            preferred_front = [
                col_map["asin"],
                col_map["sku"],
                col_map["title"],
                col_map["brand"],
                col_map["category"],
                col_map["channel"],
                "optimization_score",
                "priority",
                "score_band",
                "smart_a_plus_readiness",
                "completeness_pct",
                "issue_count",
                "top_issue_category",
                "failure_reasons",
                "optimization_tips",
                "image_completeness_pct",
                "missing_image_count",
                "feature_completeness_pct",
                "bullet_completeness_pct",
                "pricing_issue_flag",
                "discount_pct",
                "title_meta_consistency_flag",
                "channel_mismatch_flag",
            ]
            preferred_front = [
                c
                for c in preferred_front
                if c in output_df.columns and c != "-- Not Mapped --"
            ]
            remaining_cols = [c for c in output_df.columns if c not in preferred_front]
            output_df = output_df[preferred_front + remaining_cols]

            # Summary metrics
            total_rows = len(output_df)
            high_count = int((output_df["priority"] == "High").sum())
            medium_count = int((output_df["priority"] == "Medium").sum())
            low_count = int((output_df["priority"] == "Low").sum())
            avg_score = (
                round(output_df["optimization_score"].mean(), 1) if total_rows else 0
            )

            st.subheader("Summary")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rows", total_rows)
            c2.metric("High Priority", high_count)
            c3.metric("Medium Priority", medium_count)
            c4.metric("Low Priority", low_count)
            st.metric("Average Score", avg_score)

            # Charts
            st.subheader("Dashboard")

            priority_chart = (
                output_df["priority"]
                .value_counts()
                .reindex(["High", "Medium", "Low"], fill_value=0)
            )
            st.markdown("**Priority Distribution**")
            st.bar_chart(priority_chart)

            reason_counter = Counter()
            for reason_string in output_df["failure_reasons"].fillna(""):
                if clean_text(reason_string):
                    for reason in [
                        x.strip() for x in reason_string.split(";") if x.strip()
                    ]:
                        reason_counter[reason] += 1
            top_reasons_df = pd.DataFrame(
                reason_counter.most_common(10), columns=["Failure Reason", "Count"]
            )
            st.markdown("**Top Failure Reasons**")
            if not top_reasons_df.empty:
                st.bar_chart(top_reasons_df.set_index("Failure Reason"))
            else:
                st.info("No failure reasons found.")

            score_band_chart = (
                output_df["score_band"]
                .value_counts()
                .reindex(
                    [
                        "0-39 Critical",
                        "40-59 High Priority",
                        "60-79 Medium Priority",
                        "80-100 Healthy",
                    ],
                    fill_value=0,
                )
            )
            st.markdown("**Score Bands**")
            st.bar_chart(score_band_chart)

            st.subheader("Results")
            st.dataframe(output_df, use_container_width=True)

            st.info(
                "This export is designed for internal review and prioritization. It is not formatted as an Amazon bulk upload template."
            )

            if file_name.endswith(".csv"):
                output_data = output_df.to_csv(index=False).encode("utf-8")
                output_file_name = "asin_aplus_prioritizer_v2_results.csv"
                output_mime = "text/csv"
            else:
                output_buffer = BytesIO()
                output_df.to_excel(output_buffer, index=False)
                output_data = output_buffer.getvalue()
                output_file_name = "asin_aplus_prioritizer_v2_results.xlsx"
                output_mime = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.download_button(
                "Download Results File",
                data=output_data,
                file_name=output_file_name,
                mime=output_mime,
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"Error reading file: {e}")
