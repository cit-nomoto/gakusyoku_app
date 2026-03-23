# --- Litestream レプリカ用バケット ---

resource "google_storage_bucket" "db" {
  name          = "${var.app_name}-db"
  location      = var.region
  force_destroy = true
}

# --- ソースアップロード用バケット ---

resource "google_storage_bucket" "source" {
  name                        = "${data.google_project.project.project_id}-source"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

# Terraform 実行ユーザーにバケットの管理権限を付与
# (uniform_bucket_level_access 有効化後に必要)
data "google_client_openid_userinfo" "terraform_runner" {}

resource "google_storage_bucket_iam_member" "terraform_runner_admin" {
  bucket = google_storage_bucket.source.name
  role   = "roles/storage.admin"
  member = "user:${data.google_client_openid_userinfo.terraform_runner.email}"
}

# Docker ビルド用ファイルを Terraform で管理・アップロード
# (terraform apply のたびに最新版を反映)

resource "google_storage_bucket_object" "dockerfile" {
  name   = "config/Dockerfile"
  bucket = google_storage_bucket.source.name
  source = "${path.module}/../docker/Dockerfile"
}

resource "google_storage_bucket_object" "litestream_yml" {
  name   = "config/litestream.yml"
  bucket = google_storage_bucket.source.name
  source = "${path.module}/../docker/litestream.yml"
}

resource "google_storage_bucket_object" "run_sh" {
  name   = "config/run.sh"
  bucket = google_storage_bucket.source.name
  source = "${path.module}/../docker/run.sh"
}

# gakusyoku_app/ の中身を zip にまとめてアップロード
# terraform apply のたびにソースの変更を検知して自動更新される

data "archive_file" "source" {
  type        = "zip"
  source_dir  = "${path.module}/../gakusyoku_app"
  output_path = "${path.module}/../gakusyoku_app.zip"
}

resource "google_storage_bucket_object" "source" {
  name   = "${var.app_name}/source.zip"
  bucket = google_storage_bucket.source.name
  source = data.archive_file.source.output_path
}

# --- GCS → Pub/Sub 通知 ---

resource "google_pubsub_topic" "source_upload" {
  name = "${var.app_name}-source-upload"
}

# GCS サービスアカウントに Pub/Sub パブリッシャー権限を付与
resource "google_pubsub_topic_iam_member" "gcs_publisher" {
  topic  = google_pubsub_topic.source_upload.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}

# gakusyoku-app/ 配下への OBJECT_FINALIZE を検知
resource "google_storage_notification" "source_upload" {
  bucket             = google_storage_bucket.source.name
  payload_format     = "JSON_API_V1"
  topic              = google_pubsub_topic.source_upload.id
  event_types        = ["OBJECT_FINALIZE"]
  object_name_prefix = "${var.app_name}/"

  depends_on = [google_pubsub_topic_iam_member.gcs_publisher]
}
