---
name: ontology-extractor
description: 'Investigate relational databases, SQL schemas, CSVs, or tabular data to create an ontology that can be used to describe the data. The default base ontologies is Schema.org, that can be extended with other useful classes and predicates from other well known ontologies or with newly invented classes and predicates.'
argument-hint: 'Describe the source schema or provide a CSV/SQL schema'
---
# Ontology Extractor

Use this skill to turn a relational or tabular source into an ontology that can be used to describe the data. This workflow is non-interactive.

## Purpose
Automate the generation of a compact ontology module containing only the vocabulary (classes, properties, datatypes) used to map a specific relational or tabular source to RDF. This skill is optimized for speed and automation, making autonomous modeling decisions to produce a clean, minimal Turtle file.

## Outputs
- A compact Turtle (`.ttl`) file containing:
    - Reused external ontology terms (with original IRIs).
    - Project-specific extension terms (with labels and comments).
    - Necessary datatype declarations.

## Core Interaction Rule
This skill is **non-interactive**. It is designed to proceed autonomously. It follows a "best-effort" decision-making process based on the target vocabulary (e.g., Schema.org) and the source structure. It only asks for clarification if the source is critically ambiguous.

## Procedure

### 1. Source Analysis
- Analyze the source structure (e.g., CSV columns, SQL schema).
- Identify candidate entities, attributes, and relationships.

### 2. Autonomous Modeling
- **Strategy Selection:** Choose a modeling pattern (e.g., single resource per row) that preserves the highest semantic fidelity.
- **URI Design:** Implement a hierarchical URI strategy based on entity types.
- **Term Selection:** Match source fields to standard vocabularies (Schema.org, etc.). If no match exists, automatically define an extension term in a project-specific namespace.

### 3. Vocabulary Extraction
- Identify every unique IRI (Class, Property, Datatype) used in the mapping.
- **External Terms:** For reused terms, include the original IRI and a minimal declaration (e.g., `rdfs:label`).
- **Extension Terms:** For new terms, include a full declaration (`rdfs:label`, `rdfs:comment`, and type).
- **Datatypes:** Include necessary `xsd:` declarations.

### 4. Generation
- Output the final vocabulary as a single, valid Turtle (`.ttl`) document.
