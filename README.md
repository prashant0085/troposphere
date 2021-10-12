This repository contains a python script which deploys a AWS architecure.

To use this script, please follow below steps:

* Clone repo: 

`➜  ~ git clone git@github.com:prashant0085/troposphere.git`

* Install dependencies with python3

`➜  ~ pip install -r requirements.txt`

* Configure AWS credentials

`➜  ~ aws configure`

  follow the prompts and add the secret and access key with desired region and preferred output.

* Run the python file using python and redirect the output to a yaml file

`➜  ~ python3 infrastructure.py > infra.yaml`

* Use the generated yaml file to create a cloud formation stack.

`➜  ~ aws cloudformation create-stack --stack-name infra-stack --template-body file://infra.yml`
