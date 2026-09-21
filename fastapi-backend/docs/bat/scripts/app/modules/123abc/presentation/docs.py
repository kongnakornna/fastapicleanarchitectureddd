"""123Abc presentation docs — OpenAPI metadata"""

RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ / created",
    "content": {
        "application/json": {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "code": "X-001", "name": "Sample",
                "amount": "100.00", "currency": "THB",
                "status": "ACTIVE", "version": 1,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    },
}

RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {"application/json": {"example": {"detail": "amount must be >= 0"}}},
}

RESPONSE_ERROR_404 = {
    "description": "ไม่พบ entity",
    "content": {"application/json": {"example": {"detail": "123abc not found"}}},
}

RESPONSE_ERROR_409 = {
    "description": "Conflict (duplicate code / version)",
    "content": {"application/json": {"example": {"detail": "code already exists"}}},
}

RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {"application/json": {"example": {"detail": "invalid input"}}},
}