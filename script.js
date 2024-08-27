document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('question-form');
    const outputDiv = document.getElementById('questions-output');
    const loader = document.getElementById('loader');
    const questionsContent = document.getElementById('questions-content');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const jobDescription = document.getElementById('job-description').value;

        // Show loader
        loader.style.display = 'block';
        questionsContent.innerHTML = '';

        try {
            // First, generate the questions
            const response = await fetch('http://localhost:9000/generate', {
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
                questionsContent.innerHTML = html;
                console.log('data.questions',data);
                
                // Prepare the questions data to be an array of objects
                const questionsArray = data.questions
                    .split('\n')
                    .filter(q => q.trim() !== '' && !q.includes(':'))  // Remove empty lines and category headings
                    .map(q => {
                        // Assuming difficulty is somehow derived or assigned
                        const difficulty = 'Easy';  // Example: 'Easy', 'Medium', 'Hard'
                        return { question: q.trim(), difficulty: difficulty };
                    });

                // console.log('Prepared questions array:', questionsArray);  // Log to check format

                // Save the generated questions to the database
                await saveQuestionsToDatabase('12323',questionsArray,);
            } else {
                html = '<p>No questions generated.</p>';
                questionsContent.innerHTML = html;
            }
        } catch (error) {
            questionsContent.innerHTML = `<p>Error: ${error.message}</p>`;
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    async function saveQuestionsToDatabase(projectId, questionsData) {
        try {
            // Format the data to have projectId and questions array
            const formattedData = {
                projectId: projectId,
                questions: questionsData.map(q => ({
                    question: q.question,
                    difficulty: q.difficulty
                }))
            };
    
            const saveResponse = await fetch('http://localhost:9000/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formattedData)
            });
    
            if (!saveResponse.ok) {
                const errorResponse = await saveResponse.json();
                throw new Error(`Failed to save questions. Server responded with: ${JSON.stringify(errorResponse.detail)}`);
            }
    
            const saveData = await saveResponse.json();
            console.log('Questions saved successfully:', saveData);
        } catch (error) {
            console.error('Error saving questions:', error);
        }
    }


});
