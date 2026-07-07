import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Check, Clipboard, Download, FilePlus2, LoaderCircle, RotateCcw, Sparkles } from "lucide-react";

import {
  generateDocument,
  getDocumentTemplates,
  resolveApiUrl,
} from "../api/documents";
import type {
  DocumentField,
  DocumentTemplate,
  DocumentType,
  GeneratedDocument,
} from "../api/documents";
import { ErrorNotice } from "../components/ErrorNotice";
import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./DocumentsPage.module.css";

type DocumentsPageProps = {
  language: Language;
};

export function DocumentsPage({ language }: DocumentsPageProps) {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [selectedType, setSelectedType] = useState<DocumentType | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<GeneratedDocument | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadTemplates() {
    setIsLoading(true);
    setError(null);
    try {
      const items = await getDocumentTemplates(language);
      setTemplates(items);
      setSelectedType(items[0]?.type ?? null);
    } catch (caught) {
      setTemplates([]);
      setSelectedType(null);
      setError(caught instanceof Error ? caught.message : t(language, "unexpectedError"));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    setValues({});
    setResult(null);
    setCopied(false);
    void loadTemplates();
  }, [language]);

  const selectedTemplate = useMemo(
    () => templates.find((template) => template.type === selectedType) ?? null,
    [selectedType, templates],
  );

  function selectTemplate(type: DocumentType) {
    if (type === selectedType) {
      return;
    }
    setSelectedType(type);
    setValues({});
    setResult(null);
    setError(null);
    setCopied(false);
  }

  function updateValue(name: string, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTemplate || isGenerating) {
      return;
    }

    setError(null);
    setResult(null);
    setCopied(false);
    setIsGenerating(true);
    try {
      setResult(await generateDocument(selectedTemplate.type, values, language));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : t(language, "unexpectedError"));
    } finally {
      setIsGenerating(false);
    }
  }

  async function copyDocument() {
    if (!result) {
      return;
    }
    await navigator.clipboard.writeText(`${result.content}\n\n${result.disclaimer}`);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  function resetDocument() {
    setResult(null);
    setValues({});
    setError(null);
    setCopied(false);
  }

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <LoaderCircle aria-hidden="true" className={styles.spinner} size={22} />
        {t(language, "loading")}
      </div>
    );
  }

  if (error && templates.length === 0) {
    return (
      <div className={styles.loading}>
        <ErrorNotice language={language} message={error} onRetry={() => void loadTemplates()} />
      </div>
    );
  }

  return (
    <section className={styles.workspace} aria-label={t(language, "documents")}>
      <aside className={styles.templateRail}>
        <header className={styles.railHeader}>
          <p>{t(language, "documentType")}</p>
          <span>{templates.length}</span>
        </header>
        <div className={styles.templateList}>
          {templates.map((template) => (
            <button
              aria-pressed={template.type === selectedType}
              className={`${styles.templateButton} ${template.type === selectedType ? styles.templateActive : ""}`}
              key={template.type}
              onClick={() => selectTemplate(template.type)}
              type="button"
            >
              <FilePlus2 aria-hidden="true" size={18} />
              <span>
                <strong>{template.title}</strong>
                <small>{template.description}</small>
              </span>
            </button>
          ))}
        </div>
      </aside>

      <main className={styles.documentArea}>
        {selectedTemplate && !result && (
          <>
            <header className={styles.documentHeader}>
              <div>
                <p className={styles.eyebrow}>{t(language, "newDocument")}</p>
                <h1>{selectedTemplate.title}</h1>
                <p>{selectedTemplate.description}</p>
              </div>
            </header>

            <form className={styles.form} onSubmit={handleGenerate}>
              <div className={styles.fieldGrid}>
                {selectedTemplate.fields.map((field) => (
                  <DocumentInput
                    field={field}
                    key={field.name}
                    language={language}
                    onChange={(value) => updateValue(field.name, value)}
                    value={values[field.name] ?? ""}
                  />
                ))}
              </div>

              {error && (
                <div className={styles.error}>
                  <ErrorNotice language={language} message={error} />
                </div>
              )}

              <div className={styles.formActions}>
                <button className={styles.primaryButton} disabled={isGenerating} type="submit">
                  {isGenerating ? (
                    <LoaderCircle aria-hidden="true" className={styles.spinner} size={18} />
                  ) : (
                    <Sparkles aria-hidden="true" size={18} />
                  )}
                  {isGenerating ? t(language, "generating") : t(language, "generateDocument")}
                </button>
              </div>
            </form>
          </>
        )}

        {result && (
          <div className={styles.result}>
            <header className={styles.resultHeader}>
              <div>
                <p className={styles.eyebrow}>{t(language, "readyDocument")}</p>
                <h1>{result.title}</h1>
              </div>
              <div className={styles.resultActions}>
                <button onClick={resetDocument} title={t(language, "newDocument")} type="button">
                  <RotateCcw aria-hidden="true" size={18} />
                  <span>{t(language, "newAgain")}</span>
                </button>
                <button onClick={copyDocument} title={t(language, "copy")} type="button">
                  {copied ? <Check aria-hidden="true" size={18} /> : <Clipboard aria-hidden="true" size={18} />}
                  <span>{copied ? t(language, "copied") : t(language, "copy")}</span>
                </button>
                <a href={resolveApiUrl(result.pdf_url)} title={t(language, "downloadPdf")}>
                  <Download aria-hidden="true" size={18} />
                  <span>PDF</span>
                </a>
              </div>
            </header>

            <div className={styles.resultBody}>
              {result.sources.length > 0 && (
                <aside className={styles.sources} aria-label={t(language, "legalSources")}>
                  <strong>{t(language, "legalSources")}</strong>
                  <div>
                    {result.sources.map((source) => (
                      <a href={source.source_url} key={source.id} rel="noreferrer" target="_blank">
                        {source.article_number ? `${source.article_number}-modda` : source.law_title}
                      </a>
                    ))}
                  </div>
                </aside>
              )}

              <article className={styles.paper}>
                <div className={styles.documentText}>{result.content}</div>
              </article>

              <aside className={styles.disclaimer}>
                <strong>{t(language, "legalNotice")}</strong>
                <p>{result.disclaimer}</p>
              </aside>
            </div>
          </div>
        )}
      </main>
    </section>
  );
}

type DocumentInputProps = {
  field: DocumentField;
  language: Language;
  value: string;
  onChange: (value: string) => void;
};

function DocumentInput({ field, language, value, onChange }: DocumentInputProps) {
  const inputId = `document-field-${field.name}`;
  const className = field.field_type === "textarea" ? styles.fullWidth : undefined;

  return (
    <label className={className} htmlFor={inputId}>
      <span>
        {field.label}
        {field.required && <b aria-hidden="true">*</b>}
      </span>
      {field.field_type === "textarea" && (
        <textarea
          id={inputId}
          onChange={(event) => onChange(event.target.value)}
          placeholder={field.placeholder ?? undefined}
          required={field.required}
          rows={4}
          value={value}
        />
      )}
      {field.field_type === "select" && (
        <select
          id={inputId}
          onChange={(event) => onChange(event.target.value)}
          required={field.required}
          value={value}
        >
          <option value="">{t(language, "select")}</option>
          {field.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      )}
      {(field.field_type === "text" || field.field_type === "date") && (
        <input
          id={inputId}
          onChange={(event) => onChange(event.target.value)}
          placeholder={field.placeholder ?? undefined}
          required={field.required}
          type={field.field_type}
          value={value}
        />
      )}
      {field.help_text && <small>{field.help_text}</small>}
    </label>
  );
}
