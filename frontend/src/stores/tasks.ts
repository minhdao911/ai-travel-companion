import type { Task, TaskType } from "@/types";
import { defineStore } from "pinia";

export const useTaskStore = defineStore("task_store", {
  state: () => ({
    tasks: {} as Record<TaskType, Task>,
  }),
  actions: {
    addTask(task: Task) {
      this.tasks[task.type] = task;
    },
    updateTask(type: TaskType, task: Partial<Task>) {
      this.tasks[type] = { ...this.tasks[type], ...task };
    },
    removeTask(type: TaskType) {
      delete this.tasks[type];
    },
    resetTasks() {
      this.tasks = {} as Record<TaskType, Task>;
    },
  },
});
