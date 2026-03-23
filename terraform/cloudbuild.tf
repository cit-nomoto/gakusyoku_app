# --- Cloud Build トリガー実行用 SA ---

resource "google_service_account" "cloud_build_trigger" {
  account_id   = "${var.app_name}-build-trigger"
  display_name = "Cloud Build trigger SA for ${var.app_name}"
}

resource "google_project_iam_member" "cloud_build_artifact_writer" {
  project = data.google_project.project.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cloud_build_trigger.email}"
}

resource "google_project_iam_member" "cloud_build_run_admin" {
  project = data.google_project.project.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloud_build_trigger.email}"
}

resource "google_project_iam_member" "cloud_build_sa_user" {
  project = data.google_project.project.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloud_build_trigger.email}"
}

resource "google_project_iam_member" "cloud_build_builds_builder" {
  project = data.google_project.project.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.cloud_build_trigger.email}"
}

# SA に GCS ソースバケットの読み取り権限を付与
resource "google_storage_bucket_iam_member" "cloud_build_source_reader" {
  bucket = google_storage_bucket.source.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.cloud_build_trigger.email}"
}

# --- Cloud Build Pub/Sub トリガー ---

resource "google_cloudbuild_trigger" "deploy" {
  depends_on = [google_project_service.cloud_build]

  name            = "${var.app_name}-deploy"
  description     = "GCS へのソースアップロードをトリガーに Cloud Run をデプロイする"
  service_account = google_service_account.cloud_build_trigger.name

  pubsub_config {
    topic = google_pubsub_topic.source_upload.id
  }

  build {
    # Step 1: Dockerfile/litestream.yml/run.sh を GCS からダウンロード
    step {
      name       = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "bash"
      args = [
        "-c",
        "mkdir -p /workspace/docker && gsutil -m cp gs://${google_storage_bucket.source.name}/config/Dockerfile gs://${google_storage_bucket.source.name}/config/litestream.yml gs://${google_storage_bucket.source.name}/config/run.sh /workspace/docker/"
      ]
    }

    # Step 2: アプリソース source.zip を GCS からダウンロード・展開
    # 第三者は gs://<bucket>/gakusyoku-app/source.zip にアップロードすること
    # source.zip の内容は gakusyoku_app/ 以下のファイルをルートに配置すること
    # (例: main.py, models.py, requirements.txt, routes/, static/, templates/)
    step {
      name       = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "bash"
      args = [
        "-c",
        "mkdir -p /workspace/gakusyoku_app && gsutil cp gs://${google_storage_bucket.source.name}/gakusyoku-app/source.zip /workspace/source.zip && apt-get install -y unzip -qq && unzip -o /workspace/source.zip -d /workspace/gakusyoku_app"
      ]
    }

    # Step 3: Docker イメージをビルド
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-f", "docker/Dockerfile", "-t", local.image, "."]
    }

    # Step 4: Artifact Registry にプッシュ
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", local.image]
    }

    # Step 5: Cloud Run にデプロイ
    step {
      name       = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", google_cloud_run_v2_service.main.name,
        "--image", local.image,
        "--region", var.region,
        "--project", data.google_project.project.project_id,
      ]
    }

    options {
      logging = "CLOUD_LOGGING_ONLY"
    }
  }
}
