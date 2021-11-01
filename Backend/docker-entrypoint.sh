#!/bin/bash
Directory="/usr/src/Backend/migrations"
if [ ! -d "$Directory" ];
then 
	flask db init
    flask db migrate
    flask db upgrade
    python src/init_insert.py
fi


python src/routes.py