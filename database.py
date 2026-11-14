"""
SkillNova AI - Database Layer
Manages SQLite connection, schema definition, seed data, and CRUD operations.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "skillnova.db")


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DB_FILE) -> None:
    """Creates all 15 required relational tables if they do not exist."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                education TEXT,
                department TEXT,
                target_career TEXT NOT NULL,
                career_goals TEXT,
                learning_interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. skills master catalog
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                description TEXT
            );
        """)

        # 3. user_skills
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                proficiency_level TEXT NOT NULL CHECK(proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
                verified INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, skill_name)
            );
        """)

        # 4. certifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                issuer TEXT,
                issue_date TEXT,
                credential_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 5. projects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                technologies TEXT,
                repo_url TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 6. career_roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                description TEXT
            );
        """)

        # 7. career_requirements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                career_name TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                importance TEXT DEFAULT 'High' CHECK(importance IN ('Critical', 'High', 'Medium', 'Optional')),
                weight REAL DEFAULT 1.0,
                min_level TEXT DEFAULT 'Intermediate',
                FOREIGN KEY (career_name) REFERENCES career_roles(name) ON DELETE CASCADE
            );
        """)

        # 8. learning_roadmap
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_roadmap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phase_number INTEGER NOT NULL,
                phase_name TEXT NOT NULL,
                target_skills TEXT NOT NULL,
                learning_objectives TEXT,
                topics TEXT,
                estimated_duration TEXT,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Completed')),
                completion_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 9. learning_resources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                title TEXT NOT NULL,
                type TEXT,
                provider TEXT,
                url TEXT NOT NULL,
                difficulty TEXT,
                duration TEXT,
                rating REAL DEFAULT 4.8
            );
        """)

        # 10. assessments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                score REAL NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                proficiency_assessed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 11. assessment_questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_questions (
                id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                answer_index INTEGER NOT NULL,
                explanation TEXT
            );
        """)

        # 12. assessment_results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                user_answer_index INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
            );
        """)

        # 13. learning_progress
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_skills_count INTEGER DEFAULT 0,
                matched_skills_count INTEGER DEFAULT 0,
                missing_skills_count INTEGER DEFAULT 0,
                readiness_score REAL DEFAULT 0.0,
                completion_percentage REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 14. mentor_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mentor_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                message TEXT NOT NULL,
                intent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 15. agent_activity
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                agent_name TEXT NOT NULL,
                task TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                status TEXT DEFAULT 'Success',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()


def seed_database(db_path: str = DB_FILE, force_reset: bool = False) -> None:
    """Seeds career paths, questions, catalog resources, and the Hackathon Demo Student."""
    init_db(db_path)
    base_dir = os.path.dirname(__file__)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'demo.student@skillnova.ai'")
        exists = cursor.fetchone()[0] > 0
        if exists and not force_reset:
            return

        if force_reset:
            cursor.execute("DELETE FROM agent_activity")
            cursor.execute("DELETE FROM mentor_history")
            cursor.execute("DELETE FROM learning_progress")
            cursor.execute("DELETE FROM assessment_results")
            cursor.execute("DELETE FROM assessments")
            cursor.execute("DELETE FROM learning_roadmap")
            cursor.execute("DELETE FROM projects")
            cursor.execute("DELETE FROM certifications")
            cursor.execute("DELETE FROM user_skills")
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM career_requirements")
            cursor.execute("DELETE FROM career_roles")
            cursor.execute("DELETE FROM learning_resources")
            cursor.execute("DELETE FROM assessment_questions")

        # 1. Load Career Skills JSON
        career_file = os.path.join(base_dir, "data", "career_skills.json")
        if os.path.exists(career_file):
            with open(career_file, "r", encoding="utf-8") as f:
                careers_data = json.load(f)

            for career_name, details in careers_data.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO career_roles (name, category, description)
                    VALUES (?, ?, ?)
                """, (career_name, details.get("category", "General"), details.get("description", "")))

                for req in details.get("required_skills", []):
                    cursor.execute("""
                        INSERT INTO career_requirements (career_name, skill_name, importance, weight, min_level)
                        VALUES (?, ?, ?, ?, ?)
                    """, (career_name, req["name"], req.get("importance", "High"), req.get("weight", 1.0), req.get("min_level", "Intermediate")))

        # 2. Load Assessment Questions JSON
        questions_file = os.path.join(base_dir, "data", "assessment_questions.json")
        if os.path.exists(questions_file):
            with open(questions_file, "r", encoding="utf-8") as f:
                questions_data = json.load(f)

            for q in questions_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO assessment_questions (id, skill_name, difficulty, question, options_json, answer_index, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (q["id"], q["skill"], q["difficulty"], q["question"], json.dumps(q["options"]), q["answer_index"], q.get("explanation", "")))

        # 3. Load Sample Data & Resources
        sample_file = os.path.join(base_dir, "data", "sample_data.json")
        if os.path.exists(sample_file):
            with open(sample_file, "r", encoding="utf-8") as f:
                sample_data = json.load(f)

            # Insert Resources Catalog
            for res in sample_data.get("learning_resources_catalog", []):
                cursor.execute("""
                    INSERT INTO learning_resources (skill_name, title, type, provider, url, difficulty, duration, rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (res["skill"], res["title"], res["type"], res["provider"], res["url"], res["difficulty"], res["duration"], res.get("rating", 4.8)))

            # Insert Demo User
            user_info = sample_data.get("user", {})
            cursor.execute("""
                INSERT INTO users (name, email, education, department, target_career, career_goals, learning_interests)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_info.get("name", "Demo Student"),
                user_info.get("email", "demo.student@skillnova.ai"),
                user_info.get("education", "BSc Computer Science"),
                user_info.get("department", "Computer Science & Engineering"),
                user_info.get("target_career", "Full Stack Developer"),
                user_info.get("career_goals", "Become a full-stack engineer"),
                user_info.get("learning_interests", "Web Development, AI")
            ))
            demo_user_id = cursor.lastrowid

            # Insert Skills
            for sk in sample_data.get("skills", []):
                cursor.execute("""
                    INSERT INTO user_skills (user_id, skill_name, proficiency_level)
                    VALUES (?, ?, ?)
                """, (demo_user_id, sk["name"], sk["level"]))

            # Insert Certifications
            for cert in sample_data.get("certifications", []):
                cursor.execute("""
                    INSERT INTO certifications (user_id, name, issuer, issue_date, credential_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (demo_user_id, cert["name"], cert.get("issuer"), cert.get("issue_date"), cert.get("credential_id")))

            # Insert Projects
            for proj in sample_data.get("projects", []):
                cursor.execute("""
                    INSERT INTO projects (user_id, title, description, technologies, repo_url)
                    VALUES (?, ?, ?, ?, ?)
                """, (demo_user_id, proj["title"], proj.get("description"), proj.get("technologies"), proj.get("repo_url")))

            # Initial seed of agent log
            cursor.execute("""
                INSERT INTO agent_activity (user_id, agent_name, task, input_data, output_data, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                demo_user_id,
                "System Initializer",
                "Bootstrapped Hackathon Demo Profile",
                json.dumps({"user": "Demo Student", "target_career": "Full Stack Developer"}),
                json.dumps({"status": "Initialized with 3 skills, 1 certification, 1 project"}),
                "Success"
            ))

        conn.commit()


# Helper query methods
def get_user_by_id(user_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_default_demo_user(db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_skills(user_id: int, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_skills WHERE user_id = ? ORDER BY skill_name ASC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]


def get_career_roles(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM career_roles ORDER BY name ASC")
        return [dict(r) for r in cursor.fetchall()]


def get_career_requirements(career_name: str, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM career_requirements WHERE career_name = ? ORDER BY weight DESC", (career_name,))
        return [dict(r) for r in cursor.fetchall()]


def log_agent_activity(user_id: int, agent_name: str, task: str, input_data: Any, output_data: Any, status: str = "Success", db_path: str = DB_FILE) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        in_str = json.dumps(input_data) if not isinstance(input_data, str) else input_data
        out_str = json.dumps(output_data) if not isinstance(output_data, str) else output_data
        cursor.execute("""
            INSERT INTO agent_activity (user_id, agent_name, task, input_data, output_data, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, agent_name, task, in_str, out_str, status))
        conn.commit()


def get_agent_activities(user_id: Optional[int] = None, limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM agent_activity WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        else:
            cursor.execute("SELECT * FROM agent_activity ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]
