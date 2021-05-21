echo "Create Inital Code bucket"
aws cloudformation deploy --template-file s3.yaml --stack-name shadow-deployment-s3-stack
export BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name shadow-deployment-s3-stack | jq -r '.Stacks[0].Outputs[0].OutputValue')
echo $BUCKET_NAME  


echo "Upload model artifact and test data"
aws s3 cp inital_materials/prod_model/model.tar.gz s3://${BUCKET_NAME}/model/model.tar.gz
aws s3 cp inital_materials/test.csv s3://${BUCKET_NAME}/data/test.csv

echo "Upload code"
zip -r code.zip * 
aws s3 cp code.zip s3://${BUCKET_NAME}/code.zip

echo "Deploy CICD"
aws cloudformation deploy --template-file cicd.yaml --stack-name shadow-deployment-cicd-stack --capabilities CAPABILITY_NAMED_IAM