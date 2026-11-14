"""
SkillNova AI - High-Performance Native Web Server & REST API
Runs without any third-party pip dependencies using Python's built-in standard library.
Serves both the modern AI SaaS web application and the collaborative Multi-Agent API.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys

# Ensure root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import database as db
from agents.agent_coordinator import AgentCoordinator
from agents.skill_analyzer import SkillAnalyzerAgent
from agents.career_matcher import CareerMatchingAgent
from agents.learning_path import LearningPathAgent
from agents.resource_recommender import ResourceRecommendationAgent
from agents.assessment_agent import AssessmentAgent
from agents.ai_mentor import AICareerMentorAgent

PORT = 8501

# ── Load Gemini API key from .env if present ──
GEMINI_API_KEY = None
_env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _ef:
        for _line in _ef:
            _line = _line.strip()
            if _line.startswith("GEMINI_API_KEY="):
                GEMINI_API_KEY = _line.split("=", 1)[1].strip()
                break
if GEMINI_API_KEY:
    print(f"[✓] Gemini API key loaded ({len(GEMINI_API_KEY)} chars)")
else:
    print("[i] No Gemini API key found — AI Mentor will use rule-based engine")

# Initialize and seed database
db.seed_database()
coordinator = AgentCoordinator(db_module=db)


def _resolve_user(user_id=1):
    u = db.get_user_by_id(user_id)
    if not u:
        u = db.get_default_demo_user()
    return u


class SkillNovaHTTPHandler(http.server.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _get_post_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body)
        return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Static assets
        if path.startswith("/assets/"):
            file_rel = path.lstrip("/")
            file_abs = os.path.join(BASE_DIR, file_rel)
            if os.path.exists(file_abs):
                self.send_response(200)
                if file_abs.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                elif file_abs.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                self.end_headers()
                with open(file_abs, "rb") as f:
                    self.wfile.write(f.read())
                return

        # API Endpoints
        if path == "/api/pipeline":
            user_id = int(query.get("user_id", [1])[0])
            user = db.get_user_by_id(user_id) or db.get_default_demo_user()
            user_skills = db.get_user_skills(user["id"])
            career_reqs = db.get_career_requirements(user["target_career"])
            pipeline_data = coordinator.run_full_pipeline(
                user_id=user["id"],
                user_profile=user,
                user_skills=user_skills,
                career_requirements=career_reqs
            )
            self._send_json(pipeline_data)
            return

        elif path == "/api/user":
            user_id = int(query.get("user_id", [1])[0])
            user = db.get_user_by_id(user_id) or db.get_default_demo_user()
            user_skills = db.get_user_skills(user["id"])
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM certifications WHERE user_id = ?", (user["id"],))
                certs = [dict(r) for r in cursor.fetchall()]
                cursor.execute("SELECT * FROM projects WHERE user_id = ?", (user["id"],))
                projs = [dict(r) for r in cursor.fetchall()]
            self._send_json({
                "user": user,
                "skills": user_skills,
                "certifications": certs,
                "projects": projs
            })
            return

        elif path == "/api/careers":
            user_id = int(query.get("user_id", [1])[0])
            user = db.get_user_by_id(user_id) or db.get_default_demo_user()
            user_skills = db.get_user_skills(user["id"])
            roles = db.get_career_roles()
            matcher = CareerMatchingAgent()

            results = []
            for r in roles:
                r_name = r["name"]
                reqs = db.get_career_requirements(r_name)
                match_res = matcher.match_career(user_skills, r_name, reqs)
                results.append({
                    "career": r_name,
                    "category": r.get("category", "Tech"),
                    "description": r.get("description", ""),
                    "readiness_percentage": match_res["readiness_percentage"],
                    "readiness_tier": match_res["readiness_tier"],
                    "matched_count": match_res["matched_count"],
                    "missing_count": match_res["missing_count"],
                    "matched_skills": match_res["matched_skills"],
                    "missing_skills": match_res["missing_skills"],
                    "formula_summary": match_res["formula_summary"]
                })
            results.sort(key=lambda x: x["readiness_percentage"], reverse=True)
            self._send_json(results)
            return

        elif path == "/api/assessment/questions":
            skill_name = query.get("skill", ["Python"])[0]
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assessment_questions WHERE skill_name = ?", (skill_name,))
                rows = [dict(r) for r in cursor.fetchall()]

            questions = []
            for r in rows:
                q = dict(r)
                q["options"] = json.loads(q["options_json"]) if isinstance(q["options_json"], str) else q["options_json"]
                questions.append(q)
            self._send_json(questions)
            return

        elif path == "/api/resources":
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM learning_resources ORDER BY rating DESC")
                resources = [dict(r) for r in cursor.fetchall()]
            self._send_json(resources)
            return

        elif path == "/api/mentor/history":
            raw_uid = int(query.get("user_id", [1])[0])
            user = _resolve_user(raw_uid)
            user_id = user["id"]
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM mentor_history WHERE user_id = ? ORDER BY id ASC", (user_id,))
                history = [dict(r) for r in cursor.fetchall()]
            self._send_json(history)
            return

        elif path == "/api/logs":
            raw_uid = int(query.get("user_id", [1])[0])
            user = _resolve_user(raw_uid)
            logs = db.get_agent_activities(user_id=user["id"], limit=40)
            self._send_json(logs)
            return

        # Serve SPA index.html
        if path == "/" or path == "/index.html":
            index_file = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(index_file):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(index_file, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        global GEMINI_API_KEY
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._get_post_json()

        if path == "/api/career/set":
            user_id = _resolve_user(body.get("user_id", 1))["id"]
            target_career = body.get("target_career")
            with db.get_connection() as conn:
                conn.execute("UPDATE users SET target_career = ? WHERE id = ?", (target_career, user_id))
                conn.commit()
            db.log_agent_activity(
                user_id=user_id,
                agent_name="Career Matching Agent",
                task=f"Switched Target Career to {target_career}",
                input_data={"target_career": target_career},
                output_data={"status": "Updated and re-indexed"}
            )
            self._send_json({"status": "success", "target_career": target_career})
            return

        elif path == "/api/skills/add":
            user_id = _resolve_user(body.get("user_id", 1))["id"]
            skill_name = body.get("skill_name", "").strip()
            level = body.get("proficiency_level", "Beginner")
            if skill_name:
                with db.get_connection() as conn:
                    conn.execute("""
                        INSERT INTO user_skills (user_id, skill_name, proficiency_level)
                        VALUES (?, ?, ?)
                        ON CONFLICT(user_id, skill_name) DO UPDATE SET proficiency_level=excluded.proficiency_level
                    """, (user_id, skill_name, level))
                    conn.commit()
                db.log_agent_activity(
                    user_id=user_id,
                    agent_name="Skill Analyzer Agent",
                    task=f"Added/Updated Skill: {skill_name} ({level})",
                    input_data={"skill": skill_name, "level": level},
                    output_data={"status": "Saved"}
                )
                self._send_json({"status": "success", "skill": skill_name, "level": level})
            else:
                self._send_json({"status": "error", "message": "Skill name required"}, 400)
            return

        elif path == "/api/skills/delete":
            skill_id = body.get("skill_id")
            user_id = _resolve_user(body.get("user_id", 1))["id"]
            with db.get_connection() as conn:
                conn.execute("DELETE FROM user_skills WHERE id = ? AND user_id = ?", (skill_id, user_id))
                conn.commit()
            self._send_json({"status": "success"})
            return

        elif path == "/api/assessment/submit":
            user_id = _resolve_user(body.get("user_id", 1))["id"]
            skill_name = body.get("skill_name")
            user_answers = body.get("answers", {})  # {q_id: selected_index}

            # Retrieve questions
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assessment_questions WHERE skill_name = ?", (skill_name,))
                rows = [dict(r) for r in cursor.fetchall()]

            questions = []
            for r in rows:
                q = dict(r)
                q["options"] = json.loads(q["options_json"]) if isinstance(q["options_json"], str) else q["options_json"]
                questions.append(q)

            eval_res = coordinator.assessment_agent.evaluate_submission(skill_name, questions, user_answers)

            # Store in Database
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO assessments (user_id, skill_name, score, total_questions, correct_answers, proficiency_assessed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    skill_name,
                    eval_res["score"],
                    eval_res["total_questions"],
                    eval_res["correct_count"],
                    eval_res["proficiency_recommendation"]
                ))
                assessment_id = cursor.lastrowid

                # Update proficiency based on score
                rec_level = eval_res["proficiency_recommendation"]
                cursor.execute("""
                    INSERT INTO user_skills (user_id, skill_name, proficiency_level, verified)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(user_id, skill_name) DO UPDATE SET proficiency_level=?, verified=1
                """, (user_id, skill_name, rec_level, rec_level))
                conn.commit()

            db.log_agent_activity(
                user_id=user_id,
                agent_name="Assessment & Progress Agent",
                task=f"Evaluated Assessment for {skill_name}",
                input_data={"skill": skill_name, "score": eval_res["score"]},
                output_data={"directive": eval_res["adaptive_directive"]}
            )
            self._send_json(eval_res)
            return

        elif path == "/api/mentor/chat":
            user_id = body.get("user_id", 1)
            user_msg = body.get("message", "")
            user = db.get_user_by_id(user_id) or db.get_default_demo_user()
            actual_uid = user["id"]
            user_skills = db.get_user_skills(actual_uid)
            career_reqs = db.get_career_requirements(user["target_career"])
            pipeline = coordinator.run_full_pipeline(actual_uid, user, user_skills, career_reqs)

            # Save user message
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO mentor_history (user_id, role, message, intent)
                    VALUES (?, 'user', ?, 'question')
                """, (actual_uid, user_msg))
                conn.commit()

            mentor_res = coordinator.ai_mentor.generate_response(
                user_message=user_msg,
                user_context=user,
                matched_skills=pipeline["career_matching"]["matched_skills"],
                missing_skills=pipeline["career_matching"]["missing_skills"],
                readiness_pct=pipeline["career_matching"]["readiness_percentage"],
                roadmap_phases=pipeline["roadmap_phases"],
                api_key=body.get("api_key") or GEMINI_API_KEY
            )

            # Save assistant reply
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO mentor_history (user_id, role, message, intent)
                    VALUES (?, 'assistant', ?, ?)
                """, (actual_uid, mentor_res["response"], mentor_res.get("intent", "general")))
                conn.commit()

            db.log_agent_activity(
                user_id=actual_uid,
                agent_name="AI Career Mentor Agent",
                task="Advised Learner on Career Direction",
                input_data={"query": user_msg},
                output_data={"intent": mentor_res.get("intent")}
            )
            self._send_json(mentor_res)
            return

        elif path == "/api/reset":
            db.seed_database(force_reset=True)
            self._send_json({"status": "success", "message": "Demo profile restored."})
            return

        elif path == "/api/settings/apikey":
            new_key = body.get("api_key", "").strip()
            if new_key:
                GEMINI_API_KEY = new_key
                # persist to .env
                env_file = os.path.join(BASE_DIR, ".env")
                with open(env_file, "w") as ef:
                    ef.write(f"GEMINI_API_KEY={new_key}\n")
                self._send_json({"status": "success", "message": "Gemini API key saved!"})
            else:
                self._send_json({"status": "error", "message": "No key provided"}, 400)
            return

        self.send_error(404, "Endpoint Not Found")


def run_server(port=PORT):
    # Enable address reuse to avoid port binding errors on restart
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SkillNovaHTTPHandler) as httpd:
        print(f"SkillNova AI server active and listening at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down SkillNova AI server...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
