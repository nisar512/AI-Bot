from setuptools import setup, find_packages

setup(
    name="fastapi-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "sqlalchemy==2.0.27",
        "psycopg2-binary==2.9.9",
        "pydantic==2.6.1",
        "pydantic-settings==2.1.0",
        "pydantic[email]==2.6.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "elasticsearch==8.12.0",
        "selenium==4.17.2",
        "python-dotenv==1.0.1",
        "alembic==1.13.1",
        "email-validator==2.1.0.post1",
    ],
) 