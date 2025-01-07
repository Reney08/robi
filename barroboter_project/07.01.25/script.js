document.addEventListener('DOMContentLoaded', function() {
    // Read the embedded JSON data
    const positionsData = document.getElementById('positions-data').textContent;
    const positions = JSON.parse(positionsData);

    const positionButtonsContainer = document.getElementById('position-buttons');

    for (const [pos, steps] of Object.entries(positions)) {
        const button = document.createElement('button');
        button.innerText = pos;
        button.onclick = () => moveToPosition(pos);
        positionButtonsContainer.appendChild(button);
    }
});

function moveToPosition(position) {
    fetch('/move_to_position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ position: position })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('step_count').innerText = data.step_count;
    });
}
