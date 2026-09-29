import os
import re
import csv
import json
import logging

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def local(uri):
    return str(uri).split("#")[-1].split("/")[-1]

def words(text):
    """Lowercase words, CamelCase split: 'MusicArtist' -> {'music', 'artist'}."""
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", text) if len(w) > 2}

def ontology_summary(path, scenario, max_lines=150):
    """Classes and relations of the ontology, the ones matching the scenario first."""
    if not path or not os.path.exists(path):
        return "No ontology provided. Work from the scenario only."

    g = Graph()
    try:
        g.parse(path)
    except Exception:
        try:
            g.parse(path, format="xml")
        except Exception:
            return "Ontology could not be parsed. Work from the scenario only."

    relations = set()
    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for p in g.subjects(RDF.type, prop_type):
            for d in g.objects(p, RDFS.domain):
                for r in g.objects(p, RDFS.range):
                    if isinstance(d, URIRef) and isinstance(r, URIRef):
                        relations.add(f"{local(d)} --{local(p)}--> {local(r)}")

    classes = {local(c) for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)}

    scenario_words = words(scenario)
    rank = lambda text: (-len(words(text) & scenario_words), text)

    return (
        "Classes:\n" + "\n".join(sorted(classes, key=rank)[:max_lines // 2])
        + "\n\nRelations (domain --property--> range):\n"
        + "\n".join(sorted(relations, key=rank)[:max_lines])
    )

def call_gemma(client, model, system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
    )
    choice = response.choices[0]
    if not choice.message.content:
        raise ValueError(f"Empty response (finish_reason={choice.finish_reason})")
    return choice.message.content

def parse_questions(text):
    """Take everything between the first '[' and the last ']' and load it as JSON."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array in response: {text[:200]!r}")
    questions = json.loads(text[start:end + 1])
    questions = [q.strip() for q in questions if isinstance(q, str) and q.strip().endswith("?")]
    return list(dict.fromkeys(questions))  

def main():
    load_dotenv()

    with open(os.environ["SYSTEM_PROMPT"], encoding="utf-8") as f:
        system_prompt = f.read()

    num_cqs = int(os.getenv("NUM_CQS", "12"))
    model = os.getenv("GEMMA_MODEL", "gemma4")
    client = OpenAI(base_url=os.getenv("GEMMA_BASE_URL"), api_key=os.getenv("GEMMA_API_KEY", "dummy"))

    gold = pd.read_csv(os.environ["BENCHMARK_INPUT"], sep=",", on_bad_lines="skip").fillna("")
    gold.columns = gold.columns.str.strip()
    projects = gold.drop_duplicates(subset=["Project Name"])

    with open(os.getenv("QUEUE_FILE_PATH", "queue.csv"), encoding="utf-8") as f:
        ontologies = {os.path.basename(os.path.dirname(r["OntologyPath"])): r["OntologyPath"]
                      for r in csv.DictReader(f)}

    output_csv = os.environ["OUTPUT_CSV"]
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["Project Name", "Name", "Scenario", "Dataset", "Link", "generated"])

        for _, row in projects.iterrows():
            project, scenario = row["Project Name"], row["Scenario"]
            logger.info(f"Processing: {project}")

            user_prompt = (
                f"<scenario>\n{scenario or 'No scenario provided.'}\n</scenario>\n\n"
                f"<ontology_info>\nLink/URI: {row['Link'] or 'N/A'}\n"
                f"{ontology_summary(ontologies.get(project), scenario)}\n</ontology_info>\n\n"
                f"<request>\nGenerate about {num_cqs} generic Competency Questions for this "
                f"scenario, following the rules. Return ONLY a valid JSON array of strings.\n</request>"
            )

            questions = []
            for attempt in range(3):
                try:
                    questions = parse_questions(call_gemma(client, model, system_prompt, user_prompt))
                    if questions:
                        break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {project}: {e}")

            for q in questions:
                writer.writerow([project, row["Name"], scenario, row["Dataset"], row["Link"], q])
            out.flush()
            logger.info(f"Saved {len(questions)} questions.")

if __name__ == "__main__":
    main()