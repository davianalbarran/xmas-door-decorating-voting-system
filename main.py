# FastAPI Imports
from fastapi import FastAPI, Request, Header, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Misc
from typing import List, Annotated, Union
import os

class Door(BaseModel):
    number: int
    title: str = "Untitled"
    votes: int = 0

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other):
        return isinstance(other, Door) and self.number == other.number

app = FastAPI()
templates = Jinja2Templates(directory="templates")
doors = set()

# UI Rendering
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/doors", response_class=HTMLResponse)
async def read_doors(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(request=request, name="doors.html", context={"doors": doors})
    
    return JSONResponse(content=jsonable_encoder(doors))

@app.get("/add-door", response_class=HTMLResponse)
async def add_door(request: Request):
    return templates.TemplateResponse(request=request, name="add-door.html")

# Voting Logic
@app.get("/vote/{door_id}", response_class=HTMLResponse)
async def vote_door(request: Request, door_id: int):    
    door = Door(number=door_id)

    if door in doors:
        for d in doors:
            if d.number == door.number:
                d.votes += 1
                return templates.TemplateResponse(
                    request=request, 
                    name="vote.html", 
                    context={"door_id": door_id, "door_title": d.title}
                )
    
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": "Door does not exist"},
        status_code=404
    )

# Admin Functionality
@app.post("/add-door")
async def add_door(
    request: Request,
    door_id: Annotated[int, Form()],
    title: Annotated[str | None, Form()] = None
):
    # Create new door
    door = Door(number=door_id, title=title if title else "Untitled")
    doors.add(door)
    
    # Return the updated doors list template
    return templates.TemplateResponse(
        request=request,
        name="doors.html",
        context={"doors": doors}
    )

@app.post("/add-doors")
async def add_doors(door_ids: List[int]):
    for door_id in door_ids:
        door = Door(number=door_id)
        doors.add(door)

    return {"success": True}

@app.get("/save-votes")
async def save_votes():
    sVotes = ""
    for door in doors:
        sVotes += f'{door.number}: {door.votes}\n'

    with open("votes.txt", "w") as file:
        file.write(sVotes)
        return FileResponse(os.path.abspath(file.name), media_type="application/octet-stream", filename=file.name)
