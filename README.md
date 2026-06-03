# 📚 GestiLibros

> Módulo Odoo 18 para la gestión integral de una cadena de tiendas de libros.

[![Odoo](https://img.shields.io/badge/Odoo-18-714B67?style=flat-square&logo=odoo)](https://www.odoo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)

> [!IMPORTANT]
> **Este módulo está desarrollado y probado sobre Odoo 18.**
> Si se instala en Odoo 19, puede requerir ajustes menores de compatibilidad (principalmente en vistas XML y versión de la imagen Docker).
> El `docker-compose.yml` incluido en el repositorio levanta exactamente **Odoo 18 + PostgreSQL 15**, que es el entorno en el que ha sido validado.

---

## ¿Qué hace este módulo?

GestiLibros cubre el ciclo completo de una librería con varias sucursales:

- **Catálogo**: libros con portada, ISBN, géneros, precios y estado de disponibilidad
- **Autores y editoriales**: relaciones muchos-a-muchos y uno-a-muchos con el catálogo
- **Stock multi-tienda**: control de inventario independiente por cada sucursal
- **Ventas**: proceso completo con validación de stock y numeración automática (`ORD/2026/0001`)
- **Facturación automática**: al confirmar una venta se genera un `account.move` de forma transparente
- **Clientes fidelizados**: extensión de `res.partner` con código único, género favorito y puntos
- **Seguridad por roles**: usuarios (lectura) y gestores (CRUD completo) con reglas de registro

---

## Instalación

### Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- Git

### Pasos

**1. Clonar el repositorio**

```bash
git clone <url-del-repo>
cd GestiLibros
```

**2. Levantar los contenedores**

```bash
docker compose up -d
```

Esto arranca dos contenedores:
- `web` — Odoo 18 en el puerto **8069**
- `db` — PostgreSQL 15

**3. Crear la base de datos**

Abre **http://localhost:8069** en el navegador.  
Rellena el formulario de creación de base de datos (nombre, email, contraseña de administrador) y pulsa **Create database**.

**4. Instalar el módulo**

Una vez dentro de Odoo:
1. Activa el **modo desarrollador**: `Ajustes → Activar el modo desarrollador`
2. Ve a **Aplicaciones** y pulsa **Actualizar la lista de aplicaciones**
3. Busca `GestiLibros` e instala el módulo

Al instalarse se cargan automáticamente **81 registros de demostración** (libros, autores, editoriales, tiendas, stock y clientes). El módulo ya está listo para probar en el menú **GestiLibros**.

**5. Parar los contenedores**

```bash
docker compose down
```

Los datos se conservan en `volumesOdoo/` y se recuperan la próxima vez que levantes con `docker compose up -d`.

---

## Estructura del proyecto

```
GestiLibros/
├── docker-compose.yml              # Odoo 18 + PostgreSQL 15
└── volumesOdoo/
    └── addons/
        └── library/                # ← módulo Odoo
            ├── __manifest__.py     # metadatos y orden de carga
            ├── models/
            │   ├── book.py         # library.book — catálogo
            │   ├── author.py       # library.author
            │   ├── publisher.py    # library.publisher
            │   ├── partner.py      # res.partner (herencia) — clientes
            │   ├── store.py        # library.store + library.stock
            │   ├── order.py        # library.order — ventas
            │   ├── order_line.py   # library.order.line
            │   └── account_move.py # account.move (herencia) — facturas
            ├── views/
            │   ├── library_book_views.xml
            │   ├── library_author_views.xml
            │   ├── library_publisher_views.xml
            │   ├── library_partner_views.xml
            │   ├── library_store_views.xml
            │   ├── library_order_views.xml
            │   ├── library_account_move_views.xml
            │   └── library_menu.xml
            ├── security/
            │   ├── security.xml            # grupos y reglas de registro
            │   └── ir.model.access.csv     # permisos CRUD por modelo
            └── data/
                ├── library_sequence.xml    # numeración ORD/YYYY/XXXX
                └── library_data.xml        # 81 registros demo
```

---

## Modelos de datos

| Modelo | Tabla BD | Descripción |
|--------|----------|-------------|
| `library.book` | `library_book` | Catálogo de libros con precios, imagen y estado |
| `library.author` | `library_author` | Autores (M2M con libros) |
| `library.publisher` | `library_publisher` | Editoriales (O2M con libros) |
| `library.store` | `library_store` | Tiendas físicas |
| `library.stock` | `library_stock` | Inventario libro × tienda |
| `library.order` | `library_order` | Pedidos de venta |
| `library.order.line` | `library_order_line` | Líneas de cada pedido |
| `res.partner` *(herencia)* | `res_partner` | Clientes con código y puntos |
| `account.move` *(herencia)* | `account_move` | Facturas con enlace al pedido |

---

## Flujo de una venta

```
Borrador → [Confirmar] → Confirmado → [Marcar hecho] → Hecho
                ↓
         • Valida stock en tienda
         • Descuenta stock
         • Genera ORD/2026/XXXX
         • Crea factura account.move
              ↓
         [Ver factura] disponible
```

---

## Seguridad

| Rol | Acceso | Asignación |
|-----|--------|------------|
| **Usuario** (`group_library_user`) | Lectura del catálogo y pedidos confirmados/hechos/cancelados | Automática para todos los usuarios Odoo |
| **Gestor** (`group_library_manager`) | CRUD completo + ve todos los pedidos incluidos borradores | Automática para administradores del sistema |

Las **reglas de registro** sobre `library.order` aplican un filtro adicional: los usuarios básicos no pueden ver borradores de otros usuarios. Los gestores (que heredan ambos grupos) obtienen acceso total por el comportamiento OR de las reglas en Odoo.

---

## Datos de demostración

Al instalar el módulo se cargan:

- **12 editoriales** (Planeta, Anagrama, Penguin, HarperCollins…)
- **12 autores** (García Márquez, Borges, Kafka, Tolstói, Cervantes…)
- **12 libros** clásicos con ISBN, precios y estados variados
- **3 tiendas** en Madrid, Barcelona y Sevilla
- **36 registros de stock** (12 libros × 3 tiendas)
- **6 clientes** con códigos GLI-001…GLI-006 y puntos de fidelidad

---

## Características técnicas destacadas

- **Herencia de modelos**: `res.partner` y `account.move` extendidos sin romper compatibilidad con otros módulos Odoo
- **Campos calculados**: `stock_total` (suma por tiendas), `sale_count` (pedidos confirmados), `price_subtotal` y `amount_total`
- **Validaciones dobles**: restricciones SQL (`_sql_constraints`) para integridad en BD + validaciones Python (`@api.constrains`) para lógica de negocio
- **Vistas avanzadas**: Kanban con portadas, Calendar por fecha coloreado por tienda, Pivot analítico de ventas
- **Dominio dinámico**: el selector de libro en líneas de venta filtra solo libros con stock en la tienda seleccionada
- **Navegación bidireccional**: stat buttons en pedidos ↔ facturas y en clientes ↔ ventas

---

## Versiones utilizadas

| Componente | Versión |
|------------|---------|
| Odoo | **18** (imagen Docker `odoo:18`) |
| PostgreSQL | **15** (imagen Docker `postgres:15`) |
| Python | 3.12 (incluido en la imagen Odoo 18) |

El `docker-compose.yml` incluido en el repositorio fija estas versiones exactas. Si se quiere probar con Odoo 19, basta con cambiar `image: odoo:18` por `image: odoo:19` en el `docker-compose.yml`, aunque pueden surgir advertencias de compatibilidad en vistas XML.

---

## Autor

**Mauro** — Módulo desarrollado para el curso de desarrollo de módulos Odoo.
