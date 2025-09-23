from ninja import Schema


class RegisterSuccessSchema(Schema):
    success: bool
    message: str


class ErrorSchema(Schema):
    detail: str
