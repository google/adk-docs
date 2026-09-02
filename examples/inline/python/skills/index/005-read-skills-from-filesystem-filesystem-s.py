import pathlib

from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

greeting_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "greeting-skill"
)
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill, greeting_skill],
)