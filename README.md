# Thesis Code Repository

This repository contains the complete source code for the thesis project, including the implementation of the BT-LLM framework and the baseline system for human-robot interaction (HRI). It provides the necessary components for testing, replication, and understanding the developed systems.

## Overview

The BT-LLM framework integrates Behavior Trees (BTs) and a Large Language Model (LLM) to manage user instructions in a systematic, modular, and explainable manner. The framework includes features such as:
- **Behavior Tree Logic**: Modular structure for handling tasks and decision-making using `PyTrees`.
- **LLM Integration**: Processing user instructions through OpenAI's LLM for natural language understanding.
- **Explainability**: Transparent decision-making at each node, enabling explicit feedback to users.
- **Error Handling**: Validating tasks and preventing infeasible or unsafe operations.

## Contents

This repository includes the following key components:

### Main Scripts
- **`main.py`**: Primary script for running the BT-LLM framework.
- **`baseline.py`**: Script for the baseline system using a single LLM pre-prompt.
- **`furhatTest.py`, `furhatTest2.py`, `furhatTest3.py`**: Experimental scripts for integrating the framework with the Furhat robot.

### Framework Components
- **`actions.py`**: Action nodes for the behavior tree.
- **`conditions.py`**: Condition nodes for the behavior tree.
- **`prompts.py`**: Predefined LLM prompts for ambiguity classification, sequence generation, and more.
- **`state.py`**: State management for the behavior tree.
- **`utils.py`**: Utility functions used throughout the framework.

### Data Files
- **`functions.json`**: JSON file specifying available functions for tasks.
- **`ingredients.json`**: JSON file listing ingredients used in tasks.
- **`sequences.json`**: JSON file defining known task sequences.
- **`sequences_descriptions.json`**: JSON file with detailed descriptions of sequences.

### Outputs and Logs
- **`output.xlsx`**: Excel file containing generated results or analyzed data.
- **Log Files**: Transcripts of user interactions saved by `transcript_saver.py`.

### Visualization Files
- **`full_bt_root_selector.*`**: Visual representation of the full behavior tree in `.png`, `.svg`, and `.dot` formats.
- **`test_tree_.*`**: Test tree visualization files.

### Additional Utilities
- **`transcript_analysis.py`**: Script for analyzing conversation transcripts.
- **`transcript_parse.py`**: Parsing tool for handling raw transcripts.
- **`testing.py`**: Tools for evaluating behavior tree performance.
