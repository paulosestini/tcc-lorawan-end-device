# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
import dotenv
from datetime import datetime

import plotly.graph_objects as go
from dash.dash_table import DataTable

dotenv.load_dotenv()

app = Dash(__name__)

db_connection = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)


dev_map = {
    "Road 1": "aaaaaaaaaaaaaaaa",
    "Road 2": "bbbbbbbbbbbbbbbb",
    "Poli": "ab64e4da0ac1ca3f",
}

location_options = list(dev_map.keys())
event_options = ["cow", "person", "car", "dog", "danger"]
aggregation_options = {"Minute": "T", "Hour": "h", "Day": "d", "Week": "w", "Month": "m"}

app.layout = html.Div(
    [
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds, e.g., 2*1000 for 2 seconds
            n_intervals=0,
        ),
        html.Div(
            [
                html.Img(src="assets/car.png", className="logoImg"),
                html.Img(src="assets/beagle.png", className="logoImg"),
                html.Img(src="assets/person.png", className="logoImg"),
                html.Img(src="assets/road.png", className="logoImg"),
                html.Img(src="assets/cow.png", className="logoImg"),
            ],
            className="headerImages",
        ),
        html.Div(
            [
                dcc.Markdown("# Road Monitoring Dashboard", className="appHeaderText"),
            ],
            className="appHeader",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Markdown("Location", className="filterName"),
                                dcc.Dropdown(
                                    location_options,
                                    location_options[2],
                                    id="location-filter",
                                ),
                            ],
                            className="eventFilter",
                        ),
                        html.Div(
                            [
                                dcc.Markdown("Event", className="filterName"),
                                dcc.Dropdown(
                                    event_options, event_options[2], id="event-filter"
                                ),
                            ],
                            className="eventFilter",
                        ),
                    ],
                    className="eventFilterGroup",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Markdown("Aggregation", className="filterName"),
                                dcc.Dropdown(
                                    list(aggregation_options.keys()),
                                    list(aggregation_options.keys())[2],
                                    id="aggregation-filter",
                                ),
                            ],
                            className="eventFilter",
                        ),
                        html.Div(
                            [
                                dcc.Markdown("Dates", className="filterName"),
                                dcc.DatePickerRange(
                                    datetime(day=1, month=10, year=2023),
                                    datetime(day=31, month=12, year=2023),
                                    id="event-date-range",
                                ),
                            ],
                            className="eventFilter",
                        ),
                    ],
                    className="eventFilterGroup",
                ),
            ],
            className="eventFilters",
        ),
        dcc.Graph(id="event-graph"),

        html.Div(
            DataTable(
                id='event-table',
                columns=[{"name": i, "id": i} for i in ["Metric", "Value"]],
                data=[],
                # Styling for the DataTable
                style_table={'margin-left': 'auto', 'margin-right': 'auto', 'width': '50%'},
                style_header={
                    'backgroundColor': 'rgb(5, 191, 252)',
                    'fontWeight': 'bold',
                    'color': 'black'
                },
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'border': '1px solid blue'
                },
            ),
            style={'textAlign': 'center'}
        ),
    ],

    className="mainContainer",
)

@callback(
    Output("event-graph", "figure"),
    Input("interval-component", "n_intervals"),
    Input("location-filter", "value"),
    Input("event-filter", "value"),
    Input("event-date-range", "start_date"),
    Input("event-date-range", "end_date"),
    Input("aggregation-filter", "value"),
)
def update_event_graph(n, location, event, start_date, end_date, aggregation):
    df = pd.read_sql(
        f"""
            select ts, label as event
            from events
            where dev_id='{dev_map[location]}'
            and label='{event}';
        """,
        db_connection,
    )

    if len(df) != 0:
        df = (
            df.set_index("ts")
            .resample(aggregation_options[aggregation])
            .count()
            .loc[start_date:end_date]
            .reset_index()
        )
    else:
        df = pd.DataFrame({'ts': [None], 'event': [None]})

    fig = px.scatter(
        df,
        x="ts",
        y="event",
        title=f"Detection count of {event} in {location} aggregated by {aggregation}",
    )
    fig.update_traces(mode='lines+markers', line_shape='linear')

    return fig


@callback(
    Output('event-table', 'data'),
    Input("interval-component", "n_intervals"),
    Input("location-filter", "value"),
    Input("event-filter", "value"),
    Input("event-date-range", "start_date"),
    Input("event-date-range", "end_date"),
    Input("aggregation-filter", "value"),
)
def update_event_table(n, location, event, start_date, end_date, aggregation):
    df = pd.read_sql(
        f"""
        select ts, label as event
        from events
        where dev_id='{dev_map[location]}'
        and label='{event}'
        and ts between '{start_date}' and '{end_date}';
        """,
        db_connection,
    )
    if df.empty:
        return []
    
    total_events = len(df)
    df = df.set_index("ts").resample(aggregation_options[aggregation]).count()
    avg_events_per_time_unit = df.event.mean()
    max_events_per_time_unit = df.event.max()
    min_events_per_time_unit = df.event.min()
    std_deviation = df.event.std()

    table_data = [
        {'Metric': 'Total Number of Events', 'Value': total_events},
        {'Metric': f'Average Events per {aggregation}', 'Value': f'{avg_events_per_time_unit:.2f}'},
        {'Metric': f'Maximum Events in a {aggregation}', 'Value': f'{max_events_per_time_unit:.2f}'},
        {'Metric': f'Minimum Events in a {aggregation}', 'Value': f'{min_events_per_time_unit:.2f}'},
        {'Metric': f'Standard Deviation', 'Value': f'{std_deviation:.2f}'}
    ]

    return table_data

if __name__ == "__main__":
    app.run(debug=True)
