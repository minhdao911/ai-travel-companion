import { ref } from "vue";

// Interface for timer results
export interface TimerResult {
  startTime: number;
  endTime: number;
  durationMs: number;
  durationSec: string;
}

// Map to store timers by process name
const timers = new Map<
  string,
  {
    startTime: number | null;
    endTime: number | null;
  }
>();

/**
 * Start timing a process
 * @param processName Unique identifier for the process
 * @param logToConsole Whether to log to console (default: true)
 * @returns The start timestamp
 */
export function startTimer(processName: string, logToConsole = true): number {
  const startTime = Date.now();

  // Store the start time
  timers.set(processName, {
    startTime,
    endTime: null,
  });

  if (logToConsole) {
    console.log(`⏱️ ${processName} started at ${new Date(startTime).toISOString()}`);
  }

  return startTime;
}

/**
 * End timing a process and get results
 * @param processName Unique identifier for the process
 * @param logToConsole Whether to log to console (default: true)
 * @returns Timer result object or null if process wasn't started
 */
export function endTimer(processName: string, logToConsole = true): TimerResult | null {
  const timer = timers.get(processName);

  if (!timer || timer.startTime === null) {
    console.warn(`Timer "${processName}" was not started`);
    return null;
  }

  const endTime = Date.now();
  const durationMs = endTime - timer.startTime;
  const durationSec = (durationMs / 1000).toFixed(2);

  // Update timer with end time
  timers.set(processName, {
    ...timer,
    endTime,
  });

  if (logToConsole) {
    console.log(`⏱️ ${processName} completed in ${durationSec} seconds`);
  }

  return {
    startTime: timer.startTime,
    endTime,
    durationMs,
    durationSec,
  };
}

/**
 * Time an async function execution
 * @param processName Name of the process for logging
 * @param asyncFn The async function to time
 * @param logToConsole Whether to log to console (default: true)
 * @returns Result of the async function and timing information
 */
export async function timeAsync<T>(
  processName: string,
  asyncFn: () => Promise<T>,
  logToConsole = true
): Promise<{ result: T; timing: TimerResult }> {
  startTimer(processName, logToConsole);

  try {
    const result = await asyncFn();
    const timing = endTimer(processName, logToConsole);

    return {
      result,
      timing: timing as TimerResult,
    };
  } catch (error) {
    // Still record the timing even if the function fails
    const timing = endTimer(processName, logToConsole);
    throw error;
  }
}

/**
 * Get the current state of a timer
 * @param processName Name of the process
 * @returns Current timer state or null if not found
 */
export function getTimerState(processName: string) {
  return timers.get(processName) || null;
}

/**
 * Reset a specific timer
 * @param processName Name of the process to reset
 */
export function resetTimer(processName: string) {
  timers.delete(processName);
}

/**
 * Reset all timers
 */
export function resetAllTimers() {
  timers.clear();
}

// Constants for common process names
export const PROCESS_NAMES = {
  TRAVEL_PLANNING: "Travel Planning Process",
  FLIGHT_SEARCH: "Flight Search",
  HOTEL_SEARCH: "Hotel Search",
  TRAVEL_SUMMARY: "Travel Summary",
};
