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
# DATABASE
# ============================================================

DB_NAME = "construction.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # MATERIALS TABLE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # LABOR TABLE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # INSERT SAMPLE MATERIALS
    # ONLY IF TABLE IS EMPTY
    # --------------------------------------------------------

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
            ),
            (
                "Concrete",
                "Structural",
                50,
                "cubic meters",
                5500,
                "Premium Builders"
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

    # --------------------------------------------------------
    # INSERT SAMPLE LABOR
    # ONLY IF TABLE IS EMPTY
    # --------------------------------------------------------

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
# CURRENT INVENTORY COST
# ============================================================

inventory_material_cost = df_materials["total_cost"].sum()

labor_database_cost = df_labor["total_cost"].sum()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏗️ Construction Estimator")

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

    st.title(
        "🏗️ Construction Material Inventory & Cost Estimator"
    )

    st.write(
        "Manage materials, labor and estimate the complete "
        "construction project cost."
    )

    st.divider()

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Materials",
        len(df_materials)
    )

    col2.metric(
        "Material Inventory Value",
        f"₹{inventory_material_cost:,.0f}"
    )

    col3.metric(
        "Labor Records",
        len(df_labor)
    )

    col4.metric(
        "Labor Cost",
        f"₹{labor_database_cost:,.0f}"
    )

    st.divider()

    # --------------------------------------------------------
    # MATERIAL COST CHART
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SUPPLIER CHART
    # --------------------------------------------------------

    st.subheader("🏢 Material Value by Supplier")

    supplier_costs = (
        df_materials
        .groupby("supplier", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
    )

    fig2 = px.bar(
        supplier_costs,
        x="supplier",
        y="total_cost",
        title="Material Value by Supplier",
        labels={
            "supplier": "Supplier",
            "total_cost": "Value (₹)"
        }
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# MATERIAL MANAGEMENT
# ============================================================

elif page == "🧱 Materials":

    st.title("🧱 Material Inventory")

    # --------------------------------------------------------
    # MATERIAL TABLE
    # --------------------------------------------------------

    st.subheader("Current Material Inventory")

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

    with st.form("add_material"):

        col1, col2 = st.columns(2)

        with col1:

            material_name = st.text_input(
                "Material Name"
            )

            category = st.text_input(
                "Category"
            )

            quantity = st.number_input(
                "Available Quantity",
                min_value=0.0,
                value=1.0
            )

        with col2:

            unit = st.text_input(
                "Unit",
                placeholder="bags, kg, pieces, tons"
            )

            unit_price = st.number_input(
                "Unit Price (₹)",
                min_value=0.0,
                value=0.0
            )

            supplier = st.text_input(
                "Supplier"
            )

        submit = st.form_submit_button(
            "➕ Add Material"
        )

        if submit:

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

        material_dict = dict(
            zip(
                df_materials["material_id"],
                df_materials["material_name"]
            )
        )

        selected_id = st.selectbox(
            "Select Material",
            list(material_dict.keys()),
            format_func=lambda x: material_dict[x]
        )

        selected = df_materials[
            df_materials["material_id"] == selected_id
        ].iloc[0]

        with st.form("edit_material"):

            col1, col2 = st.columns(2)

            with col1:

                edit_name = st.text_input(
                    "Material Name",
                    value=selected["material_name"]
                )

                edit_category = st.text_input(
                    "Category",
                    value=selected["category"]
                )

                edit_quantity = st.number_input(
                    "Quantity",
                    min_value=0.0,
                    value=float(selected["quantity"])
                )

            with col2:

                edit_unit = st.text_input(
                    "Unit",
                    value=selected["unit"]
                )

                edit_price = st.number_input(
                    "Unit Price",
                    min_value=0.0,
                    value=float(selected["unit_price"])
                )

                edit_supplier = st.text_input(
                    "Supplier",
                    value=selected["supplier"]
                )

            update = st.form_submit_button(
                "💾 Update Material"
            )

            if update:

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

        delete_dict = dict(
            zip(
                df_materials["material_id"],
                df_materials["material_name"]
            )
        )

        delete_id = st.selectbox(
            "Select Material to Delete",
            list(delete_dict.keys()),
            format_func=lambda x: delete_dict[x],
            key="delete_material"
        )

        if st.button(
            "🗑️ Delete Material",
            type="secondary"
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
# REALISTIC COST ESTIMATOR
# ============================================================

elif page == "🧮 Cost Estimator":

    st.title("🧮 Construction Cost Estimator")

    st.write(
        "Create a project estimate using multiple materials, "
        "labor, transportation, equipment, other expenses "
        "and contingency."
    )

    st.divider()

    # ========================================================
    # PROJECT INFORMATION
    # ========================================================

    st.subheader("🏗️ Project Information")

    col1, col2, col3 = st.columns(3)

    with col1:

        project_name = st.text_input(
            "Project Name",
            placeholder="Example: Residential Building"
        )

    with col2:

        project_area = st.number_input(
            "Project Area (sq.ft)",
            min_value=0.0,
            value=1000.0
        )

    with col3:

        approved_budget = st.number_input(
            "Approved Budget (₹)",
            min_value=0.0,
            value=400000.0
        )

    st.divider()

    # ========================================================
    # MULTIPLE MATERIAL ESTIMATION
    # ========================================================

    st.subheader("🧱 Material Requirements")

    material_names = df_materials[
        "material_name"
    ].tolist()

    # Session state for selected materials

    if "estimate_materials" not in st.session_state:

        st.session_state.estimate_materials = []

    # --------------------------------------------------------
    # ADD MATERIAL TO ESTIMATE
    # --------------------------------------------------------

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:

        if material_names:

            selected_material_name = st.selectbox(
                "Select Material",
                material_names,
                key="estimate_material_select"
            )

    with col2:

        selected_quantity = st.number_input(
            "Required Quantity",
            min_value=0.0,
            value=1.0,
            key="estimate_quantity"
        )

    with col3:

        st.write("")
        st.write("")

        add_estimate_material = st.button(
            "➕ Add to Estimate"
        )

    if add_estimate_material:

        selected_row = df_materials[
            df_materials["material_name"]
            == selected_material_name
        ].iloc[0]

        material_record = {
            "Material": selected_material_name,
            "Quantity": selected_quantity,
            "Unit": selected_row["unit"],
            "Unit Price": float(
                selected_row["unit_price"]
            ),
            "Cost": (
                selected_quantity
                * float(selected_row["unit_price"])
            )
        }

        st.session_state.estimate_materials.append(
            material_record
        )

        st.success(
            f"{selected_material_name} added to estimate."
        )

    # --------------------------------------------------------
    # SHOW SELECTED MATERIALS
    # --------------------------------------------------------

    if st.session_state.estimate_materials:

        estimate_material_df = pd.DataFrame(
            st.session_state.estimate_materials
        )

        st.dataframe(
            estimate_material_df,
            use_container_width=True,
            hide_index=True
        )

        material_estimate_total = (
            estimate_material_df["Cost"].sum()
        )

    else:

        material_estimate_total = 0

        st.info(
            "Add materials to create your project estimate."
        )

    st.divider()

    # ========================================================
    # LABOR ESTIMATION
    # ========================================================

    st.subheader("👷 Labor Estimate")

    col1, col2, col3 = st.columns(3)

    with col1:

        estimate_workers = st.number_input(
            "Number of Workers",
            min_value=0,
            value=5
        )

    with col2:

        estimate_days = st.number_input(
            "Working Days",
            min_value=0,
            value=20
        )

    with col3:

        estimate_daily_wage = st.number_input(
            "Daily Wage / Worker (₹)",
            min_value=0.0,
            value=800.0
        )

    labor_estimate_total = (
        estimate_workers
        * estimate_days
        * estimate_daily_wage
    )

    st.metric(
        "Estimated Labor Cost",
        f"₹{labor_estimate_total:,.2f}"
    )

    st.divider()

    # ========================================================
    # OTHER PROJECT EXPENSES
    # ========================================================

    st.subheader("📦 Other Project Expenses")

    col1, col2, col3 = st.columns(3)

    with col1:

        transportation_cost = st.number_input(
            "🚚 Transportation Cost (₹)",
            min_value=0.0,
            value=0.0
        )

    with col2:

        equipment_cost = st.number_input(
            "🏗️ Equipment Cost (₹)",
            min_value=0.0,
            value=0.0
        )

    with col3:

        other_expenses = st.number_input(
            "📦 Other Expenses (₹)",
            min_value=0.0,
            value=0.0
        )

    other_cost_total = (
        transportation_cost
        + equipment_cost
        + other_expenses
    )

    st.divider()

    # ========================================================
    # CONTINGENCY
    # ========================================================

    st.subheader("⚠️ Contingency")

    contingency_percentage = st.number_input(
        "Contingency Percentage (%)",
        min_value=0.0,
        max_value=50.0,
        value=5.0
    )

    subtotal = (
        material_estimate_total
        + labor_estimate_total
        + other_cost_total
    )

    contingency_amount = (
        subtotal
        * contingency_percentage
        / 100
    )

    # ========================================================
    # FINAL ESTIMATE
    # ========================================================

    final_estimate = (
        subtotal
        + contingency_amount
    )

    st.divider()

    st.subheader("💰 Final Project Estimate")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Material Cost",
            f"₹{material_estimate_total:,.2f}"
        )

    with col2:

        st.metric(
            "Labor Cost",
            f"₹{labor_estimate_total:,.2f}"
        )

    with col3:

        st.metric(
            "Other Costs",
            f"₹{other_cost_total:,.2f}"
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "Subtotal",
            f"₹{subtotal:,.2f}"
        )

    with col5:

        st.metric(
            "Contingency",
            f"₹{contingency_amount:,.2f}"
        )

    with col6:

        st.metric(
            "TOTAL ESTIMATE",
            f"₹{final_estimate:,.2f}"
        )

    st.divider()

    # ========================================================
    # BUDGET COMPARISON
    # ========================================================

    st.subheader("💰 Budget Comparison")

    budget_difference = (
        approved_budget
        - final_estimate
    )

    if final_estimate <= approved_budget:

        st.success(
            f"✅ Project is within budget. "
            f"Remaining budget: "
            f"₹{budget_difference:,.2f}"
        )

    else:

        st.error(
            f"⚠️ Project is over budget by "
            f"₹{abs(budget_difference):,.2f}"
        )

    # ========================================================
    # COST BREAKDOWN CHART
    # ========================================================

    cost_breakdown = pd.DataFrame({
        "Cost Type": [
            "Materials",
            "Labor",
            "Other Expenses",
            "Contingency"
        ],
        "Amount": [
            material_estimate_total,
            labor_estimate_total,
            other_cost_total,
            contingency_amount
        ]
    })

    fig = px.pie(
        cost_breakdown,
        names="Cost Type",
        values="Amount",
        title="Complete Project Cost Breakdown"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ========================================================
    # ESTIMATE TABLE
    # ========================================================

    st.subheader("📋 Estimate Summary")

    summary = pd.DataFrame({
        "Cost Type": [
            "Materials",
            "Labor",
            "Transportation",
            "Equipment",
            "Other Expenses",
            "Subtotal",
            "Contingency",
            "Final Estimate"
        ],
        "Amount (₹)": [
            material_estimate_total,
            labor_estimate_total,
            transportation_cost,
            equipment_cost,
            other_expenses,
            subtotal,
            contingency_amount,
            final_estimate
        ]
    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # DOWNLOAD ESTIMATE
    # ========================================================

    csv_data = summary.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Estimate CSV",
        data=csv_data,
        file_name="construction_project_estimate.csv",
        mime="text/csv"
    )

    # --------------------------------------------------------
    # CLEAR ESTIMATE
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Current Estimate"
    ):

        st.session_state.estimate_materials = []

        st.rerun()


# ============================================================
# LABOR MANAGEMENT
# ============================================================

elif page == "👷 Labor":

    st.title("👷 Labor Management")

    st.subheader("Current Labor Records")

    st.dataframe(
        df_labor,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Total Labor Cost",
        f"₹{labor_database_cost:,.2f}"
    )

    st.divider()

    # ========================================================
    # ADD LABOR
    # ========================================================

    st.subheader("➕ Add Labor")

    with st.form("add_labor"):

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
                "Working Days",
                min_value=1,
                value=1
            )

            daily_wage = st.number_input(
                "Daily Wage per Worker (₹)",
                min_value=0.0,
                value=800.0
            )

        add_labor = st.form_submit_button(
            "➕ Add Labor"
        )

        if add_labor:

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
                    daily_wage
                ))

                conn.commit()
                conn.close()

                st.success(
                    "Labor added successfully!"
                )

                st.rerun()

            else:

                st.error(
                    "Enter worker type."
                )

    st.divider()

    # ========================================================
    # DELETE LABOR
    # ========================================================

    st.subheader("🗑️ Delete Labor Record")

    if len(df_labor) > 0:

        labor_dict = dict(
            zip(
                df_labor["labor_id"],
                df_labor["worker_type"]
            )
        )

        delete_labor = st.selectbox(
            "Select Labor Record",
            list(labor_dict.keys()),
            format_func=lambda x: labor_dict[x],
            key="delete_labor"
        )

        if st.button(
            "🗑️ Delete Labor"
        ):

            conn = get_connection()

            conn.execute(
                "DELETE FROM labor WHERE labor_id = ?",
                (delete_labor,)
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

    st.title("💰 Budget Analysis")

    budget = st.number_input(
        "Approved Project Budget (₹)",
        min_value=0.0,
        value=400000.0
    )

    current_project_cost = (
        inventory_material_cost
        + labor_database_cost
    )

    difference = (
        budget
        - current_project_cost
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Approved Budget",
        f"₹{budget:,.2f}"
    )

    col2.metric(
        "Current Project Cost",
        f"₹{current_project_cost:,.2f}"
    )

    col3.metric(
        "Remaining Budget",
        f"₹{difference:,.2f}"
    )

    if current_project_cost <= budget:

        st.success(
            "✅ Current project cost is within the budget."
        )

    else:

        st.error(
            "⚠️ Current project cost is over the budget."
        )

    st.divider()

    budget_data = pd.DataFrame({
        "Category": [
            "Approved Budget",
            "Current Project Cost"
        ],
        "Amount": [
            budget,
            current_project_cost
        ]
    })

    fig = px.bar(
        budget_data,
        x="Category",
        y="Amount",
        title="Budget vs Current Project Cost"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
