from core.docs.response import RESPONSE_404, response_400
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample, extend_schema_view
from portfolio.serializers import IslandSerializer, IslandTemplateSerializer, ModuleSerializer

ISLAND_TEMPLATE_LIST_SCHEMA = dict(
    tags=['islands'],
    summary='Listar templates de islas',
    description=(
        'Obtiene el catálogo de templates de islas disponibles. '
        'El catálogo es de solo lectura y es administrado mediante Django Admin.\n\n'
        '**Filtros disponibles:**\n'
        '- `kind`: Filtra los templates por tipo.\n\n'
        '**Búsqueda:**\n'
        '- `search`: Busca por nombre (`name`) o símbolo (`symbol`).'
    ),
    manual_parameters=[
        openapi.Parameter(
            'kind',
            openapi.IN_QUERY,
            description='Filtra los templates por tipo.',
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description='Busca por nombre o símbolo.',
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: {
            'description': 'Listado de templates de islas',
            'schema': IslandTemplateSerializer(many=True),
        },
    }
)


ISLAND_TEMPLATE_RETRIEVE_SCHEMA = dict(
    tags=['islands'],
    summary='Obtener template de isla',
    description=(
        'Obtiene los detalles de un template de isla específico por su ID.'
    ),
    responses={
        200: {
            'description': 'Detalles del template de isla',
            'schema': IslandTemplateSerializer(),
        },
        404: RESPONSE_404,
    }
)

#///////////////////////////////////////////////

ISLAND_LIST_SCHEMA = dict(
    tags=["islands"],
    summary="Listar islas",
    description=(
        "Obtiene las islas pertenecientes al usuario autenticado. "
        "Opcionalmente permite filtrar por módulo y tipo de isla."
    ),
    manual_parameters=[
        openapi.Parameter(
            "module",
            openapi.IN_QUERY,
            description="Filtra las islas por módulo.",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "kind",
            openapi.IN_QUERY,
            description="Filtra las islas por tipo.",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: IslandSerializer(many=True),
    },
)


ISLAND_RETRIEVE_SCHEMA = dict(
    tags=["islands"],
    summary="Obtener isla",
    description=(
        "Obtiene una isla específica perteneciente al usuario autenticado."
    ),
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_CREATE_SCHEMA = dict(
    tags=["islands"],
    summary="Crear isla",
    description=(
        "Crea una nueva isla para el usuario autenticado."
    ),
    request={
        "application/json": IslandSerializer,
    },
    responses={
        201: IslandSerializer,
    },
)


ISLAND_UPDATE_SCHEMA = dict(
    tags=["islands"],
    summary="Actualizar isla",
    description=(
        "Actualiza completamente una isla perteneciente al usuario autenticado."
    ),
    request={
        "application/json": IslandSerializer,
    },
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_PARTIAL_UPDATE_SCHEMA = dict(
    tags=["islands"],
    summary="Actualizar parcialmente una isla",
    description=(
        "Actualiza parcialmente una isla perteneciente al usuario autenticado."
    ),
    request={
        "application/json": IslandSerializer,
    },
    responses={
        200: IslandSerializer,
        404: RESPONSE_404,
    },
)


ISLAND_DESTROY_SCHEMA = dict(
    tags=["islands"],
    summary="Eliminar isla",
    description=(
        "Elimina una isla perteneciente al usuario autenticado."
    ),
    responses={
        204: "No Content",
        404: RESPONSE_404,
    },
)


#/////////////////////////////////////////

MODULE_LIST_SCHEMA = dict(
    tags=['modules'],
    summary='Listar módulos',
    description=(
        'Obtiene la lista de módulos pertenecientes al usuario autenticado. '
        'Los módulos de otros usuarios no se incluyen en la respuesta.'
    ),
    responses={
        200: ModuleSerializer(many=True),
    }
)


MODULE_RETRIEVE_SCHEMA = dict(
    tags=['modules'],
    summary='Obtener módulo',
    description=(
        'Obtiene los detalles de un módulo específico. '
        'El módulo debe pertenecer al usuario autenticado.'
    ),
    responses={
        200: ModuleSerializer(),
        404: RESPONSE_404,
    }
)


MODULE_CREATE_SCHEMA = dict(
    tags=['modules'],
    summary='Crear módulo',
    description=(
        'Crea un nuevo módulo para el usuario autenticado.'
    ),
    request=ModuleSerializer(),
    responses={
        201: ModuleSerializer(),
        400: response_400(ModuleSerializer),
    }
)


MODULE_UPDATE_SCHEMA = dict(
    tags=['modules'],
    summary='Actualizar módulo',
    description=(
        'Actualiza completamente un módulo perteneciente al usuario autenticado.'
    ),
    request=ModuleSerializer(),
    responses={
        200: ModuleSerializer(),
        400: response_400(ModuleSerializer),
        404: RESPONSE_404,
    }
)


MODULE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['modules'],
    summary='Actualizar parcialmente módulo',
    description=(
        'Actualiza parcialmente un módulo perteneciente al usuario autenticado.'
    ),
    request=ModuleSerializer(),
    responses={
        200: ModuleSerializer(),
        400: response_400(ModuleSerializer),
        404: RESPONSE_404,
    }
)


MODULE_DESTROY_SCHEMA = dict(
    tags=['modules'],
    summary='Eliminar módulo',
    description=(
        'Elimina un módulo perteneciente al usuario autenticado.'
    ),
    responses={
        204: {
            'description': 'Módulo eliminado correctamente.'
        },
        404: RESPONSE_404,
    }
)