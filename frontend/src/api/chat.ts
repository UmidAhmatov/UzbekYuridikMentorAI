import { getApiBaseUrl } from "./client";
import type { Language } from "../i18n";

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type LegalSource = {
  id: string;
  source_id: string;
  source_url: string;
  law_title: string;
  article_number: string | null;
  heading: string | null;
  score: number;
};

type StreamChatArgs = {
  message: string;
  chatId: string | null;
  history: ChatMessage[];
  language: Language;
  onContext: (chatId: string, sources: LegalSource[]) => void;
  onDelta: (text: string) => void;
  onDone: (chatId: string) => void;
  onError: (message: string) => void;
};

type SseEvent = {
  event: string;
  data: unknown;
};

export async function streamChat({
  message,
  chatId,
  history,
  language,
  onContext,
  onDelta,
  onDone,
  onError,
}: StreamChatArgs) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 120_000);

  try {
    const response = await fetch(`${getApiBaseUrl()}/chat/stream`, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        chat_id: chatId,
        history,
        language,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error("Chat endpoint javob bermadi.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const eventBlock of events) {
        const parsed = parseSseEvent(eventBlock);
        if (!parsed) {
          continue;
        }

        if (parsed.event === "context") {
          const data = parsed.data as { chat_id: string; sources: LegalSource[] };
          onContext(data.chat_id, data.sources);
        }
        if (parsed.event === "delta") {
          const data = parsed.data as { text: string };
          onDelta(data.text);
        }
        if (parsed.event === "done") {
          const data = parsed.data as { chat_id: string };
          onDone(data.chat_id);
        }
        if (parsed.event === "error") {
          const data = parsed.data as { message: string };
          onError(data.message);
        }
      }
    }
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("So'rov vaqti tugadi. Qayta urinib ko'ring.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function parseSseEvent(block: string): SseEvent | null {
  const lines = block.split("\n");
  let event = "message";
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.replace("event:", "").trim();
    }
    if (line.startsWith("data:")) {
      dataLines.push(line.replace("data:", "").trim());
    }
  }

  if (dataLines.length === 0) {
    return null;
  }
  return {
    event,
    data: JSON.parse(dataLines.join("\n")),
  };
}

