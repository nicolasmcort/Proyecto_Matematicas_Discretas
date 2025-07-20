import networkx as nx
import matplotlib.pyplot as plt
import io
from collections import deque
from typing import TypedDict, List

class DependencyAnalyzer:
    """
    Analiza el grafo de dependencias para detectar ciclos y establecer un orden válido de ejecución.
    Permite la visualización estática del grafo y calcula métricas adicionales.
    """
    def __init__(self):
        pass

    def _draw_graph_static(self, G: nx.DiGraph, title: str, buffer: io.BytesIO):
        """
        Dibuja un grafo estático con colores por defecto.
        """
        plt.figure(figsize=(10, 8))
        plt.title(title)

        pos = None
        try:
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog='dot')
        except ImportError:
            pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

        node_color_list = ['lightblue' for _ in G.nodes]

        nx.draw_networkx_nodes(G, pos, node_color=node_color_list, node_size=2000)
        
        nx.draw_networkx_edges(G, pos, edgelist=G.edges, edge_color='gray', 
                               width=1.8, arrows=True, arrowsize=35, alpha=0.7,
                               min_source_margin=15, min_target_margin=20,
                               connectionstyle='arc3,rad=0.2')
        
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.axis('off')
        plt.savefig(buffer, format="png")
        plt.close()  # Cerrar la figura para liberar memoria

    @staticmethod
    def _convert_minutes_to_hours(minutes: int) -> float:
        """Convierte una duración en minutos a horas."""
        return minutes / 60.0

    def detect_cycles(self, graph: nx.DiGraph, visualize: bool = False) -> List[str] | None:
        """
        Detecta el primer ciclo encontrado en un grafo dirigido usando DFS.
        Devuelve el ciclo como una lista de nodos [A, B, C, A] o None si no hay ciclos.
        """
        white_set = set(graph.nodes())
        gray_set = set()  # Nodos en la pila de recursión actual
        black_set = set()  # Nodos completamente visitados

        found_cycle = []  # Almacena el primer ciclo encontrado
        path = deque()  # Para reconstruir el camino

        def dfs_cycle_check(node):
            nonlocal found_cycle  # Permite modificar found_cycle de la función externa

            if node in white_set:
                white_set.remove(node)
            gray_set.add(node)
            path.append(node)

            for neighbor in graph.successors(node):
                if neighbor in gray_set:  # Ciclo detectado
                    cycle_start_index = list(path).index(neighbor)
                    current_cycle = list(path)[cycle_start_index:] + [neighbor]
                    found_cycle.append(current_cycle)  # Guarda la lista de nodos
                    return True  # Señaliza que un ciclo fue encontrado y detiene esta rama

                if neighbor in white_set:  # Si es blanco, seguir explorando
                    if dfs_cycle_check(neighbor):
                        return True  # Propagar la señal si se encontró un ciclo más abajo

            gray_set.remove(node)
            black_set.add(node)
            path.pop()
            return False

        # Se recorren todos los nodos. Se detiene en cuanto se encuentre el primer ciclo.
        for node in list(white_set):
            if node in white_set:
                if dfs_cycle_check(node):
                    break  # Detener la búsqueda global después de encontrar el primer ciclo

        return found_cycle[0] if found_cycle else None  # Retorna la lista del ciclo o None

    class OrderResult(TypedDict):
        order: List[str]
        total_duration_hours: float
        critical_tasks_count: int

    def get_tasks_order(self, graph: nx.DiGraph, visualize: bool = False) ->  OrderResult | None:
        """
        Calcula un orden válido del grafo dirigido.
        Devuelve el orden como una lista, incluyendo tiempo total y tareas críticas,
        o None si no existe (por ciclos).
        """
        try:
            order = list(nx.topological_sort(graph))
            
            total_duration_minutes = 0
            critical_tasks_count = 0
            
            for task_name in order:
                # Acceder a los atributos del nodo 
                task_data = graph.nodes[task_name]
                total_duration_minutes += task_data.get('duration', 0) 
                if task_data.get('priority') == "Crítica":
                    critical_tasks_count += 1
            
            total_duration_hours = self._convert_minutes_to_hours(total_duration_minutes)            
            return  {"order": order, "total_duration_hours":total_duration_hours, "critical_tasks_count":critical_tasks_count}
        except nx.NetworkXUnfeasible:
            return None
