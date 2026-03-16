import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Préparer la colonne Location correctement
# =========================
df["Location"] = df["Location"].fillna("Unknown").astype(str)

# Dropdown options
location_options = [{"label": loc, "value": loc} for loc in sorted(df["Location"].unique())]

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

    html.Div([
        html.H2("ECAP Store"),
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
        "alignItems": "center"
    }),

    html.Div([
        # ===== LEFT COLUMN =====
        html.Div([
            # KPI séparés
            html.Div([
                html.Div([
                    html.H5("December", style={"textAlign":"center"}),
                    dcc.Graph(id="kpi-ca-dec", style={"height":"150px"})
                ], style={"width":"48%", "backgroundColor":CARD, "padding":"10px","borderRadius":"5px"}),

                html.Div([
                    html.H5("December", style={"textAlign":"center"}),
                    dcc.Graph(id="kpi-qty-dec", style={"height":"150px"})
                ], style={"width":"48%", "backgroundColor":CARD, "padding":"10px","borderRadius":"5px"})
            ], style={"display":"flex","justifyContent":"space-between","marginBottom":"20px"}),

            # Bar top 10
            dcc.Graph(id="bar-top10", style={"height": "500px"})
        ], style={"width":"40%","padding":"20px"}),

        # ===== RIGHT COLUMN =====
        html.Div([
            dcc.Graph(id="line-ca", style={"height":"350px"}),

            html.Div([
                html.H4("Table des 100 dernières ventes"),
                dash_table.DataTable(
                    id="table",
                    page_size=10,
                    filter_action="native",
                    sort_action="native",
                    style_table={"height":"320px","overflowY":"auto"},
                    style_cell={"textAlign":"center","padding":"6px","fontSize":"12px"},
                    style_header={"backgroundColor":"#e6eef4","fontWeight":"bold"}
                )
            ])
        ], style={"width":"60%","padding":"20px"})
    ], style={"display":"flex","backgroundColor":BG})
])

# =========================
# CALLBACK
# =========================
@app.callback(
    Output("kpi-ca-dec","figure"),
    Output("kpi-qty-dec","figure"),
    Output("bar-top10","figure"),
    Output("line-ca","figure"),
    Output("table","data"),
    Output("table","columns"),
    Input("location-filter","value")
)
def update_dashboard(locations):
    data = df.copy()
    if locations:
        data = data[data["Location"].isin(locations)]

    # ===== KPI December =====
    data_dec = data[data["Month"]==12]
    data_nov = data[data["Month"]==11]

    ca_dec = data_dec["Total_price"].sum()
    ca_nov = data_nov["Total_price"].sum()
    qty_dec = data_dec["Quantity"].sum()
    qty_nov = data_nov["Quantity"].sum()

    fig_ca_dec = go.Figure(go.Indicator(
        mode="number+delta",
        value=ca_dec/1000,
        number={"suffix":"k","font":{"size":50,"color":"#2c3e50"}},
        delta={"reference": ca_nov/1000,"relative":False,
               "decreasing":{"color":"#e74c3c"},
               "increasing":{"color":"#27ae60"},
               "position":"bottom"}
    ))
    fig_ca_dec.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor=CARD)

    fig_qty_dec = go.Figure(go.Indicator(
        mode="number+delta",
        value=qty_dec,
        number={"font":{"size":50,"color":"#2c3e50"}},
        delta={"reference": qty_nov,"relative":False,
               "decreasing":{"color":"#e74c3c"},
               "increasing":{"color":"#27ae60"},
               "position":"bottom"}
    ))
    fig_qty_dec.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor=CARD)

    # ===== BAR TOP10 décroissant =====
    top = data.groupby(["Product_Category","Gender"])["Quantity"].sum().reset_index()
    top10_categories = top.groupby("Product_Category")["Quantity"].sum().nlargest(10).index
    top = top[top["Product_Category"].isin(top10_categories)]
    top = top.sort_values("Quantity", ascending=True)  # pour bar horizontal en décroissant

    fig_bar = px.bar(top, x="Quantity", y="Product_Category", color="Gender",
                     orientation="h", title="Fréquence des 10 meilleures ventes")
    fig_bar.update_layout(height=500, paper_bgcolor=CARD)

    # ===== LINE CA =====
    weekly = data.set_index("Transaction_Date").resample("W")["Total_price"].sum().reset_index()
    fig_line = px.line(weekly, x="Transaction_Date", y="Total_price",
                       title="Évolution du chiffre d'affaire par semaine")
    fig_line.update_layout(height=350, paper_bgcolor=CARD, xaxis_title="Semaine", yaxis_title="Chiffre d'affaire")

    # ===== TABLE =====
    table_df = data.sort_values("Transaction_Date", ascending=False).head(100)
    table_df["Transaction_Date"] = table_df["Transaction_Date"].dt.date
    table_df = table_df[["Transaction_Date","Gender","Location","Product_Category","Quantity","Avg_Price","Discount_pct"]]
    columns = [{"name": i.replace("_"," "), "id": i} for i in table_df.columns]

    return fig_ca_dec, fig_qty_dec, fig_bar, fig_line, table_df.to_dict("records"), columns

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run_server(debug=True)