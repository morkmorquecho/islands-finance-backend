from portfolio.serializers import (
    IslandTemplateSerializer,
    ModuleSerializer,
    IslandSerializer,
)

from core.docs.response import RESPONSE_404


# ============================================================================
# ISLAND TEMPLATE
# ============================================================================

ISLAND_TEMPLATE_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar plantillas de islas',
    description=(
        'Obtiene el catálogo de plantillas de islas disponibles. '
        'El catálogo es de solo lectura a través de esta API.'
    ),
    parameters=[
        {
            'name': 'kind',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las plantillas por tipo de isla.',
        },
        {
            'name': 'search',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Busca por nombre o símbolo de la plantilla.',
        },
    ],
    responses={
        200: IslandTemplateSerializer(many=True),
    },
)


ISLAND_TEMPLATE_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener plantilla de isla',
    description=(
        'Obtiene los detalles de una plantilla de isla específica '
        'por su identificador.'
    ),
    responses={
        200: IslandTemplateSerializer,
        404: RESPONSE_404,
    },
)


# ============================================================================
# MODULE
# ============================================================================

MODULE_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar módulos',
    description=(
        'Obtiene los módulos pertenecientes al usuario autenticado.'
    ),
    responses={
        200: ModuleSerializer(many=True),
    },
)


MODULE_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener módulo',
    description=(
        'Obtiene los detalles de un módulo perteneciente '
        'al usuario autenticado.'
    ),
    responses={
        200: ModuleSerializer,
        404: RESPONSE_404,
    },
)


MODULE_CREATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Crear módulo',
    description=(
        'Crea un nuevo módulo para el usuario autenticado.'
    ),
    request=ModuleSerializer,
    responses={
        201: ModuleSerializer,
    },
)


MODULE_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar módulo',
    description=(
        'Actualiza completamente un módulo perteneciente '
        'al usuario autenticado.'
    ),
    request=ModuleSerializer,
    responses={
        200: ModuleSerializer,
        404: RESPONSE_404,
    },
)


MODULE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar parcialmente un módulo',
    description=(
        'Actualiza parcialmente un módulo perteneciente '
        'al usuario autenticado.'
    ),
    request=ModuleSerializer,
    responses={
        200: ModuleSerializer,
        404: RESPONSE_404,
    },
)


MODULE_DESTROY_SCHEMA = dict(
    tags=['portfolio'],
    summary='Eliminar módulo',
    description=(
        'Elimina un módulo perteneciente al usuario autenticado.'
    ),
    responses={
        204: None,
        404: RESPONSE_404,
    },
)


# ============================================================================
# ISLAND
# ============================================================================

ISLAND_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar islas',
    description=(
        'Obtiene las islas pertenecientes al usuario autenticado. '
        'Las islas pueden filtrarse por módulo y tipo.'
    ),
    parameters=[
        {
            'name': 'module',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las islas por módulo.',
        },
        {
            'name': 'kind',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las islas por tipo.',
        },
    ],
    responses={
        200: IslandSerializer(many=True),
    },
)


ISLAND_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener isla',
    description=(
        'Obtiene los detalles de una isla perteneciente '
        'al usuario autenticado.'
    ),
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_CREATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Crear isla',
    description=(
        'Crea una nueva isla para el usuario autenticado.'
    ),
    request=IslandSerializer,
    responses={
        201: IslandSerializer,
    },
)


ISLAND_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar isla',
    description=(
        'Actualiza completamente una isla perteneciente '
        'al usuario autenticado.'
    ),
    request=IslandSerializer,
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar parcialmente una isla',
    description=(
        'Actualiza parcialmente una isla perteneciente '
        'al usuario autenticado.'
    ),
    request=IslandSerializer,
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_DESTROY_SCHEMA = dict(
    tags=['portfolio'],
    summary='Eliminar isla',
    description=(
        'Elimina una isla perteneciente al usuario autenticado.'
    ),
    responses={
        204: None,
        404: RESPONSE_404,
    },
)