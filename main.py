import os
import sqlite3
from flask import Flask, render_template_string, request, jsonify

# ==============================================================================
# CORES ANSI (Para o Terminal)
# ==============================================================================
VERDE = "\033[92m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
VERMELHO = "\033[91m"
RESET = "\033[0m"

# ==============================================================================
# 1. GESTÃO DO BANCO DE DADOS (SQLite)
# ==============================================================================

DB_NAME = "filmes.db"

def conectar_bd():
    """Conecta ao banco de dados e cria a tabela caso não exista."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            plataforma TEXT NOT NULL,
            genero TEXT NOT NULL,
            concluido INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn

# ==============================================================================
# 2. SISTEMA EM TERMINAL (CLI - PROMPT DE COMANDO)
# ==============================================================================

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def cli_cadastrar_filme():
    limpar_tela()
    print(f"{AZUL}=== CADASTRO DE FILME ==={RESET}")
    titulo = input("Título do filme: ").strip()
    plataforma = input("Onde assistir (ex: Netflix, Cinema, Prime Video): ").strip()
    genero = input("Gênero (ex: Ação, Drama, Sci-Fi): ").strip()
    
    concluido_in = input("Já foi assistido? (s/n): ").strip().lower()
    concluido = 1 if concluido_in == 's' else 0

    if not titulo or not plataforma or not genero:
        print(f"\n{VERMELHO}[!] Todos os campos são obrigatórios.{RESET}")
        input("\nPressione ENTER para voltar ao menu...")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO filmes (titulo, plataforma, genero, concluido) VALUES (?, ?, ?, ?)",
        (titulo, plataforma, genero, concluido)
    )
    conn.commit()
    conn.close()
    
    print(f"\n{VERDE}Filme cadastrado com sucesso!{RESET}")
    input("\nPressione ENTER para voltar ao menu...")

def cli_listar_filmes():
    limpar_tela()
    print(f"{AZUL}=== LISTA DE FILMES CADASTRADOS ==={RESET}")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma, genero, concluido FROM filmes")
    filmes = cursor.fetchall()
    conn.close()

    if not filmes:
        print(f"{VERMELHO}Nenhum filme cadastrado ainda.{RESET}")
    else:
        for f in filmes:
            status = f"{VERDE}Assistido{RESET}" if f['concluido'] == 1 else f"{AMARELO}Pendente{RESET}"
            print(f"ID: {f['id']} | Título: {f['titulo']} | Onde assistir: {f['plataforma']} | Gênero: {f['genero']} | Status: {status}")
    
    input("\nPressione ENTER para voltar ao menu...")

def cli_pesquisar_filmes():
    limpar_tela()
    print(f"{AZUL}=== PESQUISAR FILMES ==={RESET}")
    termo = input("Digite o título ou parte dele: ").strip()
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma, genero, concluido FROM filmes WHERE titulo LIKE ?", (f"%{termo}%",))
    resultados = cursor.fetchall()
    conn.close()

    print("\n--- Resultados Encontrados ---")
    if not resultados:
        print(f"{VERMELHO}Nenhum filme encontrado com esse termo.{RESET}")
    else:
        for f in resultados:
            status = f"{VERDE}Assistido{RESET}" if f['concluido'] == 1 else f"{AMARELO}Pendente{RESET}"
            print(f"ID: {f['id']} | Título: {f['titulo']} | Onde assistir: {f['plataforma']} | Gênero: {f['genero']} | Status: {status}")
            
    input("\nPressione ENTER para voltar ao menu...")

def cli_marcar_concluido():
    limpar_tela()
    print(f"{AZUL}=== MARCAR FILME COMO ASSISTIDO ==={RESET}")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma FROM filmes WHERE concluido = 0")
    pendentes = cursor.fetchall()

    if not pendentes:
        print(f"{VERMELHO}Não há filmes pendentes para assistir.{RESET}")
        conn.close()
        input("\nPressione ENTER para voltar ao menu...")
        return

    for f in pendentes:
        print(f"ID: {f['id']} | {f['titulo']} ({f['plataforma']})")
        
    try:
        filme_id = int(input("\nDigite o ID do filme que deseja marcar como assistido: "))
        cursor.execute("UPDATE filmes SET concluido = 1 WHERE id = ?", (filme_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"\n{VERDE}Status atualizado para ASSISTIDO com sucesso!{RESET}")
        else:
            print(f"\n{VERMELHO}ID não encontrado.{RESET}")
    except ValueError:
        print(f"\n{VERMELHO}Entrada inválida! Digite apenas números.{RESET}")
    
    conn.close()
    input("\nPressione ENTER para voltar ao menu...")

def cli_gerar_estatisticas():
    limpar_tela()
    print(f"{AZUL}=== ESTATÍSTICAS DO CATÁLOGO ==={RESET}")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM filmes")
    total = cursor.fetchone()[0]

    if total == 0:
        print(f"{VERMELHO}Cadastre alguns filmes primeiro para gerar estatísticas.{RESET}")
    else:
        cursor.execute("SELECT COUNT(*) FROM filmes WHERE concluido = 1")
        concluidos = cursor.fetchone()[0]
        pendentes = total - concluidos
        porcentagem = (concluidos / total) * 100

        cursor.execute("SELECT genero, COUNT(*) as qtd FROM filmes GROUP BY genero")
        generos = cursor.fetchall()
        
        print(f"Total de filmes cadastrados: {total}")
        print(f"Filmes assistidos: {VERDE}{concluidos}{RESET} ({porcentagem:.1f}%)")
        print(f"Filmes pendentes: {AMARELO}{pendentes}{RESET}")
        print("\nDistribuição por Gênero:")
        for gen in generos:
            print(f"  - {gen['genero']}: {gen['qtd']} filme(s)")

    conn.close()
    input("\nPressione ENTER para voltar ao menu...")

def executar_cli():
    while True:
        limpar_tela()
        print(f"{AZUL}=============================={RESET}")
        print(f"{VERDE}   CATÁLOGO DE FILMES (CLI)   {RESET}")
        print(f"{AZUL}=============================={RESET}")
        print("1. Cadastrar Filme")
        print("2. Listar Todos os Filmes")
        print("3. Pesquisar Filme")
        print("4. Marcar Filme como Assistido")
        print("5. Gerar Estatísticas")
        print("6. Voltar ao Menu Principal")
        print(f"{AZUL}=============================={RESET}")
        
        opcao = input("Escolha uma opção (1-6): ").strip()
        
        if opcao == '1':
            cli_cadastrar_filme()
        elif opcao == '2':
            cli_listar_filmes()
        elif opcao == '3':
            cli_pesquisar_filmes()
        elif opcao == '4':
            cli_marcar_concluido()
        elif opcao == '5':
            cli_gerar_estatisticas()
        elif opcao == '6':
            break

# ==============================================================================
# 3. SISTEMA WEB (FLASK + HTML EMBUTIDO)
# ==============================================================================

app = Flask(__name__)

HTML_WEB = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Filmes Python Web</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #0f0c1b; color: #ffffff; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #ff79c6; margin-bottom: 20px; text-shadow: 0 0 10px rgba(255,121,198,0.3); }
        h2 { color: #bd93f9; margin-bottom: 15px; }
        .card { background-color: #181528; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #2a2440; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .form-group { display: flex; gap: 10px; flex-wrap: wrap; }
        input, button { padding: 12px; border-radius: 6px; border: 1px solid #362f54; background: #0f0c1b; color: #50fa7b; outline: none; }
        input:focus { border-color: #ff79c6; }
        input[type="text"] { flex: 1; }
        button { background: linear-gradient(135deg, #bd93f9 0%, #ff79c6 100%); color: #0f0c1b; font-weight: bold; cursor: pointer; border: none; transition: transform 0.2s, opacity 0.2s; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        .grid-filmes { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }
        .filme-item { background: #0f0c1b; padding: 15px; border-radius: 8px; border-left: 5px solid #ff5555; transition: transform 0.2s; }
        .filme-item:hover { transform: translateY(-2px); }
        .filme-item.concluido { border-left-color: #50fa7b; }
        .filme-item h3 { color: #8be9fd; margin-bottom: 8px; }
        .filme-item p { color: #f1fa8c; font-size: 0.9em; margin-bottom: 4px; }
        .filme-item button { margin-top: 10px; width: 100%; padding: 8px; font-size: 0.85em; }
        .stats-box { display: flex; justify-content: space-around; text-align: center; }
        .stat-item { background: #0f0c1b; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; border: 1px solid #2a2440; }
        .stat-item p { color: #bd93f9; }
        .stat-item span { font-size: 1.8em; color: #ff79c6; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <h1>Catálogo de Filmes (Python Web)</h1>
    <div class="card">
        <h2>Cadastrar Filme</h2>
        <form id="form-cadastrar" class="form-group">
            <input type="text" id="titulo" placeholder="Título" required>
            <input type="text" id="plataforma" placeholder="Onde assistir (ex: Netflix)" required>
            <input type="text" id="genero" placeholder="Gênero" required>
            <button type="submit">Cadastrar</button>
        </form>
    </div>
    <div class="card">
        <h2>Estatísticas</h2>
        <div class="stats-box">
            <div class="stat-item"><p>Total</p><span id="stat-total">0</span></div>
            <div class="stat-item"><p>Assistidos</p><span id="stat-concluidos">0</span></div>
            <div class="stat-item"><p>Pendentes</p><span id="stat-pendentes">0</span></div>
        </div>
    </div>
    <div class="card">
        <h2>Meus Filmes</h2>
        <input type="text" id="pesquisa" placeholder="Pesquisar..." style="width: 100%; margin-bottom: 10px;" oninput="carregarFilmes()">
        <div id="grid-filmes" class="grid-filmes"></div>
    </div>
</div>
<script>
    async function carregarFilmes() {
        const termo = document.getElementById('pesquisa').value;
        const res = await fetch(`/api/filmes?pesquisa=${encodeURIComponent(termo)}`);
        const filmes = await res.json();
        
        const grid = document.getElementById('grid-filmes');
        grid.innerHTML = '';
        filmes.forEach(f => {
            const item = document.createElement('div');
            item.className = `filme-item ${f.concluido ? 'concluido' : ''}`;
            item.innerHTML = `
                <h3>${f.titulo}</h3>
                <p>Onde assistir: ${f.plataforma}</p>
                <p>Gênero: ${f.genero}</p>
                <p>Status: ${f.concluido ? 'Assistido' : 'Pendente'}</p>
                <button onclick="alternarStatus(${f.id})">${f.concluido ? 'Marcar Pendente' : 'Marcar Assistido'}</button>
            `;
            grid.appendChild(item);
        });
        carregarEstatisticas();
    }
    async function carregarEstatisticas() {
        const res = await fetch('/api/estatisticas');
        const stats = await res.json();
        document.getElementById('stat-total').innerText = stats.total;
        document.getElementById('stat-concluidos').innerText = stats.concluidos;
        document.getElementById('stat-pendentes').innerText = stats.pendentes;
    }
    document.getElementById('form-cadastrar').addEventListener('submit', async (e) => {
        e.preventDefault();
        const titulo = document.getElementById('titulo').value;
        const plataforma = document.getElementById('plataforma').value;
        const genero = document.getElementById('genero').value;
        await fetch('/api/filmes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, plataforma, genero })
        });
        document.getElementById('form-cadastrar').reset();
        carregarFilmes();
    });
    async function alternarStatus(id) {
        await fetch(`/api/filmes/${id}/status`, { method: 'PUT' });
        carregarFilmes();
    }
    carregarFilmes();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_WEB)

@app.route('/api/filmes', methods=['GET'])
def api_listar_filmes():
    termo = request.args.get('pesquisa', '')
    conn = conectar_bd()
    cursor = conn.cursor()
    if termo:
        cursor.execute("SELECT * FROM filmes WHERE titulo LIKE ?", (f"%{termo}%",))
    else:
        cursor.execute("SELECT * FROM filmes")
    filmes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(filmes)

@app.route('/api/filmes', methods=['POST'])
def api_cadastrar_filme():
    dados = request.get_json()
    titulo = dados.get('titulo')
    plataforma = dados.get('plataforma')
    genero = dados.get('genero')
    if not titulo or not plataforma or not genero:
        return jsonify({'erro': 'Dados incompletos'}), 400

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO filmes (titulo, plataforma, genero, concluido) VALUES (?, ?, ?, 0)",
        (titulo, plataforma, genero)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado com sucesso!'}), 201

@app.route('/api/filmes/<int:filme_id>/status', methods=['PUT'])
def api_alterar_status(filme_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE filmes SET concluido = NOT concluido WHERE id = ?", (filme_id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Status alterado com sucesso!'})

@app.route('/api/estatisticas', methods=['GET'])
def api_estatisticas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM filmes")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM filmes WHERE concluido = 1")
    concluidos = cursor.fetchone()[0]
    pendentes = total - concluidos

    cursor.execute("SELECT genero, COUNT(*) as qtd FROM filmes GROUP BY genero")
    generos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({
        'total': total,
        'concluidos': concluidos,
        'pendentes': pendentes,
        'generos': generos
    })

def executar_web():
    limpar_tela()
    print(f"{AZUL}=========================================={RESET}")
    print(f"{VERDE} INICIANDO SERVIDOR WEB (FLASK)...        {RESET}")
    print(" Acesse no navegador: http://127.0.0.1:5000")
    print(" Pressione CTRL+C no terminal para parar. ")
    print(f"{AZUL}=========================================={RESET}")
    app.run(debug=True, use_reloader=False)

# ==============================================================================
# 4. MENU PRINCIPAL
# ==============================================================================

if __name__ == '__main__':
    conectar_bd()
    while True:
        limpar_tela()
        print(f"{AZUL}=========================================={RESET}")
        print(f"{VERDE}     SISTEMA DE CATÁLOGO DE FILMES        {RESET}")
        print(f"{AZUL}=========================================={RESET}")
        print("1. Executar versão Terminal (Prompt/CLI)")
        print("2. Executar versão Aplicação WEB (Flask)")
        print("3. Sair")
        print(f"{AZUL}=========================================={RESET}")
        
        escolha = input("Escolha uma opção (1-3): ").strip()
        
        if escolha == '1':
            executar_cli()
        elif escolha == '2':
            executar_web()
        elif escolha == '3':
            print("\nEncerrando sistema...")
            break