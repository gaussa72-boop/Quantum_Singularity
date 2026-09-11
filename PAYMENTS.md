# Quantum Payments & Credits

Shared prepaid-credit contract. Verified idempotent payment events only. Stripe/crypto are external provider adapters; never store crypto private keys or custody funds. Production balances and ledger entries must be transactional and persistent. Reserve credits before paid generation and release on failure. Secrets stay in deployment secret management.
