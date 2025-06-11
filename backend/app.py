from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- IMPORTANTE
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary, PULP_CBC_CMD

app = Flask(__name__)
CORS(app)

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json['puzzle']
    ROWS = COLS = VALS = range(9)

    prob = LpProblem("Sudoku_Solver", LpMinimize)
    choices = [[[LpVariable(f"Choice_{v}_{r}_{c}", cat=LpBinary) for c in COLS] for r in ROWS] for v in VALS]
    prob += 0

    for r in ROWS:
        for c in COLS:
            prob += lpSum([choices[v][r][c] for v in VALS]) == 1

    for r in ROWS:
        for v in VALS:
            prob += lpSum([choices[v][r][c] for c in COLS]) == 1

    for c in COLS:
        for v in VALS:
            prob += lpSum([choices[v][r][c] for r in ROWS]) == 1

    for v in VALS:
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                prob += lpSum([choices[v][r][c]
                               for r in range(br, br+3)
                               for c in range(bc, bc+3)]) == 1

    for r in ROWS:
        for c in COLS:
            val = data[r][c]
            if val != 0:
                prob += choices[val-1][r][c] == 1

    prob.solve(PULP_CBC_CMD(msg=False))

    solved_board = [[0 for _ in COLS] for _ in ROWS]
    for r in ROWS:
        for c in COLS:
            for v in VALS:
                if choices[v][r][c].value() == 1:
                    solved_board[r][c] = v + 1

    return jsonify({'board': solved_board})

if __name__ == '__main__':
    app.run(debug=True)
