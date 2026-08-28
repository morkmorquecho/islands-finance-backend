from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from goals.serializers import (
    GoalSerializer,
    GoalCompletionSerializer,
    GoalCompletionMarkSerializer,
)


GOAL_LIST_SCHEMA = dict(
    tags=['goals'],
    summary='Listar metas',
    description=(
        'Obtiene las metas pertenecientes al usuario autenticado. '
        'Permite filtrar los resultados por isla y estado activo.'
    ),
    parameters=[
        OpenApiParameter(
            name='island',
            type=int,
            location=OpenApiParameter.QUERY,
            description='ID de la isla por la que se desea filtrar.',
            required=False,
        ),
        OpenApiParameter(
            name='active',
            type=bool,
            location=OpenApiParameter.QUERY,
            description='Filtra las metas por su estado activo.',
            required=False,
        ),
    ],
    responses={
        200: GoalSerializer(many=True),
    },
)


GOAL_RETRIEVE_SCHEMA = dict(
    tags=['goals'],
    summary='Obtener meta',
    description=(
        'Obtiene los detalles de una meta perteneciente al usuario autenticado.'
    ),
    responses={
        200: GoalSerializer,
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)


GOAL_CREATE_SCHEMA = dict(
    tags=['goals'],
    summary='Crear meta',
    description=(
        'Crea una nueva meta para el usuario autenticado.'
    ),
    request=GoalSerializer,
    responses={
        201: GoalSerializer,
    },
)


GOAL_UPDATE_SCHEMA = dict(
    tags=['goals'],
    summary='Actualizar meta',
    description=(
        'Actualiza completamente una meta perteneciente al usuario autenticado.'
    ),
    request=GoalSerializer,
    responses={
        200: GoalSerializer,
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)


GOAL_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['goals'],
    summary='Actualizar parcialmente una meta',
    description=(
        'Actualiza parcialmente una meta perteneciente al usuario autenticado.'
    ),
    request=GoalSerializer,
    responses={
        200: GoalSerializer,
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)


GOAL_DESTROY_SCHEMA = dict(
    tags=['goals'],
    summary='Eliminar meta',
    description=(
        'Elimina una meta perteneciente al usuario autenticado.'
    ),
    responses={
        204: {
            'description': 'Meta eliminada correctamente.',
        },
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)


GOAL_COMPLETIONS_SCHEMA = dict(
    tags=['goals'],
    summary='Listar cumplimientos de una meta',
    description=(
        'Obtiene todos los períodos esperados de la meta hasta la fecha actual. '
        'Los períodos faltantes se generan automáticamente antes de devolver '
        'la respuesta.\n\n'
        'La respuesta incluye el porcentaje de cumplimiento de la meta y '
        'el listado de períodos generados o existentes.'
    ),
    responses={
        200: {
            'description': 'Cumplimientos de la meta.',
            'content': {
                'application/json': {
                    'example': {
                        'compliance_rate': 75.0,
                        'results': [],
                    }
                }
            }
        },
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)


GOAL_MARK_COMPLETION_SCHEMA = dict(
    tags=['goals'],
    summary='Marcar cumplimiento de meta',
    description=(
        'Marca como cumplido un período específico de la meta. '
        'Si el período todavía no existe, se genera antes de marcarlo '
        'como cumplido.\n\n'
        'Opcionalmente puede asociarse la transacción que satisfizo la meta '
        'y proporcionar el monto real correspondiente.'
    ),
    request=GoalCompletionMarkSerializer,
    responses={
        200: GoalCompletionSerializer,
        404: {
            'description': 'Meta no encontrada.',
        },
    },
)