import { LoaderCircle, MapPinned } from "lucide-react";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { generateRoadmap } from "../api/mentor";
import type { AdviceResponse, RoadmapPayload } from "../api/mentor";
import { AdviceResult } from "../components/AdviceResult";
import { ErrorNotice } from "../components/ErrorNotice";
import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./MentorForm.module.css";

type RoadmapPageProps = {
  language: Language;
};

const emptyRoadmap: Omit<RoadmapPayload, "language"> = {
  situation: "",
  goal: "",
  region: "",
  event_date: "",
  available_documents: "",
};

export function RoadmapPage({ language }: RoadmapPageProps) {
  const [values, setValues] = useState(emptyRoadmap);
  const [result, setResult] = useState<AdviceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setResult(null);
    setError(null);
  }, [language]);

  function update(name: keyof typeof values, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      setResult(await generateRoadmap({ ...values, language }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Yo'l xaritasini tuzib bo'lmadi.");
    } finally {
      setIsLoading(false);
    }
  }

  if (result) {
    return <AdviceResult advice={result} language={language} onReset={() => setResult(null)} />;
  }

  return (
    <section className={styles.page} aria-label={t(language, "roadmap")}>
      <header className={styles.intro}>
        <p className={styles.eyebrow}>{t(language, "roadmapEyebrow")}</p>
        <h1>{t(language, "roadmapTitle")}</h1>
        <p>{t(language, "roadmapDescription")}</p>
      </header>

      <form className={styles.form} onSubmit={submit}>
        <div className={styles.grid}>
          <label className={styles.fullWidth}>
            <span>{t(language, "situation")}<b aria-hidden="true">*</b></span>
            <textarea
              onChange={(event) => update("situation", event.target.value)}
              placeholder={t(language, "situationPlaceholder")}
              required
              rows={5}
              value={values.situation}
            />
          </label>
          <label className={styles.fullWidth}>
            <span>{t(language, "goal")}<b aria-hidden="true">*</b></span>
            <textarea
              onChange={(event) => update("goal", event.target.value)}
              placeholder={t(language, "goalPlaceholder")}
              required
              rows={3}
              value={values.goal}
            />
          </label>
          <label>
            <span>{t(language, "region")}</span>
            <input
              onChange={(event) => update("region", event.target.value)}
              placeholder={t(language, "regionPlaceholder")}
              value={values.region}
            />
          </label>
          <label>
            <span>{t(language, "eventDate")}</span>
            <input
              onChange={(event) => update("event_date", event.target.value)}
              placeholder={t(language, "eventDatePlaceholder")}
              value={values.event_date}
            />
          </label>
          <label className={styles.fullWidth}>
            <span>{t(language, "availableDocuments")}</span>
            <textarea
              onChange={(event) => update("available_documents", event.target.value)}
              placeholder={t(language, "availableDocumentsPlaceholder")}
              rows={3}
              value={values.available_documents}
            />
          </label>
        </div>

        {error && (
          <div className={styles.error}>
            <ErrorNotice language={language} message={error} />
          </div>
        )}

        <div className={styles.actions}>
          <button disabled={isLoading} type="submit">
            {isLoading ? (
              <LoaderCircle aria-hidden="true" className={styles.spinner} size={18} />
            ) : (
              <MapPinned aria-hidden="true" size={18} />
            )}
            {isLoading ? t(language, "roadmapGenerating") : t(language, "generateRoadmap")}
          </button>
        </div>
      </form>
    </section>
  );
}
