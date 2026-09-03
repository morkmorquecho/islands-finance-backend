from core.docs.response import RESPONSE_404


ISLAND_TEMPLATE_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar plantillas de islas',
    description=(
        'Obtiene el catálogo de plantillas de islas disponible para el usuario '
        'autenticado. Las plantillas son de solo lectura y son administradas '
        'mediante Django Admin. Permite filtrar por tipo de isla y buscar por '
        'nombre o símbolo.'
    ),
    parameters=[
        {
            'name': 'kind',
            'in': 'query',
            'description': 'Filtra las plantillas por tipo de isla.',
            'schema': {
                'type': 'string',
                'enum': ['cash', 'asset'],
            },
        },
        {
            'name': 'search',
            'in': 'query',
            'description': 'Busca plantillas por nombre o símbolo.',
            'schema': {
                'type': 'string',
            },
        },
    ],
    responses={
        200: {
            'description': 'Listado paginado de plantillas de islas',
            'content': {
                'application/json': {
                    'example': {
                        'count': 2,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': '550e8400-e29b-41d4-a716-446655440000',
                                'name': 'Nu',
                                'kind': 'cash',
                                'symbol': None,
                                'default_rate': '0.1000',
                                'logo_url': 'https://example.com/nu.png',
                                'color': '#FFFFFF',
                            }
                        ],
                    }
                }
            }
        }
    }
)


ISLAND_TEMPLATE_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener plantilla de isla',
    description=(
        'Obtiene los detalles de una plantilla de isla específica por su '
        'identificador.'
    ),
    responses={
        200: {
            'description': 'Detalles de la plantilla de isla',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'name': 'Nu',
                        'kind': 'cash',
                        'symbol': None,
                        'default_rate': '0.1000',
                        'logo_url': 'https://example.com/nu.png',
                        'color': '#FFFFFF',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


MODULE_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar módulos',
    description=(
        'Obtiene los módulos pertenecientes al usuario autenticado.'
    ),
    responses={
        200: {
            'description': 'Listado paginado de módulos',
            'content': {
                'application/json': {
                    'example': {
                        'count': 1,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': '550e8400-e29b-41d4-a716-446655440000',
                                'name': 'Mis inversiones',
                                'type': 'investment',
                                'order': 0,
                                'total_value': '25000.00',
                                'created_at': '2026-09-03T12:00:00Z',
                                'updated_at': '2026-09-03T12:00:00Z',
                            }
                        ],
                    }
                }
            }
        }
    }
)


MODULE_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener módulo',
    description=(
        'Obtiene los detalles de un módulo perteneciente al usuario '
        'autenticado.'
    ),
    responses={
        200: {
            'description': 'Detalles del módulo',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'name': 'Mis inversiones',
                        'type': 'investment',
                        'order': 0,
                        'total_value': '25000.00',
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


MODULE_CREATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Crear módulo',
    description=(
        'Crea un nuevo módulo para el usuario autenticado. '
        'El usuario propietario se obtiene directamente de la sesión y no '
        'puede ser proporcionado por el cliente.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'example': 'Mis inversiones',
                },
                'type': {
                    'type': 'string',
                    'example': 'investment',
                },
                'order': {
                    'type': 'integer',
                    'example': 0,
                },
            },
            'required': ['name', 'type'],
        }
    },
    responses={
        201: {
            'description': 'Módulo creado correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'name': 'Mis inversiones',
                        'type': 'investment',
                        'order': 0,
                        'total_value': '0.00',
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        }
    }
)


MODULE_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar módulo',
    description=(
        'Actualiza completamente un módulo perteneciente al usuario '
        'autenticado.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'example': 'Mis inversiones',
                },
                'type': {
                    'type': 'string',
                    'example': 'investment',
                },
                'order': {
                    'type': 'integer',
                    'example': 0,
                },
            },
            'required': ['name', 'type'],
        }
    },
    responses={
        200: {
            'description': 'Módulo actualizado correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'name': 'Mis inversiones',
                        'type': 'investment',
                        'order': 0,
                        'total_value': '25000.00',
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


MODULE_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar parcialmente un módulo',
    description=(
        'Actualiza parcialmente un módulo perteneciente al usuario '
        'autenticado.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'example': 'Mis inversiones',
                },
                'type': {
                    'type': 'string',
                    'example': 'investment',
                },
                'order': {
                    'type': 'integer',
                    'example': 0,
                },
            }
        }
    },
    responses={
        200: {
            'description': 'Módulo actualizado correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'name': 'Mis inversiones',
                        'type': 'investment',
                        'order': 0,
                        'total_value': '25000.00',
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


MODULE_DESTROY_SCHEMA = dict(
    tags=['portfolio'],
    summary='Eliminar módulo',
    description=(
        'Elimina un módulo perteneciente al usuario autenticado.'
    ),
    responses={
        204: {
            'description': 'Módulo eliminado correctamente. No se devuelve contenido.'
        },
        404: RESPONSE_404,
    }
)


ISLAND_LIST_SCHEMA = dict(
    tags=['portfolio'],
    summary='Listar islas',
    description=(
        'Obtiene las islas pertenecientes al usuario autenticado. '
        'Permite filtrar los resultados por módulo y tipo de isla.'
    ),
    parameters=[
        {
            'name': 'module',
            'in': 'query',
            'description': 'Filtra las islas por el ID del módulo.',
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        },
        {
            'name': 'kind',
            'in': 'query',
            'description': 'Filtra las islas por tipo.',
            'schema': {
                'type': 'string',
                'enum': ['cash', 'asset'],
            },
        },
    ],
    responses={
        200: {
            'description': 'Listado paginado de islas',
            'content': {
                'application/json': {
                    'example': {
                        'count': 1,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': '550e8400-e29b-41d4-a716-446655440000',
                                'module': '650e8400-e29b-41d4-a716-446655440000',
                                'template': None,
                                'name': 'Ahorro',
                                'kind': 'cash',
                                'currency': 'MXN',
                                'symbol': None,
                                'asset_type': None,
                                'interest_type': 'compound',
                                'annual_rate': '0.1000',
                                'color': '#FFFFFF',
                                'summary': {
                                    'deposited': '10000.00',
                                    'currency': 'MXN',
                                    'value_native': '10500.00',
                                    'value_base': '10500.00',
                                    'interest_earned': '500.00',
                                },
                                'created_at': '2026-09-03T12:00:00Z',
                                'updated_at': '2026-09-03T12:00:00Z',
                            }
                        ],
                    }
                }
            }
        }
    }
)


ISLAND_RETRIEVE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Obtener isla',
    description=(
        'Obtiene los detalles de una isla perteneciente al usuario '
        'autenticado.'
    ),
    responses={
        200: {
            'description': 'Detalles de la isla',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'module': '650e8400-e29b-41d4-a716-446655440000',
                        'template': None,
                        'name': 'Ahorro',
                        'kind': 'cash',
                        'currency': 'MXN',
                        'symbol': None,
                        'asset_type': None,
                        'interest_type': 'compound',
                        'annual_rate': '0.1000',
                        'color': '#FFFFFF',
                        'summary': {
                            'deposited': '10000.00',
                            'currency': 'MXN',
                            'value_native': '10500.00',
                            'value_base': '10500.00',
                            'interest_earned': '500.00',
                        },
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


ISLAND_CREATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Crear isla',
    description=(
        'Crea una nueva isla para el usuario autenticado. '
        'El usuario propietario se obtiene de la sesión.\n\n'
        '**Uso de templates:** Si se proporciona un template, algunos valores '
        'pueden completarse automáticamente a partir de este: tipo, nombre, '
        'color y, según el tipo, tasa anual, símbolo y tipo de activo.\n\n'
        '**Islas de efectivo:** Requieren una moneda.\n\n'
        '**Islas de activos:** Requieren un símbolo y un tipo de activo '
        '(crypto o stock).'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'module': {
                    'type': 'string',
                    'format': 'uuid',
                    'example': '650e8400-e29b-41d4-a716-446655440000',
                },
                'template': {
                    'type': 'string',
                    'format': 'uuid',
                    'nullable': True,
                    'example': '750e8400-e29b-41d4-a716-446655440000',
                },
                'name': {
                    'type': 'string',
                    'example': 'Ahorro',
                },
                'kind': {
                    'type': 'string',
                    'enum': ['cash', 'asset'],
                    'example': 'cash',
                },
                'currency': {
                    'type': 'string',
                    'nullable': True,
                    'example': 'MXN',
                },
                'symbol': {
                    'type': 'string',
                    'nullable': True,
                    'example': 'SPY',
                },
                'asset_type': {
                    'type': 'string',
                    'enum': ['crypto', 'stock'],
                    'nullable': True,
                    'example': 'stock',
                },
                'interest_type': {
                    'type': 'string',
                    'enum': ['simple', 'compound'],
                    'nullable': True,
                    'example': 'compound',
                },
                'annual_rate': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                    'example': '0.1000',
                },
                'color': {
                    'type': 'string',
                    'example': '#FFFFFF',
                },
            },
            'required': ['module'],
        }
    },
    responses={
        201: {
            'description': 'Isla creada correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'module': '650e8400-e29b-41d4-a716-446655440000',
                        'template': None,
                        'name': 'Ahorro',
                        'kind': 'cash',
                        'currency': 'MXN',
                        'symbol': None,
                        'asset_type': None,
                        'interest_type': 'compound',
                        'annual_rate': '0.1000',
                        'color': '#FFFFFF',
                        'summary': {
                            'deposited': '0.00',
                            'currency': 'MXN',
                            'value_native': '0.00',
                            'value_base': '0.00',
                            'interest_earned': '0.00',
                        },
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        }
    }
)


ISLAND_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar isla',
    description=(
        'Actualiza completamente una isla perteneciente al usuario '
        'autenticado.\n\n'
        'Para islas de efectivo se requiere una moneda. Para islas de activos '
        'se requiere un símbolo y un tipo de activo.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'module': {
                    'type': 'string',
                    'format': 'uuid',
                },
                'template': {
                    'type': 'string',
                    'format': 'uuid',
                    'nullable': True,
                },
                'name': {
                    'type': 'string',
                },
                'kind': {
                    'type': 'string',
                    'enum': ['cash', 'asset'],
                },
                'currency': {
                    'type': 'string',
                    'nullable': True,
                },
                'symbol': {
                    'type': 'string',
                    'nullable': True,
                },
                'asset_type': {
                    'type': 'string',
                    'enum': ['crypto', 'stock'],
                    'nullable': True,
                },
                'interest_type': {
                    'type': 'string',
                    'enum': ['simple', 'compound'],
                    'nullable': True,
                },
                'annual_rate': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'color': {
                    'type': 'string',
                },
            },
            'required': ['module'],
        }
    },
    responses={
        200: {
            'description': 'Isla actualizada correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'module': '650e8400-e29b-41d4-a716-446655440000',
                        'template': None,
                        'name': 'Ahorro',
                        'kind': 'cash',
                        'currency': 'MXN',
                        'symbol': None,
                        'asset_type': None,
                        'interest_type': 'compound',
                        'annual_rate': '0.1000',
                        'color': '#FFFFFF',
                        'summary': {
                            'deposited': '10000.00',
                            'currency': 'MXN',
                            'value_native': '10500.00',
                            'value_base': '10500.00',
                            'interest_earned': '500.00',
                        },
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


ISLAND_PARTIAL_UPDATE_SCHEMA = dict(
    tags=['portfolio'],
    summary='Actualizar parcialmente una isla',
    description=(
        'Actualiza parcialmente una isla perteneciente al usuario '
        'autenticado.\n\n'
        'Las validaciones de efectivo y activos se aplican en función del '
        'tipo de isla resultante.'
    ),
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'module': {
                    'type': 'string',
                    'format': 'uuid',
                },
                'template': {
                    'type': 'string',
                    'format': 'uuid',
                    'nullable': True,
                },
                'name': {
                    'type': 'string',
                },
                'kind': {
                    'type': 'string',
                    'enum': ['cash', 'asset'],
                },
                'currency': {
                    'type': 'string',
                    'nullable': True,
                },
                'symbol': {
                    'type': 'string',
                    'nullable': True,
                },
                'asset_type': {
                    'type': 'string',
                    'enum': ['crypto', 'stock'],
                    'nullable': True,
                },
                'interest_type': {
                    'type': 'string',
                    'enum': ['simple', 'compound'],
                    'nullable': True,
                },
                'annual_rate': {
                    'type': 'string',
                    'format': 'decimal',
                    'nullable': True,
                },
                'color': {
                    'type': 'string',
                },
            }
        }
    },
    responses={
        200: {
            'description': 'Isla actualizada correctamente',
            'content': {
                'application/json': {
                    'example': {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'module': '650e8400-e29b-41d4-a716-446655440000',
                        'template': None,
                        'name': 'Ahorro',
                        'kind': 'cash',
                        'currency': 'MXN',
                        'symbol': None,
                        'asset_type': None,
                        'interest_type': 'compound',
                        'annual_rate': '0.1000',
                        'color': '#FFFFFF',
                        'summary': {
                            'deposited': '10000.00',
                            'currency': 'MXN',
                            'value_native': '10500.00',
                            'value_base': '10500.00',
                            'interest_earned': '500.00',
                        },
                        'created_at': '2026-09-03T12:00:00Z',
                        'updated_at': '2026-09-03T12:00:00Z',
                    }
                }
            }
        },
        404: RESPONSE_404,
    }
)


ISLAND_DESTROY_SCHEMA = dict(
    tags=['portfolio'],
    summary='Eliminar isla',
    description=(
        'Elimina una isla perteneciente al usuario autenticado.'
    ),
    responses={
        204: {
            'description': 'Isla eliminada correctamente. No se devuelve contenido.'
        },
        404: RESPONSE_404,
    }
)