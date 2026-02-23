from typing import List, Union
import hashlib

class Utils:
    def generate_hash_key(payload: List[Union[str, int]]) -> str:
        params_str = "".join(str(param) for param in payload)
        hash_value = hashlib.sha256(params_str.encode()).hexdigest()
        return hash_value