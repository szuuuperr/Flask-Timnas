"""Dashboard sederhana dataset Timnas (X/Twitter) dengan Flask + Chart.js.

Jalankan:
    pip install -r requirements.txt
    python app.py
lalu buka http://127.0.0.1:5000
"""
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

df = pd.read_csv("data/dataset_timnas.csv")
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["tanggal"] = df["created_at"].dt.date.astype(str)
for col in ["like_count", "repost_count", "reply_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)


def filter_data():
    """Filter data berdasarkan ?kata_kunci=... (opsional)."""
    data = df
    kata = request.args.get("kata_kunci", "").strip().lower()
    if kata:
        data = data[data["kata_kunci"].str.lower() == kata]
    return data


@app.route("/")
def dashboard():
    daftar_kata = sorted(df["kata_kunci"].dropna().unique().tolist())
    return render_template("dashboard.html", daftar_kata=daftar_kata)


@app.route("/api/ringkasan")
def ringkasan():
    data = filter_data()
    total = len(data)
    return jsonify(
        total_post=total,
        total_like=int(data["like_count"].sum()) if total else 0,
        rata_like=round(float(data["like_count"].mean()), 1) if total else 0,
        total_reply=int(data["reply_count"].sum()) if total else 0,
    )


@app.route("/api/per-kata-kunci")
def per_kata_kunci():
    hasil = (
        filter_data()["kata_kunci"]
        .value_counts()
        .sort_values(ascending=False)
    )
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())


@app.route("/api/tren-tanggal")
def tren_tanggal():
    hasil = (
        filter_data()
        .groupby("tanggal")
        .size()
        .sort_index()
    )
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())


@app.route("/api/top-post")
def top_post():
    data = filter_data().nlargest(5, "like_count")[
        ["text_clean", "like_count", "reply_count", "repost_count", "kata_kunci", "tanggal"]
    ]
    return jsonify(data=data.fillna("").to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)
