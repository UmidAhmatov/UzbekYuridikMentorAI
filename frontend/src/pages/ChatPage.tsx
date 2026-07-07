import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Send } from "lucide-react";

import { streamChat } from "../api/chat";
import type { ChatMessage, LegalSource } from "../api/chat";
import { ErrorNotice } from "../components/ErrorNotice";
import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./ChatPage.module.css";

type ChatPageProps = {
  language: Language;
};

export function ChatPage({ language }: ChatPageProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: t(language, "greeting") },
  ]);
  const [input, setInput] = useState("");
  const [chatId, setChatId] = useState<string | null>(null);
  const [sources, setSources] = useState<LegalSource[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSend = useMemo(() => input.trim().length > 0 && !isStreaming, [input, isStreaming]);

  useEffect(() => {
    setMessages([{ role: "assistant", content: t(language, "greeting") }]);
    setChatId(null);
    setSources([]);
    setError(null);
  }, [language]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) {
      return;
    }

    const history = messages.filter((message) => message.content.trim().length > 0);
    setInput("");
    setError(null);
    setSources([]);
    setIsStreaming(true);
    setMessages((current) => [...current, { role: "user", content: text }, { role: "assistant", content: "" }]);

    try {
      await streamChat({
        message: text,
        chatId,
        history,
        language,
        onContext: (nextChatId, nextSources) => {
          setChatId(nextChatId);
          setSources(nextSources);
        },
        onDelta: (delta) => {
          setMessages((current) => {
            const next = [...current];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, content: `${last.content}${delta}` };
            return next;
          });
        },
        onDone: setChatId,
        onError: (message) => {
          setError(message);
          removeEmptyAssistantMessage();
        },
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t(language, "unexpectedError"));
      removeEmptyAssistantMessage();
    } finally {
      setIsStreaming(false);
    }
  }

  function removeEmptyAssistantMessage() {
    setMessages((current) => {
      const last = current[current.length - 1];
      if (last?.role === "assistant" && last.content.trim().length === 0) {
        return current.slice(0, -1);
      }
      return current;
    });
  }

  return (
    <section className={styles.chat} aria-label={t(language, "chatTitle")}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>{t(language, "aiMentor")}</p>
          <h1 className={styles.title}>{t(language, "chatTitle")}</h1>
        </div>
        <span className={styles.badge}>{isStreaming ? t(language, "writing") : t(language, "ready")}</span>
      </header>

      {sources.length > 0 && (
        <aside className={styles.sources} aria-label={t(language, "legalSources")}>
          {sources.map((source) => (
            <a className={styles.source} href={source.source_url} key={source.id} rel="noreferrer" target="_blank">
              <span>{source.law_title}</span>
              {source.article_number && <small>{source.article_number}</small>}
            </a>
          ))}
        </aside>
      )}

      <div className={styles.messages} aria-live="polite">
        {messages.map((message, index) => (
          <article className={`${styles.message} ${styles[message.role]}`} key={`${message.role}-${index}`}>
            <p>{message.content || (message.role === "assistant" ? "..." : "")}</p>
          </article>
        ))}
      </div>

      {error && (
        <div className={styles.error}>
          <ErrorNotice language={language} message={error} />
        </div>
      )}

      <form className={styles.composer} onSubmit={handleSubmit}>
        <textarea
          aria-label={t(language, "message")}
          onChange={(event) => setInput(event.target.value)}
          placeholder={t(language, "messagePlaceholder")}
          rows={2}
          value={input}
        />
        <button
          aria-label={t(language, "send")}
          disabled={!canSend}
          title={t(language, "send")}
          type="submit"
        >
          <Send aria-hidden="true" size={20} />
        </button>
      </form>
    </section>
  );
}

