# Configuration
REGION = us-east-1
BASE_STACK = diesel-api
USAGE_STACK = diesel-usage-plan
BASE_TEMPLATE = template-base.yml
USAGE_TEMPLATE = template-usage-plan.yml

.PHONY: all deploy-base deploy-usage delete-base delete-usage delete-all

all: deploy-base deploy-usage

## Deploy the base SAM stack (Lambda, API, DynamoDB)
deploy-base:
	@echo "🚀 Deploying base stack: $(BASE_STACK)"
	sam deploy \
		--stack-name $(BASE_STACK) \
		--template-file $(BASE_TEMPLATE) \
		--region $(REGION) \
		--capabilities CAPABILITY_IAM \
		--resolve-s3 \
		--no-confirm-changeset
	@echo "✅ Base stack deployed."

## Deploy the usage plan + API key stack
deploy-usage:
	@echo "🚀 Deploying usage plan stack: $(USAGE_STACK)"
	sam deploy \
		--stack-name $(USAGE_STACK) \
		--template-file $(USAGE_TEMPLATE) \
		--region $(REGION) \
		--capabilities CAPABILITY_IAM \
		--resolve-s3 \
		--no-confirm-changeset
	@echo "✅ Usage plan stack deployed."

## Delete only the usage plan stack
delete-usage:
	@echo "🧨 Deleting usage plan stack: $(USAGE_STACK)"
	aws cloudformation delete-stack --stack-name $(USAGE_STACK) --region $(REGION)
	@echo "⏳ Waiting for usage plan stack to delete..."
	aws cloudformation wait stack-delete-complete --stack-name $(USAGE_STACK) --region $(REGION)
	@echo "✅ Usage plan stack deleted."

## Delete only the base stack
delete-base:
	@echo "🧨 Deleting base stack: $(BASE_STACK)"
	aws cloudformation delete-stack --stack-name $(BASE_STACK) --region $(REGION)
	@echo "⏳ Waiting for base stack to delete..."
	aws cloudformation wait stack-delete-complete --stack-name $(BASE_STACK) --region $(REGION)
	@echo "✅ Base stack deleted."

## Delete both stacks in correct order
delete-all: delete-usage delete-base
	@echo "🧹 All stacks cleaned up."

## Run the seed_data.py script
get-data:
	@echo "Download bulk data..."
	python scripts/get_data.py
	@echo "got the data completed."

clean-data:
	@echo "cleaning data..."
	python scripts/clean_data.py
	@echo "got the data completed."

load-data:
	@echo "loading data to DynamoDB table..."
	python scripts/load_data.py
	@echo "got the data completed."

load-data-sample:
	@echo "🐍 Running Python seed script..."
	python scripts/load_data.py
	@echo "got the data completed."
