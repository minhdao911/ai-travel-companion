import { ref, onUnmounted } from "vue";
import { TaskStatus, TaskType, MessageRole, type Message } from "@/types";
import { checkTaskStatus } from "@/services/api";
import { generateId } from "@/utils/id";
import { marked } from "marked";

// Define interface for task state
interface TaskState {
  id: string | null;
  status: TaskStatus;
  messageId: string | null;
  processingMessageSent: boolean;
}

// Define task handling configuration for different task types
interface TaskHandlerConfig {
  processingMessage: string;
  completedMessage: string;
}

export function useTasks(
  addMessage: (message: Message) => void,
  updateMessage: (id: string, data: Partial<Message>) => void
) {
  const pollInterval = ref<number | null>(null);

  // Consolidated task state
  const taskStates = ref<Record<TaskType, TaskState>>({
    [TaskType.HotelSearch]: {
      id: null,
      status: TaskStatus.Idle,
      messageId: null,
      processingMessageSent: false,
    },
    [TaskType.FlightSearch]: {
      id: null,
      status: TaskStatus.Idle,
      messageId: null,
      processingMessageSent: false,
    },
  });

  // Task-specific handling config
  const taskHandlers: Record<TaskType, TaskHandlerConfig> = {
    [TaskType.FlightSearch]: {
      processingMessage: "✈️  Analyzing flight options and prices..",
      completedMessage: "✈️  Flight search completed!",
    },
    [TaskType.HotelSearch]: {
      processingMessage: "🏨  Searching for hotels..",
      completedMessage: "🏨  Hotel search completed!",
    },
  };

  // Update task message progress based on status
  const updateTaskMessageProgress = (taskType: TaskType) => {
    const { messageId, status } = taskStates.value[taskType];

    if (messageId) {
      updateMessage(messageId, {
        loading: status === TaskStatus.Processing || status === TaskStatus.Pending,
      });
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
    const taskState = taskStates.value[taskType];
    if (taskState) {
      taskState.id = taskId;
      taskState.status = TaskStatus.Processing;
      taskState.processingMessageSent = false;
      updateTaskMessageProgress(taskType);
    }
  };

  const handleTaskStatusChange = async (taskType: TaskType, status: TaskStatus, data?: any) => {
    const taskState = taskStates.value[taskType];
    const handler = taskHandlers[taskType];

    if (status === TaskStatus.Failed) {
      addMessage({
        id: generateId(),
        content: `${taskType} failed. Please try again.`,
        role: MessageRole.Task,
        loading: false,
      });
    } else if (status === TaskStatus.Completed) {
      if (taskType === TaskType.FlightSearch) {
        const output = await marked.parse(data);
        addMessage({
          id: generateId(),
          content: output,
          role: MessageRole.Task,
          loading: false,
        });
      }
    } else if (status === TaskStatus.Processing) {
      if (data?.url && !taskState.processingMessageSent) {
        addMessage({
          id: generateId(),
          content: handler.processingMessage,
          role: MessageRole.Task,
        });
        taskState.processingMessageSent = true;
      }
    }
  };

  const monitorTaskStatus = async () => {
    try {
      // Check statuses of all active tasks
      for (const taskType in taskStates.value) {
        const taskState = taskStates.value[taskType as TaskType];
        if (taskState.id) {
          const { status, data } = await checkTaskStatus(taskState.id);

          // Update task status if changed
          if (taskState.status !== status) {
            taskState.status = status;
            updateTaskMessageProgress(taskType as TaskType);

            // Reset processing message flag when status changes from Processing to something else
            if (status !== TaskStatus.Processing) {
              taskState.processingMessageSent = false;
            }

            // Handle specific task status changes
            await handleTaskStatusChange(taskType as TaskType, status, data);
          }
        }
      }

      // Check if all tasks are completed or failed
      const allTasksFinished = Object.values(taskStates.value).every(
        (task) =>
          task.status === TaskStatus.Completed ||
          task.status === TaskStatus.Failed ||
          task.status === TaskStatus.Idle
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
        loading: false,
      });
      return true; // Stop due to error
    }
  };

  // Store task message ID and set initial progress
  const addTaskMessage = (taskType: TaskType, message: Message) => {
    const taskState = taskStates.value[taskType];

    // Store message ID for later updates
    taskState.messageId = message.id;

    // Set initial progress
    message.loading = true;

    addMessage(message);
    return message.id;
  };

  // Clean up polling when component is unmounted
  onUnmounted(() => {
    stopPolling();
  });

  return {
    tasks: taskStates,
    startPolling,
    stopPolling,
    setTaskProcessing,
    monitorTaskStatus,
    addTaskMessage,
  };
}
