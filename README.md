# mlops-project
End to end MLops project 
The goal of this project is to create a end to end mlops pipeline for text classification using twitter cutomer services messages for apple service.

How to use :

1. pull the docker image  : docker pull niconomist98/fastapi:latest
2. run the container to get the fastapi server available for inference :  docker run niconomist98/fastapi:latest
3. go to http://localhost:8000/docs to send a request for inference to the classification model


Arquitectura de la solución:
![alt text](<Untitled diagram _ Mermaid Chart-2025-07-11-131515.png>)



 Flujo de MLOPS

1. Ingesta de Datos (Data Ingestion) 

    Origen: Los datos brutos de texto se originan en una Fuente de Datos externa.

    Almacenamiento Crudo: Estos datos se cargan inicialmente en Amazon S3 Raw, sirviendo como la zona de aterrizaje.

    Pre-validación y Movimiento: Una función AWS Lambda: Ingesta se activa automáticamente con la llegada de nuevos archivos a S3 Raw. Realiza una validación básica y mueve los datos a Amazon S3 Staging. Esta es la primera capa de preparación.

2. Preprocesamiento (Preprocessing) 

    Orquestación: MWAA AIRFLOW AWS (el orquestador central) inicia el trabajo de preprocesamiento.

    Transformación: Un trabajo de Amazon EMR/Glue: Preprocesamiento lee los datos del Amazon S3 Staging. Aplica operaciones de limpieza de texto, tokenización, lematización, eliminación de stop words y genera características relevantes para el modelo.

    Almacenamiento de Características: Los datos preprocesados y las características se guardan en Amazon S3 Features, listos para el entrenamiento o la inferencia.

3. Entrenamiento (Training) 

    Orquestación: MWAA AIRFLOW AWS dispara el proceso de entrenamiento.

    Entrenamiento del Modelo: Amazon SageMaker: Entrenamiento toma los datos de Amazon S3 Features y entrena el modelo de Machine Learning.

    Registro del Modelo: Una vez entrenado, el modelo (junto con sus métricas) se registra en Amazon SageMaker: Model Registry. Esto permite la gestión de versiones y la aprobación de modelos para el despliegue.

4. Inferencia Batch (Batch Inference) 

    Orquestación: MWAA AIRFLOW AWS también activa la ejecución de la inferencia batch.

    Aplicación del Modelo: Un trabajo de Amazon EMR/Glue: Transformación Batch lee los nuevos datos de s3, carga la versión del modelo desde Amazon SageMaker: Model Registry y aplica el modelo para generar predicciones.

    Resultados: Las predicciones finales se almacenan en Amazon S3 (Resultados).

5. Monitoreo (Monitoring) 

    Observabilidad Continua: Amazon CloudWatch: Monitoreo/Alertas recopila logs y métricas de todos los componentes (Lambda, EMR/Glue, SageMaker, MWAA, S3).

    Detección de Problemas: CloudWatch genera alertas y notificaciones si se detectan anomalías, errores o degradación en el rendimiento del sistema o del modelo, lo que es clave para el manejo proactivo de fallos y el reentrenamiento automático.

