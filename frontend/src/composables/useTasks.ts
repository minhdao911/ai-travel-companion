import { ref, onUnmounted } from "vue";
import { TaskStatus, TaskType, type Message, MessageRole } from "@/types";
import { checkTaskStatus, getTravelSummary } from "@/services/api";
import { useTravelStore } from "@/stores/travel";
import { marked } from "marked";
import { useTaskStore } from "@/stores/tasks";
import { generateId } from "@/utils/id";

export function useTasks(
  setLoading: (loading: boolean) => void,
  addMessage: (message: Omit<Message, "id"> & { id?: string }) => void,
  updateMessage: (id: string, data: Partial<Message>) => void
) {
  const travelStore = useTravelStore();
  const taskStore = useTaskStore();

  const pollInterval = ref<number | null>(null);

  // Update task message progress based on status
  const updateTaskMessageProgress = (taskType: TaskType) => {
    const { messageId, status } = taskStore.tasks[taskType];

    if (messageId) {
      updateMessage(messageId, {
        loading: status === TaskStatus.Processing || status === TaskStatus.Pending,
      });
    }
  };

  const startPolling = (taskType: TaskType) => {
    // Poll every 2 seconds
    pollInterval.value = setInterval(() => monitorTaskStatus(taskType), 2000) as unknown as number;
  };

  const stopPolling = () => {
    if (pollInterval.value !== null) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
    }
  };

  const setTaskProcessing = (taskType: TaskType, taskId: string) => {
    const taskState = taskStore.tasks[taskType];
    if (taskState) {
      taskStore.updateTask(taskType, {
        id: taskId,
        status: TaskStatus.Processing,
      });
      updateTaskMessageProgress(taskType);
    }
  };

  const handleTaskStatusChange = async (taskType: TaskType, status: TaskStatus, data?: any) => {
    if (status === TaskStatus.Failed) {
      addMessage({
        role: MessageRole.Task,
        content: `${taskType} failed. Please try again.`,
        taskType: taskType,
      });
      setLoading(false);
    } else if (status === TaskStatus.Completed) {
      if (taskType === TaskType.FlightSearch) {
        travelStore.setContext({ flights: data });

        const loadingMessageId = generateId();
        addMessage({
          id: loadingMessageId,
          role: MessageRole.Info,
          content: "🛫 Analyzing flight options and prices...",
          loading: true,
        });

        const summary = await getTravelSummary(data);
        const output = await marked.parse(summary);

        updateMessage(loadingMessageId, {
          loading: false,
        });
        addMessage({
          role: MessageRole.Task,
          content: output,
          taskType: taskType,
        });
        setLoading(false);
      }
    }
  };

  const isTaskProcessing = (status: TaskStatus) => {
    return status === TaskStatus.Processing || status === TaskStatus.Pending;
  };

  const monitorTaskStatus = async (taskType: TaskType) => {
    try {
      // Check status of active task
      const taskState = taskStore.tasks[taskType];
      if (taskState.id) {
        const { status, data } = await checkTaskStatus(taskState.id);

        // Update task status if changed
        if (taskState.status !== status) {
          taskStore.updateTask(taskType, { status });
          updateTaskMessageProgress(taskType as TaskType);

          // Handle specific task status changes
          await handleTaskStatusChange(taskType as TaskType, status, data);
        }

        if (isTaskProcessing(status)) return false;
      }
      stopPolling();
      return true; // Some tasks are still running
    } catch (e) {
      console.error("Error checking task status:", e);
      addMessage({
        role: MessageRole.Info,
        content: "An error occurred. Please try again.",
      });
      stopPolling();
      return true; // Stop due to error
    }
  };

  const initializeTask = (taskType: TaskType, message: Message) => {
    // Store task message ID and set initial progress
    taskStore.addTask({
      status: TaskStatus.Processing,
      type: taskType,
      messageId: message.id,
    });

    addMessage(message);
    return message.id;
  };

  // Clean up polling when component is unmounted
  onUnmounted(() => {
    stopPolling();
  });

  return {
    startPolling,
    stopPolling,
    setTaskProcessing,
    initializeTask,
  };
}
