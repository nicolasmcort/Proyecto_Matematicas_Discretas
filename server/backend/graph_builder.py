import networkx as nx
from task import Task

class GraphBuilder:
    """
    Construye un grafo dirigido de dependencias a partir de una lista de objetos Task.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    @staticmethod
    def _convert_to_minutes(duration: int, unit: str) -> int:
        """Convierte una duración dada a minutos."""
        if unit == "hours":
            return duration * 60
        elif unit == "minutes":
            return duration
        else:
            raise ValueError(f"Unidad de duración no soportada: '{unit}'. Use 'hours' o 'minutes'.")

    def build_graph(self, tasks: list['Task']) -> nx.DiGraph:
        """
        Construye el grafo de dependencias.

        Args:
            tasks (list[Task]): Una lista de objetos Task.

        Returns:
            nx.DiGraph: El grafo dirigido construido.
        """
        self.graph.clear()

        for task in tasks:
            duration_in_minutes = self._convert_to_minutes(task.duration, task.duration_unit)
            
            # Añadir el nodo con sus atributos
            self.graph.add_node(task.name, duration=duration_in_minutes, priority=task.priority)
            
            # Procesar sus dependencias (añadir aristas)
            for dependency_name in task.dependencies:
                self.graph.add_edge(dependency_name, task.name)
                
        return self.graph

    def get_graph(self) -> nx.DiGraph:
        """
        Devuelve el grafo actualmente construido.
        """
        return self.graph
