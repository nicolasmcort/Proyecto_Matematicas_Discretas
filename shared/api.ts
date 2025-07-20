/**
 * Shared code between client and server
 * Useful to share types between client and server
 * and/or small pure JS functions that can be used on both client and server
 */

/**
 * Example response type for /api/demo
 */
export interface DemoResponse {
  message: string;
}

export interface Task {
    id: number;
    name: string;
    duration: number;
    unit: "Horas" | "Minutos";
    priority: "Alta" | "Media" | "Baja" | "Crítica";
    dependencies: string;
}

export interface ProjectData {
    duracion_total: number;
    tareas_criticas: number;
    ciclos_detectados: Array<string> | null;
    orden_tareas: Array<string> | null;
    image_base64: string;
}