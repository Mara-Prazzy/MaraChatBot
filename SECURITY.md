# Security and private runtime configuration

The repository history was rebuilt to remove committed runtime secrets and private authentication records. Original author/committer metadata is retained in commit-message notes; rewritten commits have new hashes and attribution. Historical hardcoded AWS credentials were replaced with inert placeholders. Current Cognito authentication continues to read runtime environment variables.

Repository cleanup does not revoke credentials or remove independent clones, forks, deployment bundles, or cached GitHub objects. Credential revocation is still required and has not been performed through this repository.

## Required account-side response

- Revoke or confirm revocation of all four OpenAI API keys exposed in historical environment files. Review usage and billing.
- Deactivate and delete both exposed AWS access key pairs: the environment-file pair and the separate historical hardcoded pair. Review available CloudTrail, GuardDuty, IAM changes, sessions, and billing; investigate any credentials or resources created by unauthorized access.
- Rotate the Cognito app client secret and delete the compromised secret. Add a replacement before deleting the old one, or replace and delete the old app client. The user pool ID, app client ID, and region are identifiers and do not require replacement solely because they were public.
- Revoke the mail app password or reset the mailbox password represented by MAIL_PSWD.
- Generate a fresh authentication cookie signing key and invalidate existing cookies.
- Reset the application account password whose bcrypt hash was public. Reset any reused password too.

## Before running or redeploying

Use .env.example only as a list of variable names. Provide fresh values through private deployment secrets or an ignored local .env. Do not put replacement values in source files, examples, notebooks, logs, issues, or commits. Prefer an IAM role over long-lived AWS credentials; omit static credential variables when using the default AWS credential provider chain.

The application expects private account YAML files under Security/Users/ and private cookie configuration at Security/default_login_cookie_summit.yaml. Provision fresh private records outside version control before startup. The existing loader expects each user record to contain email, name, password (bcrypt hash), and flag_1st. Cookie configuration expects a cookie mapping containing name, key, and expiry_days. Do not reuse the exposed records or signing key.

The reviewed Reddit vector-store data file is retained: its key-like pattern was a substring in a URL, not an issued API key.

## Other copies and future commits

Reclone after the history rewrite. Do not merge or push branches from an old clone. Review and clean forks, deployment images/bundles, CI artifacts, and logs. Ask GitHub Support about sensitive cached commits if needed; Support assistance depends on its current policy.

Enable GitHub secret scanning and push protection in repository settings. Use a redacted full-history scanner before publishing changes. Never paste secret values into a public report.

Provider dashboards:
- OpenAI: https://platform.openai.com/api-keys
- AWS IAM: https://console.aws.amazon.com/iam/
- Amazon Cognito: https://console.aws.amazon.com/cognito/
- GitHub security settings: https://github.com/Mara-Prazzy/MaraChatBot/settings/security_analysis
- GitHub Support: https://support.github.com/
