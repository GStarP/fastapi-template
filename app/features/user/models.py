from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=64)
    password = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:  # type: ignore
        table = "user"
        ordering = ["-created_at"]
