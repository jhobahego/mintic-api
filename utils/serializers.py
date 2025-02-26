"""
Utilidades para serializar objetos de MongoDB a formatos compatibles con JSON
"""
from bson import ObjectId
from typing import Dict, Any, List, Union

def serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializa un documento de MongoDB para que sea compatible con JSON,
    convirtiendo ObjectId a strings.
    
    Args:
        doc: Documento de MongoDB
        
    Returns:
        Documento serializado
    """
    if doc is None:
        return None
    
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_mongo_doc(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_mongo_doc(item) if isinstance(item, dict) else 
                str(item) if isinstance(item, ObjectId) else item 
                for item in value
            ]
        else:
            result[key] = value
    return result

def serialize_mongo_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Serializa una lista de documentos de MongoDB para que sean compatibles con JSON,
    convirtiendo ObjectId a strings.
    
    Args:
        docs: Lista de documentos de MongoDB
        
    Returns:
        Lista de documentos serializados
    """
    return [serialize_mongo_doc(doc) for doc in docs]
