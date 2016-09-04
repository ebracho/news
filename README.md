## News

A web application that provides users with article suggestions based on their browsing history.



### Setup

#### Install dependencies

`pip install requirements.txt`

#### Set MySQL Database Uri environment variable

`$ export DATABASE_URI="mysql://myuser:mypass@localhost:3306/mydb?charset=utf8"`


### Run

uwsgi --socket <host>:<port> --protocol=http --master -w news

