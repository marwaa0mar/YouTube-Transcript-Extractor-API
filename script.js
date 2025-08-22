// script.js
document.getElementById('submitBtn').addEventListener('click', async function() {
    const input = document.getElementById('inputField').value;
    const loadingIndicator = document.getElementById('loadingIndicator');
    const responseOutput = document.getElementById('responseOutput');

    if (!input) {
        responseOutput.textContent = 'Please enter a query.';
        return;
    }

    loadingIndicator.style.display = 'block';
    responseOutput.textContent = '';

    try {
        // Send input as query parameter
        const url = `https://0bdcc47e4e39.ngrok-free.app/app-info/dQw4w9WgXcQ?query=${encodeURIComponent(input)}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        responseOutput.textContent = `Response: ${JSON.stringify(data)}`;
    } catch (error) {
        responseOutput.textContent = `Error: ${error.message}`;
    } finally {
        loadingIndicator.style.display = 'none';
    }
});