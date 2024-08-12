# InterviewQGen

**InterviewQGen** is a web-based tool designed to generate tailored interview questions based on job descriptions. Using advanced AI technologies, it transforms job descriptions into a list of insightful interview questions categorized into Easy, Medium, and Hard levels.

## Features

- **Job Description Input**: Enter a detailed job description to get relevant questions.
- **AI-Powered Question Generation**: Utilizes state-of-the-art AI models to craft questions tailored to the job role.
- **User-Friendly Interface**: Professional and dynamic UI for a seamless user experience.
- **Real-Time Processing**: Instant question generation with a visually appealing loader.
- **Caching**: Efficient caching mechanism to speed up repeated requests.
- **Concurrency**: Optimized handling of multiple requests for better performance.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: FastAPI
- **AI Models**: Hugging Face Transformers for summarization, LangChain OpenAI for question generation
- **Environment**: Python, Uvicorn for serving the FastAPI application

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/InterviewQGen.git
    cd InterviewQGen
    ```

2. **Set Up a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` File**

    Add your OpenAI API key to a `.env` file in the root directory:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. **Run the Application**

    ```bash
    uvicorn main:app --reload --workers 4
    ```

    This command starts the FastAPI server with 4 worker processes for handling requests.

2. **Access the API**

    The API will be available at `http://127.0.0.1:8000`.

3. **Endpoints**

    - **POST /generate**: Generates interview questions based on a job description.
    
      **Request Body:**
      
      ```json
      {
        "description": "The job description text here."
      }
      ```

      **Response:**
      
      ```json
      {
        "questions": "Generated interview questions here."
      }
      ```

## Code Overview

- `main.py`: Contains the FastAPI application code including endpoints, model initialization, and logic for summarizing job descriptions and generating interview questions.
- `requirements.txt`: Lists the Python packages required for the application.

## Contributing

Contributions are welcome! Please follow the standard GitHub fork-and-pull request workflow. Ensure that any changes are tested and adhere to the project's coding standards.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Hugging Face Transformers**: For the BART model used in summarization.
- **OpenAI**: For the API used in generating interview questions.
- **FastAPI**: For providing the web framework to build this application.

For any questions or feedback, please open an issue or reach out via email.

