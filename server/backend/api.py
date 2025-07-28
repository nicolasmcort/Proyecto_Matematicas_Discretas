from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, TypedDict
import io
import base64

from dependency_analyzer import DependencyAnalyzer
from graph_builder import GraphBuilder
from task import Task

app = FastAPI()

origins = [  
    "http://localhost",  
    # "http://localhost:8080",   # Líneas para servidor de desarrollo de Vite 
    # "http://127.0.0.1:8080",   # (puerto 8080) para desarrollo local sin Docker
    "http://localhost:3000",  
    "http://frontend:80",     
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessagePayload(BaseModel):
    message: str

class TaskInput(BaseModel):
    id: int
    name: str
    duration: float
    unit: str
    priority: str
    dependencies: List[int]

class ProjectData(BaseModel):
    duracion_total: float
    tareas_criticas: int
    ciclos_detectados: Optional[List[str]] = None
    orden_tareas: Optional[List[str]] = None
    image_base64: str


@app.post("/generate-plan", response_model=ProjectData)
async def generate_plan(tasks: List[TaskInput]):
    try:
        task_map: Dict[int, Task] = {}
        all_tasks: List[Task] = []
        for t in tasks:
            task = Task(
                t.name,
                t.duration,
                t.unit,
                t.priority,
                []  # Las dependencias se poblarán en el siguiente paso
            )
            task_map[t.id] = task
            all_tasks.append(task)
            
        # Segundo bucle para poblar las dependencias usando el task_map
        for t in tasks:
            task = task_map[t.id]
            task.dependencies = [task_map[dep_id].name for dep_id in t.dependencies if dep_id in task_map]

        builder = GraphBuilder()
        graph = builder.build_graph(all_tasks)

        analyzer = DependencyAnalyzer()
        cycles_str = analyzer.detect_cycles(graph, visualize=False)
        order_result = analyzer.get_tasks_order(graph, visualize=False)

        duracion_total = 0.0
        tareas_criticas = 0

        # Extraer la información
        order_tasks: Optional[List[str]] = None
        if order_result:
            order_tasks = order_result["order"]
            duracion_total = order_result["total_duration_hours"]
            tareas_criticas = order_result["critical_tasks_count"]

        buffer = io.BytesIO()
        if cycles_str: 
            graph_title = "Grafo con Dependencias Cíclicas"
        else: 
            graph_title = "Grafo de Dependencias sin Ciclos"
        analyzer._draw_graph_static(graph, graph_title, buffer=buffer)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return ProjectData(
            duracion_total=duracion_total,
            tareas_criticas=tareas_criticas,
            ciclos_detectados=cycles_str,
            orden_tareas=order_tasks,
            image_base64=image_base64,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


