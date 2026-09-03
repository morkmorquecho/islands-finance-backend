TRANSACTION_LIST_SCHEMA = dict(
    tags=['transactions'],
    summary='Listar transacciones',
    description=(
        'Obtiene las transacciones pertenecientes al usuario autenticado. '
        'El usuario no puede consultar transacciones de otros usuarios.\n\n'
        '**Filtros disponibles:**\n'
        '- `island`: filtra por isla\n'
        '- `type`: filtra por tipo de transacción\n'
        '- `category`: filtra por categoría\n\n'
        '**Ordenamiento disponible:**\n'
        '- `date`\n'
        '- `created_at`\n\n'
        'También se pueden utilizar filtros por fecha como '
        '`date__gte` y `date__lte` para consultar un rango de transacciones.'
    ),
    parameters=[
        {
            'name': 'island',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
            'description': 'Filtra las transacciones por isla.',
        },
        {
            'name': 'type',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
                'enum': [
                    'deposit',
                    'withdrawal',
                    'expense',
                    'buy',
                    'sell',
                ],
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
            'name': 'date__gte',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
                'format': 'date',
            },
            'description': 'Fecha mínima de las transacciones.',
        },
        {
            'name': 'date__lte',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
                'format': 'date',
            },
            'description': 'Fecha máxima de las transacciones.',
        },
        {
            'name': 'ordering',
            'in': 'query',
            'required': False,
            'schema': {
                'type': 'string',
                'enum': [
                    'date',
                    '-date',
                    'created_at',
                    '-created_at',
                ],
            },
            'description': 'Campo por el que se ordenan los resultados.',
        },
    ],
    responses={
        200: {
            'description': 'Lista paginada de transacciones.',
            'content': {
                'application/json': {
                    'example': {
                        'count': 2,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': '550e8400-e29b-41d4-a716-446655440000',
                                'island': '650e8400-e29b-41d4-a716-446655440000',
                                'type': 'deposit',
                                'date': '2026-01-15',
                                'amount': '1000.00',
                                'quantity': None,
                                'price_at_tx': None,
                                'category': None,
                                'note': 'Depósito inicial',
                                'created_at': '2026-01-15T10:30:00Z',
                                'updated_at': '2026-01-15T10:30:00Z',
                            }
                        ],
                    }
                }
            },
        },
    },
)


TRANSACTION_RETRIEVE_SCHEMA = dict(
    tags=['transactions'],
    summary='Obtener transacción',
    description=(
        'Obtiene los detalles de una transacción perteneciente al usuario '
        'autenticado.'
    ),
    responses={
        200: {
            'description': 'Detalles de la transacción.',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'island': '650e8400-e29b-41d4-a716-446655440000',
                        'type': 'deposit',
                        'date': '2026-01-15',
                        'amount': '1000.00',
                        'quantity': None,
                        'price_at_tx': None,
                        'category': None,
                        'note': 'Depósito inicial',
                        'created_at': '2026-01-15T10:30:00Z',
                        'updated_at': '2026-01-15T10:30:00Z',
                    }
                }
            },
        },
        404: {
            'description': 'Transacción no encontrada o no pertenece al usuario autenticado.',
        },
    },
)


TRANSACTION_CREATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Crear transacción',
    description=(
        'Crea una nueva transacción asociada al usuario autenticado. '
        'El usuario solo puede crear transacciones sobre sus propias islas.\n\n'
        '**Islas de efectivo (`cash`):**\n'
        '- Solo aceptan `deposit`, `withdrawal` y `expense`.\n'
        '- `amount` es requerido.\n'
        '- `quantity` y `price_at_tx` no aplican.\n\n'
        '**Islas de activos (`asset`):**\n'
        '- Solo aceptan `buy` y `sell`.\n'
        '- `quantity` y `price_at_tx` son requeridos.\n'
        '- `amount` no aplica.\n\n'
        '`category` solamente puede utilizarse cuando `type` es `expense`.\n\n'
        'Las operaciones de retiro, gasto y venta se validan contra las '
        'tenencias o saldo disponible de la isla.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'island': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'ID de una isla perteneciente al usuario autenticado.',
                },
                'type': {
                    'type': 'string',
                    'enum': [
                        'deposit',
                        'withdrawal',
                        'expense',
                        'buy',
                        'sell',
                    ],
                },
                'date': {
                    'type': 'string',
                    'format': 'date',
                },
                'amount': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'quantity': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'price_at_tx': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'category': {
                    'type': 'string',
                    'nullable': True,
                },
                'note': {
                    'type': 'string',
                    'nullable': True,
                },
            },
            'required': [
                'island',
                'type',
                'date',
            ],
        }
    },
    responses={
        201: {
            'description': 'Transacción creada correctamente.',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'island': '650e8400-e29b-41d4-a716-446655440000',
                        'type': 'deposit',
                        'date': '2026-01-15',
                        'amount': '1000.00',
                        'quantity': None,
                        'price_at_tx': None,
                        'category': None,
                        'note': 'Depósito inicial',
                        'created_at': '2026-01-15T10:30:00Z',
                        'updated_at': '2026-01-15T10:30:00Z',
                    }
                }
            },
        },
        400: {
            'description': (
                'Datos inválidos o la transacción no cumple las reglas '
                'de la isla.'
            ),
        },
    },
)


TRANSACTION_UPDATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Actualizar transacción',
    description=(
        'Actualiza completamente una transacción perteneciente al usuario '
        'autenticado.\n\n'
        'Se vuelven a aplicar las reglas de validación según el tipo de isla '
        'y de transacción. En operaciones de retiro, gasto o venta se verifica '
        'nuevamente que exista saldo o cantidad suficiente.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'island': {
                    'type': 'string',
                    'format': 'uuid',
                },
                'type': {
                    'type': 'string',
                    'enum': [
                        'deposit',
                        'withdrawal',
                        'expense',
                        'buy',
                        'sell',
                    ],
                },
                'date': {
                    'type': 'string',
                    'format': 'date',
                },
                'amount': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'quantity': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'price_at_tx': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'category': {
                    'type': 'string',
                    'nullable': True,
                },
                'note': {
                    'type': 'string',
                    'nullable': True,
                },
            },
            'required': [
                'island',
                'type',
                'date',
            ],
        }
    },
    responses={
        200: {
            'description': 'Transacción actualizada correctamente.',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'island': '650e8400-e29b-41d4-a716-446655440000',
                        'type': 'expense',
                        'date': '2026-01-15',
                        'amount': '150.00',
                        'quantity': None,
                        'price_at_tx': None,
                        'category': 'food',
                        'note': 'Comida',
                        'created_at': '2026-01-15T10:30:00Z',
                        'updated_at': '2026-01-16T10:30:00Z',
                    }
                }
            },
        },
        400: {
            'description': (
                'Datos inválidos o la transacción actualizada no cumple '
                'las reglas de la isla.'
            ),
        },
        404: {
            'description': 'Transacción no encontrada o no pertenece al usuario autenticado.',
        },
    },
)


TRANSACTION_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['transactions'],
    summary='Actualizar parcialmente una transacción',
    description=(
        'Actualiza parcialmente una transacción perteneciente al usuario '
        'autenticado. Los campos omitidos conservan su valor actual.\n\n'
        'Las reglas de validación de la transacción se vuelven a evaluar '
        'utilizando tanto los valores enviados como los valores existentes.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'island': {
                    'type': 'string',
                    'format': 'uuid',
                },
                'type': {
                    'type': 'string',
                    'enum': [
                        'deposit',
                        'withdrawal',
                        'expense',
                        'buy',
                        'sell',
                    ],
                },
                'date': {
                    'type': 'string',
                    'format': 'date',
                },
                'amount': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'quantity': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'price_at_tx': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'category': {
                    'type': 'string',
                    'nullable': True,
                },
                'note': {
                    'type': 'string',
                    'nullable': True,
                },
            },
        }
    },
    responses={
        200: {
            'description': 'Transacción actualizada correctamente.',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'island': '650e8400-e29b-41d4-a716-446655440000',
                        'type': 'expense',
                        'date': '2026-01-15',
                        'amount': '150.00',
                        'quantity': None,
                        'price_at_tx': None,
                        'category': 'food',
                        'note': 'Comida',
                        'created_at': '2026-01-15T10:30:00Z',
                        'updated_at': '2026-01-16T10:30:00Z',
                    }
                }
            },
        },
        400: {
            'description': (
                'Datos inválidos o la transacción actualizada no cumple '
                'las reglas de la isla.'
            ),
        },
        404: {
            'description': 'Transacción no encontrada o no pertenece al usuario autenticado.',
        },
    },
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
            'description': 'Transacción no encontrada o no pertenece al usuario autenticado.',
        },
    },
)