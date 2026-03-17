import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("data.csv", encoding="utf-8")

# 2. Garder uniquement les colonnes utiles
df = df[["CustomerID", "Gender", "Location", "Product_Category", "Quantity",
    "Avg_Price", "Transaction_Date", "Month", "Discount_pct"
    ]]

# 3. Remplacer les valeurs manquantes dans CustomerID par 0
df['CustomerID'] = df['CustomerID'].fillna(0)

# Convertir CustomerID en entier
df['CustomerID'] = df['CustomerID'].astype(int)

# 4. Convertir Transaction_Date en format date
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])

# 5. Créer Total_price avec la remise
df['Total_price'] = df['Quantity'] * df['Avg_Price'] * (1 - df['Discount_pct'] / 100)

# =========================
# Global Style
# =========================
CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "padding": "15px",
    "borderRadius": "12px",
    "boxShadow": "0 2px 6px rgba(0,0,0,0.10)"
}

FONT = {"font-family": "Segoe UI, Roboto, sans-serif"}

px.defaults.template = "simple_white"
px.defaults.color_discrete_sequence = ["#1f77b4", "#d62728"]

# =========================
# Dropdown
# =========================
location_options = [
    {"label": loc, "value": loc}
    for loc in sorted(
        df.loc[~df["Location"].isin(["Unknown"]), "Location"].dropna().unique()
    )
]

# =========================
# App
# =========================
app = dash.Dash(__name__)
server = app.server

app.title = "ECAP Store"


HEADER = "#bfe3ee"
BG = "#f8fbfd"
CARD = "#ffffff"

# =========================
# Layout
# =========================
app.layout = html.Div([

    # ===== HEADER =====
    html.Div([
        html.H2("ECAP Store", style={"margin": 0, **FONT}),
        dcc.Dropdown(
            id="location-filter",
            options=location_options,
            multi=True,
            placeholder="Choisissez des zones",
            style={"width": "300px"}
        )
    ], style={
        "backgroundColor": HEADER,
        "padding": "10px 30px",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        **FONT
    }),

    # ===== BODY =====
    html.Div([

        # ===== LEFT COLUMN =====
        html.Div([

            # KPI
            html.Div([
                html.Div([
                    html.H5("December", style={"textAlign": "center", "fontSize": "26px", "margin": "0", **FONT}),
                    dcc.Graph(id="kpi-ca-dec")
                ], style={**CARD_STYLE, "width": "45%"}),

                html.Div([
                    html.H5("December", style={"textAlign": "center", "fontSize": "26px", "margin": "0", **FONT}),
                    dcc.Graph(id="kpi-qty-dec")
                ], style={**CARD_STYLE, "width": "45%"})

            ], style={
                "display": "flex",
                "justifyContent": "space-between",
                "marginBottom": "20px"
            }),

            # BAR CHART
            html.Div([
                dcc.Graph(id="bar-top10")
            ], style={**CARD_STYLE})

        ], style={
            "width": "40%",
            "padding": "20px",
            "display": "flex",
            "flexDirection": "column"
        }),

        # ===== RIGHT COLUMN =====
        html.Div([

            # LINE CHART
            html.Div([
                dcc.Graph(id="line-ca")
            ], style={**CARD_STYLE, "marginBottom": "20px"}),

            # TABLE
            html.Div([
                html.H4("Table des 100 dernières ventes", style={**FONT}),
                dash_table.DataTable(
                    id="table",
                    page_size=10,
                    filter_action="native",
                    sort_action="native",
                    style_table={
                        "height": "350px",
                        "overflowY": "auto"
                    },
                    style_cell={
                        "textAlign": "center",
                        "padding": "6px",
                        "fontSize": "12px",
                        **FONT
                    },
                    style_header={
                        "backgroundColor": "#e6eef4",
                        "fontWeight": "bold",
                        **FONT
                    }
                )
            ], style={**CARD_STYLE})

        ], style={
            "width": "60%",
            "padding": "20px",
            "display": "flex",
            "flexDirection": "column"
        })

    ], style={
        "display": "flex",
        "alignItems": "flex-start",
        "backgroundColor": BG
    })

])

# =========================
# CALLBACK
# =========================
@app.callback(
    Output("kpi-ca-dec", "figure"),
    Output("kpi-qty-dec", "figure"),
    Output("bar-top10", "figure"),
    Output("line-ca", "figure"),
    Output("table", "data"),
    Output("table", "columns"),
    Input("location-filter", "value")
)
def update_dashboard(locations):

    data = df.copy()
    if locations:
        data = data[data["Location"].isin(locations)]

    # ===== KPI December =====
    data_dec = data[data["Month"] == 12]
    data_nov = data[data["Month"] == 11]

    ca_dec = data_dec["Total_price"].sum()
    ca_nov = data_nov["Total_price"].sum()
    qty_dec = data_dec["Quantity"].sum()
    qty_nov = data_nov["Quantity"].sum()

    # ===== KPI CA DEC =====
    fig_ca_dec = go.Figure(go.Indicator(
        mode="number+delta",
        value=ca_dec / 1000,
        number={"suffix": "k", "font": {"size": 80, "color": "black"}},
        delta={
            "reference": ca_nov / 1000,
            "relative": False,
            "valueformat": ".1f",
            "suffix": "k",
            "decreasing": {"color": "#ff1900", "symbol": "▼ "},
            "increasing": {"color": "#27ae3b", "symbol": "▲ "},
            "position": "bottom"
        }
    ))
    fig_ca_dec.update_layout(height=150, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=CARD)

    # ===== KPI QTY DEC =====
    fig_qty_dec = go.Figure(go.Indicator(
        mode="number+delta",
        value=qty_dec / 1000,
        number={"suffix": "k", "font": {"size": 80, "color": "black"}},
        delta={
            "reference": qty_nov / 1000,
            "relative": False,
            "valueformat": ".1f",
            "suffix": "k",
            "decreasing": {"color": "#ff1900", "symbol": "▼ "},
            "increasing": {"color": "#27ae3b", "symbol": "▲ "},
            "position": "bottom"
        }
    ))
    fig_qty_dec.update_layout(height=150, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=CARD)

    # ===== BAR TOP10 =====
    top = (
        data.groupby(["Product_Category", "Gender"])["Quantity"]
        .sum()
        .reset_index()
    )

    top10_categories = (
        top.groupby("Product_Category")["Quantity"]
        .sum()
        .nlargest(10)
        .index
    )

    top = top[top["Product_Category"].isin(top10_categories)]
    top = top.sort_values(["Quantity"], ascending=True)

    fig_bar = px.bar(
        top,
        x="Quantity",
        y="Product_Category",
        color="Gender",
        orientation="h",
        title="<b>Fréquence des 10 meilleures ventes</b>",
        color_discrete_map={"F": "#1f77b4", "M": "#d62728"}
    )

    fig_bar.update_layout(
        height=600,
        paper_bgcolor=CARD,
        plot_bgcolor="white",
        title_font=dict(size=20, color="black"),
        xaxis_title="Total vente",
        yaxis_title="Catégorie du produit",
        legend_title="Sexe",
        bargap=0.15,
        barmode="group"
    )

    fig_bar.update_traces(marker_line_width=0.5, marker_line_color="black")

    # ===== LINE CA =====
    weekly = data.set_index("Transaction_Date").resample("W")["Total_price"].sum().reset_index()

    fig_line = px.line(
        weekly,
        x="Transaction_Date",
        y="Total_price",
        title="<b>Évolution du chiffre d'affaire par semaine</b>"
    )

    fig_line.update_layout(
        height= 400,
        paper_bgcolor=CARD,
        xaxis_title="Semaine",
        yaxis_title="Chiffre d'affaire",
        title_font=dict(size=18, color="black")
    )

    # ===== TABLE =====
    table_df = data.sort_values("Transaction_Date", ascending=False).head(100)
    table_df["Transaction_Date"] = table_df["Transaction_Date"].dt.date
    table_df = table_df[
        ["Transaction_Date", "Gender", "Location",
         "Product_Category", "Quantity", "Avg_Price", "Discount_pct"]
    ]
    columns = [{"name": i.replace("_", " "), "id": i} for i in table_df.columns]

    return fig_ca_dec, fig_qty_dec, fig_bar, fig_line, table_df.to_dict("records"), columns

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run_server(debug=True)