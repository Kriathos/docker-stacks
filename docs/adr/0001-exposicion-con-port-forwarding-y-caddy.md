# 0001: Exposición a internet con port forwarding y Caddy, sin Cloudflare Tunnel ni proxy

Los servicios se publican reenviando puertos del router a la PC y usando Caddy como entrada HTTP, con registros DNS en nube gris. Se descartó Cloudflare Tunnel y el proxy de Cloudflare porque el proxy limita las solicitudes a 100 MB (rompe subidas a MinIO y al fileserver) y porque los servicios TCP (SQL Server, DB2, Postgres, SFTP, Kafka) no pueden exponerse sin que cada cliente instale software o sin pagar Spectrum.

Actualización: los Postgres ya no publican puerto. Se administran desde pgAdmin, según la [ADR 0005](0005-postgres-sin-puertos-y-reglas-de-puertos.md).
