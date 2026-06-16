data "aws_iam_policy_document" "observability_task" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]

    resources = [
      "${aws_cloudwatch_log_group.application.arn}:*",
      "${aws_cloudwatch_log_group.firelens.arn}:*",
      "${aws_cloudwatch_log_group.otel_collector.arn}:*"
    ]
  }

  statement {
    sid    = "WriteOpenSearch"
    effect = "Allow"

    actions = [
      "es:ESHttpPost",
      "es:ESHttpPut"
    ]

    resources = [
      var.opensearch_domain_arn,
      "${var.opensearch_domain_arn}/*"
    ]
  }
}

resource "aws_iam_policy" "observability_task" {
  name        = "${var.name}-observability-task-policy"
  description = "Allows ECS observability components to write logs and telemetry."
  policy      = data.aws_iam_policy_document.observability_task.json
  tags        = var.tags
}
