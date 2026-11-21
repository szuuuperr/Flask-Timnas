"""Studi kasus: Dashboard nilai mahasiswa dengan Flask + Chart.js.

Jalankan:
    pip install -r requirements.txt
    python app.py
lalu buka http://127.0.0.1:5000
"""
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
df = pd.read_csv("data/nilai.csv")


def huruf(n):
    """Konversi nilai angka ke nilai huruf."""
    if n >= 85:
        return "A"
    if n >= 70:
        return "B"
    if n >= 55:
        return "C"
    if n >= 40:
        return "D"
    return "E"


df["grade"] = df["nilai"].apply(huruf)


def filter_data():
    """Ambil filter ?angkatan=2022 dari URL (opsional)."""
    data = df
    angkatan = request.args.get("angkatan", type=int)
    if angkatan:
        data = data[data["angkatan"] == angkatan]
    return data


@app.route("/")
def dashboard():
    daftar_angkatan = sorted(df["angkatan"].unique().tolist())
    return render_template("dashboard.html", daftar_angkatan=daftar_angkatan)


@app.route("/api/ringkasan")
def ringkasan():
    data = filter_data()
    return jsonify(
        mahasiswa=int(data["nim"].nunique()),
        rata_rata=round(float(data["nilai"].mean()), 1),
        lulus=round(float((data["nilai"] >= 55).mean() * 100), 1),
    )


@app.route("/api/rata-prodi")
def rata_prodi():
    hasil = filter_data().groupby("prodi")["nilai"].mean().round(1)
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())


@app.route("/api/distribusi-grade")
def distribusi_grade():
    hasil = filter_data()["grade"].value_counts().reindex(list("ABCDE"), fill_value=0)
    return jsonify(labels=hasil.index.tolist(), data=hasil.tolist())


@app.route("/api/tren-semester")
def tren_semester():
    hasil = filter_data().groupby(["semester", "prodi"])["nilai"].mean().round(1).unstack()
    return jsonify(
        labels=[f"Semester {s}" for s in hasil.index],
        datasets=[{"label": p, "data": hasil[p].tolist()} for p in hasil.columns],
    )


if __name__ == "__main__":
    app.run(debug=True)
