#!/usr/bin/env python3
"""Consumidor Python para el stack Kafka Zookeeper."""

import json
import argparse
import sys
from datetime import datetime
from confluent_kafka import Consumer, KafkaError


def create_consumer(bootstrap_servers, group_id=None):
    if group_id is None:
        group_id = f'consumer-zookeeper-{int(datetime.now().timestamp() * 1000)}'

    config = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
    }

    try:
        return Consumer(config)
    except Exception as exc:
        print(f"❌ No se pudo conectar a Kafka: {exc}")
        sys.exit(1)


def format_message(msg):
    try:
        payload = json.loads(msg.value().decode('utf-8'))
    except Exception:
        return None

    data = payload.get('payload', {})
    op = data.get('op', '?')
    op_map = {'c': 'CREATE', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}

    return {
        'operation': op_map.get(op, op),
        'before': data.get('before'),
        'after': data.get('after'),
        'table': data.get('source', {}).get('table'),
        'database': data.get('source', {}).get('db'),
        'timestamp': data.get('ts_ms'),
    }


def main():
    parser = argparse.ArgumentParser(description='Consumer para Kafka Zookeeper')
    parser.add_argument('--bootstrap-servers', default='localhost:51435', help='Broker Kafka Zookeeper (default: localhost:51435)')
    parser.add_argument('--topic', default='cdc.public.clientes', help='Topic a consumir')
    parser.add_argument('--max-messages', type=int, default=None, help='Máximo mensajes a procesar')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    parser.add_argument('--group-id', default=None, help='Grupo de consumidores')
    args = parser.parse_args()

    consumer = create_consumer(args.bootstrap_servers, args.group_id)
    consumer.subscribe([args.topic])

    print('▶ Iniciando consumidor Kafka Zookeeper')
    print(f'  Broker: {args.bootstrap_servers}')
    print(f'  Topic: {args.topic}')
    print('  Presiona Ctrl+C para finalizar\n')

    count = 0
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"❌ Error Kafka: {msg.error()}")
                break

            formatted = format_message(msg)
            if not formatted:
                print('⚠️ Mensaje no parseable')
                continue

            count += 1
            print('─' * 72)
            print(f"Operacion: {formatted['operation']}")
            print(f"Tabla: {formatted['table']} | DB: {formatted['database']}")
            print(f"Antes: {formatted['before']}")
            print(f"Después: {formatted['after']}")
            if args.verbose:
                print(f"Partition: {msg.partition()} | Offset: {msg.offset()} | Timestamp: {formatted['timestamp']}")

            if args.max_messages and count >= args.max_messages:
                print(f"✅ Se procesaron {count} mensajes")
                break
    except KeyboardInterrupt:
        print('\n👋 Detenido por el usuario')
    finally:
        consumer.close()


if __name__ == '__main__':
    main()
