#!/bin/bash
# Define some environment variables used in the lab
echo "export de_project="de-c2w3a1"" >> $HOME/.bashrc
echo "export AWS_DEFAULT_REGION=us-east-1" >> $HOME/.bashrc
source $HOME/.bashrc
echo "export DBHOST=$(aws rds describe-db-instances --db-instance-identifier $de_project"-rds" --output text --query "DBInstances[].Endpoint.Address")" >> $HOME/.bashrc
echo "export DBPORT=3306" >> $HOME/.bashrc
echo "export DBNAME="taxi_trips"" >> $HOME/.bashrc
echo "export DBUSER="admin"" >> $HOME/.bashrc
echo "export DBPASSWORD="adminpwrd"" >> $HOME/.bashrc
source $HOME/.bashrc
echo "export MYSQL_CONNECTION_STRING="mysql+pymysql://$DBUSER:$DBPASSWORD@$DBHOST:$DBPORT/$DBNAME"" >> $HOME/.bashrc
source $HOME/.bashrc
# Notify that the script ran successfully
echo "Environment setup completed successfully. Database connection variables and CLI paths have been configured."
echo "Connection string MYSQL_CONNECTION_STRING: $MYSQL_CONNECTION_STRING"