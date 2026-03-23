resource "google_artifact_registry_repository" "main" {
  depends_on = [google_project_service.artifact_registry]

  location      = var.region
  repository_id = var.app_name
  format        = "DOCKER"
}

locals {
  image = "${google_artifact_registry_repository.main.location}-docker.pkg.dev/${data.google_project.project.project_id}/${google_artifact_registry_repository.main.repository_id}/app:latest"
}
