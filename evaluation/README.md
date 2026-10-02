# KEAC Competition, Task 1: Evaluation Service

A small Flask service that exposes your generated questions to the competition evaluator. Point it at your CSV file, start it, and the evaluator can download the file over HTTP.

## Requirements

- Python 
- [Flask](https://flask.palletsprojects.com/)
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (if the service loads `.env` with it)

```bash
pip install flask pandas python-dotenv
```

## Configuration

Create a `.env` file in the project root and set the path to your generated questions file:

```env
# Path to the CSV file with your generated questions
GENERATED_QUESTIONS="generated.csv"
```

The path can be relative to the directory you run the service from, or absolute.

## Running the Service

```bash
python service_for_eval.py
```

The server listens on `http://0.0.0.0:8080/`.

## API Endpoints

| Method | Endpoint   | Description |
|--------|------------|-------------|
| `GET`  | `/gtg`     | Health check. Returns `OK` if the service is running. |
| `GET`, `POST` | `/get_csv` | Returns the CSV file configured in `.env` as a download. Responds with `404` if the file is not found. |


## Troubleshooting

- **`404` from `/get_csv`**: the file at `GENERATED_QUESTIONS` doesn't exist. Check the path in `.env` and the directory you started the service from.
- **Evaluator can't connect**: make sure port `8080` is open and reachable from the evaluator's network.