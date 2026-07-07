import { apiRequest } from "./client";
import type { Language } from "../i18n";

export type DocumentType =
  | "davo_arizasi"
  | "shikoyat"
  | "ishonchnoma"
  | "mehnat_shartnomasi"
  | "ijara_shartnomasi"
  | "sud_arizasi";

export type DocumentField = {
  name: string;
  label: string;
  field_type: "text" | "textarea" | "date" | "select";
  required: boolean;
  placeholder: string | null;
  help_text: string | null;
  options: string[];
};

export type DocumentTemplate = {
  type: DocumentType;
  title: string;
  description: string;
  fields: DocumentField[];
};

export type DocumentSource = {
  id: string;
  source_url: string;
  law_title: string;
  article_number: string | null;
  heading: string | null;
};

export type GeneratedDocument = {
  id: string;
  type: DocumentType;
  title: string;
  content: string;
  disclaimer: string;
  sources: DocumentSource[];
  pdf_url: string;
};

export function getDocumentTemplates(language: Language): Promise<DocumentTemplate[]> {
  return apiRequest<DocumentTemplate[]>(`/documents/templates?language=${encodeURIComponent(language)}`);
}

export function generateDocument(
  type: DocumentType,
  values: Record<string, string>,
  language: Language,
): Promise<GeneratedDocument> {
  return apiRequest<GeneratedDocument>("/documents/generate", {
    method: "POST",
    body: JSON.stringify({ type, values, language }),
  });
}

export { resolveApiUrl } from "./client";

