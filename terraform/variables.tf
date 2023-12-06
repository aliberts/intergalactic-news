variable "github_repo_owner" {
  description = "Github Repo Owner"
  type        = string
  default     = "aliberts"
}

variable "github_repo_name" {
  description = "Github Repo Name"
  type        = string
  default     = "intergalactic-news"
}

variable "region" {
  description = "AWS Region"
  type        = string
  default     = "eu-west-3"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "976114805627"
}

variable "project_name" {
  description = "Project Name"
  type        = string
  default     = "inews"
}

variable "stage" {
  description = "Stage"
  type        = string
}

variable "google_api_key" {
  description = "Google API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "mailchimp_api_key" {
  description = "Mailchimp API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "schedule_expression" {
  description = "EventBridge Schedule Expression"
  type        = string
}

variable "event_file" {
  description = "JSON Event file path"
  type        = string
}
