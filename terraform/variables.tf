variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
  default     = "hogefuga-pj"
}

variable "region" {
  description = "デプロイリージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "app_name" {
  description = "アプリケーション名（リソース名のプレフィックスに使用）"
  type        = string
  default     = "gakusyoku-app"
}
