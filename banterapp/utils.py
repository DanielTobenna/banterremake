import uuid

def generate_ref_code():
	code= str(uuid.uuid4()).replace("-", "")[:12]
	return code

def transaction_hash_code():
	transaction_hash = str(uuid.uuid4()).replace("-", "")[:16]
	return transaction_hash
