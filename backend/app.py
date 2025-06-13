# Importa as bibliotecas necessárias
from flask import Flask, request, jsonify           # Flask para criar a API web
from flask_cors import CORS                         # CORS para permitir requisições de diferentes origens (ex: do front-end)
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary, PULP_CBC_CMD  # PuLP para resolver o problema de otimização (Sudoku)

# Inicializa o aplicativo Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir chamadas de outros domínios (útil para comunicação com o front-end)

# Define a rota da API que irá resolver o Sudoku
@app.route('/solve', methods=['POST'])
def solve():
    # Recebe os dados enviados no corpo da requisição (JSON) e extrai o tabuleiro (puzzle)
    data = request.json['puzzle']
    
    # Define os índices para linhas, colunas e valores (de 0 a 8)
    ROWS = COLS = VALS = range(9)

    # Cria um problema de programação linear inteiro (LP), com objetivo arbitrário (não importa para resolver Sudoku)
    prob = LpProblem("Sudoku_Solver", LpMinimize)

    # Cria variáveis binárias: choices[v][r][c] = 1 se valor v está na posição (r, c)
    choices = [[[LpVariable(f"Choice_{v}_{r}_{c}", cat=LpBinary)
                 for c in COLS] for r in ROWS] for v in VALS]

    # Função objetivo: zero (não há minimização real, apenas restrições)
    prob += 0

    # Restrição 1: Cada célula deve ter exatamente um valor
    for r in ROWS:
        for c in COLS:
            prob += lpSum([choices[v][r][c] for v in VALS]) == 1

    # Restrição 2: Cada valor aparece exatamente uma vez em cada linha
    for r in ROWS:
        for v in VALS:
            prob += lpSum([choices[v][r][c] for c in COLS]) == 1

    # Restrição 3: Cada valor aparece exatamente uma vez em cada coluna
    for c in COLS:
        for v in VALS:
            prob += lpSum([choices[v][r][c] for r in ROWS]) == 1

    # Restrição 4: Cada valor aparece exatamente uma vez em cada subgrade 3x3
    for v in VALS:
        for br in range(0, 9, 3):         # Linhas dos blocos
            for bc in range(0, 9, 3):     # Colunas dos blocos
                prob += lpSum([choices[v][r][c]
                               for r in range(br, br+3)
                               for c in range(bc, bc+3)]) == 1

    # Adiciona as restrições das pistas já preenchidas no tabuleiro (valores fixos)
    for r in ROWS:
        for c in COLS:
            val = data[r][c]
            if val != 0:
                # Garante que a célula (r, c) terá obrigatoriamente o valor especificado
                prob += choices[val-1][r][c] == 1

    # Resolve o problema usando o solucionador CBC (incluso com PuLP)
    prob.solve(PULP_CBC_CMD(msg=False))  # msg=False evita prints no terminal

    # Constrói o tabuleiro solucionado com os valores encontrados
    solved_board = [[0 for _ in COLS] for _ in ROWS]
    for r in ROWS:
        for c in COLS:
            for v in VALS:
                if choices[v][r][c].value() == 1:
                    solved_board[r][c] = v + 1  # Corrige índice: valores vão de 1 a 9

    # Retorna o tabuleiro resolvido como JSON
    return jsonify({'board': solved_board})

# Executa o servidor Flask localmente na porta 3001
if __name__ == '__main__':
    app.run(debug=True, port=3001)
