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

- **Catálogo**: libros con portada, ISBN, género (modelo configurable), precios y estado de disponibilidad automático
- **Autores y editoriales**: autores con foto y vista Kanban; país basado en `res.country`; control de duplicados
- **Stock multi-tienda**: inventario independiente por sucursal con aviso de stock bajo mínimo
- **Ventas**: proceso completo con validación de stock y numeración automática (`ORD/2026/0001`)
- **Facturación automática**: al cerrar la venta se genera y **se confirma** un `account.move` de forma transparente
- **Clientes fidelizados**: extensión de `res.partner` con código automático, género favorito y puntos
- **Seguridad por roles**: tres roles asignables (Consulta, Vendedor y Gestor) con aislamiento por tienda

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
| `library.genre` | `library_genre` | Géneros literarios configurables (compartidos con clientes) |
| `library.book` | `library_book` | Catálogo de libros con precios, imagen y estado calculado |
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
                ↓                                          ↓
         • Valida stock en tienda                   • Confirma (contabiliza)
         • Descuenta stock                            la factura automáticamente
         • Genera ORD/2026/XXXX
         • Crea factura account.move (borrador)
              ↓
         [Ver factura] disponible
```

---

## Seguridad

| Rol | Acceso | Asignación |
|-----|--------|------------|
| **Consulta** (`group_library_user`) | Solo lectura del catálogo, tiendas, stock y ventas | Automática para todo empleado interno |
| **Vendedor** (`group_library_seller`) | Vende y gestiona el stock de **su** tienda; consulta el resto. Hereda Consulta | Manual, desde Ajustes → Usuarios |
| **Gestor** (`group_library_manager`) | CRUD completo del catálogo, géneros, todas las tiendas, ventas y clientes. Hereda Vendedor | Manual; el administrador lo recibe por defecto |

Los tres roles aparecen como un **selector de rol** en Ajustes → Usuarios (categoría *GestiLibros*). Ser **Gestor no implica ser administrador de Odoo**: un responsable de tienda puede vender sin tener permisos de sistema.

Las **reglas de registro** (`ir.rule`) aplican el aislamiento por tienda: un Vendedor solo puede crear/editar las ventas y el stock de la tienda de la que es responsable, pero puede **consultar** las del resto. El Gestor obtiene acceso total por el comportamiento OR de las reglas en Odoo.

---

## Datos de demostración

Al instalar el módulo se cargan:

- **12 géneros** literarios configurables
- **12 editoriales** (Planeta, Anagrama, Penguin, HarperCollins…)
- **12 autores** con foto (García Márquez, Borges, Kafka, Tolstói, Cervantes…)
- **12 libros** clásicos con portada, ISBN, precios y estados variados
- **3 tiendas** en Madrid, Barcelona y Sevilla, cada una con su usuario responsable (`central`, `norte`, `sur`)
- **36 registros de stock** (12 libros × 3 tiendas), con ejemplos por debajo del mínimo
- **6 clientes** con códigos GLI-001…GLI-006 y puntos de fidelidad

---

## Características técnicas destacadas

- **Herencia de modelos**: `res.partner` y `account.move` extendidos sin romper compatibilidad con otros módulos Odoo
- **Campos calculados**: `stock_total` (suma por tiendas), `state` del libro (a partir del stock), `below_minimum` (stock bajo mínimo), `purchase_count` (compras del cliente), `price_subtotal` y `amount_total`
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

**Mauro Valdés Sanjuan** — Módulo desarrollado para el curso de desarrollo de módulos Odoo.
