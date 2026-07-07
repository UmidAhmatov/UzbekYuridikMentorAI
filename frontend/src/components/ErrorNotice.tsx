import { AlertTriangle, RotateCcw } from "lucide-react";

import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./ErrorNotice.module.css";

type ErrorNoticeProps = {
  message: string;
  language: Language;
  onRetry?: () => void;
};

export function ErrorNotice({ message, language, onRetry }: ErrorNoticeProps) {
  return (
    <div className={styles.notice} role="alert">
      <AlertTriangle aria-hidden="true" size={19} />
      <span>{message}</span>
      {onRetry && (
        <button onClick={onRetry} type="button">
          <RotateCcw aria-hidden="true" size={16} />
          {t(language, "retry")}
        </button>
      )}
    </div>
  );
}

