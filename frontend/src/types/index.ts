export type DatasetStatistics = {
  id: number;
  dataset_id: number;
  missing_count: number;
  duplicate_count: number;
  unique_text_count: number;
  vocabulary_size: number;
  avg_text_length: number;
  median_text_length: number;
  std_text_length: number;
  vocabulary_richness: number;
  class_distribution: Record<string, { count: number; proportion: number }>;
  word_frequency_data: Array<{ term: string; count: number }>;
  ngram_statistics: Record<string, unknown>;
  metrics_payload: Record<string, any>;
  created_at: string;
};

export type Dataset = {
  id: number;
  name: string;
  dataset_type: string;
  file_name: string;
  file_size: number;
  row_count: number;
  column_count: number;
  columns: string[];
  text_column: string | null;
  label_column: string | null;
  task_type: string;
  sample_rows: Array<Record<string, unknown>>;
  validation_report: {
    checks: Array<{ label: string; status: string }>;
    warnings: string[];
    blocking_errors: string[];
  };
  created_at: string;
  statistics?: DatasetStatistics | null;
};

export type ComparisonMetric = {
  metric_name: string;
  original_value: number | null;
  synthetic_value: number | null;
  absolute_difference: number | null;
  relative_difference: number | null;
  similarity_score: number | null;
  interpretation: string;
  category: string;
  direction: string;
};

export type Comparison = {
  id: number;
  original_dataset_id: number;
  synthetic_dataset_id: number;
  overall_score: number;
  fidelity_score: number;
  diversity_score: number;
  utility_score: number;
  status: string;
  interpretation: string;
  configuration: Record<string, any>;
  payload: Record<string, any>;
  created_at: string;
  metrics: ComparisonMetric[];
};

export type ComparisonDetail = {
  comparison: Comparison;
  original_dataset: Dataset;
  synthetic_dataset: Dataset;
};

