# 🚀 LLM Benchmark Automation and Visualization Guide

This tool is designed to automate the benchmark testing of local Large Language Models (LLMs) hosted on Ollama, evaluate their inference performance, stability, and speed (Tokens/sec), and visualize the results using high-resolution charts.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Setup & Preparation](#2-setup--preparation)
3. [Running the Benchmark](#3-running-the-benchmark)
4. [Visualization & Chart Analysis](#4-visualization--chart-analysis)
5. [Project Structure & Files](#5-project-structure--files)
6. [Benchmark Logic & Questions](#6-benchmark-logic--questions)

---

## 1. Prerequisites

To ensure the system works correctly, make sure the following components are installed and running:
- **Operating System:** Linux (Ubuntu/Debian recommended)
- **Python:** Python 3.8 or later
- **Ollama:** Local model inference server (must be running on port `localhost:11434`)
- **GPU Drivers (Optional):** ROCm for AMD GPUs or CUDA for NVIDIA GPUs (required for Ollama to leverage hardware acceleration)

---

## 2. Setup & Preparation

### Step 1: Create and Activate Virtual Environment
Open a terminal in the project directory and create a virtual environment to isolate dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Required Libraries
Install the required packages for data processing and chart generation:
```bash
pip install pandas matplotlib seaborn requests
```

### Step 3: Start the Ollama Server
Ensure the Ollama service is running in the background.
```bash
# Check Ollama service status
systemctl status ollama
```

---

## 3. Running the Benchmark

Start the entire test suite by running `benchmark.py`:
```bash
python3 benchmark.py
```

### 💬 Execution Flow & Interactive Prompts:
1. **Model Selection:** The script fetches and lists all models installed on Ollama. Enter the number corresponding to the model you want to test, or select the last option (`RUN ALL MODELS SEQUENTIALLY`) to evaluate all of them.
2. **Timeout Configuration:** Set the maximum response duration for each test question in seconds (Default: `300` seconds, enter `0` for unlimited). This is critical to prevent base models from infinite generation loops or larger models from getting stuck when running on CPU.
3. **Dual CSV Saving:** After completion, results are automatically recorded in two places:
   - `benchmark_results_YYYYMMDD_HHMMSS.csv` (Session-specific timestamped archive file)
   - `benchmark_results.csv` (Cumulative all-time master database)
4. **Auto-Visualization:** Once the test finishes, the visualization scripts are triggered automatically to update all charts with the latest data.

---

## 4. Visualization & Chart Analysis

By default, the visualization tools read the cumulative `benchmark_results.csv` database. However, you can also visualize any specific historical test session.

### 📊 Available Chart Types
1. **01_model_hiz_karsilastirma.png:** Displays the average token production speed (Tokens / Second) of models sorted from fastest to slowest.
2. **02_kategori_bazli_hizlar.png:** Compares the performance of models across different benchmark categories (Knowledge, Reasoning, Coding, Creativity, etc.) side-by-side.
3. **03_model_kararlilik_boxplot.png:** A boxplot visualizing inference speed stability and latency fluctuations for each model.
4. **04_boyut_vs_hiz_korelasyon.png:** A scatter plot illustrating the relationship between model parameter size (Billion - B) and inference speed (T/s), including CPU/GPU utilization impact.
5. **05_toplam_sure_karsilastirma.png:** Shows the total elapsed time (seconds) each model took to complete the entire benchmark suite.

### 🛠️ Manual Chart Generation

**To regenerate the charts for all-time cumulative data:**
```bash
python3 visualize_all.py
python3 visualize_benchmark.py
```

**To visualize a specific historical test run:**
```bash
python3 visualize_all.py benchmark_results_20260524_134216.csv
python3 visualize_benchmark.py benchmark_results_20260524_134216.csv
```

---

## 5. Project Structure & Files

* **`benchmark.py`:** The main execution script that connects to the Ollama API, runs the tests, and logs details.
* **`visualize_benchmark.py`:** Script to draw average speed and category speed charts (Charts 1 and 2).
* **`visualize_all.py`:** Script to generate the size correlation, speed stability boxplot, and total duration charts (Charts 3, 4, and 5).
* **`questions.json`:** Contains the benchmark prompts and their corresponding generation temperatures.
* **`benchmark_results.csv`:** The master database file compiling all historical test records.
* **`logbook.md`:** Manual notebook for hardware configurations, notes, and observations.

---

## 6. Benchmark Logic & Questions

The benchmark prompts (`questions.json`) are structured across 6 categories designed to stress-test specific capabilities:

1. **Knowledge [KNL-01]:** Tests academic/factual knowledge quality and model tone.
2. **Reasoning [REA-01]:** Evaluates mathematical and logical step-by-step problem-solving skills.
3. **Reasoning/Coding [COD-01]:** Evaluates code writing, structural formatting, and algorithmic design.
4. **Instruction Following [INS-01]:** Measures how well the model adheres to strict rules and constraints.
5. **Creativity [CRT-01]:** Assesses fictional storytelling and creative expression.
6. **Safety/Guardrails [SAF-01]:** Tests model response guardrails when faced with unsafe prompts (evaluating refusal rates or boundaries).
