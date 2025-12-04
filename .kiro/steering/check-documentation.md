# Documentation Check Reminder

When creating or updating Python or CDK code:

1. Always check Context7 for up-to-date library documentation before implementing:
   - Use `resolve-library-id` to find the correct library ID
   - Use `get-library-docs` to fetch current documentation

2. Key libraries to verify:
   - **FastAPI** - Check for latest patterns, middleware, and validation
   - **Pydantic** - Verify validator syntax (e.g., `pattern` not `regex` in v2)
   - **boto3** - Check DynamoDB operations and reserved keywords
   - **AWS CDK** - Verify construct APIs and best practices
   - **@aws-cdk/aws-lambda-python-alpha** - Check PythonFunction bundling options

3. Also check AWS documentation MCP server for:
   - AWS service-specific guidance
   - CloudFormation resource specifications
   - Regional availability of services

4. Pay attention to breaking changes between library versions
