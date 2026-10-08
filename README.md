# Guía de instalación y configuración del entorno local

Este repositorio contiene el Dash del análisis del dataset KRKPA7 

A continuación se describen los pasos para clonar el repositorio, configurar el entorno virtual utilizando Anaconda e instalar las dependencias necesarias

## Requisitos Previos

- Git
- Anaconda o Miniconda instalado en el sistema

## Pasos para la Configuración

### 1. Clonar el repositorio
Abre tu terminal o Anaconda Powershell Prompt y ejecuta:

git clone https://github.com/Vala2007/dash.git
cd dash

### 2. Crear y activar el entorno
Crea un entorno aislado para evitar conflictos entre versiones de librerías:

conda create --name dash_proyecto python=3.erdasemeolvido
conda activate dash_proyecto

### 3. Instalación de dependencias

pip install -r requirements.txt

### 4. Ejecución del Dashboard
Una vez instalado el entorno y con el ambiente activado, ejecuta el archivo principal:

python app.py

Abre tu navegador e ingresa a la siguiente dirección IP local:
http://127.0.0.1:8050/
