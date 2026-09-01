from ledger.serializers import TransactionSerializer


TRANSACTION_LIST_SCHEMA = dict(
    tags=['transactions'],
    summary='Listar transacciones',
    description=(
        'Obtiene las transacciones del usuario autenticado.\n\n'
        '**Filtros disponibles:**\n'
        '- `island`: filtra por isla.\n'
        '- `type`: filtra por tipo de transacción.\n'
        '- `category`: filtra por categoría.\n\n'
        '**Ordenamiento disponible:**\n'
        '- `date`\n'
        '- `created_at`\n\n'
        'Las transacciones pertenecientes a otros usuarios no se incluyen '
        'en los resultados.'
    ),
    parameters=[
        {
            'name': 'island',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las transacciones por isla.',
        },
        {
            'name': 'type',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las transacciones por tipo.',
        },
        {
            'name': 'category',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': 'Filtra las transacciones por categoría.',
        },
        {
            'name': 'ordering',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
            },
            'description': (
                'Campo por el que se ordenan los resultados. '
                'Valores permitidos: `date`, `created_at`. '
                'Puede utilizarse con `-` para orden descendente.'
            ),
        },
    ],
    responses={
        200: TransactionSerializer(many=True),
    }
)


TRANSACTION_RETRIEVE_SCHEMA = dict(
    tags=['transactions'],
    summary='Obtener transacción',
    description=(
        'Obtiene los detalles de una transacción específica. '
        'Solo puede accederse a transacciones pertenecientes al usuario autenticado.'
    ),
    responses={
        200: TransactionSerializer,
        404: {
            'description': 'Transacción no encontrada.',
        },
    }
)


TRANSACTION_CREATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Crear transacción',
    description=(
        'Crea una nueva transacción asociada al usuario autenticado.\n\n'
        'La isla debe pertenecer al usuario autenticado.\n\n'
        '**Reglas según el tipo de isla:**\n'
        '- Las islas de tipo `cash` aceptan transacciones `deposit`, '
        '`withdrawal` y `expense` y requieren `amount`.\n'
        '- Las islas de tipo `asset` aceptan transacciones `buy` y `sell` '
        'y requieren `quantity` y `price_at_tx`.\n'
        '- `category` solo está permitido cuando `type` es `expense`.\n\n'
        'Para islas de tipo `cash`, `quantity` y `price_at_tx` no son aplicables. '
        'Para islas de tipo `asset`, `amount` no es aplicable.'
    ),
    request={
        'application/json': TransactionSerializer,
    },
    responses={
        201: TransactionSerializer,
        400: {
            'description': (
                'Datos inválidos. Puede producirse por una isla que no '
                'pertenece al usuario, combinación inválida de tipo e isla, '
                'campos requeridos ausentes o campos no aplicables.'
            ),
        },
    }
)


TRANSACTION_UPDATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Actualizar transacción',
    description=(
        'Actualiza completamente una transacción existente perteneciente '
        'al usuario autenticado.\n\n'
        'Se aplican las mismas reglas de validación que durante la creación '
        'de una transacción.'
    ),
    request={
        'application/json': TransactionSerializer,
    },
    responses={
        200: TransactionSerializer,
        400: {
            'description': (
                'Datos inválidos según las reglas de validación de la transacción.'
            ),
        },
        404: {
            'description': 'Transacción no encontrada.',
        },
    }
)


TRANSACTION_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Actualizar parcialmente transacción',
    description=(
        'Actualiza parcialmente una transacción existente perteneciente '
        'al usuario autenticado.\n\n'
        'Los campos omitidos conservan su valor actual. '
        'Las reglas de validación de la transacción continúan aplicándose '
        'a la combinación resultante de los valores existentes y los nuevos.'
    ),
    request={
        'application/json': TransactionSerializer,
    },
    responses={
        200: TransactionSerializer,
        400: {
            'description': (
                'Datos inválidos según las reglas de validación de la transacción.'
            ),
        },
        404: {
            'description': 'Transacción no encontrada.',
        },
    }
)


TRANSACTION_DESTROY_SCHEMA = dict(
    tags=['transactions'],
    summary='Eliminar transacción',
    description=(
        'Elimina una transacción perteneciente al usuario autenticado.'
    ),
    responses={
        204: {
            'description': 'Transacción eliminada correctamente.',
        },
        404: {
            'description': 'Transacción no encontrada.',
        },
    }
)