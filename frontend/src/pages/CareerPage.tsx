import { BriefcaseBusiness, LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { generateCareerAdvice } from "../api/mentor";
import type { AdviceResponse, CareerPayload } from "../api/mentor";
import { AdviceResult } from "../components/AdviceResult";
import { ErrorNotice } from "../components/ErrorNotice";
import type { Language } from "../i18n";
import { t } from "../i18n";
import styles from "./MentorForm.module.css";

type CareerPageProps = {
  language: Language;
};

const emptyCareer: Omit<CareerPayload, "language"> = {
  current_role: "",
  experience_level: "",
  target_role: "",
  skills: "",
  region: "",
  employment_type: "",
  notes: "",
};

export function CareerPage({ language }: CareerPageProps) {
  const [values, setValues] = useState(emptyCareer);
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
      setResult(await generateCareerAdvice({ ...values, language }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Karyera rejasini tuzib bo'lmadi.");
    } finally {
      setIsLoading(false);
    }
  }

  if (result) {
    return <AdviceResult advice={result} language={language} onReset={() => setResult(null)} />;
  }

  return (
    <section className={styles.page} aria-label={t(language, "career")}>
      <header className={styles.intro}>
        <p className={styles.eyebrow}>{t(language, "careerEyebrow")}</p>
        <h1>{t(language, "careerTitle")}</h1>
        <p>{t(language, "careerDescription")}</p>
      </header>

      <form className={styles.form} onSubmit={submit}>
        <div className={styles.grid}>
          <label>
            <span>{t(language, "currentRole")}<b aria-hidden="true">*</b></span>
            <input
              onChange={(event) => update("current_role", event.target.value)}
              placeholder={t(language, "currentRolePlaceholder")}
              required
              value={values.current_role}
            />
          </label>
          <label>
            <span>{t(language, "experienceLevel")}<b aria-hidden="true">*</b></span>
            <input
              onChange={(event) => update("experience_level", event.target.value)}
              placeholder={t(language, "experienceLevelPlaceholder")}
              required
              value={values.experience_level}
            />
          </label>
          <label>
            <span>{t(language, "targetRole")}<b aria-hidden="true">*</b></span>
            <input
              onChange={(event) => update("target_role", event.target.value)}
              placeholder={t(language, "targetRolePlaceholder")}
              required
              value={values.target_role}
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
          <label className={styles.fullWidth}>
            <span>{t(language, "skills")}<b aria-hidden="true">*</b></span>
            <textarea
              onChange={(event) => update("skills", event.target.value)}
              placeholder={t(language, "skillsPlaceholder")}
              required
              rows={4}
              value={values.skills}
            />
          </label>
          <label>
            <span>{t(language, "employmentType")}</span>
            <input
              onChange={(event) => update("employment_type", event.target.value)}
              placeholder={t(language, "employmentTypePlaceholder")}
              value={values.employment_type}
            />
          </label>
          <label>
            <span>{t(language, "notes")}</span>
            <input
              onChange={(event) => update("notes", event.target.value)}
              placeholder={t(language, "notesPlaceholder")}
              value={values.notes}
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
              <BriefcaseBusiness aria-hidden="true" size={18} />
            )}
            {isLoading ? t(language, "careerGenerating") : t(language, "generateCareer")}
          </button>
        </div>
      </form>
    </section>
  );
}
