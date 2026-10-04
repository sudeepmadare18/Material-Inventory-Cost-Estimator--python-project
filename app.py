import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Construction Cost Estimator",
    page_icon="🏗️",
    layout="wide"
)


# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

def get_connection():
    return sqlite3.connect("construction.db")


# ---------------------------------------------------
# CREATE DATABASE TABLES
# ---------------------------------------------------

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # Materials table
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

    # Labor table
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

    # Add sample material data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM materials")
    material_count = cursor.fetchone()[0]

    if material_count == 0:

        materials_data = [
            ("Cement", "Construction", 150, "bags", 450, "ABC Suppliers"),
            ("Steel", "Structural", 500, "kg", 65, "XYZ Steel"),
            ("Bricks", "Masonry", 5000, "pieces", 9, "BuildMart"),
            ("Sand", "Construction", 20, "tons", 1800, "River Sand Suppliers"),
            ("Tiles", "Finishing", 1000, "pieces", 35, "Modern Tiles"),
            ("Concrete", "Construction", 50, "cubic meters", 5500, "Premium Builders")
        ]

        cursor.executemany("""
        INSERT INTO materials
        (material_name, category, quantity, unit, unit_price, supplier)
        VALUES (?, ?, ?, ?, ?, ?)
        """, materials_data)

    # Add sample labor data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM labor")
    labor_count = cursor.fetchone()[0]

    if labor_count == 0:

        labor_data = [
            ("Mason", 5, 20, 800),
            ("Carpenter", 3, 15, 900),
            ("Electrician", 2, 10, 1000),
            ("Plumber", 2, 8, 900),
            ("Painter", 3, 12, 700)
        ]

        cursor.executemany("""
        INSERT INTO labor
        (worker_type, workers, days, daily_wage)
        VALUES (?, ?, ?, ?)
        """, labor_data)

    conn.commit()
    conn.close()


initialize_database()


# ---------------------------------------------------
# LOAD MATERIAL DATA
# ---------------------------------------------------

conn = get_connection()

materials_query = """
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
"""

df_materials = pd.read_sql_query(materials_query, conn)


# ---------------------------------------------------
# LOAD LABOR DATA
# ---------------------------------------------------

labor_query = """
SELECT
    labor_id,
    worker_type,
    workers,
    days,
    daily_wage,
    workers * days * daily_wage AS total_cost
FROM labor
"""

df_labor = pd.read_sql_query(labor_query, conn)

conn.close()


# ---------------------------------------------------
# CALCULATE COSTS
# ---------------------------------------------------

total_material_cost = df_materials["total_cost"].sum()
total_labor_cost = df_labor["total_cost"].sum()

total_project_cost = total_material_cost + total_labor_cost

approved_budget = 400000

remaining_budget = approved_budget - total_project_cost


# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🏗️ Construction Material Inventory & Cost Estimator")

st.write(
    "A simple dashboard for tracking construction materials, "
    "labor costs and project budget."
)


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Materials",
        "Labor",
        "Budget Analysis"
    ]
)


# ===================================================
# DASHBOARD
# ===================================================

if page == "Dashboard":

    st.header("📊 Project Dashboard")

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

    # Material category chart

    category_costs = df_materials.groupby(
        "category",
        as_index=False
    )["total_cost"].sum()

    fig = px.bar(
        category_costs,
        x="category",
        y="total_cost",
        title="Material Cost by Category"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Budget pie chart

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
        title="Project Budget Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)


# ===================================================
# MATERIALS
# ===================================================

elif page == "Materials":

    st.header("🧱 Material Inventory")

    st.dataframe(
        df_materials,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Add New Material")

    with st.form("material_form"):

        material_name = st.text_input("Material Name")

        category = st.text_input("Category")

        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            value=1.0
        )

        unit = st.text_input("Unit")

        unit_price = st.number_input(
            "Unit Price",
            min_value=0.0,
            value=0.0
        )

        supplier = st.text_input("Supplier")

        submit = st.form_submit_button(
            "Add Material"
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


# ===================================================
# LABOR
# ===================================================

elif page == "Labor":

    st.header("👷 Labor Information")

    st.dataframe(
        df_labor,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Total Labor Cost",
        f"₹{total_labor_cost:,.2f}"
    )


# ===================================================
# BUDGET ANALYSIS
# ===================================================

elif page == "Budget Analysis":

    st.header("💰 Budget Analysis")

    st.write(
        f"Approved Project Budget: "
        f"₹{approved_budget:,.2f}"
    )

    st.write(
        f"Estimated Project Cost: "
        f"₹{total_project_cost:,.2f}"
    )

    st.write(
        f"Remaining Budget: "
        f"₹{remaining_budget:,.2f}"
    )

    if total_project_cost <= approved_budget:

        st.success(
            "✅ Project is within the approved budget."
        )

    else:

        st.error(
            "⚠️ Project is over the approved budget."
        )

    budget_comparison = pd.DataFrame({
        "Category": [
            "Approved Budget",
            "Estimated Cost"
        ],
        "Amount": [
            approved_budget,
            total_project_cost
        ]
    })

    fig = px.bar(
        budget_comparison,
        x="Category",
        y="Amount",
        title="Budget vs Estimated Cost"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
