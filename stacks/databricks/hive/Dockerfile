# Hive Metastore con driver de Postgres y soporte s3a para MinIO.
# Apache Hive 4.0.0 trae Hadoop 3.3.6; los JARs de s3a deben ser de esa misma versión.
FROM apache/hive:4.0.0

USER root
ADD https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar /opt/hive/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar /opt/hive/lib/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.367/aws-java-sdk-bundle-1.12.367.jar /opt/hive/lib/
# ADD deja los JARs con permisos 600 (root); el usuario hive no podría leerlos
RUN chmod 644 /opt/hive/lib/postgresql-42.7.3.jar /opt/hive/lib/hadoop-aws-3.3.6.jar /opt/hive/lib/aws-java-sdk-bundle-1.12.367.jar
USER hive
