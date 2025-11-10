from flask import Flask, render_template, request, redirect, session, url_for
import pyodbc

app = Flask(__name__)
app.secret_key = "troque_essa_chave_para_uma_secreta_e_segura"  # altere em produção

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
       
    nome = request.form.get("nome", "").strip()
    sobrenome = request.form.get("sobrenome", "").strip()
    email = request.form.get("email", "").strip()
    idade = request.form.get("idade") or None
    imc = request.form.get("imc") or None
    treina = request.form.get("treina", "")
    tempo_treino = request.form.get("tempo_treino", "")

    try:
        idade_val = int(idade) if idade not in (None, "") else None
    except:
        idade_val = None
    try:
        imc_val = float(imc) if imc not in (None, "") else None
    except:
        imc_val = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nome, sobrenome, email, idade, imc, treina, tempo_treino)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, sobrenome, email, idade_val, imc_val, treina, tempo_treino))
        conn.commit()
        conn.close()
    except Exception as e:
        
        return f"Erro ao salvar no banco: {e}", 500

    
    session['user_temp'] = {
        "nome": nome,
        "sobrenome": sobrenome,
        "email": email,
        "idade": idade_val,
        "imc": imc_val,
        "treina": treina,
        "tempo_treino": tempo_treino
    }

    
    return redirect(url_for('sucesso'))


@app.route("/sucesso")
def sucesso():
    
    user = session.get('user_temp', {})
    return render_template("success.html", user=user)


@app.route("/treino")
def treino():
    
    if 'user_temp' not in session:
        return redirect(url_for('index'))
    return render_template("treino.html")

@app.route("/gerar_treino", methods=["POST"])
def gerar_treino():
    if 'user_temp' not in session:
        return redirect(url_for('index'))

    dias = request.form.get("dias")
    try:
        dias_int = int(dias)
    except:
        dias_int = 3  # default seguro

    cronogramas = {
        2: [
            ("Dia 1", "Peito e Tríceps - 4 exercícios de 3 séries"),
            ("Dia 2", "Costas e Bíceps - 4 exercícios de 3 séries")
        ],
        3: [
            ("Dia 1", "Peito - 4 exercícios de 3 séries"),
            ("Dia 2", "Costas - 4 exercícios de 3 séries"),
            ("Dia 3", "Pernas - 5 exercícios de 4 séries")
        ],
        4: [
            ("Dia 1", "Peito - 4 exercícios de 3 séries"),
            ("Dia 2", "Costas - 4 exercícios de 3 séries"),
            ("Dia 3", "Pernas - 5 exercícios de 4 séries"),
            ("Dia 4", "Ombro e Braços - 4 exercícios de 3 séries")
        ],
        5: [
            ("Dia 1", "Peito - 4 exercícios de 3 séries"),
            ("Dia 2", "Costas - 4 exercícios de 3 séries"),
            ("Dia 3", "Pernas - 5 exercícios de 4 séries"),
            ("Dia 4", "Ombro - 4 exercícios de 3 séries"),
            ("Dia 5", "Core + Cardio leve - 20 minutos")
        ],
        6: [
            ("Dia 1", "Peito e Tríceps"),
            ("Dia 2", "Costas e Bíceps"),
            ("Dia 3", "Pernas"),
            ("Dia 4", "Ombros"),
            ("Dia 5", "Treino funcional/HIIT"),
            ("Dia 6", "Abdômen + Mobilidade")
        ]
    }

    plano = cronogramas.get(dias_int, cronogramas[3])
    user = session.get('user_temp', {})

    #-- nova funcionalidade: tempo para sair do sedentarismo 
    
    if dias_int <= 3:
        tempo_para_sair = "Estimativa: aproximadamente 2 meses para sair do sedentarismo."
    elif dias_int >= 5:
        tempo_para_sair = "Estimativa: aproximadamente 2 semanas para sair do sedentarismo."
    else:  # aqui entra o caso dias_int == 4
        tempo_para_sair = "Estimativa: aproximadamente 1 mês para sair do sedentarismo."

    return render_template(
        "resultado_treino.html",
        user=user,
        dias=dias_int,
        plano=plano,
        tempo_para_sair=tempo_para_sair
    )


if __name__ == "__main__":
    app.run(debug=True)



