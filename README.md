# mlops-project

Proyecto MLOps End-to-End 🚀

El objetivo de este proyecto es crear una pipeline MLOps completa para **clasificación de texto** utilizando mensajes de servicio al cliente de Twitter para el servicio de Apple.

---

## 🚀 Cómo Usar: Servidor de Inferencia

Puedes poner en marcha rápidamente el modelo de clasificación para inferencia a través de un servidor FastAPI.

1.  **Pull de la Imagen Docker**:
    ```bash
    docker pull niconomist98/fastapi:latest
    ```
2.  **Ejecutar el Contenedor**:
    Esto hará que el servidor FastAPI esté disponible para inferencia.
    ```bash
    docker run -p 8000:8000 niconomist98/fastapi:latest
    ```
3.  **Acceder a la Documentación de la API**:
    Ve a [http://localhost:8000/docs](http://localhost:8000/docs) para enviar una solicitud de inferencia al modelo de clasificación.

---

## 🏗️ Arquitectura de la Solución

El sistema está diseñado con una arquitectura modular y nativa de la nube utilizando servicios de AWS.

![alt text](Untitled%20diagram%20_%20Mermaid%20Chart-2025-07-11-131515.png)

---

## 🌊 Flujo de MLOPS

Este proyecto implementa un robusto flujo de trabajo MLOps, dividido en etapas distintas y automatizadas.

### 1. Ingesta de Datos (Data Ingestion) 📥

* **Origen**: Los datos brutos de texto se originan en una `Fuente de Datos` externa.
* **Almacenamiento Crudo**: Estos datos se cargan inicialmente en **Amazon S3 Raw**, sirviendo como la zona de aterrizaje.
* **Pre-validación y Movimiento**: Una función **AWS Lambda: Ingesta** se activa automáticamente con la llegada de nuevos archivos a `S3 Raw`. Realiza una validación básica y mueve los datos a **Amazon S3 Staging**. Esta es la primera capa de preparación.

---

### 2. Preprocesamiento (Preprocessing) 🧹

* **Orquestación**: **MWAA AIRFLOW AWS** (el orquestador central) inicia el trabajo de preprocesamiento.
* **Transformación**: Un trabajo de **Amazon EMR/Glue: Preprocesamiento** lee los datos del `Amazon S3 Staging`. Aplica operaciones de limpieza de texto, tokenización, lematización, eliminación de *stop words* y genera características relevantes para el modelo.
* **Almacenamiento de Características**: Los datos preprocesados y las características se guardan en **Amazon S3 Features**, listos para el entrenamiento o la inferencia.

---

### 3. Entrenamiento (Training) 🧠

* **Orquestación**: **MWAA AIRFLOW AWS** dispara el proceso de entrenamiento.
* **Entrenamiento del Modelo**: **Amazon SageMaker: Entrenamiento** toma los datos de `Amazon S3 Features` y entrena el modelo de Machine Learning.
* **Registro del Modelo**: Una vez entrenado, el modelo (junto con sus métricas) se registra en **Amazon SageMaker: Model Registry**. Esto permite la gestión de versiones y la aprobación de modelos para el despliegue.

---

### 4. Inferencia Batch (Batch Inference) 🎯

* **Orquestación**: **MWAA AIRFLOW AWS** también activa la ejecución de la inferencia batch.
* **Aplicación del Modelo**: Un trabajo de **Amazon EMR/Glue: Transformación Batch** lee los nuevos datos de S3, carga la versión del modelo desde **Amazon SageMaker: Model Registry** y aplica el modelo para generar predicciones.
* **Resultados**: Las predicciones finales se almacenan en **Amazon S3 (Resultados)**.

---

### 5. Monitoreo (Monitoring) 📊

* **Observabilidad Continua**: **Amazon CloudWatch: Monitoreo/Alertas** recopila logs y métricas de todos los componentes (Lambda, EMR/Glue, SageMaker, MWAA, S3).
* **Detección de Problemas**: CloudWatch genera alertas y notificaciones si se detectan anomalías, errores o degradación en el rendimiento del sistema o del modelo, lo que es clave para el manejo proactivo de fallos y el reentrenamiento automático.

---

## 📈 Propuesta de Monitoreo (MVP)

Esta propuesta describe una estrategia de monitoreo fundamental, diseñada para establecer una capacidad de supervisión esencial sobre un sistema de Machine Learning batch en un entorno de producción.

### 1. Registro de Eventos (Logs) Centralizado 📝

La base de cualquier sistema de monitoreo radica en la recolección de información sobre el comportamiento del sistema.

* **Consolidación de Logs**: Configurar todos los componentes del sistema (funciones **AWS Lambda**, **AWS Glue Jobs**, **Amazon SageMaker Jobs**, y **MWAA / Apache Airflow**) para que sus logs sean remitidos de manera centralizada a **Amazon CloudWatch Logs**.
* **Identificación de Fallos**: El código de las aplicaciones debe ser instrumentado para emitir mensajes de error explícitos conteniendo la etiqueta "ERROR" o "FAILED", cuando se detecten condiciones anómalas o interrupciones en el procesamiento.

---

### 2. Alertas Automatizadas para Fallos Críticos 🚨

La detección inmediata de interrupciones operacionales es primordial para mantener la continuidad del servicio.

* **Monitoreo del Estado de Ejecución**: Se deben establecer alarmas sobre las métricas que reflejan el estado final de las ejecuciones de los componentes:
    * Para **AWS Lambda (Fase de Ingesta)**: Configurar una alarma basada en la métrica `Errors`, activándose ante cualquier ocurrencia.
    * Para **AWS Glue/EMR Jobs (Fases de Preprocesamiento e Inferencia)**: Establecer una alarma sobre la métrica `JobRunStatus` que se dispare cuando el estado sea "Failed" (Fallido).
    * Para **Jobs de Amazon SageMaker (Fase de Entrenamiento)**: Configurar una alarma en la métrica `TrainingJobStatus` para detectar el estado "Failed" (Fallido).
    * Para **DAGs de MWAA/Apache Airflow (Orquestación)**: Implementar una alarma sobre la métrica `DagRunStatus` que indique el estado "Failed" (Fallido) del flujo de trabajo completo.
* **Mecanismo de Notificación**: Todas las alarmas críticas deben estar vinculadas a un tema de **Amazon Simple Notification Service (SNS)**. Este tema enviará notificaciones directas a los canales designados para informar sobre incidentes en un periodo de tiempo reducido.

---

### 3. Monitoreo de Degradación de Rendimiento del Modelo 📉

Más allá de los fallos operacionales, comprender el rendimiento del modelo en producción es crucial.

* **Métricas de Rendimiento Post-Entrenamiento**:
    * En el script de entrenamiento de SageMaker: Asegúrate de que el script reporte métricas clave como **Accuracy, F1-Score, Precisión, Recall o AUC** (dependiendo del tipo de problema ML) a **CloudWatch Metrics** al finalizar el entrenamiento.
    * **Alerta Clave**: Configurar una alarma de CloudWatch que se active si alguna de estas métricas reportadas (ej., **F1-Score**) cae por debajo de un **umbral predefinido** (por ejemplo, `F1-Score < 0.85`). Esto avisará que el nuevo modelo entrenado no cumple con los estándares mínimos, requiriendo una revisión manual antes de ser considerado para inferencia.
* **Monitoreo de Degradación de Predicciones (Inferencia)**:
    * **Métricas a Recopilar**: Después de que los jobs de EMR/Glue generen las predicciones y las guarden en **Amazon S3 Resultados**, se añade un paso adicional que calcule métricas descriptivas de estas predicciones.
        * Para **modelos de clasificación**:
            * **Porcentaje de clases predichas**: ¿Cuántas predicciones son de la Clase A, Clase B?
            * **Media/Desviación estándar de probabilidades**: Si el modelo predice probabilidades, ¿cómo se distribuyen?
        * Para **modelos de regresión**:
            * **Media y Desviación estándar de los valores predichos**.
            * **Rango de predicciones**.
        * Estas métricas calculadas se deben enviar a **CloudWatch Metrics**.
    * **Alerta Clave**: Configurar alarmas de CloudWatch que detecten **cambios significativos** en estas métricas de distribución de predicciones en `Amazon S3 Resultados`. Por ejemplo, si el porcentaje de una clase predicha cambia más de un **X%** (ej., `Porcentaje_ClaseA < 0.10` o `> 0.50`), o si la media de las probabilidades predichas para una clase cambia en un **Y%** respecto a un *baseline* establecido.
    * **Acción Sugerida**: Notificación vía Amazon SNS. Una deriva en las predicciones es una señal fuerte de que el modelo (o los datos de entrada) ha cambiado, y puede requerir un reentrenamiento o una investigación.

---

### 4. Panel de Control Simplificado (Dashboard) 🖥️

Una representación visual concisa facilita la supervisión operacional inmediata.

* **Creación del Dashboard**: Se debe establecer un panel de control único en **Amazon CloudWatch Dashboards**.
* **Métricas Esenciales de Salud**: Este dashboard contendrá gráficos que representen las métricas de estado más relevantes para cada componente, tales como:
    * La métrica `Errors` para la función Lambda de ingesta.
    * La métrica `JobRunStatus` para los jobs de AWS Glue/EMR.
    * La métrica `DagRunStatus` para los DAGs de MWAA.
    * Este dashboard también incluirá las **métricas de rendimiento del modelo** (ej., F1-Score del entrenamiento) y las **métricas de distribución de predicciones** (ej., media de probabilidades de inferencia), ofreciendo una visión holística de la salud operativa y del modelo.