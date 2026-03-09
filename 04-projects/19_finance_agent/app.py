"""
Day 19: Personal Finance Agent
Track expenses, categorize spending, get insights using natural language.
"""

import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment
load_dotenv(dotenv_path='../../.env')
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# Page config
st.set_page_config(page_title="Finance Agent", page_icon="💰", layout="wide")
st.title("💰 Personal Finance Agent")
st.caption("Track expenses, categorize spending, get insights - all with natural language")

# Initialize session state
if "expenses" not in st.session_state:
    st.session_state.expenses = [
        {"id": 1, "amount": 50.00, "category": "Food", "description": "Grocery shopping", "date": "2024-01-15"},
        {"id": 2, "amount": 120.00, "category": "Transport", "description": "Uber rides", "date": "2024-01-16"},
        {"id": 3, "amount": 30.00, "category": "Entertainment", "description": "Netflix subscription", "date": "2024-01-17"},
        {"id": 4, "amount": 200.00, "category": "Shopping", "description": "New headphones", "date": "2024-01-18"},
        {"id": 5, "amount": 45.00, "category": "Food", "description": "Restaurant dinner", "date": "2024-01-19"},
    ]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []

# ========== TOOLS ==========

def add_expense(amount: float, category: str, description: str) -> str:
    """Add a new expense."""
    new_id = max([e["id"] for e in st.session_state.expenses], default=0) + 1
    expense = {
        "id": new_id,
        "amount": amount,
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.expenses.append(expense)
    return f"✅ Added expense: ${amount:.2f} for {description} ({category})"

def get_all_expenses() -> str:
    """Get all expenses."""
    if not st.session_state.expenses:
        return "No expenses recorded yet."
    
    result = "All expenses:\n"
    for e in st.session_state.expenses:
        result += f"• ${e['amount']:.2f} - {e['description']} ({e['category']}) - {e['date']}\n"
    return result

def get_expenses_by_category(category: str) -> str:
    """Get expenses filtered by category."""
    filtered = [e for e in st.session_state.expenses if e["category"].lower() == category.lower()]
    if not filtered:
        return f"No expenses found in category: {category}"
    
    total = sum(e["amount"] for e in filtered)
    result = f"Expenses in {category} (Total: ${total:.2f}):\n"
    for e in filtered:
        result += f"• ${e['amount']:.2f} - {e['description']} - {e['date']}\n"
    return result

def get_spending_summary() -> str:
    """Get spending summary by category."""
    if not st.session_state.expenses:
        return "No expenses recorded yet."
    
    categories = {}
    for e in st.session_state.expenses:
        cat = e["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += e["amount"]
    
    total = sum(categories.values())
    result = f"📊 Spending Summary (Total: ${total:.2f}):\n"
    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total) * 100
        result += f"• {cat}: ${amount:.2f} ({percentage:.1f}%)\n"
    return result

def delete_expense(expense_id: int) -> str:
    """Delete an expense by ID."""
    for i, e in enumerate(st.session_state.expenses):
        if e["id"] == expense_id:
            removed = st.session_state.expenses.pop(i)
            return f"🗑️ Deleted expense: ${removed['amount']:.2f} - {removed['description']}"
    return f"Expense with ID {expense_id} not found."

def get_insights() -> str:
    """Get spending insights and recommendations."""
    if len(st.session_state.expenses) < 3:
        return "Not enough data for insights. Add more expenses!"
    
    categories = {}
    for e in st.session_state.expenses:
        cat = e["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += e["amount"]
    
    total = sum(categories.values())
    highest_cat = max(categories.items(), key=lambda x: x[1])
    
    insights = f"💡 Spending Insights:\n"
    insights += f"• Total spending: ${total:.2f}\n"
    insights += f"• Highest category: {highest_cat[0]} (${highest_cat[1]:.2f})\n"
    insights += f"• Number of transactions: {len(st.session_state.expenses)}\n"
    insights += f"• Average transaction: ${total/len(st.session_state.expenses):.2f}\n"
    
    if highest_cat[1] / total > 0.4:
        insights += f"\n⚠️ You're spending {(highest_cat[1]/total)*100:.0f}% on {highest_cat[0]}. Consider budgeting!"
    
    return insights

# ========== TOOL SCHEMAS ==========

finance_tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="add_expense",
            description="Add a new expense with amount, category, and description.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "amount": types.Schema(type=types.Type.NUMBER, description="Amount spent in dollars"),
                    "category": types.Schema(type=types.Type.STRING, description="Category: Food, Transport, Entertainment, Shopping, Bills, Health, or Other"),
                    "description": types.Schema(type=types.Type.STRING, description="Brief description of the expense")
                },
                required=["amount", "category", "description"]
            )
        ),
        types.FunctionDeclaration(
            name="get_all_expenses",
            description="Get a list of all recorded expenses.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_expenses_by_category",
            description="Get expenses filtered by a specific category.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "category": types.Schema(type=types.Type.STRING, description="Category to filter by")
                },
                required=["category"]
            )
        ),
        types.FunctionDeclaration(
            name="get_spending_summary",
            description="Get a summary of spending broken down by category with totals and percentages.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="delete_expense",
            description="Delete an expense by its ID number.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "expense_id": types.Schema(type=types.Type.INTEGER, description="ID of the expense to delete")
                },
                required=["expense_id"]
            )
        ),
        types.FunctionDeclaration(
            name="get_insights",
            description="Get spending insights, patterns, and recommendations.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        )
    ]
)

# ========== TOOL DISPATCHER ==========

def execute_tool(func_call):
    """Execute the tool and return result."""
    name = func_call.name
    args = dict(func_call.args) if func_call.args else {}
    
    tool_info = {"name": name, "args": args}
    
    if name == "add_expense":
        result = add_expense(args["amount"], args["category"], args["description"])
    elif name == "get_all_expenses":
        result = get_all_expenses()
    elif name == "get_expenses_by_category":
        result = get_expenses_by_category(args["category"])
    elif name == "get_spending_summary":
        result = get_spending_summary()
    elif name == "delete_expense":
        result = delete_expense(args["expense_id"])
    elif name == "get_insights":
        result = get_insights()
    else:
        result = f"Unknown tool: {name}"
    
    tool_info["result"] = result
    return result, tool_info

# ========== AGENT LOOP ==========

def run_agent(message: str, max_iterations: int = 5):
    """Run the agent loop."""
    tool_calls = []
    
    # System instruction
    system = """You are a helpful personal finance assistant. You help users:
- Track their expenses
- Categorize spending
- Get insights about their finances
- Manage their budget

Be friendly and helpful. When adding expenses, confirm the details.
Categories available: Food, Transport, Entertainment, Shopping, Bills, Health, Other"""

    # Start conversation
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=message)])]
    
    for _ in range(max_iterations):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[finance_tools],
                system_instruction=system
            )
        )
        
        part = response.candidates[0].content.parts[0]
        
        # Check for tool call
        if part.function_call:
            func_call = part.function_call
            result, tool_info = execute_tool(func_call)
            tool_calls.append(tool_info)
            
            # Add to conversation
            contents.append(types.Content(role="model", parts=[part]))
            contents.append(types.Content(role="user", parts=[
                types.Part.from_function_response(
                    name=func_call.name,
                    response={"result": result}
                )
            ]))
            continue
        
        # Text response - done
        return response.text, tool_calls
    
    return "Max iterations reached", tool_calls

# ========== SIDEBAR ==========

with st.sidebar:
    st.header("📊 Quick Stats")
    
    if st.session_state.expenses:
        total = sum(e["amount"] for e in st.session_state.expenses)
        st.metric("Total Spent", f"${total:.2f}")
        st.metric("Transactions", len(st.session_state.expenses))
        
        # Category breakdown
        st.subheader("By Category")
        categories = {}
        for e in st.session_state.expenses:
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + e["amount"]
        
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{cat}:** ${amount:.2f}")
    else:
        st.info("No expenses yet")
    
    st.divider()
    if st.button("🗑️ Clear All Data"):
        st.session_state.expenses = []
        st.session_state.messages = []
        st.session_state.tool_calls = []
        st.rerun()

# ========== CHAT INTERFACE ==========

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show tool calls for assistant messages
        if message["role"] == "assistant" and "tool_calls" in message and message["tool_calls"]:
            with st.expander("🔧 Tool Calls", expanded=False):
                for tc in message["tool_calls"]:
                    st.markdown(f"**{tc['name']}**")
                    if tc.get("args"):
                        st.json(tc["args"])
                    st.text(tc["result"])
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask me about your finances..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, tool_calls = run_agent(prompt)
            st.markdown(response)
            
            # Show tool calls
            if tool_calls:
                with st.expander("🔧 Tool Calls", expanded=False):
                    for tc in tool_calls:
                        st.markdown(f"**{tc['name']}**")
                        if tc.get("args"):
                            st.json(tc["args"])
                        st.text(tc["result"])
                        st.divider()
    
    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "tool_calls": tool_calls
    })
    st.rerun()

# Example prompts
if not st.session_state.messages:
    st.markdown("### 💡 Try asking:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- *Add $25 for lunch*")
        st.markdown("- *Show my spending summary*")
        st.markdown("- *How much did I spend on food?*")
    with col2:
        st.markdown("- *Give me spending insights*")
        st.markdown("- *List all my expenses*")
        st.markdown("- *I spent $100 on groceries*")