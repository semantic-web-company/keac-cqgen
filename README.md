# KEAC Competition, Task 1: Automated Question Generation from Scenarios

A script that takes either a scenario, dataset and (if available) an ontology, 
and generates Competency Questions (CQs) with a Gemma model.

## How it works

For every unique project in the benchmark file, the script:

1. Reads the (sub)project's `Scenario`, `Dataset` and `Link` from the benchmark CSV.
2. Downloads the linked file and checks whether it is an ontology.
3. Processes Scenario cases (rows in the input table that have content in the `Scenario` column):
   - If there is a linked ontology, it builds a short ontology summary: classes and relations (`Domain --property--> Range`), 
with the ones whose names overlap with the scenario listed first. Supports any format `rdflib` can parse. 
If the ontology is missing or cannot be parsed, the model works from the scenario only.
   - Sends the scenario and ontology summary, together with the system prompt, to the model and asks for a JSON array of questions.
   - Parses the response, keeps only non-empty strings ending with `?`, removes duplicates, and writes them to the output CSV. 
Each project is retried up to 3 times if the call or the parsing fails.
4. Processes Dataset cases (rows in the input table that have content in the `Dataset` column):
   - The dataset is then sent to the model and the model is requested to create an ontology describing the dataset.
   - The returned ontology is sent to the model and the model is requested to generate competency questions based on it.
5. Process Link cases (rows in the input file that have no Scenario and no Dataset content and have a link):


## Requirements

- Python 
- An OpenAI-compatible endpoint serving Gemma

```bash
pip install pandas python-dotenv openai rdflib wget
```

## Configuration

Create a `.env` file (see `.env_example`) in the project root and set the following:

```env
# Data
BENCHMARK_INPUT=your_file.csv
OUTPUT_CSV=your_output_with_generated_questions.csv
ONTOLOGIES_DIR=your_dir_where_ontologies_will_be_downloaded.csv

# Prompt
SYSTEM_PROMPT_CQ=data/cq-system_prompt.txt
SYSTEM_PROMPT_ONTOLOGY=data/ontology-extractor-system-prompt.md

# Gemma settings
GEMMA_BASE_URL=
GEMMA_API_KEY=dummy
GEMMA_MODEL=gemma4
NUM_CQS=20
```

| Variable                 | Required | Description                                                                                         |
|--------------------------|----------|-----------------------------------------------------------------------------------------------------|
| `BENCHMARK_INPUT`        | yes      | Comma-separated CSV with at least the columns `Project Name`, `Name`, `Scenario`, `Dataset`, `Link` |
| `OUTPUT_CSV`             | yes      | Where the generated questions are written                                                           |
| `ONTOLOGIES_DIR`         | yes      | Path to folder where downloaded ontologies will be stored.                                          |
| `SYSTEM_PROMPT_CQ`       | yes      | Path to a text file with the system prompt for CQ generation.                                       |
| `SYSTEM_PROMPT_ONTOLOGY` | yes      | Path to a text file with the system prompt for ontology generation.                                 |
| `GEMMA_BASE_URL`         | yes      | Base URL of the OpenAI-compatible API                                                               |
| `GEMMA_API_KEY`          | no       | API key (default: `dummy`)                                                                          |
| `GEMMA_MODEL`            | no       | Model name (default: `gemma4`)                                                                      |
| `NUM_CQS`                | no       | Approximate number of questions per project (default: `12`)                                         |

## Input files

**Benchmark file** (`BENCHMARK_INPUT`): one row per competency question is fine, since the script keeps only the first row of each `Project Name`.



## Running the project

```bash
python generate_cqs.py
```

Progress is logged to the console, and the output CSV is flushed after every project,
so partial results are kept if the run is interrupted.

## Output

A CSV with the columns:

`Project Name, Name, Scenario, Dataset, Link, generated`

There is one row per generated question, with the question in the `generated` column.