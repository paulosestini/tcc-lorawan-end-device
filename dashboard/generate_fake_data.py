import pandas as pd
import numpy as np

# Header
# ID Location Timestamp Event

location_probs = {"Road 1": 0.2, "Road 2": 0.3, "Road 3": 0.5}
event_probs = {"car": 0.4, "person": 0.3, "dog": 0.1, "cow": 0.2}

dates = pd.date_range("2022-01-01 00:00", "2022-12-31 23:00", freq="d")

data = pd.DataFrame()

for date in dates:
    n_samples = 100
    samples = {
        "location": np.random.choice(
            list(location_probs.keys()), size=n_samples, p=list(location_probs.values())
        ),
        "event": np.random.choice(
            list(event_probs.keys()), size=n_samples, p=list(event_probs.values())
        ),
        "timestamp": [
            date.replace(
                hour=np.random.randint(0, 24),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60),
            )
            for _ in range(n_samples)
        ],
    }
    samples = pd.DataFrame(samples)
    data = pd.concat([data, samples])

data = data.reset_index(drop=True)
data.to_csv("fake_events.csv")
