import streamlit as st
import pandas as pd
import sqlite3

# Create a connection to the database
def get_db_connection():
    conn = sqlite3.connect('CodeSnippetLibrary.db')
    return conn

# Initialize the database
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
   
# Initialize the database
init_db()

# Fetch snippets from the database
def fetch_snippets(search_query ="", language_filter = "", tag_filter = ""):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * from snippets where 1=1'
    params = []

    if search_query:
        query += " AND (title LIKE ?" 
        params.append(f"%{search_query}%")
        
    if language_filter and language_filter != "All":
            query += " AND language = ?"
            params.append(language_filter)
            
    if tag_filter:
        query += " AND tag = ?"
        params.append(f"%{tag_filter}%")
        
    query += " ORDER BY created_at DESC"            

    cursor.execute(query, params)
    snippets = cursor.fetchall()   
    conn.close()

    return [{'id': row[0], 'title': row[1], 'language': row[2], 'use_case': row[3], 'tags': row[4], 'code': row[5] ,'author': row[6]} for row in snippets]
    
def get_snippet_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM snippets")
    count = cursor.fetchone()[0]
    conn.close()
    return count   
    
def get_top_contribute():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT author, COUNT(*) as count FROM snippets GROUP BY author ORDER BY count DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result if result else ("No contribute", 0)
        
def get_languages():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT language FROM snippets")
        languages = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ["All"] + languages
            
def insert_snippet(title, language, use_case, tags, code, author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO snippets (title, language, use_case, tags, code, author) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, language, use_case, tags, code, author),
    )
    conn.commit()
    conn.close()
        
def update_snippet(snippet_id, title, language, use_case, tags, code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE snippets SET title = ?, language = ?, use_case = ?, tags = ?, code = ? WHERE id = ?",
                   (title, language, use_case, tags, code, snippet_id),
    )
    conn.commit()
    conn.close()

def delete_snippet(snippet_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("delete from snippets where id = ?", (snippet_id,))
    conn.commit()
    conn.close()

st.title("Code Snippet Library")

total_snippets = get_snippet_count()
top_contributor, top_contributions = get_top_contribute()

st.write(f"Total snippets: {total_snippets}")
st.write(f"Top contributor: {top_contributor} ({top_contributions} snippets)")

search_query = st.text_input("Search by title:")
language_filter = st.selectbox("Filter by language", get_languages())
tag_filter = st.text_input("Filter by tag")

snippets = fetch_snippets(search_query, language_filter, tag_filter)

st.write("### Available Snippets")
        
if snippets:
    for snippet in snippets:
        with st.expander(f"{snippet["title"]} ({snippet['language']}"):
            st.code(snippet['code'], language=snippet['language'].lower())
            st.write(f"**Use case:** {snippet['use_case']}")
            st.write(f"**Tags:** {snippet['tags']}")
            st.write(f"**Author:** {snippet['author']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form(f"edit_snippet_{snippet['id']}"):
                    new_title = st.text_input("Title", value=snippet['title'])
                    new_language = st.text_input("Language", value=snippet['language'])
                    new_use_case = st.text_input("Use case", value=snippet['use_case'])
                    new_tags = st.text_input("Tags", value=snippet['tags'])
                    new_code = st.text_area("Code", value=snippet['code'], height=150)
                    
                    update_submitted = st.form_submit_button("Update Snippet")
                    if update_submitted:
                        update_snippet(snippet['id'], new_title, new_language, new_use_case, new_tags, new_code)
                        st.success("Snippet updated successfully")
                        st.rerun()
                        
            if col2.button("Delete", key=f"delete_{snippet['id']}"):
                delete_snippet(snippet['id'])
                st.success("Snippet deleted successfully")
                st.rerun()                           
                            
else:
    st.write("No snippets Available. Please try differenet filters or search.")     
            
st.sidebar.title(" Add New Snippet")

with st.sidebar.form("snippet_form"):
    title = st.text_input("Snippet Title")
    language = st.text_input("Programming Language")
    use_case = st.text_input("Use case")
    tags = st.text_input("Tags (comma separated)")
    code = st.text_area("Code Snippet", height=150)
    author = st.text_input("Author Name")

            
            
    submitted = st.form_submit_button("Add Snippet")
    if submitted:
        if title and language and use_case and code and author:
            insert_snippet(title, language, use_case, tags, code, author)
            st.sidebar.success("Snippet added successfully")
            st.rerun()
        else:
            st.sidebar.error("All fields are required")     
                   
                                   