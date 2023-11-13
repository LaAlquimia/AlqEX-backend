from core.currency import TokenParams
from cryptocoins.utils.register import register_token

ALQ = 420
CODE = 'ALQ'
DECIMALS = 4
BLOCKCHAINS = {
    'BNB': TokenParams(
        symbol=CODE,
        contract_address='0x4b48c0db4e460c894bfc031d602a5c3b57a26857',
        decimal_places=18,
    ),
}
ALQ_CURRENCY = register_token(ALQ, CODE, BLOCKCHAINS)
