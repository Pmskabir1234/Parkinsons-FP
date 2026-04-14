# Dev Simulator – Real-World Coding Simulator

Stop solving toy problems. Start surviving real codebases.


## What is Dev simulator?
Dev Simulator is not LeetCode. It's not another "build a todo app" tutorial.
Dev Simulator is a real-world coding simulator — part internship, part game, part bootcamp — where you're thrown into messy, broken, underdocumented projects and asked to survive. Built with Streamlit and Django.
If you've ever wondered "why does this feel nothing like my actual job?" when practicing on coding platforms — DevArena is your answer.

## The Problem with Traditional Coding Practice
Traditional PlatformsReal JobsClean, isolated problemsMessy, interconnected systemsWrite code from scratchUnderstand someone else's code firstGreen checkmarksStack traces at 2amPerfect documentation"It worked last week"One right answer10 acceptable tradeoffs
DevArena bridges this gap.

## Core Features
1. Broken World Projects
Instead of "build a todo app from scratch," you receive:

A messy, real-looking project with history and baggage
Bugs already baked in — some obvious, some lurking
Incomplete or misleading documentation
A confusing codebase written by "a previous developer"

Your mission:

Fix the bugs
Add a new feature
Understand the architecture without a guide


This is exactly what Day 1 at any real engineering job looks like.


2.  Debugging Battles
Timed debugging challenges that simulate real incident response:

Real error logs and stack traces
Performance bottlenecks and memory leaks
Broken API integrations
Race conditions and async nightmares

The rule: You don't write code. You fix broken systems. Under pressure. On a clock.

## Tech Stack
Frontend : StreamlitBackend 

Backend : APIDjango + Django REST Framework, SQLite3

Auth: Django AllauthTask 

## Getting Started
Prerequisites

Python 3.10+
Docker & Docker Compose
Node.js 18+ (for any JS challenges)

Installation
bash Clone the repo
git clone https://github.com/Pmskabir1234/Dev-Simulator.git
cd devsimulator

## Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Set up environment variables
cp .env.example .env

## Edit .env with your settings

## Run database migrations
python manage.py migrate

## Start the Django backend
python manage.py runserver

## In a separate terminal, start the Streamlit frontend
streamlit run app.py

## Not built comepletely, feel free to contribute 
