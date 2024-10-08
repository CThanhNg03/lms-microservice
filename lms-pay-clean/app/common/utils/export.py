import io
from typing import List
import pandas as pd


def to_df(data: List[object], exclude: List[str] = []):
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame([item.__dict__ for item in data])
    df.drop('_sa_instance_state', axis=1, errors='ignore', inplace=True)
    for col in exclude:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True, errors='ignore')
    return df

def export_to_file(data: List[object], file_type: str, exclude: List[str] = []):
    df = to_df(data, exclude = exclude)
    stream = io.BytesIO()
    if file_type == 'csv':
        mediatype = 'text/csv'
        df.to_csv(stream, index=False)
    elif file_type == 'xlsx':
        mediatype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        with pd.ExcelWriter(stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
    else:
        raise ValueError("Invalid file type")

    stream.seek(0)
    return {"content": stream, "media_type": mediatype}
    