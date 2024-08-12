document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('question-form');
    const outputDiv = document.getElementById('questions-output');
    const loader = document.getElementById('loader');
    const questionsContent = document.getElementById('questions-content');
    debugger;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
debugger;
        const jobDescription = document.getElementById('job-description').value;

        // Show loader
        loader.style.display = 'block';
        questionsContent.innerHTML = '';

        try {
            const response = await fetch('http://127.0.0.1:8000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    description: jobDescription
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate questions.');
            }

            const data = await response.json();

            // Process and display the questions
            let html = '';
            if (data.questions) {
                html = `<pre>${data.questions}</pre>`;
            } else {
                html = '<p>No questions generated.</p>';
            }

            questionsContent.innerHTML = html;
        } catch (error) {
            questionsContent.innerHTML = `<p>Error: ${error.message}</p>`;
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });
});
