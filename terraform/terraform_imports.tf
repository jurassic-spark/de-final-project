# Existing schema Lambda, created before it was recorded
# in the shared Terraform state.
# import {
#   to = aws_lambda_function.schema_load_lambda
#   id = "schema_load_lambda"
# }

# # Existing execution role currently used by the schema Lambda.
# import {
#   to = aws_iam_role.schema_load_lambda_role
#   id = "schema-load-lambda-205de61918df476cedea9fdadf"
# }

# # Existing policy allowing access to the RDS-managed secret.
# import {
#   to = aws_iam_policy.schema_load_lambda_secrets_policy
#   id = "arn:aws:iam::194169601943:policy/schema-load-lambda-secrets-access"
# }

# Existing attachment between the schema role and secret policy.
# import {
#   to = aws_iam_role_policy_attachment.schema_load_lambda_secrets_policy_attach
#   id = "schema-load-lambda-205de61918df476cedea9fdadf/arn:aws:iam::194169601943:policy/schema-load-lambda-secrets-access"
# }