PROJECT="llm-demo"
STACK_NAME="llm-ecs"
REGION="eu-west-1"

TEMPLATE="./infra/2-ecs.yml"

deploy="aws cloudformation deploy \
    --template-file $TEMPLATE \
    --stack-name $STACK_NAME
    --no-fail-on-empty-changeset \
    --parameter-overrides Project=$PROJECT \
    --region $REGION \
    --capabilities CAPABILITY_IAM \
    --tags Project=$PROJECT"
    

echo "$deploy"
$deploy