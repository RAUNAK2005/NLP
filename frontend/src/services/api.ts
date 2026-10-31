import type { Comparison, ComparisonDetail, Dataset } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function runDemo(): Promise<Comparison> {
  return request<Comparison>("/api/demo/run", { method: "POST" });
}

export function listComparisons(): Promise<Comparison[]> {
  return request<Comparison[]>("/api/comparisons");
}

export function getComparisonDetail(id: string): Promise<ComparisonDetail> {
  return request<ComparisonDetail>(`/api/comparisons/${id}/detail`);
}

export function listDatasets(): Promise<Dataset[]> {
  return request<Dataset[]>("/api/datasets");
}

export async function uploadDataset(file: File, datasetType: string, textColumn?: string, labelColumn?: string): Promise<Dataset> {
  const form = new FormData();
  form.append("file", file);
  form.append("dataset_type", datasetType);
  form.append("task_type", "sentiment_classification");
  if (textColumn) form.append("text_column", textColumn);
  if (labelColumn) form.append("label_column", labelColumn);
  const response = await fetch(`${API_URL}/api/datasets/upload`, { method: "POST", body: form });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "Upload failed");
  }
  return response.json();
}

export function createComparison(original_dataset_id: number, synthetic_dataset_id: number): Promise<Comparison> {
  return request<Comparison>("/api/comparisons", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ original_dataset_id, synthetic_dataset_id }),
  });
}

export const reportUrl = (id: number, type: "json" | "csv" | "pdf") => `${API_URL}/api/reports/comparisons/${id}.${type}`;

