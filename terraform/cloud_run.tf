# --- アプリ実行用サービスアカウント ---

resource "google_service_account" "app" {
  account_id   = var.app_name
  display_name = "${var.app_name} runtime SA"
}

# Litestream が GCS バケットへ読み書きするための権限
resource "google_project_iam_member" "app_storage_admin" {
  project = data.google_project.project.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# --- Cloud Run サービス ---

resource "google_cloud_run_v2_service" "main" {
  depends_on = [google_project_service.cloud_run]

  name     = "${var.app_name}-lite"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.app.email

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = local.image
      ports {
        container_port = 8080
      }
    }
  }

  # 初回 terraform apply 時はイメージがまだ存在しないためスキップ
  # deploy.sh または Cloud Build でイメージを push した後に反映される
  lifecycle {
    ignore_changes = [template[0].containers[0].image]
  }
}

# 公開アクセス（IAM 認証なし）
resource "google_cloud_run_v2_service_iam_member" "cloud_run_noauth" {
  location = google_cloud_run_v2_service.main.location
  project  = google_cloud_run_v2_service.main.project
  name     = google_cloud_run_v2_service.main.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" {
  value = google_cloud_run_v2_service.main.uri
}
