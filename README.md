# 🤖 Company-Research-bot-
A proof of concept of an AI-powered research assistant that helps analysts quickly gather company information, configure analysis parameters, and generate customized reports through conversational workflows using Microsoft 365 Agents SDK with Python.

## Usage examples

### Gather company data
![Gather data wizard's of the coast - 1](./testing/manual_testing/tcg%20gaming%20giants/1/1.png)
![Gather data wizard's of the coast - 1](./testing/manual_testing/tcg%20gaming%20giants/1/2.png)
![Gather data wizard's of the coast - 1](./testing/manual_testing/tcg%20gaming%20giants/1/3.png)
![Gather data wizard's of the coast - 1](./testing/manual_testing/tcg%20gaming%20giants/1/4.png)

### Perform data analysis on most recent gathered data
![Peform data analysis on tcg gaming giants - 1](./testing/manual_testing/tcg%20gaming%20giants/1/10.png)
![Peform data analysis on tcg gaming giants - 2](./testing/manual_testing/tcg%20gaming%20giants/1/11.png)
![Peform data analysis on tcg gaming giants - 3](./testing/manual_testing/tcg%20gaming%20giants/1/12.png)

### Create data report on most recent data analysis done
![Make data report on tcg gaming giants - 1](./testing/manual_testing/tcg%20gaming%20giants/1/13.png)
![Make data report on tcg gaming giants - 2](./testing/manual_testing/tcg%20gaming%20giants/1/14.png)
![Make data report on tcg gaming giants - 3](./testing/manual_testing/tcg%20gaming%20giants/1/15.png)
![Make data report on tcg gaming giants - 4](./testing/manual_testing/tcg%20gaming%20giants/1/16.png)
![Make data report on tcg gaming giants - 5](./testing/manual_testing/tcg%20gaming%20giants/1/17.png)
![Make data report on tcg gaming giants - 6](./testing/manual_testing/tcg%20gaming%20giants/1/18.png)

## 📦 Install dependencies
pip install -r requirements.txt

## ▶️ Run python bot backend
python3 app.py

## 🧪 Run Microsoft 365 Agents SDK bot emulator
teamsapptester

## ✅ Run unit tests
- python3 -m pytest -v "testing/unit_testing/test_company_research_agent.py"

## 🏗️ Architecture Diagram

See [architecture-diagram.md](architecture-diagram.md).

## 📋 Specifications
- AI Model: gpt-4o-mini
- Data analysis is for now limited to only use 3 most recent data gather actions to keep a moderate AI model prompt token usage.
- Data report is for now limited to only use 3 most recent data analysis actions to keep a moderate AI model prompt token usage.