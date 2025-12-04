# AWS Credentials Reminder

When performing AWS operations that require authentication:

1. Always check if valid AWS credentials are configured before running AWS CLI commands
2. If credentials are missing or expired, prompt the user to set temporary credentials:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key_id
   export AWS_SECRET_ACCESS_KEY=your_secret_access_key
   export AWS_SESSION_TOKEN=your_session_token
   ```
3. Verify the correct AWS account is being used with `aws sts get-caller-identity`
4. Never store or log actual credential values
5. Do not run `aws configure` - use environment variables for temporary credentials
