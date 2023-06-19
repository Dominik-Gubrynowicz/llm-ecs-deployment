PROJECT="llm-demo"
STACK_NAME="llm-network"
REGION="eu-west-1"

TEMPLATE="./infra/1-network.yml"

deploy="aws cloudformation deploy \
    --template-file $TEMPLATE \
    --stack-name $STACK_NAME
    --no-fail-on-empty-changeset \
    --parameter-overrides Project=$PROJECT \
    --region $REGION \
    --tags Project=$PROJECT"

echo "$deploy"
$deploy