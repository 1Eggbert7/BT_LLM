# BT-ACTION: A Test-Driven Approach for Modular Understanding of User Instructions Leveraging Behaviour Trees and LLMs

This repository contains the complete source code for the **BT-ACTION** framework, which integrates Behavior Trees (BTs) and Large Language Models (LLMs) for managing natural language instructions in human-robot interaction (HRI) settings. It includes both the BT-LLM implementation and a baseline system for comparison.

## Overview

**BT-ACTION** combines the modular structure of Behavior Trees with the language understanding capabilities of an LLM to interpret, validate, and execute user instructions. Key features include:

- **Behavior Tree Logic**: Task and decision-handling structured using `PyTrees`.
- **LLM Integration**: Natural language understanding powered by OpenAI’s LLM.
- **Explainability**: Transparent, step-by-step decision-making for user-facing feedback.
- **Error Handling**: Built-in task validation to detect ambiguity, infeasibility, or safety issues.

## Contents

This repository includes the following key components:

### Main Scripts
- **`main.py`** – Launches the BT-ACTION framework.
- **`baseline.py`** – Baseline implementation using a static pre-prompt approach.
- **`furhatTest.py`, `furhatTest2.py`, `furhatTest3.py`** – Experimental integration scripts for use with the Furhat robot.

### Framework Components
- **`actions.py`** – Behavior Tree action nodes.
- **`conditions.py`** – Condition-checking nodes within the tree.
- **`prompts.py`** – Prompt templates for the LLM (classification, plan generation, etc.).
- **`state.py`** – State management across BT nodes.
- **`utils.py`** – Utility functions used throughout the framework.

### Data Files
- **`functions.json`** – Definitions of available task functions.
- **`ingredients.json`** – Ingredient information for food-related tasks.
- **`sequences.json`** – Predefined task sequences.
- **`sequences_descriptions.json`** – Descriptions of those sequences for explainability.

### Outputs and Logs
- **`output.xlsx`** – Stores experiment outputs or generated results.
- **Log Files** – Interaction transcripts saved via `transcript_saver.py`.

### Visualization Files
- **`full_bt_root_selector.*`** – Visualizations of the complete Behavior Tree (`.png`, `.svg`, `.dot`).
- **`test_tree_.*`** – Test-specific tree visualization files.

### Additional Utilities
- **`transcript_analysis.py`** – Tool for analyzing user interaction logs.
- **`transcript_parse.py`** – Parser for raw transcript formatting.
- **`testing.py`** – Tools for evaluating behavior tree performance and accuracy.
