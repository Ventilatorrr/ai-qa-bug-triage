from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one number.")

        return password
        