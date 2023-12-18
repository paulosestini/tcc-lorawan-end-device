# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
import dotenv
from datetime import datetime, timedelta

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
event_options = ["cow", "person", "car", "dog", "danger", "event"]
aggregation_options = {"Minute": "T", "Hour": "h", "Day": "d", "Week": "w", "Month": "m"}

app.layout = html.Div(
    [
        dcc.Interval(
            id='interval-component',
            interval=2*1000,  # in milliseconds, e.g., 2*1000 for 2 seconds
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

                html.Div([
                    html.H3("Alerta"),
                    dcc.Graph(id='circle-graph', style={'height': '50px', 'width': '50px'}),
                    dcc.Interval(
                        id='circle-interval-component',
                        interval=1*1000,  # in milliseconds
                        n_intervals=0
                    ),
                    ]),
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
            and label='{event}'
            and ts >= '{start_date.split('T')[0]} 00:00'
            and ts <= '{end_date.split('T')[0]} 23:59'
            ;
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

@app.callback(
    Output('circle-graph', 'figure'),
    Input('circle-interval-component', 'n_intervals'),
    Input("location-filter", "value"),
)
def update_circle_color(n, location):
    query = f"""
        select ts, label as event
        from events
        where dev_id='{dev_map[location]}'
        and label='danger'
        and ts >= '{datetime.utcnow() - timedelta(seconds=5)}'
        ;
        """
    
    df = pd.read_sql(
        query,
        db_connection,
    )


    color = 'red' if not df.empty else 'green'

    fig = go.Figure(data=[go.Scatter(
        x=[0.5],
        y=[0.5],
        mode='markers',
        marker=dict(size=50, color=color)
    )])

    fig.update_layout(
        xaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

if __name__ == "__main__":
    app.run(debug=True)
