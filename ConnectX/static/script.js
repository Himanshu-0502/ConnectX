const boardElement = document.getElementById('game-board');
const statusElement = document.getElementById('status');
const resetButton = document.getElementById('reset-button');
let board = Array.from({ length: 7 }, () => Array(7).fill(0));
let turn = 0;
let gameOver = false;

function createBoard() {
    boardElement.innerHTML = ''; // Clear the existing board
    for (let r = 0; r < 7; r++) {
        for (let c = 0; c < 7; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell', 'empty');
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener('click', handleCellClick);
            boardElement.appendChild(cell);
        }
    }
}

function handleCellClick(e) {
    if (gameOver || turn !== 0) return;
    const col = e.target.dataset.col;
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ col: parseInt(col) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            board = data.board;
            turn = data.turn;
            updateBoard();
            if (data.winner !== undefined) {
                statusElement.textContent = `You Win!`;
                gameOver = true;
            } else if (turn === 1) {
                aiMove();
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function aiMove() {
    fetch('/ai_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            board = data.board;
            turn = data.turn;
            updateBoard();
            if (data.winner !== undefined) {
                statusElement.textContent = `AI Wins!`;
                gameOver = true;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateBoard() {
    board.forEach((row, rIdx) => {
        row.forEach((cell, cIdx) => {
            const cellElement = document.querySelector(`[data-row='${rIdx}'][data-col='${cIdx}']`);
            cellElement.classList.remove('red', 'yellow', 'empty');
            if (cell === 1) {
                cellElement.classList.add('red');
            } else if (cell === 2) {
                cellElement.classList.add('yellow');
            } else {
                cellElement.classList.add('empty');
            }
        });
    });
}

function resetGame() {
    fetch('/reset', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        board = data.board;
        turn = data.turn;
        gameOver = false;
        statusElement.textContent = 'Status';
        updateBoard();
    })
    .catch(error => console.error('Error:', error));
}

resetButton.addEventListener('click', resetGame);

createBoard();