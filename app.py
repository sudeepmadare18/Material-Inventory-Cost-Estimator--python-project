import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Construction Cost Estimator",
    page_icon="🏗️",
    layout="wide"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect("construction.db")


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- MATERIALS TABLE ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        unit_price REAL NOT NULL,
        supplier TEXT NOT NULL
    )
    """)

    # ---------------- LABOR TABLE ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS labor (
        labor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_type TEXT NOT NULL,
        workers INTEGER NOT NULL,
        days INTEGER NOT NULL,
        daily_wage REAL NOT NULL
    )
    """)

    conn.commit()

    # Add sample materials only when database is empty

    cursor.execute("SELECT COUNT(*) FROM materials")
    material_count = cursor.fetchone()[0]

    if material_count == 0:

        materials = [
            (
                "Cement",
                "Construction",
                150,
                "bags",
                450,
                "ABC Suppliers"
            ),
            (
                "Steel",
                "Structural",
                500,
                "kg",
                65,
                "XYZ Steel"
            ),
            (
                "Bricks",
                "Masonry",
                5000,
                "pieces",
                9,
                "BuildMart"
            ),
            (
                "Sand",
                "Construction",
                20,
                "tons",
                1800,
                "River Sand Suppliers"
            ),
            (
                "Tiles",
                "Finishing",
                1000,
                "pieces",
                35,
                "Modern Tiles"
            )
        ]

        cursor.executemany("""
        INSERT INTO materials
        (
            material_name,
            category,
            quantity,
            unit,
            unit_price,
            supplier
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, materials)

    # Add sample labor only when database is empty

    cursor.execute("SELECT COUNT(*) FROM labor")
    labor_count = cursor.fetchone()[0]

    if labor_count == 0:

        labor = [
            ("Mason", 5, 20, 800),
            ("Carpenter", 3, 15, 900),
            ("Electrician", 2, 10, 1000),
            ("Plumber", 2, 8, 900),
            ("Painter", 3, 12, 700)
        ]

        cursor.executemany("""
        INSERT INTO labor
        (
            worker_type,
            workers,
            days,
            daily_wage
        )
        VALUES (?, ?, ?, ?)
        """, labor)

    conn.commit()
    conn.close()


initialize_database()


# ============================================================
# LOAD MATERIALS
# ============================================================

def load_materials():

    conn = get_connection()

    query = """
    SELECT
        material_id,
        material_name,
        category,
        quantity,
        unit,
        unit_price,
        supplier,
        quantity * unit_price AS total_cost
    FROM materials
    ORDER BY material_id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ============================================================
# LOAD LABOR
# ============================================================

def load_labor():

    conn = get_connection()

    query = """
    SELECT
        labor_id,
        worker_type,
        workers,
        days,
        daily_wage,
        workers * days * daily_wage AS total_cost
    FROM labor
    ORDER BY labor_id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ============================================================
# LOAD DATA
# ============================================================

df_materials = load_materials()
df_labor = load_labor()


# ============================================================
# COST CALCULATIONS
# ============================================================

total_material_cost = df_materials["total_cost"].sum()

total_labor_cost = df_labor["total_cost"].sum()

total_project_cost = (
    total_material_cost +
    total_labor_cost
)

approved_budget = 400000

remaining_budget = (
    approved_budget -
    total_project_cost
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🏗️ Construction Material Inventory & Cost Estimator"
)

st.write(
    "Manage construction materials, calculate labor costs, "
    "estimate project expenses and monitor the project budget."
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Select Section",
    [
        "📊 Dashboard",
        "🧱 Materials",
        "🧮 Cost Estimator",
        "👷 Labor",
        "💰 Budget Analysis"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.header("📊 Project Dashboard")

    # ---------------- METRICS ----------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Material Cost",
        f"₹{total_material_cost:,.0f}"
    )

    col2.metric(
        "Labor Cost",
        f"₹{total_labor_cost:,.0f}"
    )

    col3.metric(
        "Total Project Cost",
        f"₹{total_project_cost:,.0f}"
    )

    col4.metric(
        "Remaining Budget",
        f"₹{remaining_budget:,.0f}"
    )

    st.divider()

    # ---------------- MATERIAL CATEGORY CHART ----------------

    st.subheader("📊 Material Cost by Category")

    category_costs = (
        df_materials
        .groupby("category", as_index=False)["total_cost"]
        .sum()
    )

    fig = px.bar(
        category_costs,
        x="category",
        y="total_cost",
        title="Material Cost by Category",
        labels={
            "category": "Category",
            "total_cost": "Cost (₹)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------- BUDGET PIE CHART ----------------

    st.subheader("💰 Project Cost Distribution")

    budget_data = pd.DataFrame({
        "Cost Type": [
            "Materials",
            "Labor"
        ],
        "Amount": [
            total_material_cost,
            total_labor_cost
        ]
    })

    fig2 = px.pie(
        budget_data,
        names="Cost Type",
        values="Amount",
        title="Material vs Labor Cost"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# MATERIAL MANAGEMENT
# ============================================================

elif page == "🧱 Materials":

    st.header("🧱 Material Inventory Management")

    # ---------------- SHOW MATERIALS ----------------

    st.subheader("Current Materials")

    st.dataframe(
        df_materials,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # ADD MATERIAL
    # ========================================================

    st.subheader("➕ Add New Material")

    with st.form("add_material_form"):

        col1, col2 = st.columns(2)

        with col1:

            material_name = st.text_input(
                "Material Name"
            )

            category = st.text_input(
                "Category"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=1.0
            )

        with col2:

            unit = st.text_input(
                "Unit",
                placeholder="bags / kg / pieces / tons"
            )

            unit_price = st.number_input(
                "Unit Price (₹)",
                min_value=0.0,
                value=0.0
            )

            supplier = st.text_input(
                "Supplier"
            )

        add_button = st.form_submit_button(
            "➕ Add Material"
        )

        if add_button:

            if (
                material_name
                and category
                and unit
                and supplier
            ):

                conn = get_connection()

                conn.execute("""
                INSERT INTO materials
                (
                    material_name,
                    category,
                    quantity,
                    unit,
                    unit_price,
                    supplier
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    material_name,
                    category,
                    quantity,
                    unit,
                    unit_price,
                    supplier
                ))

                conn.commit()
                conn.close()

                st.success(
                    "Material added successfully!"
                )

                st.rerun()

            else:

                st.error(
                    "Please fill all fields."
                )

    st.divider()

    # ========================================================
    # EDIT MATERIAL
    # ========================================================

    st.subheader("✏️ Edit Material")

    if len(df_materials) > 0:

        material_options = dict(
            zip(
                df_materials["material_id"],
                df_materials["material_name"]
            )
        )

        selected_id = st.selectbox(
            "Select Material",
            options=list(material_options.keys()),
            format_func=lambda x: material_options[x]
        )

        selected_material = df_materials[
            df_materials["material_id"] == selected_id
        ].iloc[0]

        with st.form("edit_material_form"):

            col1, col2 = st.columns(2)

            with col1:

                edit_name = st.text_input(
                    "Material Name",
                    value=selected_material["material_name"]
                )

                edit_category = st.text_input(
                    "Category",
                    value=selected_material["category"]
                )

                edit_quantity = st.number_input(
                    "Quantity",
                    min_value=0.0,
                    value=float(selected_material["quantity"])
                )

            with col2:

                edit_unit = st.text_input(
                    "Unit",
                    value=selected_material["unit"]
                )

                edit_price = st.number_input(
                    "Unit Price (₹)",
                    min_value=0.0,
                    value=float(selected_material["unit_price"])
                )

                edit_supplier = st.text_input(
                    "Supplier",
                    value=selected_material["supplier"]
                )

            update_button = st.form_submit_button(
                "💾 Update Material"
            )

            if update_button:

                conn = get_connection()

                conn.execute("""
                UPDATE materials
                SET
                    material_name = ?,
                    category = ?,
                    quantity = ?,
                    unit = ?,
                    unit_price = ?,
                    supplier = ?
                WHERE material_id = ?
                """, (
                    edit_name,
                    edit_category,
                    edit_quantity,
                    edit_unit,
                    edit_price,
                    edit_supplier,
                    selected_id
                ))

                conn.commit()
                conn.close()

                st.success(
                    "Material updated successfully!"
                )

                st.rerun()

    st.divider()

    # ========================================================
    # DELETE MATERIAL
    # ========================================================

    st.subheader("🗑️ Delete Material")

    if len(df_materials) > 0:

        delete_options = dict(
            zip(
                df_materials["material_id"],
                df_materials["material_name"]
            )
        )

        delete_id = st.selectbox(
            "Select Material to Delete",
            options=list(delete_options.keys()),
            format_func=lambda x: delete_options[x],
            key="delete_material"
        )

        if st.button(
            "🗑️ Delete Selected Material"
        ):

            conn = get_connection()

            conn.execute(
                "DELETE FROM materials WHERE material_id = ?",
                (delete_id,)
            )

            conn.commit()
            conn.close()

            st.success(
                "Material deleted successfully!"
            )

            st.rerun()


# ============================================================
# COST ESTIMATOR
# ============================================================

elif page == "🧮 Cost Estimator":

    st.header("🧮 Construction Cost Estimator")

    st.write(
        "Enter the required quantities and costs to estimate "
        "the total construction expense."
    )

    st.divider()

    # ---------------- MATERIAL ESTIMATE ----------------

    st.subheader("🧱 Material Estimate")

    material_names = df_materials["material_name"].tolist()

    if material_names:

        selected_material_name = st.selectbox(
            "Select Material",
            material_names
        )

        selected_material = df_materials[
            df_materials["material_name"]
            == selected_material_name
        ].iloc[0]

        col1, col2, col3 = st.columns(3)

        with col1:

            required_quantity = st.number_input(
                f"Required Quantity ({selected_material['unit']})",
                min_value=0.0,
                value=float(selected_material["quantity"])
            )

        with col2:

            estimate_unit_price = st.number_input(
                "Unit Price (₹)",
                min_value=0.0,
                value=float(selected_material["unit_price"])
            )

        with col3:

            material_estimate = (
                required_quantity *
                estimate_unit_price
            )

            st.metric(
                "Material Cost",
                f"₹{material_estimate:,.2f}"
            )

        st.divider()

        # ---------------- LABOR ESTIMATE ----------------

        st.subheader("👷 Labor Estimate")

        col1, col2, col3 = st.columns(3)

        with col1:

            number_of_workers = st.number_input(
                "Number of Workers",
                min_value=0,
                value=1
            )

        with col2:

            number_of_days = st.number_input(
                "Number of Days",
                min_value=0,
                value=1
            )

        with col3:

            daily_wage = st.number_input(
                "Daily Wage per Worker (₹)",
                min_value=0.0,
                value=800.0
            )

        labor_estimate = (
            number_of_workers
            * number_of_days
            * daily_wage
        )

        st.metric(
            "Labor Cost",
            f"₹{labor_estimate:,.2f}"
        )

        st.divider()

        # ---------------- OTHER EXPENSES ----------------

        st.subheader("📦 Other Expenses")

        other_expenses = st.number_input(
            "Other Expenses (₹)",
            min_value=0.0,
            value=0.0
        )

        # ---------------- FINAL ESTIMATE ----------------

        estimated_total = (
            material_estimate
            + labor_estimate
            + other_expenses
        )

        st.divider()

        st.subheader("💰 Estimated Project Cost")

        st.metric(
            "Total Estimated Cost",
            f"₹{estimated_total:,.2f}"
        )

        if estimated_total <= approved_budget:

            st.success(
                f"Within budget! "
                f"Remaining: ₹{approved_budget - estimated_total:,.2f}"
            )

        else:

            st.error(
                f"Over budget by "
                f"₹{estimated_total - approved_budget:,.2f}"
            )


# ============================================================
# LABOR MANAGEMENT
# ============================================================

elif page == "👷 Labor":

    st.header("👷 Labor Management")

    # ---------------- LABOR TABLE ----------------

    st.subheader("Current Labor")

    st.dataframe(
        df_labor,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Total Labor Cost",
        f"₹{total_labor_cost:,.2f}"
    )

    st.divider()

    # ========================================================
    # ADD LABOR
    # ========================================================

    st.subheader("➕ Add Labor")

    with st.form("labor_form"):

        col1, col2 = st.columns(2)

        with col1:

            worker_type = st.text_input(
                "Worker Type",
                placeholder="Mason / Carpenter / Electrician"
            )

            workers = st.number_input(
                "Number of Workers",
                min_value=1,
                value=1
            )

        with col2:

            days = st.number_input(
                "Number of Days",
                min_value=1,
                value=1
            )

            wage = st.number_input(
                "Daily Wage per Worker (₹)",
                min_value=0.0,
                value=800.0
            )

        add_labor_button = st.form_submit_button(
            "➕ Add Labor"
        )

        if add_labor_button:

            if worker_type:

                conn = get_connection()

                conn.execute("""
                INSERT INTO labor
                (
                    worker_type,
                    workers,
                    days,
                    daily_wage
                )
                VALUES (?, ?, ?, ?)
                """, (
                    worker_type,
                    workers,
                    days,
                    wage
                ))

                conn.commit()
                conn.close()

                st.success(
                    "Labor added successfully!"
                )

                st.rerun()

            else:

                st.error(
                    "Please enter worker type."
                )

    st.divider()

    # ========================================================
    # DELETE LABOR
    # ========================================================

    st.subheader("🗑️ Delete Labor")

    if len(df_labor) > 0:

        labor_options = dict(
            zip(
                df_labor["labor_id"],
                df_labor["worker_type"]
            )
        )

        delete_labor_id = st.selectbox(
            "Select Labor Record",
            options=list(labor_options.keys()),
            format_func=lambda x: labor_options[x]
        )

        if st.button(
            "🗑️ Delete Labor"
        ):

            conn = get_connection()

            conn.execute(
                "DELETE FROM labor WHERE labor_id = ?",
                (delete_labor_id,)
            )

            conn.commit()
            conn.close()

            st.success(
                "Labor record deleted successfully!"
            )

            st.rerun()


# ============================================================
# BUDGET ANALYSIS
# ============================================================

elif page == "💰 Budget Analysis":

    st.header("💰 Budget Analysis")

    # ---------------- BUDGET INPUT ----------------

    budget = st.number_input(
        "Approved Project Budget (₹)",
        min_value=0.0,
        value=float(approved_budget)
    )

    estimated_cost = (
        total_material_cost +
        total_labor_cost
    )

    difference = (
        budget -
        estimated_cost
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Approved Budget",
        f"₹{budget:,.2f}"
    )

    col2.metric(
        "Estimated Cost",
        f"₹{estimated_cost:,.2f}"
    )

    col3.metric(
        "Difference",
        f"₹{difference:,.2f}"
    )

    if estimated_cost <= budget:

        st.success(
            "✅ Project is within the approved budget."
        )

    else:

        st.error(
            "⚠️ Project is over the approved budget."
        )

    st.divider()

    # ---------------- BUDGET CHART ----------------

    budget_comparison = pd.DataFrame({
        "Category": [
            "Approved Budget",
            "Estimated Cost"
        ],
        "Amount": [
            budget,
            estimated_cost
        ]
    })

    fig = px.bar(
        budget_comparison,
        x="Category",
        y="Amount",
        title="Approved Budget vs Estimated Cost",
        labels={
            "Category": "Type",
            "Amount": "Amount (₹)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------- COST BREAKDOWN ----------------

    st.subheader("📊 Cost Breakdown")

    cost_breakdown = pd.DataFrame({
        "Cost Type": [
            "Materials",
            "Labor"
        ],
        "Amount": [
            total_material_cost,
            total_labor_cost
        ]
    })

    st.dataframe(
        cost_breakdown,
        use_container_width=True,
        hide_index=True
    )

    fig2 = px.pie(
        cost_breakdown,
        names="Cost Type",
        values="Amount",
        title="Project Cost Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
