import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import dotenv

dotenv.load_dotenv()

db_connection = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# Header
# ID dev_id Timestamp label

dev_id_probs = {"aaaaaaaaaaaaaaaa": 1}
label_probs = {"car": 0.4, "person": 0.3, "dog": 0.1, "cow": 0.2}

dates = pd.date_range("2022-01-01 00:00", "2022-12-31 23:00", freq="d")

data = pd.DataFrame()

for date in dates:
    n_samples = 20
    samples = {
        "dev_id": np.random.choice(
            list(dev_id_probs.keys()), size=n_samples, p=list(dev_id_probs.values())
        ),
        "label": np.random.choice(
            list(label_probs.keys()), size=n_samples, p=list(label_probs.values())
        ),
        "ts": [
            date.replace(
                hour=np.random.randint(0, 24),
                minute=np.random.randint(0, 60),
                second=np.random.randint(0, 60),
            ).isoformat()
            for _ in range(n_samples)
        ],
    }
    samples = pd.DataFrame(samples)
    data = pd.concat([data, samples])
data["ts"] = data["ts"] + ".293502+00:00"
data = data.reset_index(drop=True)

print(data)
data.to_sql(name="events", con=db_connection, if_exists="append", index=False)
