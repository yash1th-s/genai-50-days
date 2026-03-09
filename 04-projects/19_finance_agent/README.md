# Day 19: Personal Finance Agent 💰

An AI-powered personal finance assistant that helps you track expenses, categorize spending, and get insights - all using natural language.

## Features

- **Add Expenses** - "I spent $50 on groceries"
- **View All Expenses** - "Show me all my expenses"
- **Filter by Category** - "How much did I spend on food?"
- **Spending Summary** - "Give me a breakdown of my spending"
- **Get Insights** - "What are my spending patterns?"
- **Delete Expenses** - "Remove expense #3"

## Tools

The agent has 6 tools:
1. `add_expense` - Add new expense with amount, category, description
2. `get_all_expenses` - List all recorded expenses
3. `get_expenses_by_category` - Filter expenses by category
4. `get_spending_summary` - Category breakdown with percentages
5. `delete_expense` - Remove an expense by ID
6. `get_insights` - Get spending patterns and recommendations

## Categories

- Food
- Transport
- Entertainment
- Shopping
- Bills
- Health
- Other

## Run

```bash
cd 04-projects/19_finance_agent
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

```
User Input
    ↓
Agent Loop
    ↓
LLM decides which tool(s) to call
    ↓
Execute tools → Add results to conversation
    ↓
Loop until LLM gives final response
    ↓
Display response + tool calls
```

## Key Concepts

- **Agent Loop** from Day 18
- **Multiple Tools** from Day 17
- **Tool Calling** from Day 16
- **Streamlit UI** from Day 15

This project combines everything from the Agents section into a working application.