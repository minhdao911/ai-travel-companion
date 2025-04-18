import type { Message } from "@/types";
import { hash } from "@/utils/common";

const API_URL = import.meta.env.VITE_API_URL;

// Types to represent the structured data coming from the stream
// Keep these in sync with the backend event types
type StreamEventToken = {
  type: "token";
  content: string;
};

type StreamEventToolStart = {
  type: "tool_start";
  name: string;
  input: any;
};

type StreamEventToolEnd = {
  type: "tool_end";
  name: string;
};

type StreamEventToolCallChunk = {
  type: "tool_call_chunk";
  chunk: {
    name?: string;
    args?: string;
    id?: string;
    index?: number;
  };
};

type StreamEventError = {
  type: "error";
  message: string;
};

type StreamEventEnd = {
  type: "end";
};

type StreamEvent =
  | StreamEventToken
  | StreamEventToolStart
  | StreamEventToolEnd
  | StreamEventToolCallChunk
  | StreamEventError
  | StreamEventEnd;

// Callbacks for the stream handler
interface StreamCallbacks {
  onToken?: (token: string) => void;
  onToolCallChunk?: (chunk: StreamEventToolCallChunk["chunk"]) => void;
  onToolStart?: (name: string, input: any) => void;
  onToolEnd?: (name: string) => void;
  onError?: (message: string) => void;
  onEnd?: () => void;
}

/**
 * Calls the backend streaming endpoint and processes Server-Sent Events.
 */
export const streamChat = async (
  // Use the updated Message type, selecting necessary fields + optional tool fields
  messages: Array<
    Pick<Message, "role" | "content"> & Partial<Pick<Message, "tool_calls" | "tool_call_id">>
  >,
  callbacks: StreamCallbacks
): Promise<void> => {
  try {
    const response = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ messages }), // Send the message history
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    // Process the stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = ""; // Buffer for incoming data chunks

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        // console.log("Stream finished.");
        break; // Exit the loop when the stream is done
      }

      // Decode the chunk and add it to the buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages (delimit by \n\n)
      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const messageLine = buffer.substring(0, boundary); // Extract the message line
        buffer = buffer.substring(boundary + 2); // Remove the processed message and \n\n

        if (messageLine.startsWith("data:")) {
          const jsonData = messageLine.substring(5).trim(); // Remove "data:" prefix
          if (jsonData) {
            try {
              const event: StreamEvent = JSON.parse(jsonData);

              // Call the appropriate callback based on the event type
              switch (event.type) {
                case "token":
                  callbacks.onToken?.(event.content);
                  break;
                case "tool_call_chunk":
                  callbacks.onToolCallChunk?.(event.chunk);
                  break;
                case "tool_start":
                  callbacks.onToolStart?.(event.name, event.input);
                  break;
                case "tool_end":
                  callbacks.onToolEnd?.(event.name);
                  break;
                case "error":
                  console.error("Stream Error Event:", event.message);
                  callbacks.onError?.(event.message);
                  break;
                case "end":
                  // console.log("Received end event from stream.");
                  // The finally block handles the actual onEnd callback call
                  break;
              }
            } catch (e) {
              console.error("Failed to parse stream data:", jsonData, e);
              callbacks.onError?.(`Failed to parse stream data: ${jsonData}`);
            }
          }
        }
        // Check for the next message boundary in the updated buffer
        boundary = buffer.indexOf("\n\n");
      }
    }
    // console.log("Stream processing loop finished.");
  } catch (error) {
    console.error("Failed to stream recommendation:", error);
    callbacks.onError?.(
      error instanceof Error ? error.message : "An unknown streaming error occurred"
    );
  } finally {
    // console.log("Calling onEnd callback.");
    // Ensure onEnd is always called, regardless of how the stream finished
    callbacks.onEnd?.();
  }
};

export const getChatTitle = async (userInput: string): Promise<string> => {
  const response = await fetch(`${API_URL}/api/chat/summary`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_input: userInput }),
  });

  if (!response.ok) {
    throw new Error("Failed to get chat title");
  }

  const data = await response.json();
  return data.summary;
};

export const verifyAdmin = async (username: string, password: string): Promise<boolean> => {
  const response = await fetch(`${API_URL}/api/verify-admin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "include",
    body: `username=${username}&password=${hash(password)}`,
  });

  if (!response.ok) {
    throw new Error("Unauthorized");
  }

  const data = await response.json();
  return data.is_admin;
};

export const checkAdmin = async (): Promise<boolean> => {
  const response = await fetch(`${API_URL}/api/check-admin`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to check admin status");
  }

  const data = await response.json();
  return data.is_admin;
};
