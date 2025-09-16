from flask import Flask, render_template, request, redirect
import pyodbc

app = Flask(__name__)


db_config = {
    "server": r"MOBILITY_028115\SQLEXPRESS03",
    "database": "cadastro_db",
    "trusted_connection": "yes",
    "driver": "{ODBC Driver 17 for SQL Server}"
}

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={db_config['driver']};"
        f"SERVER={db_config['server']};"
        f"DATABASE={db_config['database']};"
        f"Trusted_Connection={db_config['trusted_connection']};"
    )
    return conn

def init_db():
    conn = pyodbc.connect(
        f"DRIVER={db_config['driver']};"
        f"SERVER={db_config['server']};"
        f"Trusted_Connection={db_config['trusted_connection']};"
    )
    cursor = conn.cursor()
    cursor.execute("IF DB_ID('cadastro_db') IS NULL CREATE DATABASE cadastro_db;")
    conn.commit()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    IF OBJECT_ID('usuarios', 'U') IS NULL
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(100) NOT NULL,
        sobrenome NVARCHAR(100) NOT NULL,
        email NVARCHAR(150) NOT NULL,
        idade INT,
        imc FLOAT,
        treina NVARCHAR(10),
        tempo_treino NVARCHAR(100)
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["POST"])
def cadastro():
    nome = request.form["nome"]
    sobrenome = request.form["sobrenome"]
    email = request.form["email"]
    idade = request.form["idade"]
    imc = request.form["imc"]
    treina = request.form["treina"]
    tempo_treino = request.form["tempo_treino"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nome, sobrenome, email, idade, imc, treina, tempo_treino)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, sobrenome, email, idade, imc, treina, tempo_treino))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
