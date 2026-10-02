# KEAC Competition, Task 1: Automated Question Generation from Scenarios

A script that takes a scenario and (if available) an ontology, and generates Competency Questions (CQs) with a Gemma model.

## How it works

For every unique project in the benchmark file, the script:

1. Reads the project's `Scenario` and `Link` from the benchmark CSV.
2. Looks up the project's ontology file in the queue file (matched by the name of the ontology's parent folder).
3. Builds a short ontology summary: classes and relations (`Domain --property--> Range`), with the ones whose names overlap with the scenario listed first. Supports any format `rdflib` can parse. If the ontology is missing or cannot be parsed, the model works from the scenario only.
4. Sends the scenario and ontology summary, together with the system prompt, to the model and asks for a JSON array of questions.
5. Parses the response, keeps only non-empty strings ending with `?`, removes duplicates, and writes them to the output CSV. Each project is retried up to 3 times if the call or the parsing fails.

## Requirements

- Python 
- An OpenAI-compatible endpoint serving Gemma

```bash
pip install pandas python-dotenv openai rdflib
```

## Configuration

Create a `.env` file in the project root and set the following:

```env
# Data
BENCHMARK_INPUT=your_file.csv
OUTPUT_CSV=your_output_with_generated_questions.csv
QUEUE_FILE_PATH=your_queue.csv

# Prompt
SYSTEM_PROMPT=your_system_prompt.txt

# Gemma settings
GEMMA_BASE_URL=
GEMMA_API_KEY=dummy
GEMMA_MODEL=gemma4
NUM_CQS=20
```

| Variable | Required | Description |
|---|---|---|
| `BENCHMARK_INPUT` | yes | Comma-separated CSV with at least the columns `Project Name`, `Name`, `Scenario`, `Dataset`, `Link` |
| `OUTPUT_CSV` | yes | Where the generated questions are written |
| `QUEUE_FILE_PATH` | no | CSV with an `OntologyPath` column (default: `queue.csv`) |
| `SYSTEM_PROMPT` | yes | Path to a text file with the system prompt |
| `GEMMA_BASE_URL` | yes | Base URL of the OpenAI-compatible API |
| `GEMMA_API_KEY` | no | API key (default: `dummy`) |
| `GEMMA_MODEL` | no | Model name (default: `gemma4`) |
| `NUM_CQS` | no | Approximate number of questions per project (default: `12`) |

## Input files

**Benchmark file** (`BENCHMARK_INPUT`): one row per competency question is fine, since the script keeps only the first row of each `Project Name`.

**Queue file** (`QUEUE_FILE_PATH`): a CSV with an `OntologyPath` column. The name of the folder containing each ontology file must match the `Project Name`, e.g.:

```csv
OntologyPath
ontologies/Polifonia/ontology.owl
ontologies/Wine/wine.rdf
```

## Running the project

```bash
python generate_cqs.py
```

Progress is logged to the console, and the output CSV is flushed after every project, so partial results are kept if the run is interrupted.

## Output

A CSV with the columns:

`Project Name, Name, Scenario, Dataset, Link, generated`

There is one row per generated question, with the question in the `generated` column.