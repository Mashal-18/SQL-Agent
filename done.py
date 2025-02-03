import pandas as pd
import sqlite3
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Excel data
excel_file = 'students_marks.xlsx'  # Provide the actual path of the Excel file
sheet_data = pd.read_excel(excel_file)

# Preview the data to understand its structure
print(sheet_data.head())

# Connect to SQLite database (creates a new file or connects to existing one)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Dynamically create table based on the Excel columns
columns = ', '.join([f'"{col}" TEXT' for col in sheet_data.columns])
create_table_query = f'CREATE TABLE IF NOT EXISTS excel_data ({columns})'
cursor.execute(create_table_query)

# Insert data into the SQL table
for _, row in sheet_data.iterrows():
    values = tuple(row)
    placeholders = ', '.join(['?'] * len(values))
    insert_query = f'''INSERT INTO excel_data ({", ".join([f'"{col}"' for col in sheet_data.columns])}) VALUES ({placeholders})'''
    cursor.execute(insert_query, values)

conn.commit()

def generate_sql_query(user_query):
    """
    Generates an SQL query based on the user's natural language input
    using OpenAI's GPT-4 (chat model).
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that converts natural language questions into SQL queries."},
        {"role": "user", "content": user_query}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the GPT-4 chat model
        messages=messages,
        max_tokens=100
    )
    
    sql_query = response['choices'][0]['message']['content'].strip()
    return sql_query

def execute_sql_query(query):
    """
    Executes the SQL query and returns the result.
    """
    cursor.execute(query)
    return cursor.fetchall()

def format_results_with_llm(results):
    """
    Formats the SQL query results using OpenAI's GPT-4 (chat model).
    """
    results_str = "\n".join([str(row) for row in results])
    messages = [
        {"role": "system", "content": "You are a helpful assistant that formats SQL query results into a readable and concise format."},
        {"role": "user", "content": f"Format the following results:\n{results_str}"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the GPT-4 chat model
        messages=messages,
        max_tokens=150
    )
    
    formatted_results = response['choices'][0]['message']['content'].strip()
    return formatted_results

def list_tables():
    """
    Lists all table names in the SQLite database.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

# Call the function to list tables
list_tables()

# Main loop to interact with the user
while True:
    user_query = input("Ask a question (or type 'exit' to quit): ")
    if user_query.lower() == 'exit':
        break
    
    # Use LLM to convert the natural language query to SQL
    sql_query = generate_sql_query(user_query)
    print(f"Generated SQL: {sql_query}")
    
    # Manually correct the generated SQL query if needed
    sql_query = sql_query.replace('`TableName`', 'excel_data').replace('`Pass/Fail Status`', '`Pass/Fail`')
    print(f"Corrected SQL: {sql_query}")
    
    # Execute the SQL query
    try:
        result = execute_sql_query(sql_query)
        print("Raw Result:")
        for row in result:
            print(row)
        
        # Format the results using LLM
        formatted_result = format_results_with_llm(result)
        print("Formatted Result:")
        print(formatted_result)
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")

# Close the database connection
conn.close()