from ninja import Schema


class RegisterSuccessSchema(Schema):
    success: bool
    message: str
