from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from core.docs.response import RESPONSE_404
from goals.serializers import (
    GoalSerializer,
    GoalCompletionSerializer,
    GoalCompletionMarkSerializer,
)

GOAL_LIST_SCHEMA = dict(
    tags=['goals'],
    summary='Listar metas',
    description=(
        'Obtiene las metas del usuario autenticado. '
        'Las metas se filtran automáticamente por el usuario actual. '
        'Permite filtrar por isla y por estado activo.'
    ),
    parameters=[
        OpenApiParameter(
            name='island',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='ID de la isla por la que se desean filtrar las metas.',
            examples=[
                OpenApiExample(
                    'Ejemplo',
                    value=1,
                )
            ],
        ),
        OpenApiParameter(
            name='active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Filtra las metas según si están activas.',
            examples=[
                OpenApiExample(
                    'Activas',
                    value=True,
                )
            ],
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
        'Obtiene una meta específica del usuario autenticado. '
        'La meta debe pertenecer al usuario que realiza la solicitud.'
    ),
    responses={
        200: GoalSerializer,
        404: RESPONSE_404,
    },
)


GOAL_CREATE_SCHEMA = dict(
    tags=['goals'],
    summary='Crear meta',
    description=(
        'Crea una nueva meta asociada automáticamente al usuario autenticado. '
        'La isla seleccionada debe pertenecer al usuario que realiza la solicitud.'
    ),
    request={
        'application/json': GoalSerializer,
    },
    responses={
        201: GoalSerializer,
    },
)


GOAL_UPDATE_SCHEMA = dict(
    tags=['goals'],
    summary='Actualizar meta',
    description=(
        'Actualiza completamente una meta del usuario autenticado. '
        'La meta debe pertenecer al usuario que realiza la solicitud.'
    ),
    request={
        'application/json': GoalSerializer,
    },
    responses={
        200: GoalSerializer,
        404: RESPONSE_404,
    },
)


GOAL_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['goals'],
    summary='Actualizar parcialmente una meta',
    description=(
        'Actualiza parcialmente una meta del usuario autenticado. '
        'Solo se modifican los campos enviados en la solicitud.'
    ),
    request={
        'application/json': GoalSerializer,
    },
    responses={
        200: GoalSerializer,
        404: RESPONSE_404,
    },
)


GOAL_DESTROY_SCHEMA = dict(
    tags=['goals'],
    summary='Eliminar meta',
    description=(
        'Elimina una meta del usuario autenticado.'
    ),
    responses={
        204: None,
        404: RESPONSE_404,
    },
)


GOAL_COMPLETIONS_SCHEMA = dict(
    tags=['goals'],
    summary='Obtener cumplimientos de una meta',
    description=(
        'Obtiene los períodos esperados de una meta hasta la fecha actual. '
        'Los registros faltantes se generan automáticamente antes de devolver '
        'la información.\n\n'
        'La respuesta incluye la tasa de cumplimiento y la lista de períodos '
        'de cumplimiento ordenados por fecha esperada.'
    ),
    responses={
        200: {
            'description': 'Cumplimientos de la meta.',
            'content': {
                'application/json': {
                    'example': {
                        'compliance_rate': 0.75,
                        'results': [
                            {
                                'id': 1,
                                'goal': 10,
                                'expected_date': '2026-09-01',
                                'completed_date': '2026-09-01',
                                'actual_amount': '1000.00',
                                'transaction': 25,
                            },
                            {
                                'id': 2,
                                'goal': 10,
                                'expected_date': '2026-09-08',
                                'completed_date': None,
                                'actual_amount': None,
                                'transaction': None,
                            },
                        ],
                    },
                },
            },
        },
        404: RESPONSE_404,
    },
)


GOAL_MARK_COMPLETION_SCHEMA = dict(
    tags=['goals'],
    summary='Marcar cumplimiento de una meta',
    description=(
        'Marca como cumplido un período específico de una meta.\n\n'
        'El período indicado por `expected_date` se crea automáticamente si '
        'todavía no existe. Al marcarlo como cumplido, se establece la fecha '
        'actual como `completed_date`.\n\n'
        'Opcionalmente se puede asociar una transacción y proporcionar el '
        'monto real cumplido. Si no se proporciona `actual_amount` pero se '
        'proporciona una transacción, se utiliza automáticamente el monto de '
        'dicha transacción.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'expected_date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Fecha del período esperado que se desea marcar como cumplido.',
                    'example': '2026-09-01',
                },
                'transaction_id': {
                    'type': 'integer',
                    'nullable': True,
                    'description': 'ID de la transacción que cumplió la meta. Es opcional.',
                    'example': 25,
                },
                'actual_amount': {
                    'type': 'number',
                    'format': 'decimal',
                    'nullable': True,
                    'description': 'Monto realmente cumplido. Es opcional.',
                    'example': '1000.00',
                },
            },
            'required': ['expected_date'],
        },
    },
    responses={
        200: {
            'description': 'Período marcado como cumplido.',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'goal': 10,
                        'expected_date': '2026-09-01',
                        'completed_date': '2026-09-04',
                        'actual_amount': '1000.00',
                        'transaction': 25,
                    },
                },
            },
        },
        400: {
            'description': 'Datos de entrada inválidos.',
        },
        404: RESPONSE_404,
    },
)