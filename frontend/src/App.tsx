import { useEffect, useState } from "react";
import { BriefcaseBusiness, FileText, Languages, MapPinned, MessageSquareText } from "lucide-react";

import { ErrorBoundary } from "./components/ErrorBoundary";
import type { Language } from "./i18n";
import { languageOptions, t } from "./i18n";
import { CareerPage } from "./pages/CareerPage";
import { ChatPage } from "./pages/ChatPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { RoadmapPage } from "./pages/RoadmapPage";
import styles from "./App.module.css";

type AppView = "chat" | "documents" | "roadmap" | "career";

function App() {
  const [view, setView] = useState<AppView>("documents");
  const [language, setLanguage] = useState<Language>(() => {
    const stored = window.localStorage.getItem("uzbekmentor-language");
    return stored === "uz-cyrillic" || stored === "ru" ? stored : "uz-latin";
  });

  useEffect(() => {
    window.localStorage.setItem("uzbekmentor-language", language);
    document.documentElement.lang = language === "ru" ? "ru" : "uz";
  }, [language]);

  const navItems = [
    { id: "chat" as const, label: t(language, "chat"), icon: MessageSquareText },
    { id: "documents" as const, label: t(language, "documents"), icon: FileText },
    { id: "roadmap" as const, label: t(language, "roadmap"), icon: MapPinned },
    { id: "career" as const, label: t(language, "career"), icon: BriefcaseBusiness },
  ];

  return (
    <main className={styles.shell}>
      <section className={styles.appFrame}>
        <header className={styles.appHeader}>
          <div className={styles.brand}>
            <span className={styles.brandMark}>O'M</span>
            <span>
              <strong>O'zbekMentorAI</strong>
              <small>{t(language, "brandSubtitle")}</small>
            </span>
          </div>

          <nav aria-label={t(language, "mainNavigation")} className={styles.nav}>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  aria-current={view === item.id ? "page" : undefined}
                  aria-label={item.label}
                  className={view === item.id ? styles.active : ""}
                  key={item.id}
                  onClick={() => setView(item.id)}
                  title={item.label}
                  type="button"
                >
                  <Icon aria-hidden="true" size={18} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <label className={styles.language}>
            <Languages aria-hidden="true" size={17} />
            <span>{t(language, "language")}</span>
            <select
              aria-label={t(language, "language")}
              onChange={(event) => setLanguage(event.target.value as Language)}
              value={language}
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </header>

        <div className={styles.content}>
          <ErrorBoundary language={language}>
            {view === "chat" && <ChatPage language={language} />}
            {view === "documents" && <DocumentsPage language={language} />}
            {view === "roadmap" && <RoadmapPage language={language} />}
            {view === "career" && <CareerPage language={language} />}
          </ErrorBoundary>
        </div>
      </section>
    </main>
  );
}

export default App;

