import { apiRequest } from "./client";
import type { Language } from "../i18n";

export type AdviceSource = {
  id: string;
  source_url: string;
  law_title: string;
  article_number: string | null;
  heading: string | null;
};

export type AdviceResponse = {
  title: string;
  content: string;
  disclaimer: string;
  sources: AdviceSource[];
};

export type RoadmapPayload = {
  situation: string;
  goal: string;
  region: string;
  event_date: string;
  available_documents: string;
  language: Language;
};

export type CareerPayload = {
  current_role: string;
  experience_level: string;
  target_role: string;
  skills: string;
  region: string;
  employment_type: string;
  notes: string;
  language: Language;
};

export function generateRoadmap(payload: RoadmapPayload): Promise<AdviceResponse> {
  return apiRequest<AdviceResponse>("/roadmap/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateCareerAdvice(payload: CareerPayload): Promise<AdviceResponse> {
  return apiRequest<AdviceResponse>("/career/advise", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

