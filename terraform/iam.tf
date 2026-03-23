# --- operators IAM バインディング ---
# GCS ソースバケットへの書き込み権限
# gakusyoku-app/ プレフィックス配下のみアップロード可能
locals {
  operators = [
    "hogefuga@example.com",
  ]
}

resource "google_storage_bucket_iam_member" "operators_source_upload" {
  for_each = toset(local.operators)

  bucket = google_storage_bucket.source.name
  role   = "roles/storage.objectUser"
  member = "user:${each.value}"

  condition {
    title      = "gakusyoku-app prefix only"
    expression = "resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.source.name}/objects/gakusyoku-app/\")"
  }
}

# バケット内オブジェクトの一覧・閲覧権限（バケット一覧は与えない）
# Console で直接 URL を開いてオブジェクトを確認できるようにする
# roles/storage.legacyBucketReader = storage.buckets.get + storage.objects.list + storage.objects.get

resource "google_storage_bucket_iam_member" "operators_source_reader" {
  for_each = toset(local.operators)

  bucket = google_storage_bucket.source.name
  role   = "roles/storage.legacyBucketReader"
  member = "user:${each.value}"
}

# Cloud Run ログ閲覧権限

resource "google_project_iam_member" "operators_log_viewer" {
  for_each = toset(local.operators)

  project = data.google_project.project.project_id
  role    = "roles/logging.viewer"
  member  = "user:${each.value}"
}

resource "google_project_iam_member" "operators_run_viewer" {
  for_each = toset(local.operators)

  project = data.google_project.project.project_id
  role    = "roles/run.viewer"
  member  = "user:${each.value}"
}

