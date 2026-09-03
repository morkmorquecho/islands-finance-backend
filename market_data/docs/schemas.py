from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

ASSET_SEARCH_SCHEMA = dict(
    tags=['market_data'],
    summary='Buscar activos',
    description=(
        'Busca activos financieros según el tipo especificado.\n\n'
        '**Tipos de activo:**\n'
        '- `crypto`: Busca criptomonedas utilizando CoinGecko.\n'
        '- `stock`: Busca acciones utilizando Twelve Data.\n\n'
        'La búsqueda devuelve como máximo 10 resultados.'
    ),
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Texto utilizado para buscar el activo.',
            example='bitcoin',
        ),
        OpenApiParameter(
            name='asset_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Tipo de activo a buscar.',
            enum=['crypto', 'stock'],
            example='crypto',
        ),
    ],
    responses={
        200: {
            'description': 'Resultados de búsqueda de activos',
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
                                {
                                    'id': 'ethereum',
                                    'name': 'Ethereum',
                                    'symbol': 'eth',
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
                                {
                                    'symbol': 'AAPL',
                                    'name': 'Apple Inc',
                                    'exchange': 'NASDAQ',
                                    'currency': 'USD',
                                },
                            ],
                        },
                    },
                }
            },
        },
        400: {
            'description': 'Parámetros de búsqueda inválidos',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'q and asset_type (crypto|stock) are required'
                    }
                }
            },
        },
    },
)