import json
from datetime import datetime

from . import os, st
from .BasePage import BasePage
from APIModules.ObjectModels.Task import Task

class ConfigPage(BasePage):

    def render(self):
        super().render(keys={"WATSON_API_KEY": os.getenv("WATSON_API_KEY")})
        with open("initial_state.json") as f:initial_state_from_json : dict = json.load(f)
        initial_team_members = st.session_state.get('team')
        if not initial_team_members:st.session_state.team = initial_state_from_json.get('team', ["Alessio", "Joy", "Nicola C", "Nicola D", "Dragosh"])
        initial_tasks = st.session_state.get('tasks')
        if not initial_tasks:st.session_state.tasks = [Task(**task).model_dump() for task in initial_state_from_json.get('tasks', [])]
        initial_assignments = st.session_state.get('assignments')
        if not initial_tasks:st.session_state.assignments = initial_state_from_json.get('assignments', {})

        with st.expander("Set Team", expanded=True):
            st.header("Configurazione")
            new_member = st.text_input("Enter team name", value="Team name")
            if st.button("Add team member"):
                st.session_state.team.append(new_member)
        with st.expander("Tasks", expanded=True):
            st.header("Task")
            new_task_name = st.text_input("Enter task name", value="Task name")
            new_task_description = st.text_area("Enter task description", value="Task description")
            new_task_start_date = st.date_input("Enter task start date", value=datetime.today())
            new_task_end_date = st.date_input("Enter task end date", value=datetime.today())
            if st.button("Add Task"):
                new_task = Task(
                    name=new_task_name, description=new_task_description, 
                    start_date=new_task_start_date, end_date=new_task_end_date
                )
                st.session_state.tasks.append(new_task.model_dump())
        with st.expander("Assing Tasks", expanded=True):
            st.header("Assing Tasks")
            cols = st.columns(2)
            with cols[0]:_team_member = st.selectbox("Team Member", st.session_state.team)
            _tasks_to_assing = st.multiselect("Task", [task['name'] for task in st.session_state.tasks])
            task_indices = [i for i, task in enumerate(st.session_state.tasks) if task['name'] in _tasks_to_assing]
            tasks_selected = [task["name"] for i, task in enumerate(st.session_state.tasks) if i in task_indices]
            if st.button("Assing Task"):
                st.session_state.assignments[_team_member] = tasks_selected
        if os.getenv("DEBUG_INITIAL_STATE", True):
            st.write(st.session_state)
