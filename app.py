"""
SkillNova AI - Collaborative Multi-Agent Adaptive Learning & Career Intelligence Platform
Tagline: Discover Skills. Bridge Gaps. Build Your Future.
Main Application Entrypoint.
"""

import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="SkillNova AI - Career Intelligence",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Database & Agents
import database as db
from agents.agent_coordinator import AgentCoordinator
from modules.profile import render_profile_view
from modules.skill_analysis import render_skill_analysis_view
from modules.career_matching import render_career_explorer_view
from modules.roadmap import render_roadmap_view
from modules.resources import render_resources_view
from modules.assessment import render_assessment_view
from modules.progress import render_progress_view
from modules.mentor import render_mentor_view


# Load CSS
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# Seed database on first startup
if "db_initialized" not in st.session_state:
    db.seed_database()
    st.session_state["db_initialized"] = True

# Initialize Demo User in Session State
if "current_user_id" not in st.session_state:
    demo_user = db.get_default_demo_user()
    st.session_state["current_user_id"] = demo_user["id"] if demo_user else 1

user_id = st.session_state["current_user_id"]
user = db.get_user_by_id(user_id)
if not user:
    db.seed_database(force_reset=True)
    user = db.get_default_demo_user()

user_skills = db.get_user_skills(user_id)
career_reqs = db.get_career_requirements(user["target_career"])

# Coordinator execution & pipeline caching
coordinator = AgentCoordinator(db_module=db)

if ("pipeline_cache" not in st.session_state or
    st.session_state.get("pipeline_needs_refresh", False)):
    pipeline_res = coordinator.run_full_pipeline(
        user_id=user_id,
        user_profile=user,
        user_skills=user_skills,
        career_requirements=career_reqs
    )
    st.session_state["pipeline_cache"] = pipeline_res
    st.session_state["pipeline_needs_refresh"] = False
else:
    pipeline_res = st.session_state["pipeline_cache"]

skill_analysis = pipeline_res["skill_analysis"]
career_matching = pipeline_res["career_matching"]
roadmap_phases = pipeline_res["roadmap_phases"]
recommended_resources = pipeline_res["recommended_resources"]


# ==========================================================
# SIDEBAR NAVIGATION & BRANDING
# ==========================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.8rem 0 1.2rem 0; border-bottom: 1px solid rgba(79, 128, 225, 0.2); margin-bottom: 1rem;">
        <div style="font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #60A5FA, #C084FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🌌 SkillNova AI
        </div>
        <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 500; margin-top: 0.2rem;">
            Discover Skills. Bridge Gaps. Build Your Future.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active User Profile Summary in Sidebar
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.7rem 0.9rem; margin-bottom: 1.2rem;">
        <div style="font-size: 0.8rem; color: #818CF8; font-weight: 600; text-transform: uppercase;">Learner Profile</div>
        <div style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">{user['name']}</div>
        <div style="font-size: 0.8rem; color: #94A3B8;">Role: <span style="color: #38BDF8;">{user['target_career']}</span></div>
        <div style="font-size: 0.8rem; color: #34D399; margin-top: 0.3rem;">Readiness: <strong>{career_matching['readiness_percentage']}%</strong></div>
    </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "Navigation",
        [
            "Dashboard",
            "My Profile",
            "Skill Assessment",
            "Skill Gap Analysis",
            "Career Explorer",
            "Personalized Learning Roadmap",
            "Learning Resources",
            "Progress Tracker",
            "AI Career Mentor",
            "Multi-Agent Activity Center",
            "Settings"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)

    # Multi-Agent Status Monitor in Sidebar
    st.markdown("""
    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
        🤖 Multi-Agent Fleet Status
    </div>
    """, unsafe_allow_html=True)
    agents_status = [
        ("Skill Analyzer", "Active"),
        ("Career Matcher", "Active"),
        ("Learning Path", "Active"),
        ("Resource Curator", "Active"),
        ("Assessment Engine", "Active"),
        ("AI Career Mentor", "Active")
    ]
    for a_name, a_stat in agents_status:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 0.35rem; color: #CBD5E1;">
            <span>• {a_name}</span>
            <span style="color: #34D399; font-weight: 600;">● {a_stat}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset Demo Student Data", use_container_width=True):
        db.seed_database(force_reset=True)
        st.session_state["pipeline_needs_refresh"] = True
        st.toast("Restored Demo Student hackathon profile!")
        st.rerun()


# ==========================================================
# PAGE ROUTING
# ==========================================================

# 1. DASHBOARD PAGE
if nav_selection == "Dashboard":
    # Hero Welcome Banner
    completed_phases = sum(1 for p in roadmap_phases if p.get("status") == "Completed")
    learning_progress_pct = round((completed_phases / len(roadmap_phases) * 100), 1) if roadmap_phases else 0.0

    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-title">Welcome back, {user['name']} 👋</div>
        <div class="hero-tagline">
            SkillNova AI collaborative agents have evaluated your portfolio against <strong>{user['target_career']}</strong> industry benchmarks.
        </div>
        <div style="display: flex; gap: 1.5rem; margin-top: 1.2rem; flex-wrap: wrap;">
            <span class="agent-badge badge-active">Target Role: {user['target_career']}</span>
            <span class="agent-badge badge-matched">Readiness: {career_matching['readiness_percentage']}%</span>
            <span class="agent-badge">Roadmap Progress: {learning_progress_pct}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 10 Metric Cards Required by Section 3:
    # 1. Total Existing Skills
    # 2. Matched Skills
    # 3. Missing Skills
    # 4. Career Readiness %
    # 5. Learning Progress %
    # 6. Recommended Next Activity
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Existing Skills</div>
            <div class="stat-value" style="color: #38BDF8;">{len(user_skills)}</div>
            <div style="color: #64748B; font-size: 0.8rem;">In Learner Profile</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Matched Skills</div>
            <div class="stat-value" style="color: #34D399;">{career_matching['matched_count']}</div>
            <div style="color: #64748B; font-size: 0.8rem;">Role Compatible</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Missing Skills</div>
            <div class="stat-value" style="color: #F43F5E;">{career_matching['missing_count']}</div>
            <div style="color: #64748B; font-size: 0.8rem;">Curriculum Target</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Career Readiness</div>
            <div class="stat-value" style="color: #60A5FA;">{career_matching['readiness_percentage']}%</div>
            <div style="color: #64748B; font-size: 0.8rem;">Weighted Benchmark</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Roadmap Done</div>
            <div class="stat-value" style="color: #C084FC;">{learning_progress_pct}%</div>
            <div style="color: #64748B; font-size: 0.8rem;">{completed_phases}/{len(roadmap_phases)} Completed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Next Learning Activity & Fast Action Callout
    next_phase = next((p for p in roadmap_phases if p.get("status") in ["In Progress", "Pending"]), None)
    top_resource = recommended_resources[0] if recommended_resources else None

    c_rec1, c_rec2 = st.columns([3, 2])
    with c_rec1:
        st.markdown(f"""
        <div class="glass-panel" style="border-left: 4px solid #38BDF8;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div class="glass-panel-title">⚡ Recommended Next Learning Activity</div>
                <span class="agent-badge badge-matched">Autonomous Recommendation</span>
            </div>
            <p style="color: #F8FAFC; font-size: 1.1rem; font-weight: 600; margin: 0.3rem 0;">
                {next_phase['phase_name'] if next_phase else 'All curriculum phases achieved!'}
            </p>
            <p style="color: #94A3B8; font-size: 0.92rem;">
                <strong>Key Focus:</strong> {next_phase['learning_objectives'] if next_phase else 'Ready for senior job placement and capstone showcases.'}
            </p>
            {f"<div style='margin-top: 0.6rem;'><a href='{top_resource['url']}' target='_blank' style='display: inline-block; padding: 0.4rem 0.9rem; background: #2563EB; color: white; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600;'>Start Learning: {top_resource['title']} ↗</a></div>" if top_resource else ""}
        </div>
        """, unsafe_allow_html=True)

    with c_rec2:
        st.markdown(f"""
        <div class="glass-panel" style="border-left: 4px solid #A855F7;">
            <div class="glass-panel-title">🎯 Career Readiness Status</div>
            <p style="color: #F1F5F9; font-size: 1rem; margin: 0.3rem 0;">
                Tier: <strong style="color: #38BDF8;">{career_matching['readiness_tier']}</strong>
            </p>
            <p style="color: #94A3B8; font-size: 0.88rem;">
                {career_matching['formula_summary']}
            </p>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #34D399;">
                ✓ Multi-Agent pipeline refreshed and synchronized with SQLite database.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Interactive Quick Charts on Dashboard
    col_chart_left, col_chart_right = st.columns([1, 1])
    with col_chart_left:
        st.markdown('<div class="glass-panel-title">📊 Competency Breakdown for Target Career</div>', unsafe_allow_html=True)
        breakdown_df = pd.DataFrame([
            {"Type": "Matched Skills", "Count": career_matching['matched_count']},
            {"Type": "Priority Gaps", "Count": career_matching['priority_missing_count']},
            {"Type": "Other Missing", "Count": career_matching['missing_count'] - career_matching['priority_missing_count']}
        ])
        fig_dash = px.pie(
            breakdown_df,
            names="Type",
            values="Count",
            hole=0.6,
            color="Type",
            color_discrete_map={
                "Matched Skills": "#10B981",
                "Priority Gaps": "#F43F5E",
                "Other Missing": "#6366F1"
            }
        )
        fig_dash.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#CBD5E1"), orientation="h", y=-0.1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=250
        )
        st.plotly_chart(fig_dash, use_container_width=True)

    with col_chart_right:
        st.markdown('<div class="glass-panel-title">🗺️ Roadmap Milestone Stages</div>', unsafe_allow_html=True)
        phase_names = [f"P{p['phase_number']}: {p['target_skills']}" for p in roadmap_phases]
        phase_statuses = [1 if p.get("status") == "Completed" else (0.5 if p.get("status") == "In Progress" else 0.1) for p in roadmap_phases]
        fig_phases = go.Figure(go.Bar(
            x=phase_statuses,
            y=phase_names,
            orientation='h',
            marker=dict(
                color=phase_statuses,
                colorscale=[[0, '#334155'], [0.5, '#38BDF8'], [1.0, '#10B981']]
            )
        ))
        fig_phases.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(14,22,38,0.4)",
            xaxis=dict(visible=False, range=[0, 1.1]),
            yaxis=dict(color="#CBD5E1", autorange="reversed"),
            height=250,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_phases, use_container_width=True)


# 2. MY PROFILE
elif nav_selection == "My Profile":
    render_profile_view(user_id=user_id)

# 3. SKILL ASSESSMENT
elif nav_selection == "Skill Assessment":
    render_assessment_view(user_id=user_id)

# 4. SKILL GAP ANALYSIS
elif nav_selection == "Skill Gap Analysis":
    render_skill_analysis_view(analysis_data=skill_analysis, career_match_data=career_matching)

# 5. CAREER EXPLORER
elif nav_selection == "Career Explorer":
    render_career_explorer_view(user_id=user_id, user_skills=user_skills, current_target_career=user["target_career"])

# 6. PERSONALIZED LEARNING ROADMAP
elif nav_selection == "Personalized Learning Roadmap":
    render_roadmap_view(user_id=user_id, target_career=user["target_career"], roadmap_phases=roadmap_phases)

# 7. LEARNING RESOURCES
elif nav_selection == "Learning Resources":
    render_resources_view(recommended_resources=recommended_resources, target_career=user["target_career"])

# 8. PROGRESS TRACKER
elif nav_selection == "Progress Tracker":
    render_progress_view(
        user_id=user_id,
        readiness_score=career_matching["readiness_percentage"],
        roadmap_phases=roadmap_phases,
        user_skills=user_skills
    )

# 9. AI CAREER MENTOR
elif nav_selection == "AI Career Mentor":
    render_mentor_view(
        user_id=user_id,
        user_context=user,
        matched_skills=career_matching["matched_skills"],
        missing_skills=career_matching["missing_skills"],
        readiness_pct=career_matching["readiness_percentage"],
        roadmap_phases=roadmap_phases,
        api_key=st.session_state.get("llm_api_key", None)
    )

# 10. MULTI-AGENT ACTIVITY CENTER
elif nav_selection == "Multi-Agent Activity Center":
    st.markdown('<div class="hero-title">🤖 Multi-Agent Activity & Orchestration Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline">Inspect the live collaborative communication, execution traces, and decision logs among all 6 specialized AI agents.</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Agent Fleet Cards
    st.markdown('<div class="glass-panel-title">Fleet Specifications & Division of Labor</div>', unsafe_allow_html=True)
    agent_specs = [
        {"name": "Skill Analyzer Agent", "role": "Skill Decomposition & Proficiency", "desc": "Evaluates raw user competencies, identifies strong vs weak skills, and surfaces targeted recommendations."},
        {"name": "Career Matching Agent", "role": "Career Benchmarking & Readiness", "desc": "Calculates mathematically weighted readiness scores and identifies missing vs matched skill gaps."},
        {"name": "Learning Path Agent", "role": "Curriculum Architecture", "desc": "Generates chronological multi-phase roadmaps and updates phases based on diagnostic test performance."},
        {"name": "Resource Recommender Agent", "role": "Educational Material Curator", "desc": "Discovers and filters vetted, zero-cost courses, documentation, and exercises matching learner level."},
        {"name": "Assessment & Progress Agent", "role": "Diagnostic Evaluator", "desc": "Administers adaptive MCQs, calculates scores, and feeds performance signals to the coordinator."},
        {"name": "AI Career Mentor Agent", "role": "Personalized Career Strategist", "desc": "Provides real-time contextual guidance, concept explanations, and tailored project architectures."}
    ]

    cols_agent = st.columns(3)
    for idx, ag in enumerate(agent_specs):
        col = cols_agent[idx % 3]
        col.markdown(f"""
        <div class="glass-panel" style="margin-bottom: 0.8rem; height: 190px;">
            <div style="display: flex; justify-content: space-between;">
                <span class="agent-badge badge-active">{ag['name']}</span>
                <span style="color: #34D399; font-size: 0.8rem;">● Online</span>
            </div>
            <div style="font-weight: 700; color: #F1F5F9; font-size: 0.95rem; margin: 0.4rem 0 0.2rem 0;">{ag['role']}</div>
            <p style="color: #94A3B8; font-size: 0.82rem; line-height: 1.35;">{ag['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Workflow Architecture Diagram
    st.markdown('<div class="glass-panel-title">🔄 Multi-Agent Pipeline Dataflow</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(79, 128, 225, 0.2); border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 1.5rem;">
        <span class="agent-badge" style="background: #1E293B; color: #F8FAFC;">Learner Profile & Goals</span>
        <span style="color: #60A5FA;"> ➔ </span>
        <span class="agent-badge badge-active">Skill Analyzer Agent</span>
        <span style="color: #60A5FA;"> ➔ </span>
        <span class="agent-badge badge-matched">Career Matching Agent</span>
        <span style="color: #60A5FA;"> ➔ </span>
        <span class="agent-badge" style="color: #C084FC; border-color: #A855F7;">Learning Path Agent</span>
        <br><br>
        <span style="color: #60A5FA;">⬇ Feedback Loop</span>
        <br><br>
        <span class="agent-badge" style="color: #34D399; border-color: #10B981;">AI Career Mentor Agent</span>
        <span style="color: #60A5FA;"> ⬅ </span>
        <span class="agent-badge badge-missing">Assessment & Progress Agent</span>
        <span style="color: #60A5FA;"> ⬅ </span>
        <span class="agent-badge" style="color: #F59E0B; border-color: #F59E0B;">Resource Recommendation Agent</span>
    </div>
    """, unsafe_allow_html=True)

    # Live Database Execution Logs
    st.markdown('<div class="glass-panel-title">📜 Real-Time Agent Execution & Decision Logs</div>', unsafe_allow_html=True)
    logs = db.get_agent_activities(user_id=user_id, limit=30)
    if logs:
        for l in logs:
            st.markdown(f"""
            <div class="log-item">
                <span style="color: #60A5FA;">[{l['timestamp']}]</span> &nbsp;
                <strong style="color: #F8FAFC;">{l['agent_name']}</strong> &nbsp;
                <span class="agent-badge" style="font-size: 0.72rem; padding: 0.15rem 0.5rem;">{l['task']}</span> &nbsp;
                <span style="color: #34D399; float: right;">✓ {l['status']}</span>
                <div style="color: #94A3B8; font-size: 0.76rem; margin-top: 0.3rem;">
                    <strong>Output Payload:</strong> {str(l['output_data'])[:160]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity logged yet.")

# 11. SETTINGS
elif nav_selection == "Settings":
    st.markdown('<div class="hero-title">⚙️ System Configuration & Preferences</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-tagline">Customize runtime parameters, AI LLM connectors, and local SQLite database state.</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    c_set1, c_set2 = st.columns(2)
    with c_set1:
        st.markdown('<div class="glass-panel-title">🤖 Optional External LLM Integration</div>', unsafe_allow_html=True)
        st.info("SkillNova AI operates completely offline with zero paid API dependencies using its intelligent contextual rule engine. You may optionally supply an API key to enable live LLM generation.")
        curr_key = st.session_state.get("llm_api_key", "")
        new_key = st.text_input("Enter OpenAI / Gemini API Key (Optional):", value=curr_key, type="password")
        if st.button("Save API Configuration"):
            st.session_state["llm_api_key"] = new_key
            st.success("API Key saved to session.")

    with c_set2:
        st.markdown('<div class="glass-panel-title">💾 Local Database Administration</div>', unsafe_allow_html=True)
        st.markdown("All learner profiles, skill inventories, assessments, roadmaps, and agent telemetry are persisted in SQLite.")
        if st.button("🔄 Reset Demo Student State to Default", type="secondary"):
            db.seed_database(force_reset=True)
            st.session_state["pipeline_needs_refresh"] = True
            st.success("Database restored to pristine demo student scenario!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-panel-title">ℹ️ Platform Specifications</div>', unsafe_allow_html=True)
    st.markdown("""
    - **Platform:** SkillNova AI v1.0.0 (Hackathon Edition)
    - **Engine:** Collaborative 6-Agent AI Architecture
    - **Database:** SQLite 3 (15 Relational Tables)
    - **UI Framework:** Streamlit Dark SaaS Edition
    - **Data Visualizations:** Plotly Interactive Radar & Gauge Suite
    """)
