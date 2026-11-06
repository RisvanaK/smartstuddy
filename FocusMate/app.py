"""FocusMate — pastel Chiikawa study planner with a Groq-powered AI page.
Run: streamlit run app.py
"""
from datetime import date, datetime, time as dt_time
from pathlib import Path
import base64
import html
import time

import pandas as pd
import streamlit as st

st.set_page_config(page_title="FocusMate Study Planner", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
DOODLES = ROOT / "images" / "study_doodles.svg"
SUBJECTS = ["Mathematics", "Science", "English", "Computer Science", "Social Studies", "Revision", "Other"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def img_data(path):
    if not path.exists():
        return ""
    mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


DECOR = img_data(DOODLES)
HEADER_FRIENDS = img_data(ROOT / "images" / "header_friends.png")
HEADER_STUDY = img_data(ROOT / "images" / "header_study.png")
READING_FRIENDS = img_data(ROOT / "images" / "reading_friends.png")
CORNER_FRIENDS = img_data(ROOT / "images" / "corner_friends.png")
SIDE_FRIENDS = img_data(ROOT / "images" / "side_friends.png")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');
:root {--pink:#ff7eae;--rose:#ffe3ed;--ink:#49384e;--lav:#eee5ff;--blue:#e4f5ff;}
html,body,[class*="css"],[data-testid="stApp"] {font-family:'Nunito',sans-serif;}
.stApp {background:linear-gradient(125deg,#fff1f6 0%,#fff9f4 43%,#e8f5ff 100%);color:var(--ink);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#ffe8f0,#f5e9ff 65%,#e7f5ff);border-right:1px solid #f9cbdc;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {border-radius:13px;padding:5px 7px;}
h1,h2,h3 {font-family:'Fredoka',sans-serif!important;color:#55394f!important;}
[data-testid="stMetric"] {background:#fffafc;border:1px solid #f9dbe5;border-radius:20px;padding:16px;box-shadow:0 5px 15px #ebbad333;}
.stButton>button {border-radius:16px;font-family:'Nunito',sans-serif;font-weight:800;border-color:#f7bed1;}
.stButton>button[kind="primary"] {background:linear-gradient(90deg,#ff83af,#ff639f);color:white;border:0;}
.stButton>button:hover {border-color:#f48db5;color:#d93b7d;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:20px!important;background:#ffffffb5;border-color:#f5dbe5!important;}
[data-testid="stProgress"]>div>div>div {background:#ff85b4;}
.hero {border-radius:26px;padding:22px 26px;margin:4px 0 20px;background:linear-gradient(105deg,#ffe0ed,#f4e9ff 55%,#dff4ff);border:2px solid #fff;box-shadow:0 6px 22px #eabfd13b;display:flex;align-items:center;justify-content:space-between;gap:20px;}
.hero h1 {margin:0;font-size:clamp(26px,3vw,40px);}
.hero p {font-size:16px;margin:8px 0 0;}
.hero img {width:min(230px,35%);max-height:140px;object-fit:contain;border-radius:15px;mix-blend-mode:multiply;}
.pill {display:inline-block;background:#ffe1ec;border-radius:30px;padding:6px 13px;color:#9c4774;font-weight:800;font-size:13px;margin-bottom:9px;}
.quote {background:linear-gradient(110deg,#fff0f5,#fff7df);border:1px solid #f9d9e7;border-radius:20px;padding:19px;font-weight:800;color:#a2527d;}
.timer {font-family:'Fredoka',sans-serif;text-align:center;font-size:clamp(55px,8vw,96px);color:#ed6a9e;background:#fff7fb;border:8px solid #ffd4e5;border-radius:40px;padding:24px;margin:10px auto;max-width:430px;}
.small-note {color:#9a7288;font-size:14px;}
.sidebar-img {width:100%;max-width:230px;border-radius:15px;mix-blend-mode:multiply;}
.scene-banner {width:100%;height:160px;object-fit:cover;object-position:center;border-radius:24px;border:3px solid white;box-shadow:0 7px 22px #e9b8cd55;margin:4px 0 18px;}
.character-strip {width:100%;max-height:165px;object-fit:contain;object-position:center;border-radius:20px;}
.cute-panel {background:#fff9fc;border:1px solid #f6d6e3;padding:14px;border-radius:22px;text-align:center;margin:8px 0 18px;}
.cute-panel img {width:100%;max-height:160px;object-fit:contain;border-radius:16px;}
.banner-doodle {width:100%;max-height:110px;object-fit:cover;border-radius:18px;margin:8px 0;}
</style>
""", unsafe_allow_html=True)

# Session state is intentionally lightweight; data resets when a new session starts.
def init(name, value):
    if name not in st.session_state:
        st.session_state[name] = value

init("tasks", [
    {"subject":"Mathematics","task":"Practice Algebra","due":str(date.today()),"done":False},
    {"subject":"Science","task":"Revise Chapter 4","due":str(date.today()),"done":True},
])
init("schedule", [])
init("study_minutes", 0)
init("sessions", 0)
init("timer_mode", "Study")
init("timer_duration", 25 * 60)
init("timer_end", None)
init("timer_recorded", False)
init("ai_result", "")


def hero(title, subtitle, tag=" STUDY WITH JOY "):
    st.markdown(f'<div class="hero"><div><span class="pill">{html.escape(tag)}</span><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div></div>', unsafe_allow_html=True)


def art():
    if DECOR:
        st.markdown(f'<img class="banner-doodle" src="{DECOR}" alt="Pastel study decorations">', unsafe_allow_html=True)


def scene(image_data, caption=""):
    if image_data:
        st.markdown(f'<img class="scene-banner" src="{image_data}" alt="Cute pastel character illustration">', unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def friends(image_data, message=""):
    if image_data:
        st.markdown(f'<div class="cute-panel"><img src="{image_data}" alt="Cute study companions"><div class="small-note">{html.escape(message)}</div></div>', unsafe_allow_html=True)


def task_list(prefix, with_delete=False):
    if not st.session_state.tasks:
        st.info("No homework yet. Add your first task! ")
    for task in list(st.session_state.tasks):
        idx = st.session_state.tasks.index(task)
        with st.container(border=True):
            cols = st.columns([6, 2, 1] if with_delete else [6, 2])
            with cols[0]:
                checked = st.checkbox(f"{task['subject']} — {task['task']}", value=task["done"], key=f"{prefix}_{idx}")
                if checked != task["done"]:
                    st.session_state.tasks[idx]["done"] = checked
                    st.rerun()
            with cols[1]:
                st.caption(f" {task['due']}")
            if with_delete:
                with cols[2]:
                    if st.button("", key=f"delete_{idx}", help="Delete task"):
                        st.session_state.tasks.pop(idx)
                        st.rerun()


with st.sidebar:
    st.title("FocusMate")
    st.caption("Your personal study companion")
    st.divider()
    page = st.radio("Explore", ["Dashboard", "Homework", "Timetable", "Focus Timer", "My Progress", "AI Smart Planner"], label_visibility="collapsed")
    st.divider()
    st.markdown("** Small steps, big dreams!**")
    st.caption("Plan • Focus • Grow ")
    friends(SIDE_FRIENDS, "You can do it! ")

if page == "Dashboard":
    scene(HEADER_FRIENDS)
    hero("Welcome to FocusMate! ", "A little planning makes every study day brighter.")
    total = len(st.session_state.tasks)
    done = sum(t["done"] for t in st.session_state.tasks)
    a,b,c,d = st.columns(4)
    a.metric(" All Tasks", total)
    b.metric(" Completed", done)
    c.metric(" To Do", total-done)
    d.metric(" Study Minutes", st.session_state.study_minutes)
    left,right = st.columns([1.7,1])
    with left:
        st.subheader(" My Homework")
        task_list("dashboard")
    with right:
        st.subheader(" Today's Encouragement")
        st.markdown('<div class="quote"> You can do hard things, one little step at a time! </div>', unsafe_allow_html=True)
        st.write(" Remember to take breaks and drink water.")
        friends(READING_FRIENDS, "Study together, shine together! ")
    st.subheader(" Homework Progress")
    st.progress(done/total if total else 0)
    st.caption(f"{done} of {total} tasks completed")
    art()

elif page == "Homework":
    hero("Homework Garden ", "Plant a task, finish it, and watch your progress bloom!")
    scene(HEADER_STUDY)
    with st.form("homework_form", clear_on_submit=True):
        st.subheader(" Add Homework")
        name = st.text_input("What do you need to do?", placeholder="e.g. Complete algebra worksheet")
        a,b = st.columns(2)
        with a:
            subject = st.selectbox("Subject", SUBJECTS)
        with b:
            due = st.date_input("Due date", min_value=date.today())
        if st.form_submit_button(" Add Homework", type="primary"):
            if name.strip():
                st.session_state.tasks.append({"subject":subject,"task":name.strip(),"due":str(due),"done":False})
                st.success("Task added! You got this! ")
            else:
                st.warning("Please enter a homework task.")
    st.subheader(" My Homework List")
    task_list("homework", with_delete=True)

elif page == "Timetable":
    hero("My Study Timetable ", "Make time for learning and little breaks.")
    friends(READING_FRIENDS, "A little planning makes a big difference.")
    with st.form("timetable_form", clear_on_submit=True):
        st.subheader(" Add a Study Session")
        a,b = st.columns(2)
        with a:
            day = st.selectbox("Day", DAYS)
            subject = st.selectbox("Subject", SUBJECTS)
        with b:
            start = st.time_input("Start time", value=dt_time(16,0))
            duration = st.number_input("Minutes", min_value=15, max_value=180, value=60, step=15)
        if st.form_submit_button(" Add to Timetable", type="primary"):
            st.session_state.schedule.append({"Day":day,"Subject":subject,"Start":start.strftime("%H:%M"),"Minutes":int(duration)})
            st.success("Study session added! ")
    st.subheader(" Weekly Schedule")
    if st.session_state.schedule:
        df = pd.DataFrame(st.session_state.schedule)
        df["Day"] = pd.Categorical(df["Day"], categories=DAYS, ordered=True)
        st.dataframe(df.sort_values(["Day","Start"]), use_container_width=True, hide_index=True)
        if st.button(" Clear Timetable"):
            st.session_state.schedule = []
            st.rerun()
    else:
        st.info("No sessions yet. Add one above!")
    art()

elif page == "Focus Timer":
    hero("Cozy Focus Timer ", "Study a little, rest a little, and keep going!")
    scene(HEADER_STUDY)
    mode = st.radio("Timer mode", ["Study", "Break"], horizontal=True)
    if mode != st.session_state.timer_mode:
        st.session_state.timer_mode = mode
        st.session_state.timer_duration = 25*60 if mode == "Study" else 5*60
        st.session_state.timer_end = None
        st.session_state.timer_recorded = False

    @st.fragment(run_every="1s")
    def ticking_timer():
        if st.session_state.timer_end is None:
            remaining = st.session_state.timer_duration
        else:
            remaining = max(0, int(st.session_state.timer_end-time.time()+0.999))
        minutes, seconds = divmod(remaining, 60)
        st.markdown(f'<div class="timer">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
        base = 25*60 if st.session_state.timer_mode == "Study" else 5*60
        st.progress(min(1.0,max(0.0,1-remaining/base)))
        if remaining == 0 and st.session_state.timer_end is not None and not st.session_state.timer_recorded:
            st.session_state.timer_recorded = True
            st.session_state.timer_end = None
            if st.session_state.timer_mode == "Study":
                st.session_state.study_minutes += 25
                st.session_state.sessions += 1
            st.success(" Session complete! Great work!")

    ticking_timer()
    a,b,c = st.columns(3)
    with a:
        if st.button(" Start", type="primary", use_container_width=True):
            if st.session_state.timer_end is None:
                st.session_state.timer_end = time.time()+st.session_state.timer_duration
                st.session_state.timer_recorded = False
                st.rerun()
    with b:
        if st.button(" Pause", use_container_width=True):
            if st.session_state.timer_end is not None:
                st.session_state.timer_duration = max(1,int(st.session_state.timer_end-time.time()+0.999))
                st.session_state.timer_end = None
                st.rerun()
    with c:
        if st.button(" Reset", use_container_width=True):
            st.session_state.timer_end = None
            st.session_state.timer_duration = 25*60 if mode == "Study" else 5*60
            st.session_state.timer_recorded = False
            st.rerun()
    st.metric(" Completed Focus Sessions", st.session_state.sessions)
    st.caption("Keep this page open while your timer is running.")

elif page == "My Progress":
    hero("Look How Far You've Come! ", "Every small win deserves a little celebration.")
    friends(CORNER_FRIENDS, "Every little victory counts! ")
    total = len(st.session_state.tasks)
    done = sum(t["done"] for t in st.session_state.tasks)
    a,b,c = st.columns(3)
    a.metric(" Completion", f"{done/total:.0%}" if total else "0%")
    b.metric(" Study Minutes", st.session_state.study_minutes)
    c.metric(" Focus Sessions", st.session_state.sessions)
    st.subheader(" Homework Status")
    if total:
        st.bar_chart(pd.DataFrame({"Tasks":[done,total-done]}, index=["Completed","Pending"]), color="#f58ab6")
        df = pd.DataFrame(st.session_state.tasks)
        grouped = df.groupby("subject")["done"].mean().mul(100).rename("Completion %")
        st.subheader(" Subject Progress")
        st.bar_chart(grouped, color="#a99af5")
    else:
        st.info("Add homework to see your progress!")
    st.subheader(" Achievements")
    if done >= 1:
        st.success(" First Step — Completed your first homework!")
    if done >= 5:
        st.success(" Task Master — Completed five tasks!")
    if st.session_state.sessions:
        st.success(" Focus Champion — Finished a focus session!")
    if not done and not st.session_state.sessions:
        st.info("Your achievements will appear here soon!")
    art()

elif page == "AI Smart Planner":
    hero("My AI Study Buddy ", "Tell me about your day and I'll help you make a cute study plan!", " POWERED BY REAL AI ")
    scene(HEADER_FRIENDS)
    st.info(" This page uses Groq's AI model to create a personalized plan. It needs internet access and your private API key.")
    with st.form("ai_form"):
        st.subheader(" Let's Plan Your Study Time")
        selected = st.multiselect("Which subjects will you study?", SUBJECTS, default=["Mathematics","Science"])
        hours = st.slider("How much time do you have today?", min_value=1.0, max_value=6.0, value=2.0, step=0.5)
        a,b = st.columns(2)
        difficulties = {}
        for idx, subject in enumerate(selected):
            with (a if idx%2==0 else b):
                difficulties[subject] = st.selectbox(f"{subject} difficulty", ["Easy","Medium","Hard"], index=1, key=f"difficulty_{subject}")
        goal = st.text_input("What's your main study goal? (optional)", placeholder="e.g. Prepare for Friday's Maths test")
        submitted = st.form_submit_button(" Generate My AI Study Plan", type="primary", use_container_width=True)

    if submitted:
        if not selected:
            st.warning("Choose at least one subject first.")
        else:
            try:
                api_key = st.secrets.get("GROQ_API_KEY", "")
            except Exception:
                api_key = ""
            if not api_key or api_key == "PASTE_YOUR_GROQ_API_KEY_HERE":
                st.error("Missing GROQ_API_KEY. Add it to .streamlit/secrets.toml and restart the app.")
            else:
                try:
                    from groq import Groq
                    client = Groq(api_key=api_key, timeout=35.0, max_retries=0)
                    subjects_text = ", ".join(f"{s} ({difficulties[s]})" for s in selected)
                    prompt = f"""You are FocusMate, a friendly study planner for a 15-year-old student.
Create a practical, encouraging study timetable in clear, simple English.
Subjects and difficulty: {subjects_text}
Total available time INCLUDING breaks: {int(hours*60)} minutes.
Main goal: {goal.strip() or 'Make steady progress'}.
Requirements:
- Use a Markdown table with columns: Order, Activity, Minutes, What to do.
- Allocate MORE study time to harder subjects.
- Include at least one short break if the total time is 60 minutes or more.
- The sum of all table minutes MUST equal exactly {int(hours*60)}.
- Include 3 brief study tips and a cheerful one-sentence encouragement.
- Do not invent school deadlines, personal facts, or claim to know the student's grades.
- No extra introductory paragraphs. Keep the result concise."""
                    with st.spinner(" Your AI study buddy is planning..."):
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[{"role":"system","content":"You are a helpful and age-appropriate study planning assistant."},{"role":"user","content":prompt}],
                            temperature=0.4,
                            max_tokens=1200,
                        )
                    result = response.choices[0].message.content or ""
                    if result.strip():
                        st.session_state.ai_result = result
                    else:
                        st.error("The AI returned an empty response. Please try again.")
                except Exception as exc:
                    st.error(f"AI request failed: {type(exc).__name__}: {exc}")
                    st.info("Check your internet connection, API key and Groq free-tier limits, then try again.")

    if st.session_state.ai_result:
        st.subheader(" Your Personalized Study Plan")
        st.markdown(st.session_state.ai_result)
        st.download_button(" Save My Plan (.txt)", data=st.session_state.ai_result, file_name="focusmate_ai_study_plan.txt", mime="text/plain")
        st.caption("AI suggestions can contain mistakes. Double-check the total minutes and adjust the plan to fit your needs.")
    art()

st.divider()
st.caption(" FocusMate • Plan gently, learn happily. Study data is kept only in this browser session; AI requests are sent to Groq.")
