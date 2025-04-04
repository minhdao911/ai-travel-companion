import { ref, onUnmounted } from "vue";
import { TaskStatus, TaskType, MessageRole, type Message } from "@/types";
import { checkTaskStatus } from "@/services/api";
import { generateId } from "@/services/id";

export function useTasks(
  addMessage: (message: Message) => void,
  updateMessage: (id: string, data: Partial<Message>) => void
) {
  const pollInterval = ref<number | null>(null);
  const taskMessages = ref<{ [taskType: string]: string | null }>({
    [TaskType.HotelSearch]: null,
    [TaskType.FlightSearch]: null,
    [TaskType.FlightPick]: null,
    [TaskType.HotelPick]: null,
  });

  const tasks = ref<{
    [TaskType.HotelSearch]: {
      id: string | null;
      status: TaskStatus;
    };
    [TaskType.FlightSearch]: {
      id: string | null;
      status: TaskStatus;
    };
    [TaskType.FlightPick]: {
      id: string | null;
      status: TaskStatus;
    };
    [TaskType.HotelPick]: {
      id: string | null;
      status: TaskStatus;
    };
  }>({
    [TaskType.HotelSearch]: { id: null, status: TaskStatus.Pending },
    [TaskType.FlightSearch]: { id: null, status: TaskStatus.Pending },
    [TaskType.FlightPick]: { id: null, status: TaskStatus.Pending },
    [TaskType.HotelPick]: { id: null, status: TaskStatus.Pending },
  });

  // Update task message progress based on status
  const updateTaskMessageProgress = (taskType: TaskType) => {
    const messageId = taskMessages.value[taskType];
    const task = tasks.value[taskType];

    if (messageId && task) {
      if (task.status === TaskStatus.Completed) {
        updateMessage(messageId, { completed: true });
      } else {
        updateMessage(messageId, { completed: false });
      }
    }
  };

  const startPolling = () => {
    // Poll every 2 seconds
    pollInterval.value = setInterval(monitorTaskStatus, 2000) as unknown as number;
  };

  const stopPolling = () => {
    if (pollInterval.value !== null) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
    }
  };

  const setTaskProcessing = (taskType: TaskType, taskId: string) => {
    if (tasks.value[taskType]) {
      tasks.value[taskType].id = taskId;
      tasks.value[taskType].status = TaskStatus.Processing;
      // Update progress for this task
      updateTaskMessageProgress(taskType);
    }
  };

  const monitorTaskStatus = async () => {
    try {
      // Check statuses of all active tasks
      for (const taskType in tasks.value) {
        const task = tasks.value[taskType as TaskType];
        if (task.id && task.status !== TaskStatus.Completed && task.status !== TaskStatus.Failed) {
          const { status, data } = await checkTaskStatus(task.id);

          // Update task status if changed
          if (task.status !== status) {
            task.status = status;
            // Update progress for this task
            updateTaskMessageProgress(taskType as TaskType);
          }

          // Handle status changes
          if (status === TaskStatus.Completed) {
            if (taskType === TaskType.FlightSearch) {
              // For completed tasks, create a new message without progress bar
              addMessage({
                id: generateId(),
                content: `Flight search completed! View your flights <a class="underline" href="${data.url}" target="_blank">here</a>.`,
                role: MessageRole.Task,
                completed: true,
              });
            } else if (taskType === TaskType.HotelSearch) {
              addMessage({
                id: generateId(),
                content: "Hotel search completed!",
                role: MessageRole.Task,
                completed: true,
              });
            }
          } else if (status === TaskStatus.Failed) {
            addMessage({
              id: generateId(),
              content: `${taskType} search failed. Please try again.`,
              role: MessageRole.Task,
              completed: true,
            });
          }
        }
      }

      // Check if all tasks are completed or failed
      const allTasksFinished = Object.values(tasks.value).every(
        (task) => task.status === TaskStatus.Completed || task.status === TaskStatus.Failed
      );

      if (allTasksFinished) {
        stopPolling();
        return true; // All tasks are finished
      }

      return false; // Some tasks are still running
    } catch (e) {
      console.error("Error checking task status:", e);
      stopPolling();
      addMessage({
        id: generateId(),
        content: "Task status check failed. Please try again.",
        role: MessageRole.Task,
        completed: true,
      });
      return true; // Stop due to error
    }
  };

  // Store task message ID and set initial progress
  const addTaskMessage = (taskType: TaskType, message: Message) => {
    const task = tasks.value[taskType];
    // Store message ID for later updates
    taskMessages.value[taskType] = message.id;

    // Set initial progress based on current task status
    if (task) {
      message.completed = task.status === TaskStatus.Completed;
    }

    addMessage(message);
    return message.id;
  };

  // Clean up polling when component is unmounted
  onUnmounted(() => {
    stopPolling();
  });

  return {
    tasks,
    startPolling,
    stopPolling,
    setTaskProcessing,
    monitorTaskStatus,
    addTaskMessage,
  };
}
