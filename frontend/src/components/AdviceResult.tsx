import { Check, Clipboard, RotateCcw } from "lucide-react";
import { useState } from "react";

import type { AdviceResponse } from "../api/mentor";
import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./AdviceResult.module.css";

type AdviceResultProps = {
  advice: AdviceResponse;
  language: Language;
  onReset: () => void;
};

export function AdviceResult({ advice, language, onReset }: AdviceResultProps) {
  const [copied, setCopied] = useState(false);

  async function copyAdvice() {
    await navigator.clipboard.writeText(`${advice.content}\n\n${advice.disclaimer}`);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return (
    <div className={styles.result}>
      <header className={styles.header}>
        <div>
          <p>{t(language, "adviceResult")}</p>
          <h1>{advice.title}</h1>
        </div>
        <div className={styles.actions}>
          <button onClick={onReset} title={t(language, "startOver")} type="button">
            <RotateCcw aria-hidden="true" size={18} />
            <span>{t(language, "startOver")}</span>
          </button>
          <button onClick={copyAdvice} title={t(language, "copy")} type="button">
            {copied ? <Check aria-hidden="true" size={18} /> : <Clipboard aria-hidden="true" size={18} />}
            <span>{copied ? t(language, "copied") : t(language, "copy")}</span>
          </button>
        </div>
      </header>

      <div className={styles.body}>
        {advice.sources.length > 0 && (
          <aside className={styles.sources} aria-label={t(language, "legalSources")}>
            <strong>{t(language, "legalSources")}</strong>
            <div>
              {advice.sources.map((source) => (
                <a href={source.source_url} key={source.id} rel="noreferrer" target="_blank">
                  {source.article_number ? `${source.article_number}` : source.law_title}
                </a>
              ))}
            </div>
          </aside>
        )}
        <article className={styles.paper}>{advice.content}</article>
        <aside className={styles.disclaimer}>
          <strong>{t(language, "legalNotice")}</strong>
          <p>{advice.disclaimer}</p>
        </aside>
      </div>
    </div>
  );
}

