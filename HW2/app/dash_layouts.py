from datetime import datetime

from app.dash_callbacks import DashCallbacks
from dataframes.dataframe_handler import DataFrameHandler
from config.constants import START_DATE, END_DATE, PROJECT_NAME, UPLOADED_LOGS_PATH, ONSHAPE_LOGS_PATH
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


class DashPageLayouts:
    def __init__(self, dash_app: dash.Dash, db_handler: 'DatabaseHandler', utils):
        self.dash_app = dash_app
        self.db_handler = db_handler
        self.df_handler = DataFrameHandler(db_handler, utils)
        self.uploaded_json = None
        self.data_source_title = "Default Log"
        self.utils = utils
        self.define_layout()
        self.create_callbacks()
        self.utils.logger.info("Dash app pages loaded, and dataframes processed.")

    def create_callbacks(self):
        DashCallbacks(self.dash_app, self.df_handler, self.db_handler, self, self.utils)

    # Define individual page layouts with graphs and filters
    def dashboard_layout(self):
        return self._create_layout("Dashboard", [
            self._create_card("Activity Over Time", dcc.Graph(figure=self._create_line_chart(
                self.df_handler.activity_over_time, 'Date', 'ActivityCount', 'Activity Over Time')
            ), 12),
            self._create_card("Document Usage Frequency", dcc.Graph(figure=self._create_bar_chart(
                self.df_handler.document_usage, 'Document', 'UsageCount', 'Document Usage Frequency')
            ), 6),
            self._create_card("User Activity Distribution", dcc.Graph(figure=self._create_pie_chart(
                self.df_handler.user_activity, 'User', 'ActivityCount', 'User Activity Distribution')
            ), 6)
        ])

    def graphs_layout(self):
        self.data_source_title = "Default Log" if self.df_handler.selected_log_path == ONSHAPE_LOGS_PATH \
            else "Selected Uploaded Log"
        return self._create_layout("Interactive Graphs", [
            html.H4(f"Current Data Source - {self.data_source_title}", className="mb-4"),
            self._create_card("Filters", self._create_filters(), 12),
            self._create_card("Activity Over Time", dcc.Graph(figure=self._create_line_chart(
                self.df_handler.activity_over_time, 'Date', 'ActivityCount', 'Activity Over Time')
            ), 12),
            self._create_card("Document Usage Frequency", dcc.Graph(figure=self._create_bar_chart(
                self.df_handler.document_usage, 'Document', 'UsageCount', 'Document Usage Frequency')
            ), 6),
            self._create_card("User Activity Distribution", dcc.Graph(figure=self._create_pie_chart(
                self.df_handler.user_activity, 'User', 'ActivityCount', 'User Activity Distribution')
            ), 6)
        ])

    def alerts_layout(self):
        alerts_list, unread_alerts_count = self.create_alerts_list()
        return self._create_layout("Real-time Alerts", [
            self._create_card("Recent Alerts", html.Div(id='alerts-list', children=alerts_list), 12),
            self._create_card("Acknowledge All", dbc.Button("Acknowledge All", color="success", className="w-100",
                                                            id="acknowledge-all-button"), 12),
        ])

    def search_glossary_layout(self):
        text_input = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Input(id="input", placeholder="Search...", type="text"),
                            width=8
                        ),
                        dbc.Col(
                            dbc.Button(children=html.I(className="fas fa-search", style=dict(display="inline-block")),
                                       id="search-button",
                                       n_clicks=0, size='lg',
                                       style=dict(fontSize='1.7vh', backgroundColor="#007BC4", textAlign="center")),
                            width=4
                        )
                    ],
                    align="center"
                ),
                html.Br(),
                # html.P("Search results:"),
                html.P(id="output")
            ]
        )

        return self._create_layout("Search OnShape Glossary", [
            self._create_card("Search", text_input, 10)
        ])

    def upload_log_layout(self):
        return self._create_layout("Upload Log", [
            self._create_card("Upload JSON", self._create_upload_component(), 12)
        ])

    def create_header(self):
        current_date = datetime.now().strftime('%d-%m-%Y')
        logo_path = "/static/SFM-logo.png"
        return dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Img(src=logo_path, height="40px"), width="auto"),
                    dbc.Col(html.H1(PROJECT_NAME, className="text-white"), width="auto"),
                    dbc.Col(
                        html.H2(
                            current_date,
                            className="text-white mt-2",
                            style={"fontSize": "1.2rem", "color": "lightgrey"}
                        ),
                        width="auto"
                    )
                ], align="center", justify="start"),
            ], fluid=True),
            color="primary",
            dark=True,
            style={"width": "100%"}
        )

    def create_side_menu(self):
        alert_count = str(self.df_handler.get_unread_alerts_count())
        return dbc.Col([
            dbc.Nav(
                [
                    self._create_nav_link("fas fa-tachometer-alt", " Dashboard", "/"),
                    self._create_nav_link("fas fa-chart-line", " Graphs", "/graphs"),
                    self._create_nav_link("fas fa-magnifying-glass", " Search Glossary", "/search-glossary"),
                    self._create_nav_link("fas fa-cloud", " Upload Logs", "/upload-log"),
                    self._create_nav_link("fas fa-bell", " Alerts", "/alerts",
                                          alert_count,
                                          "danger", "alerts-count-badge"),
                ],
                vertical=True,
                pills=True,
                className="bg-dark h-100 p-3",
                style={"height": "100%"}
            ),
        ], width=2, className="bg-dark", style={"height": "100%", "overflow": "hidden"})

    def create_footer(self):
        return dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.P(f"© 2024 {PROJECT_NAME}, Inc.", className="text-white text-center mb-0"),
                            width="auto")
                ], align="center", justify="center", className="w-100")
            ]),
            color="primary",
            dark=True,
            style={"width": "100%"}
        )

    def define_layout(self):
        self.dash_app.layout = html.Div([
            self.create_header(),
            dbc.Container([
                dbc.Row([
                    self.create_side_menu(),
                    dcc.Location(id='url'),
                    dbc.Col(html.Div(id="page-content"), width=10, style={"height": "100%", "overflow": "auto"})
                ], style={"flex": "1", "overflow": "hidden", "height": "calc(100vh - 56px)"})
            ], fluid=True,
                style={"display": "flex", "flexDirection": "row", "flexGrow": "1", "height": "calc(100vh - 56px)"}),
            self.create_footer()
        ], style={"display": "flex", "flexDirection": "column", "height": "100vh"})

    def _create_layout(self, title: str, children: list) -> dbc.Container:
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.H2(title, style={"fontSize": "2.5rem", "textAlign": "left", "margin": "20px 0"}),
                    width=12
                )
            ]),
            dbc.Row(children)
        ], style={"padding": "20px"})

    def _create_card(self, title: str, content: html, width: int) -> dbc.Col:
        return dbc.Col(dbc.Card([
            dbc.CardHeader(title),
            dbc.CardBody([content])
        ]), width=width, className="mb-3 mt-3")

    def _create_filters(self) -> html.Div:
        # If the selected log path is not uploaded logs, then the default value for the logs dropdown should be empty
        # Otherwise, it should be the first uploaded log
        default_log_value = ""
        if self.df_handler.filters_data['uploaded-logs']:
            default_log_value = self.df_handler.filters_data['uploaded-logs'][
                0] if self.df_handler.selected_log_path == UPLOADED_LOGS_PATH else ""

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='document-dropdown', options=self.df_handler.filters_data['documents'],
                                     placeholder='Select Document'), width=4),
                dbc.Col(dcc.Dropdown(id='user-dropdown', options=self.df_handler.filters_data['users'],
                                     placeholder='Select User'), width=4),
                dbc.Col(dcc.Dropdown(id='description-dropdown', options=self.df_handler.filters_data['descriptions'],
                                     placeholder='Select Description'), width=4),
                dbc.Col(dcc.Dropdown(id='logs-dropdown', options=self.df_handler.filters_data['uploaded-logs'],
                                     placeholder='Select Log', value=default_log_value), width=4)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.DatePickerRange(id='date-picker-range',
                                            start_date=datetime.strptime(START_DATE, '%d-%m-%Y').date(),
                                            end_date=datetime.strptime(END_DATE, '%d-%m-%Y').date(),
                                            display_format='DD-MM-YYYY'), width=12)
            ], className="mb-3"),
            dbc.Button("Apply Filters", id='apply-filters', color="primary", className="w-100")
        ])

    def create_alerts_list(self) -> tuple:
        if self.df_handler.alerts_df.shape[0] == 0:
            alerts_list = html.P("No alerts to display", style={"color": "grey"})
        else:
            alerts_list = html.Ul([
                html.Li(
                    f"{row['Time']} - {row['Description']} by User: {row['User']} in Document: {row['Document']}",
                    style={"color": "grey" if row['Status'] == "read" else "black",
                           "fontWeight": "bold" if row['Status'] == "unread" else "normal"}
                ) for _, row in self.df_handler.alerts_df.iterrows()
            ], id='alerts-list', className="list-unstyled")

        unread_alerts_count = self.df_handler.get_unread_alerts_count()
        return alerts_list, str(unread_alerts_count)

    def _create_nav_link(self, icon_class: str, text: str, href: str, badge_text: str = "",
                         badge_color: str = "", badge_id: str = "") -> dbc.NavLink:
        children = [html.I(className=icon_class), html.Span(text, className="ml-4")]
        if badge_text:
            children.append(dbc.Badge(badge_text, color=badge_color, className="ml-2", id=badge_id))
        return dbc.NavLink(children, href=href, active="exact", className="text-white gap-6")

    def _validate_graph_data(self, df, x, y):
        if not isinstance(df, pd.DataFrame):  # if df is [] list then return empty df
            return pd.DataFrame({x: [], y: []}), x, y
        if x is None or y is None:
            return pd.DataFrame({x: [], y: []}), x, y
        return df, x, y

    def _create_line_chart(self, df: pd.DataFrame, x: str, y: str, title: str) -> px.line:
        df, x, y = self._validate_graph_data(df, x, y)
        if len(df) == 0:
            return px.line(title=title)
        return px.line(df, x=x, y=y, title=title)

    def _create_bar_chart(self, df: pd.DataFrame, x: str, y: str, title: str) -> px.bar:
        df, x, y = self._validate_graph_data(df, x, y)
        if len(df) == 0:
            return px.bar(title=title)
        return px.bar(df, x=x, y=y, title=title)

    def _create_pie_chart(self, df: pd.DataFrame, names: str, values: str, title: str) -> px.pie:
        if names is None or values is None or len(df) == 0:
            return px.pie(title=title)
        return px.pie(df, names=names, values=values, title=title)

    def _create_upload_component(self) -> html.Div:
        return html.Div([
            dcc.Upload(
                id='upload-json',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0'
                },
                multiple=False,  # Single file upload
                accept='.json'  # Accept only JSON files
            ),
            html.Div(id='output-json-upload', style={'margin': '10px 0'}),
            dbc.Checkbox(
                id='default-data-source',
                className="mb-3",
                label="Default data source"
            ),
            dbc.Button("Submit", id='submit-button', color="primary", className="w-100", disabled=True),
            html.Div(id='submit-status', style={'margin': '10px 0'})
        ])
