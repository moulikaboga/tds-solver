# tds-solver
Automated solver for Tools in Data Science assignments
# TDS Solver

An API that automatically answers questions from the Tools in Data Science graded assignments at IIT Madras' Online Degree in Data Science program.

## Features

- Accepts any question from the graded assignments
- Processes attached files as needed
- Returns the correct answer in JSON format
- Handles various types of questions including CSV analysis, calculations, and general queries

## API Usage

The API accepts POST requests with the question and optional file attachments.

### Endpoint

```
POST https://your-app.vercel.app/api/
```

### Request Format

The request should be a `multipart/form-data` with the following fields:

- `question`: The question from the assignment
- `file` (optional): Any file attachment needed to answer the question

### Example Request

```bash
curl -X POST "https://your-app.vercel.app/api/" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download and unzip file abcd.zip which has a single extract.csv file inside. What is the value in the 'answer' column of the CSV file?" \
  -F "file=@abcd.zip"
```

### Response Format

The API returns a JSON object with a single field `answer`:

```json
{
  "answer": "1234567890"
}
```

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the server locally: `uvicorn app:app --reload`

## Deployment

This application can be deployed to various platforms including:

- Vercel
- Heroku
- Railway
- Azure
- AWS

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.