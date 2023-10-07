# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
import dotenv
from datetime import datetime

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
event_options = ["cow", "person", "car", "dog"]
aggregation_options = {"Hour": "h", "Day": "d", "Week": "w", "Month": "m"}

app.layout = html.Div(
    [
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
                                    location_options[0],
                                    id="location-filter",
                                ),
                            ],
                            className="eventFilter",
                        ),
                        html.Div(
                            [
                                dcc.Markdown("Event", className="filterName"),
                                dcc.Dropdown(
                                    event_options, event_options[0], id="event-filter"
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
                                    list(aggregation_options.keys())[0],
                                    id="aggregation-filter",
                                ),
                            ],
                            className="eventFilter",
                        ),
                        html.Div(
                            [
                                dcc.Markdown("Dates", className="filterName"),
                                dcc.DatePickerRange(
                                    datetime(day=1, month=1, year=2022),
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
    ],
    className="mainContainer",
)


@callback(
    Output("event-graph", "figure"),
    Input("location-filter", "value"),
    Input("event-filter", "value"),
    Input("event-date-range", "start_date"),
    Input("event-date-range", "end_date"),
    Input("aggregation-filter", "value"),
)
def update_event_graph(location, event, start_date, end_date, aggregation):
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

    fig = px.line(
        df,
        x="ts",
        y="event",
        title=f"Detection count of {event} in {location} aggregated by {aggregation}",
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
