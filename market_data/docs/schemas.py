from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)


ASSET_SEARCH_SCHEMA = dict(
    tags=['market_data'],
    summary='Buscar activos financieros',
    description=(
        'Busca activos por nombre, símbolo o texto relacionado según el tipo '
        'de activo seleccionado.\n\n'
        '**Tipos de activo soportados:**\n'
        '- `crypto`: busca criptomonedas mediante CoinGecko. La respuesta '
        'utiliza el `id` de CoinGecko como identificador del activo.\n'
        '- `stock`: busca acciones mediante Twelve Data. La respuesta utiliza '
        'el `symbol` de Twelve Data como identificador del activo.\n\n'
        'La búsqueda devuelve como máximo 10 resultados.'
    ),

    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Texto utilizado para buscar el activo.',
            examples=[
                OpenApiExample(
                    'Bitcoin',
                    value='bitcoin',
                ),
                OpenApiExample(
                    'Apple',
                    value='apple',
                ),
            ],
        ),
        OpenApiParameter(
            name='asset_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Tipo de activo que se desea buscar.',
            enum=['crypto', 'stock'],
            examples=[
                OpenApiExample(
                    'Criptomonedas',
                    value='crypto',
                ),
                OpenApiExample(
                    'Acciones',
                    value='stock',
                ),
            ],
        ),
    ],

    responses={
        200: {
            'description': 'Resultados de búsqueda encontrados.',
            'content': {
                'application/json': {
                    'examples': {
                        'crypto': {
                            'summary': 'Búsqueda de criptomonedas',
                            'value': [
                                {
                                    'id': 'bitcoin',
                                    'name': 'Bitcoin',
                                    'symbol': 'btc',
                                    'currency': 'USD',
                                },
                            ],
                        },
                        'stock': {
                            'summary': 'Búsqueda de acciones',
                            'value': [
                                {
                                    'symbol': 'AMXL.MX',
                                    'name': 'America Movil',
                                    'exchange': 'BMV',
                                    'currency': 'MXN',
                                },
                            ],
                        },
                    },
                },
            },
        },
        400: {
            'description': 'Parámetros de búsqueda inválidos o faltantes.',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'q and asset_type (crypto|stock) are required',
                    },
                },
            },
        },
    },
)