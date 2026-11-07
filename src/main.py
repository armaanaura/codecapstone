from fastapi import FastAPI, Header, HTTPException
from .auth.validate_user import validate_user
from .services.topic_progress_per_user import topic_progress
from .services.submit_solution import submit_solution
app = FastAPI()

@app.get("/")
def home():
    return {
        "message" : "hello world"
    }
    
@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "name": "Armaan"
    }
    
@app.get("/topic/{topic_name}/capstone")
def get_topic_progress(
    user_id : str,
    topic_id : int,
    auth_token : str = Header() #this will ask api to get details from http header not in parameter
):
    if not validate_user(user_id, auth_token):
        raise HTTPException(
            status_code = 401,
            detail="Invalid authentication token"
        )
    
    response : dict = topic_progress(user_id, topic_id)
    
    return response

@app.post("/question/{question_id}/submit")
def submit_solution_endpoint(
    user_id : str,
    topic_id : int,
    question_id : str,
    code_language : str,
    solution : str,
    ai_review_enabled : bool,
    auth_token : str = Header()
):
    if not validate_user(user_id, auth_token):
        raise HTTPException(
            status_code = 401,
            detail="Invalid authentication token"
        )
    
    response : dict = submit_solution(user_id, topic_id, question_id, code_language, solution, ai_review_enabled = ai_review_enabled)
    
    return response