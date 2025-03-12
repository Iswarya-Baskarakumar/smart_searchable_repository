import streamlit as st
import sqlite3
import pandas as pd

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('CodeSnippetLibrary.db')  # Create or connect to SQLite database
    return conn

# Function to initialize the database and create the table
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            language TEXT NOT NULL,
            use_case TEXT,
            tags TEXT,
            code TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Call the function to initialize the database
init_db()

# Function to fetch snippets based on search criteria
def fetch_snippets(search_query="", language_filter="", tag_filter=""):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM snippets WHERE 1=1"
    params = []

    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")

    if language_filter and language_filter != "All":
        query += " AND language = ?"
        params.append(language_filter)

    if tag_filter:
        query += " AND tags LIKE ?"
        params.append(f"%{tag_filter}%")

    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    snippets = cursor.fetchall()
    conn.close()
    
    return [{'id': row[0], 'title': row[1], 'language': row[2], 'use_case': row[3], 'tags': row[4], 'code': row[5], 'author': row[6]} for row in snippets]

# Function to get total count of snippets
def get_snippet_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM snippets")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Function to get the top contributor (author with the most snippets)
def get_top_contributor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT author, COUNT(*) as count FROM snippets GROUP BY author ORDER BY count DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result if result else ("No contributors", 0)

# Function to get unique programming languages for filtering
def get_languages():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT language FROM snippets")
    languages = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ["All"] + languages

# Function to insert a new snippet into SQLite
def insert_snippet(title, language, use_case, tags, code, author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO snippets (title, language, use_case, tags, code, author) VALUES (?, ?, ?, ?, ?, ?)",
        (title, language, use_case, tags, code, author),
    )
    conn.commit()
    conn.close()

# Function to update an existing snippet (without modifying the author)
def update_snippet(snippet_id, title, language, use_case, tags, code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE snippets SET title=?, language=?, use_case=?, tags=?, code=? WHERE id=?",
        (title, language, use_case, tags, code, snippet_id),
    )
    conn.commit()
    conn.close()

# Function to delete a snippet
def delete_snippet(snippet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM snippets WHERE id=?", (snippet_id,))
    conn.commit()
    conn.close()
    
# Streamlit UI
st.title("📚 Code Snippet Library")

# Display total snippet count and top contributor
total_snippets = get_snippet_count()
top_contributor, top_contributions = get_top_contributor()

st.write(f"📌 **Total Snippets:** {total_snippets}")
st.write(f"🏆 **Top Contributor:** {top_contributor} ({top_contributions} snippets)")

# Search and filter options
search_query = st.text_input("🔍 Search by Title:")
language_filter = st.selectbox("📌 Filter by Language:", get_languages())
tag_filter = st.text_input("🏷️ Filter by Tag:")

# Fetch and display snippets based on search and filters
snippets = fetch_snippets(search_query, language_filter, tag_filter)

st.write("### Available Snippets")

if snippets:
    for snippet in snippets:
        with st.expander(f"🔹 {snippet['title']} ({snippet['language']})"):
            st.code(snippet['code'], language=snippet['language'].lower())
            st.write(f"**Use Case:** {snippet['use_case']}")
            st.write(f"**Tags:** {snippet['tags']}")
            st.write(f"**Author:** {snippet['author']}")

            col1, col2 = st.columns(2)

            # Edit Form (Author field removed)
            with col1:
                with st.form(f"edit_form_{snippet['id']}"):
                    new_title = st.text_input("Title", snippet['title'])
                    new_language = st.text_input("Language", value=snippet['language'])
                    new_use_case = st.text_input("Use Case", snippet['use_case'])
                    new_tags = st.text_input("Tags", snippet['tags'])
                    new_code = st.text_area("Code Snippet", snippet['code'], height=150)

                    update_submitted = st.form_submit_button("Update Snippet")
                    if update_submitted:
                        update_snippet(snippet['id'], new_title, new_language, new_use_case, new_tags, new_code)
                        st.success("✅ Snippet updated successfully!")
                        st.rerun()

            # Delete Button
            if col2.button("❌ Delete", key=f"delete_{snippet['id']}"):
                delete_snippet(snippet['id'])
                st.warning("⚠️ Snippet deleted!")
                st.rerun()
else:
    st.write("🚫 No snippets available. Please try a different search or filter.")

# UI for adding a new snippet
st.sidebar.title("➕ Add a New Code Snippet")

with st.sidebar.form("snippet_form"):
    title = st.text_input("Snippet Title")
    language = st.text_input("Programming Language")
    use_case = st.text_input("Use Case")
    tags = st.text_input("Tags (comma-separated)")
    code = st.text_area("Code Snippet", height=150)
    author = st.text_input("Author Name")

    submitted = st.form_submit_button("Add Snippet")
    if submitted:
        if title and language and code and author:
            insert_snippet(title, language, use_case, tags, code, author)
            st.sidebar.success("✅ Snippet added successfully!")
            st.rerun()
        else:
            st.sidebar.error("❌ Title, Language, Code, and Author are required fields!")
