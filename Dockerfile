# base image  
FROM python:3.11.3 

# set work directory  
WORKDIR /home/app/webapp  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1  

# install dependencies  
COPY requirements.txt /home/app/webapp/  
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy whole project to your docker home directory. 
COPY . .  

# port where the Django app runs  
EXPOSE 8000

# start server  
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]